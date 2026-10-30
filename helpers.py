"""Shared number-theoretic helpers for the companion book."""
import math
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

# House style for figures
plt.rcParams.update({
    "figure.dpi": 130, "savefig.dpi": 160, "font.family": "serif",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.alpha": 0.25, "axes.titlesize": 11, "axes.labelsize": 10,
})
SLATE, BLUE, RUST, GREEN, GOLD, GREY = "#2f4858", "#1f5f8b", "#a0652d", "#3f8a6b", "#c9a227", "#8a8f94"

def sieve(n):
    """Boolean numpy array isprime[0..n]."""
    s = np.ones(n + 1, dtype=bool); s[:2] = False
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = False
    return s

_SMALL = sieve(20000)
PRIMES = np.flatnonzero(_SMALL)

def nu(h, p):
    return len({x % p for x in h})

def local_factor(h, p):
    k = len(h)
    return (1 - nu(h, p) / p) * (1 - 1 / p) ** (-k)

def singular_series(h, P=20000):
    """Product of local factors over primes <= P for a distinct tuple.

    For an admissible tuple, the omitted product is
    1 + O_k(1 / (P log P)) once P >= 2*k and no prime greater
    than P divides a tuple difference. Without that condition,
    omitted collision primes can contribute O_k(1/p) corrections.
    The plots use this finite product as a numerical approximation.
    """
    if len(set(h)) != len(h):
        raise ValueError("The singular series requires distinct entries")
    if P < 2:
        raise ValueError("The prime cutoff must be at least 2")
    k = len(h); s = 1.0
    disc = 1
    for i in range(k):
        for j in range(i + 1, k):
            disc *= abs(h[i] - h[j])
    primes = PRIMES if P <= 20000 else np.flatnonzero(sieve(int(P)))
    for p in primes:
        if p > P:
            break
        if p <= 2 * k or disc % p == 0:
            f = local_factor(h, int(p))
            if f == 0:
                return 0.0
            s *= f
        else:
            s *= (1 - k / p) * (1 - 1 / p) ** (-k)
    return s

def c_p(h, p):
    """c_p = (nu-1)/(p-nu) for admissible h at p."""
    n = nu(h, p)
    if n == p:
        raise ValueError("c_p is defined only for a shape admissible at p")
    return (n - 1) / (p - n)

def distinct_prime_factors(n):
    """Distinct prime factors of a positive integer, in increasing order."""
    if n < 1 or int(n) != n:
        raise ValueError("Expected a positive integer")
    m = int(n); factors = []
    if m % 2 == 0:
        factors.append(2)
        while m % 2 == 0:
            m //= 2
    p = 3
    while p * p <= m:
        if m % p == 0:
            factors.append(p)
            while m % p == 0:
                m //= p
        p += 2
    if m > 1:
        factors.append(m)
    return factors

def dilation_ratio(h, q):
    """f_h(q) = prod_{p | q}(1+c_p), for an admissible distinct h."""
    if len(set(h)) != len(h):
        raise ValueError("The shape must have distinct entries")
    for p in np.flatnonzero(sieve(len(h))):
        if nu(h, int(p)) == p:
            raise ValueError("The undilated shape must be admissible")
    r = 1.0
    for p in distinct_prime_factors(q):
        r *= 1 + c_p(h, p)
    return r

def tuple_count(isprime, h, q, lo=0, hi=None):
    """N_h(q; (lo, hi]) = #{lo < a <= hi : a + h_j q all prime}."""
    hi = q if hi is None else hi
    a = np.arange(lo + 1, hi + 1)
    ok = np.ones(len(a), dtype=bool)
    for hj in h:
        ok &= isprime[a + hj * q]
    return int(ok.sum())

def log_integral(h, q, u=0.0, v=None, n=2000):
    """I_h(q;(u,v]) = int_u^v dt / prod_j log(t + h_j q), Simpson's rule."""
    v = q if v is None else v
    t = np.linspace(u, v, 2 * n + 1)
    g = np.ones_like(t)
    for hj in h:
        g /= np.log(t + hj * q)
    w = np.ones_like(t); w[1:-1:2] = 4; w[2:-1:2] = 2
    return float((v - u) / (6 * n) * np.sum(w * g))

def phi(q):
    r = q
    for p in distinct_prime_factors(q):
        r -= r // p
    return r

def lift_scale(q):
    """ell_q = (phi(q)/q) log q."""
    return phi(q) / q * math.log(q)

def reduced_residues(q, lo=0, hi=None):
    hi = q if hi is None else hi
    a = np.arange(lo + 1, hi + 1)
    return a[np.gcd(a, q) == 1]

def lift_indices(isprime, q, a_values, m_max):
    """For each reduced residue a, the list of m in [1, m_max] with a + m q prime (as a ragged list)."""
    m = np.arange(1, m_max + 1)
    out = []
    for a in a_values:
        out.append(m[isprime[a + m * q]])
    return out
