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
         paper proves and "conjecture" only for unproved hypotheses.
Kernel:  Quarto runs the Python cells with the Jupyter python3 kernel
         (anaconda3/envs/GSE_544); matplotlib mathtext limits figure labels to
         \mathbf{...}, \mathbb{...}, \leq, etc. (no \mathfrak, \operatorname, \bmod).
