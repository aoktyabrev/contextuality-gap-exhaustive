"""Algebraic degree of the Lovasz theta optimum (Stage 9, block 9.a).

Two things happen here and they must not be confused.

  theta_honest  produces a high-precision value together with a MEASURED number of
                honest digits: the matching prefix of a dps run and a 2*dps run,
                minus five.  The solver's own residual is never used as the digit
                count -- that was settled in Stage 2.

  find_minpoly  searches for an integer relation among 1, t, ..., t^d by ascending
                degree, under the digit budget B(d) = floor((D - 20) / (d + 1)).
                Ascending order is what makes the first hit MINIMAL, hence
                irreducible over Q -- no separate irreducibility test is needed.

A found polynomial is a HYPOTHESIS, not a result.  Stage 2 exists because the source's
authors' PSLQ candidate at 15 digits was a false positive -- which their own paper says
plainly, having tested it and reported it as such.  It was never offered as a closed
form and nothing was withdrawn.  Here the only defence asked for by
PREREGISTRATION_STAGE9 2.4 is reproduction at doubled precision; nothing in this module
proves anything, and the word "proved" belongs only to the exact certificates of
quadc5/numfield.py.
"""
from __future__ import annotations
import subprocess, os
import numpy as np
from mpmath import mp, mpf, matrix, nstr, pslq, floor, log10, fabs

from .g6 import decode_g6, edges_of
from .theta import theta_cvxpy
from .hiprec import refine

DEGREES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 14, 16, 20, 24]
MIN_HONEST = 150
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DREADNAUT = os.path.join(ROOT, "build", "nauty2_9_3", "dreadnaut")


def _dual_start(n, edges):
    """Double-precision dual: min t s.t. t I - B >= 0, B fixed off the edges."""
    import cvxpy as cp
    Eset = set((min(i, j), max(i, j)) for (i, j) in edges)
    B = cp.Variable((n, n), symmetric=True)
    t = cp.Variable()
    cons = [t * np.eye(n) - B >> 0]
    for i in range(n):
        for j in range(i, n):
            if i == j or (i, j) not in Eset:
                cons.append(B[i, j] == 1)
    cp.Problem(cp.Minimize(t), cons).solve(solver="CLARABEL")
    return (B.value + B.value.T) / 2, float(t.value)


def matching_digits(a, b, dps, levels=None):
    """Length of the common decimal prefix of two mpf values.

    `levels` is the (dps_a, dps_b) pair the two values came from.  It is not
    decoration: comparing a value with ITSELF is what manufactured 955 honest digits
    and failed gate G9.1 on 2026-08-26, and this function now refuses to do it.

    Bit-identical values from two DIFFERENT precisions are the strongest agreement
    available, not the weakest -- for a Delta = 0 graph theta is the integer alpha and
    Gauss-Newton lands on it exactly, so every level returns that integer.  `dps` is
    returned there as a lower bound.  Treating that case as uninformative -- a first,
    wrong, correction made the same day -- sent 304 such graphs escalating to the
    precision ceiling and reported 297 of them as low_precision.
    """
    if levels is not None and levels[0] == levels[1]:
        raise ValueError(f"comparing a value with itself at dps={levels[0]}: the "
                         "check's precision must be derived from the measurement's, "
                         "never equal to it")
    mp.dps = dps
    d = fabs(a - b)
    if d == 0:
        return dps
    return int(floor(-log10(d / max(fabs(a), mpf(1)))))


def numeric_rank(X, tol=1e-8):
    """Rank of the primal optimum at double precision -- a covariate, not a result."""
    w = np.linalg.eigvalsh(np.asarray(X, dtype=float))
    m = max(abs(w).max(), 1.0)
    return int((w > tol * m).sum())


