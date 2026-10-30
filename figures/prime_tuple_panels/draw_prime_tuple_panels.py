"""Compact prime-tuple tables for a six-inch-wide book figure.

Place scale-counts.csv and comparison-metadata.json beside this script, then
call build_figure() from a Quarto Python chunk. The returned Matplotlib Figure
remains open. The command-line entry point also accepts --data-dir and saves
PNG, vector PDF, and SVG review copies without changing the input data.

Predicted counts are rounded only in cell text. Colours and column maxima use
the full-precision predictions. The caption should define the three windows,
the ordered count pairs, the rounding convention, and the displayed maximum.
"""

from pathlib import Path
import argparse
import csv
import json

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, Normalize, to_rgb
from matplotlib.patches import Rectangle
import numpy as np


SCALES = (1_000_000, 10_000_000)
WINDOWS = ("full", "first_half", "second_half")
WINDOW_LABELS = ("Full interval", "First half", "Second half")
EXPECTED_MODULI = {
    1_000_000: (1025895, 1163047, 1375881, 1572178, 1765286, 1909377),
    10_000_000: (10121385, 11630514, 13758805, 15721824, 17652866, 19093875),
}
INK = "#293d49"
PANEL_GAP = 10.2 / 72  # One count-row height, in inches.
WIDTH, HEIGHT = 6.0, 5.95 + PANEL_GAP
COUNT_FONT_SIZE = 8.0
DISPLAY_ERROR_LIMIT = 5.0
CMAP = LinearSegmentedColormap.from_list(
    "absolute_relative_error", ["#fbfcfd", "#dce8f1", "#91b3cd", "#477fa5", "#1b4e74"]
)


def _luminance(rgb):
    linear = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in rgb]
    return sum(v * w for v, w in zip(linear, (0.2126, 0.7152, 0.0722)))


def _text_colour(value, norm):
    background = _luminance(CMAP(norm(value))[:3])
    dark_contrast = (background + 0.05) / (_luminance(to_rgb(INK)) + 0.05)
    white_contrast = 1.05 / (background + 0.05)
    return INK if dark_contrast >= white_contrast else "white"


def _load_panels(data_dir):
    metadata = json.loads((data_dir / "comparison-metadata.json").read_text())
    with (data_dir / "scale-counts.csv").open(newline="") as stream:
        records = list(csv.DictReader(stream))
    lookup = {}
    for record in records:
        key = (
            int(record["Q"]), int(record["q"]),
            tuple(map(int, record["shape"].split(","))), record["window"],
        )
        assert key not in lookup, f"Duplicate data record: {key}"
        lookup[key] = record
    shapes = [tuple(h) for h in metadata["shapes"]]
    assert shapes == [(1, 3, 7), (1, 5, 11), (1, 7, 13)]
    panels = []
    for q_scale in SCALES:
        all_q = [int(q) for q in metadata["moduli"][str(q_scale)]]
        assert len(all_q) == 40 and all_q == sorted(set(all_q))
        ranks = np.rint(np.linspace(0, len(all_q) - 1, 6)).astype(int)
        qs = tuple(all_q[i] for i in ranks)
        assert qs == EXPECTED_MODULI[q_scale], "The previously selected moduli must be preserved"
        counts = np.empty((9, 6), dtype=np.int64)
        predictions = np.empty((9, 6))
        errors = np.empty((9, 6))
        for si, shape in enumerate(shapes):
            for wi, window in enumerate(WINDOWS):
                row = 3 * si + wi
                for col, q in enumerate(qs):
                    record = lookup[q_scale, q, shape, window]
                    n, prediction = int(record["count"]), float(record["prediction"])
                    assert n >= 0 and np.isfinite(prediction) and prediction > 0
                    signed_error = 100 * (n / prediction - 1)
                    assert abs(signed_error - float(record["relative_error_percent"])) < 1e-9
                    counts[row, col] = n
                    predictions[row, col] = prediction
                    errors[row, col] = abs(signed_error)
            assert np.array_equal(counts[3 * si], counts[3 * si + 1] + counts[3 * si + 2])
            assert np.allclose(
                predictions[3 * si], predictions[3 * si + 1] + predictions[3 * si + 2],
                rtol=1e-10, atol=1e-10,
            )
        assert np.all(errors <= DISPLAY_ERROR_LIMIT), "A selected cell exceeds the display colour scale"
        panels.append((q_scale, qs, counts, predictions, errors))
    return shapes, panels


def _inch_text(fig, x, y, text, **kwargs):
    return fig.text(x / WIDTH, y / HEIGHT, text, **kwargs)


