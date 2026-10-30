"""Regenerate Figure 3.2 data for the moduli saved in comparison-metadata.json.

Run with the book's Python environment. The saved moduli preserve the original
samples independently of changes to NumPy's random sampling implementation.
"""
from pathlib import Path
import csv
import json
import sys
import numpy as np

OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(OUT.parents[1]))
from helpers import sieve, dilation_ratio, log_integral


def main():
    meta = json.loads((OUT / 'comparison-metadata.json').read_text())
    shapes = [tuple(h) for h in meta['shapes']]
    cutoff = meta['singular_series_cutoff']
    primes = np.flatnonzero(sieve(cutoff))
    bases = []
    for h in shapes:
        residues = np.sort(np.array(h)[:, None] % primes[None, :], axis=0)
        occupied = 1 + np.sum(np.diff(residues, axis=0) != 0, axis=0)
        assert np.all(occupied < primes)
        bases.append(float(np.exp(np.sum(
            np.log1p(-occupied / primes) - len(h) * np.log1p(-1.0 / primes)))))
    records = []
    for Q in meta['scales']:
        qs = meta['moduli'][str(Q)]
        is_prime = sieve((1 + max(map(max, shapes))) * max(qs))
        for q in qs:
            intervals = [(0.0, float(q)), (0.0, q / 2), (q / 2, float(q))]
            for h, base in zip(shapes, bases):
                hits = is_prime[h[0] * q + 1:(h[0] + 1) * q + 1].copy()
                for hj in h[1:]:
                    hits &= is_prime[hj * q + 1:(hj + 1) * q + 1]
                left = int(np.count_nonzero(hits[:q // 2]))
                right = int(np.count_nonzero(hits[q // 2:]))
                counts = [left + right, left, right]
                singular = base * dilation_ratio(h, q)
                for name, count, (u, v) in zip(
                        ['full', 'first_half', 'second_half'], counts, intervals):
                    predicted = singular * log_integral(h, q, u=u, v=v)
                    records.append(dict(Q=Q, q=q, shape=','.join(map(str, h)),
                        window=name, count=count, prediction=predicted,
                        relative_error_percent=100 * (count / predicted - 1)))
        del is_prime, hits
    with (OUT / 'scale-counts.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(f'Wrote {len(records)} counts and predictions.')


if __name__ == '__main__':
    main()