def theta_honest(code=None, n=None, edges=None, dps=240, target=MIN_HONEST,
                 max_dps=1920):
    """High-precision theta, its MEASURED honest-digit count, and whether the
    refinement actually CONVERGED.

    The honest count compares a run at level d against a run at level 2d and the
    value returned is the 2d one, so the count understates that value's accuracy --
    the safe direction.

    But agreement between levels is only evidence of accuracy when the iteration is
    converging.  Gauss-Newton on some degenerate optima settles on a stable point that
    is NOT the optimum, and every precision level then reproduces that same wrong
    point: for GCY^fW the values at dps 960, 1920 and 3840 agree with each other to
    465 and 945 digits while agreeing with the truth theta = alpha = 3 to only 359.
    Two runs agreeing tells you the iteration is stable, not that it is right.  This
    is a limitation of the Stage 2 measure, which was calibrated on four
    non-degenerate values and never met this case.

    The residual separates the two cleanly, and by mechanism rather than by a tuned
    threshold: a converged run has residual ~ 10^-dps, so doubling dps drops it by
    hundreds of orders (measured: 3.06e-241 -> 5.65e-482 for DUW).  A stalled run
    returns the SAME residual at every precision (1.44e-31 at both 240 and 480 for
    FCRto).  A ratio anywhere near 1 therefore means the value is not measurable by
    this instrument, and saying so is the honest report -- guessing is not.
    """
    if code is not None:
        n, adj = decode_g6(code)
        edges = edges_of(n, adj)
    pr = theta_cvxpy(n, edges, solver="CLARABEL")
    B0, t0 = _dual_start(n, edges)
    cache = {}

    def at(d):
        if d not in cache:
            cache[d] = refine(n, edges, pr["X"], B0, pr["theta"], dps=d)
        return cache[d]

    d, prev = dps, None
    while True:
        lo, hi = at(d), at(2 * d)
        mp.dps = 2 * d
        converged = hi["residual"] < lo["residual"] * mpf(10) ** -10
        h = matching_digits(lo["theta"], hi["theta"], 2 * d, levels=(d, 2 * d)) - 5
        if not converged or h >= target or 2 * d >= max_dps:
            break
        if prev is not None and h < 1.3 * prev:
            break
        prev, d = h, d * 2
    return dict(theta=hi["theta"], honest=h, dps_used=2 * d, converged=bool(converged),
                residual_lo=lo["residual"], residual_hi=hi["residual"],
                rank=numeric_rank(pr["X"]), n=n, edges=edges,
                seed=(pr["X"], B0, pr["theta"]))


def higher(rec, factor=2):
    """A strictly higher-precision value, with a conservative honest count.

    The level is DERIVED from rec["dps_used"], never written as a constant.  Hard-coding
    it is what failed gate G9.1 on 2026-08-26: for graphs that had escalated, the
    "confirmation" ran at the same dps as the search, matching_digits compared a value
    with itself, and the count came back as the full dps -- 955 digits for a value
    correct to 389.  matching_digits now refuses that comparison outright.

    The count returned measures the accuracy of the SEARCH value, and PSLQ then runs on
    the higher one, so it understates -- the safe direction.  That is sound only
    because theta_honest has already established that the refinement CONVERGES; on a
    stalled refinement the two levels agree without either being right, and this
    function would hand PSLQ digits that do not exist.
    """
    n, edges = rec["n"], rec["edges"]
    X0, B0, t0 = rec["seed"]
    d2 = factor * rec["dps_used"]
    r = refine(n, edges, X0, B0, t0, dps=d2)
    h = matching_digits(rec["theta"], r["theta"], d2,
                        levels=(rec["dps_used"], d2)) - 5
    return r["theta"], h, d2


def budget(D, d):
    """Digits allowed per coefficient at degree d given D honest digits."""
    return (D - 20) // (d + 1)