def build_figure(data_dir=None):
    """Return an open six-inch-wide Matplotlib Figure from the saved dataset."""
    data_dir = Path(data_dir) if data_dir is not None else Path(__file__).resolve().parent
    shapes, panels = _load_panels(data_dir)
    settings = {
        "font.family": "STIXGeneral", "mathtext.fontset": "stix", "font.size": 8,
        "axes.grid": False, "pdf.fonttype": 42, "ps.fonttype": 42,
        "savefig.bbox": None, "savefig.pad_inches": 0,
    }
    with plt.rc_context(settings):
        fig = plt.figure(figsize=(WIDTH, HEIGHT), facecolor="white")
        norm = Normalize(0, DISPLAY_ERROR_LIMIT)
        count_artists = []
        header_artists = []
        outlined_cells = []
        _inch_text(
            fig, 0.06, 5.90 + PANEL_GAP, "Each pair: (actual count, predicted count)",
            ha="left", va="top", fontsize=8, color=INK,
        )
        for panel_index, (q_scale, qs, counts, predictions, errors) in enumerate(panels):
            # Coordinates are in inches so every panel has the same print size.
            main_bottom = (3.325 + PANEL_GAP, 0.665)[panel_index]
            main_height = 2.025
            main_top = main_bottom + main_height
            table_left, table_width = 0.06, 5.88
            main_left, main_width = 0.80, 5.14
            window_width = main_left - table_left
            column_width = main_width / 6
            x_edges = np.concatenate(([0.0], window_width + np.arange(7) * column_width))
            # Both 9 pt header rows accommodate the 8 pt glyph metrics even
            # at low-DPI inline rendering; count rows retain 10.2 pt height.
            pattern_height, window_header_height = 0.125, 0.125
            count_height = (main_height / 3 - pattern_height - window_header_height) / 3
            y_edges = np.concatenate((
                [0.0], np.cumsum(np.tile(
                    [pattern_height, window_header_height, count_height, count_height, count_height], 3,
                )),
            ))
            summary_bottom, summary_height = main_bottom - 0.21, 0.18
            ax = fig.add_axes([
                table_left / WIDTH, main_bottom / HEIGHT, table_width / WIDTH, main_height / HEIGHT,
            ])
            summary = fig.add_axes([
                main_left / WIDTH, summary_bottom / HEIGHT,
                main_width / WIDTH, summary_height / HEIGHT,
            ])
            # Each pattern has a full-width heading, a separate Window header,
            # and three count rows. Header count columns remain blank.
            table_errors = np.ma.masked_all((15, 7))
            for si in range(3):
                table_errors[5 * si + 2:5 * si + 5, 1:] = errors[3 * si:3 * si + 3]
            image = ax.pcolormesh(
                x_edges, y_edges, table_errors,
                cmap=CMAP, norm=norm, shading="flat", rasterized=False,
            )
            ax.set_xlim(0, table_width)
            ax.set_ylim(main_height, 0)
            ax.set_xticks([])
            ax.set_yticks([])
            for boundary in y_edges[1:-1]:
                ax.axhline(boundary, color="white", linewidth=0.65, zorder=3)
            for boundary in x_edges[1:-1]:
                ax.axvline(boundary, color="white", linewidth=0.65, zorder=1.5)
            for spine in ax.spines.values():
                spine.set_visible(False)

            for si, shape in enumerate(shapes):
                heading_row = 5 * si
                top, bottom = y_edges[heading_row:heading_row + 2]
                ax.axhspan(top, bottom, color="#edf0f2", linewidth=0, zorder=2)
                label = ax.text(
                    0.06, (top + bottom) / 2, "Pattern: (" + ",".join(map(str, shape)) + ")",
                    ha="left", va="center", fontsize=8, weight="bold", color=INK, zorder=4,
                )
                header_artists.append((label, ax, top, bottom))
                top, bottom = y_edges[heading_row + 1:heading_row + 3]
                label = ax.text(
                    window_width - 0.06, (top + bottom) / 2, "Window",
                    ha="right", va="center", fontsize=8, weight="bold", color=INK,
                )
                header_artists.append((label, ax, top, bottom))
                for wi, window_label in enumerate(WINDOW_LABELS):
                    top, bottom = y_edges[heading_row + wi + 2:heading_row + wi + 4]
                    ax.text(
                        window_width - 0.06, (top + bottom) / 2, window_label,
                        ha="right", va="center", fontsize=8, color=INK,
                    )
            for col, q in enumerate(qs):
                center_x = main_left + (col + 0.5) * main_width / 6
                _inch_text(
                    fig, center_x, main_top + 0.075, f"{q:,}",
                    ha="center", va="bottom", fontsize=8, color=INK,
                )
            exponent = int(round(np.log10(q_scale)))
            _inch_text(
                fig, 0.06, main_top + 0.265, rf"({chr(97 + panel_index)}) $Q=10^{{{exponent}}}$",
                ha="left", va="bottom", fontsize=9, weight="bold", color=INK,
            )
            _inch_text(
                fig, main_left + main_width / 2, main_top + 0.255, "Modulus $q$",
                ha="center", va="bottom", fontsize=8, color=INK,
            )
            for row in range(9):
                display_row = 5 * (row // 3) + 2 + row % 3
                top, bottom = y_edges[display_row:display_row + 2]
                for col in range(6):
                    center_x = window_width + (col + 0.5) * column_width
                    text = ax.text(
                        center_x, (top + bottom) / 2,
                        f"({counts[row, col]}, {predictions[row, col]:.0f})",
                        ha="center", va="center", fontsize=COUNT_FONT_SIZE,
                        color=_text_colour(errors[row, col], norm),
                    )
                    count_artists.append((text, ax, x_edges[col + 1], x_edges[col + 2], top, bottom))

            maxima = errors.max(axis=0)
            largest_rows = np.argmax(errors, axis=0)
            for col, row in enumerate(largest_rows):
                # Select exactly one cell per column from unrounded errors.
                assert errors[row, col] == maxima[col]
                display_row = 5 * (int(row) // 3) + 2 + int(row) % 3
                top, bottom = y_edges[display_row:display_row + 2]
                inset_x, inset_y = 0.013, 0.007
                outline = Rectangle(
                    (x_edges[col + 1] + inset_x, top + inset_y),
                    column_width - 2 * inset_x, bottom - top - 2 * inset_y,
                    fill=False, edgecolor=_text_colour(maxima[col], norm),
                    linewidth=0.5, zorder=5,
                )
                outline.set_gid(f"largest-error-Q{q_scale}-q{qs[col]}")
                ax.add_patch(outline)
                outlined_cells.append((q_scale, qs[col], int(row)))
            summary.pcolormesh(
                np.arange(-0.5, 6, 1), [-0.5, 0.5], maxima[None, :],
                cmap=CMAP, norm=norm, shading="flat", rasterized=False,
            )
            summary.set_xlim(-0.5, 5.5)
            summary.set_ylim(-0.5, 0.5)
            summary.set_xticks([])
            summary.set_yticks([])
            for boundary in np.arange(0.5, 5.6, 1):
                summary.axvline(boundary, color="white", linewidth=0.65)
            for spine in summary.spines.values():
                spine.set_visible(False)
            _inch_text(
                fig, main_left - 0.06, summary_bottom + summary_height / 2, "Largest error",
                ha="right", va="center", fontsize=8, color=INK,
            )
            for col, value in enumerate(maxima):
                summary.text(
                    col, 0, f"{value:.1f}%", ha="center", va="center", fontsize=8.1,
                    weight="bold", color=_text_colour(value, norm),
                )

        colourbar_ax = fig.add_axes([0.80 / WIDTH, 0.30 / HEIGHT, 5.04 / WIDTH, 0.07 / HEIGHT])
        colourbar = fig.colorbar(image, cax=colourbar_ax, orientation="horizontal")
        colourbar.set_ticks([0, 1, 2, 3, 4, 5], labels=["0%", "1%", "2%", "3%", "4%", "5%"])
        colourbar.ax.tick_params(labelsize=7, length=2, width=0.4, pad=2)
        colourbar.outline.set_visible(False)
        colourbar.solids.set_rasterized(False)
        colourbar.set_label("Percentage error", fontsize=8, color=INK, labelpad=3)

        # Check actual text bounds at the physical figure size. This also draws
        # the figure without closing it, ready for display in a Quarto chunk.
        fig.canvas.draw()
        renderer = fig.canvas.get_renderer()
        assert len(outlined_cells) == 12
        assert len({(q_scale, q) for q_scale, q, _ in outlined_cells}) == 12
        for text, ax, cell_left, cell_right, top, bottom in count_artists:
            bounds = text.get_window_extent(renderer)
            lower_left = ax.transData.transform((cell_left, bottom))
            upper_right = ax.transData.transform((cell_right, top))
            assert bounds.x0 > lower_left[0] + 1, "Count label is too wide for its cell"
            assert bounds.x1 < upper_right[0] - 1, "Count label is too wide for its cell"
            assert bounds.y0 > lower_left[1], "Count label is too tall for its cell"
            assert bounds.y1 < upper_right[1], "Count label is too tall for its cell"
        assert len(header_artists) == 12
        assert sum(text.get_text() == "Window" for text, *_ in header_artists) == 6
        for text, ax, top, bottom in header_artists:
            bounds = text.get_window_extent(renderer)
            assert bounds.y0 > ax.transData.transform((0, bottom))[1], "Header extends below its row"
            assert bounds.y1 < ax.transData.transform((0, top))[1], "Header extends above its row"
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--dpi", type=int, default=300)
    args = parser.parse_args()
    plt.switch_backend("Agg")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    fig = build_figure(args.data_dir)
    with plt.rc_context({"pdf.fonttype": 42, "ps.fonttype": 42}):
        for extension in ("png", "pdf", "svg"):
            path = args.output_dir / f"prime-tuple-panels.{extension}"
            fig.savefig(path, dpi=args.dpi, facecolor="white", bbox_inches=None)
            print(path)
    plt.close(fig)


if __name__ == "__main__":
    main()
