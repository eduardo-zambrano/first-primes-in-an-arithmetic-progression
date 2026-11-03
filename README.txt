The First Primes in an Arithmetic Progression
A reader's companion (Quarto book) to "Simultaneous prime-tuple asymptotics and quenched
Poisson laws for almost all moduli", Eduardo Zambrano, October 2026.

Build:   ./render.sh          (renders HTML + PDF outside Dropbox, then syncs _book/)
Open:    _book/index.html     (the "Download PDF" button in the sidebar serves the PDF)
Source:  index.qmd, 01-*.qmd ... 11-*.qmd, references.qmd, A-*.qmd, B-*.qmd, references.bib
Code:    helpers.py holds the number-theoretic helpers. Empirical prime data
         are generally recomputed by sieving at render time. Figure 3.2 uses the
         saved counts and predictions in figures/prime_tuple_panels/, with a
         regeneration script and a renderer in that directory. Other figures are schematic
         diagrams or labelled finite Euler-product approximations.
Style:   custom.scss (slate/parchment palette), Palatino body text, MathJax 3.
         MathJax and an ES6 polyfill load synchronously from jsDelivr and cdnjs,
         so pages opened offline or on a slow link take a few seconds to appear;
         self-hosting MathJax (resources + html-math-method url) would fix this.
House:   no em-dashes, no inline URLs (use pandoc citations), explanations
         before theorem statements, "Hardy-Littlewood prediction" for what the
         paper proves and "conjecture" only for unproved hypotheses. Theorem 1.1 is
         "Prime-tuple asymptotics for almost all moduli" (chapter 3 title: "Prime tuples
         for almost all moduli"); running text calls it "the tuple theorem", an alias
         introduced in chapter 3. The Analytic Input is the only other "counting theorem".
Kernel:  Quarto runs the Python cells with the Jupyter python3 kernel
         (anaconda3/envs/GSE_544); matplotlib mathtext limits figure labels to
         \mathbf{...}, \mathbb{...}, \leq, etc. (no \mathfrak, \operatorname, \bmod).
Repo:    git repository in this directory (the paper above it is not tracked).
         Remote: https://github.com/eduardo-zambrano/first-primes-in-an-arithmetic-progression
         Build output (_book, .quarto, *_files, __pycache__) is ignored; only sources are
         committed. Note that .git lives inside Dropbox: commit from one machine at a time.
Deploy:  .github/workflows/deploy.yml renders the book on every push to main (Quarto +
         TinyTeX, Python 3.11 with numpy/matplotlib/jupyter, TeX Gyre fonts) and publishes
         _book to GitHub Pages at
         https://eduardo-zambrano.github.io/first-primes-in-an-arithmetic-progression/
Access:  The site is password-protected with StatiCrypt v3 (as the earlier SET Quarto sites
         were). The step runs only when the repository secret SITE_PASSWORD exists; set or
         change it with  gh secret set SITE_PASSWORD --repo eduardo-zambrano/first-primes-in-an-arithmetic-progression
         and re-run the workflow. Deleting the secret publishes the site open. When
         protected, search.json is removed (it would expose the text); the PDF download is
         left reachable by the author's decision (30 October 2026). The --short flag is
         required: StatiCrypt otherwise prompts for passwords under 14 characters and
         silently skips encryption on CI. The workflow fails if any page is unencrypted.
Status:  3 November 2026. Theorem 1.1 renamed on 1 November to match the paper (see House);
         preface wording tightened on 1 and 3 November; section 1.3 says Hardy and Littlewood
         "proposed" how to account for local correlations. Last clean render 3 November.
         Literature comparisons (MRSTT, KWX) added to chapter 3; Appendix B corrected.
         Preprint-provenance notes in chapters 4 and 10 remain commented out.
         No analytics or visitor tracking on the site, by the author's decision (3 November);
         GitHub Insights > Traffic counts visits to the repository page only, not the site.