def _pslq_at(t, D, d):
    """One PSLQ attempt.  Returns the primitive integer polynomial or None."""
    B = budget(D, d)
    if B < 3:
        return None, "budget_exhausted"
    mp.dps = D
    tt = +t
    vec = [mpf(1)]
    for _ in range(d):
        vec.append(vec[-1] * tt)
    rel = pslq(vec, tol=mpf(10) ** (-(D - 5)), maxcoeff=10 ** B, maxsteps=20000)
    if rel is None:
        return None, "no_relation"
    if rel[-1] == 0:                       # degenerate: a lower-degree relation
        return None, "no_relation"
    from math import gcd
    g = 0
    for c in rel:
        g = gcd(g, abs(int(c)))
    rel = [int(c) // g for c in rel]
    if rel[-1] < 0:
        rel = [-c for c in rel]
    return rel, "hit"


def find_minpoly(t, D, confirm=None, degrees=DEGREES):
    """Ascending search for an integer relation among 1, t, ..., t^d.

    `confirm`, when given, is a zero-argument callable returning (t2, D2) at strictly
    higher precision.  A hit is accepted only if PSLQ at D2 digits returns the same
    primitive polynomial.

    PREREGISTRATION_STAGE9 2.4 asks for reproduction "at doubled precision".  What is
    done here is STRONGER: the confirmation runs against an independently refined value
    with roughly twice the honest digits of the search itself, so a spurious relation
    found at D digits has to survive being tested at 2D.  Repeating the search at the
    same honest-digit count would pass by construction, and a test that cannot fail is
    vacuous.  Strengthening a sealed check is allowed; weakening it is not.

    status is one of
        hit               found, and reproduced against the higher-precision value
        pslq_unstable     found at D, not reproduced at D2
        not_found         nothing up to max(degrees) within the height budget
    The last is deliberately ambiguous and must be reported as such: degree above the
    ladder OR coefficients above 10^B(d).  This experiment cannot separate them.
    """
    tried = []
    for d in degrees:
        rel, why = _pslq_at(t, D, d)
        tried.append(dict(degree=d, budget=budget(D, d), outcome=why))
        if rel is None:
            continue
        if confirm is None:
            return dict(degree=d, poly=rel, status="hit", ladder=tried,
                        confirmed_at=None)
        t2, D2 = confirm()
        rel2, _ = _pslq_at(t2, D2, d)
        if rel2 == rel:
            return dict(degree=d, poly=rel, status="hit", ladder=tried,
                        confirmed_at=D2)
        return dict(degree=d, poly=rel, poly_alt=rel2, status="pslq_unstable",
                    ladder=tried, confirmed_at=D2)
    return dict(degree=None, poly=None, status="not_found", ladder=tried,
                confirmed_at=None)


def aut_dreadnaut(n, adj):
    """|Aut| by nauty.  The independent route required by the repository rule."""
    lines = [f"n={n} g"]
    for i in range(n):
        nb = [str(j) for j in range(n) if j != i and (adj[i] >> j) & 1]
        lines.append(" ".join(nb) + ";")
    lines.append(".")
    lines.append("x")
    lines.append("q")
    out = subprocess.run([DREADNAUT], input="\n".join(lines) + "\n",
                         capture_output=True, text=True, timeout=120).stdout
    for tok in out.split():
        if tok.startswith("grpsize="):
            v = tok[len("grpsize="):].rstrip(";")
            return int(round(float(v))) if ("e" in v or "." in v) else int(v)
    raise RuntimeError("dreadnaut printed no grpsize:\n" + out)


def aut_networkx(n, adj, cap=200000):
    """|Aut| by explicit isomorphism enumeration.  Slow, independent, capped."""
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                G.add_edge(i, j)
    cnt, orb = 0, set()
    for iso in nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter():
        cnt += 1
        orb.add(iso[0])
        if cnt > cap:
            return None, None
    return cnt, len(orb)


def vertex_orbits(n, adj):
    """Number of vertex orbits, via dreadnaut's orbit count."""
    lines = [f"n={n} g"]
    for i in range(n):
        nb = [str(j) for j in range(n) if j != i and (adj[i] >> j) & 1]
        lines.append(" ".join(nb) + ";")
    lines += [".", "x", "o", "q"]
    out = subprocess.run([DREADNAUT], input="\n".join(lines) + "\n",
                         capture_output=True, text=True, timeout=120).stdout
    for line in out.splitlines():
        if "orbit" in line and ";" in line and "grpsize" in line:
            return int(line.split()[0])
    return None
