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

A found polynomial is a HYPOTHESIS, not a result.  Stage 2 exists because the
source's authors published a PSLQ hit as a closed form and withdrew it.  Here the
only defence asked for by PREREGISTRATION_STAGE9 2.4 is reproduction at doubled
precision; nothing in this module proves anything, and the word "proved" belongs
only to the exact certificates of quadc5/numfield.py.
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


def matching_digits(a, b, dps):
    """Length of the common decimal prefix of two mpf values, or None.

    None means the two values are bit-identical, and that is NOT evidence of `dps`
    honest digits -- it means the comparison carries no information, almost always
    because both came from the same refinement.  Returning `dps` there is how a
    fabricated count of 955 honest digits reached PSLQ and failed gate G9.1 on
    2026-08-26; see REPORT_STAGE9.  Callers must treat None as unmeasurable and
    compare against a genuinely higher precision instead.
    """
    mp.dps = dps
    d = fabs(a - b)
    if d == 0:
        return None
    return int(floor(-log10(d / max(fabs(a), mpf(1)))))


def numeric_rank(X, tol=1e-8):
    """Rank of the primal optimum at double precision -- a covariate, not a result."""
    w = np.linalg.eigvalsh(np.asarray(X, dtype=float))
    m = max(abs(w).max(), 1.0)
    return int((w > tol * m).sum())


def theta_honest(code=None, n=None, edges=None, dps=240, target=MIN_HONEST,
                 max_dps=3840):
    """High-precision theta plus its MEASURED honest-digit count, escalating as needed.

    The honest count always compares a run at level d against a run at level 2d, and
    the value returned is the 2d one -- so the count UNDERSTATES the returned value's
    accuracy, which is the safe direction.

    Escalation is not decoration.  hiprec.refine damps with lambda = 10^(-dps//2), and
    on a DEGENERATE optimum -- which is what a Delta = 0 graph typically has -- the
    damping floor caps attainable accuracy at roughly dps/2 digits, not dps.  Measured
    on FCRto: 113 correct digits at dps 240, 233 at 480, 389 at 960.  A fixed dps is
    therefore not enough; the count has to be measured and the precision raised until
    it clears `target`.
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

    d, prev, plateau = dps, None, False
    while True:
        lo, hi = at(d), at(2 * d)
        h = matching_digits(lo["theta"], hi["theta"], 2 * d)
        h = None if h is None else h - 5
        if h is not None and h >= target:
            break
        if prev is not None and h is not None and h < 1.3 * prev:
            # Doubling the precision bought almost nothing.  Gauss-Newton has
            # plateaued on a degenerate optimum and further escalation only burns
            # time -- for a graph that needs dps 3840 that is minutes, per graph.
            plateau = True
            break
        if 2 * d >= max_dps:
            break
        prev, d = h, d * 2
    return dict(theta=hi["theta"], honest=h, dps_used=2 * d, plateau=plateau,
                rank=numeric_rank(pr["X"]), n=n, edges=edges,
                seed=(pr["X"], B0, pr["theta"]))


def higher(rec, factor=2, backoff=0.90):
    """A strictly higher-precision value than rec's, with a usable digit count.

    Two separate defects were found here by gate G9.1 on 2026-08-26 and both are
    fixed in this function.

    First, the level must be DERIVED from rec["dps_used"].  Hard-coding it meant that
    for graphs which had escalated, the "confirmation" ran at the same dps as the
    search; matching_digits saw two identical values and reported the full dps as
    honest digits, and PSLQ then chased 955 digits of a value correct to 389.

    Second, the flat five-digit margin of the sealed rule does not survive a PLATEAU.
    Gauss-Newton on a degenerate optimum stops gaining: for FCRto the value is correct
    to 113, 233, 389, 389 digits at dps 240, 480, 960, 1920.  Once two consecutive
    levels are equally accurate, their matching prefix equals that accuracy and minus
    five leaves nothing -- PSLQ was handed 395 digits of a 389-digit value and declared
    a true relation unstable.  The margin therefore scales: `backoff` of the measured
    count.  This only ever makes the confirmation MORE conservative, and it still runs
    far above the search precision, so it remains a test that can fail.
    """
    n, edges = rec["n"], rec["edges"]
    X0, B0, t0 = rec["seed"]
    d2 = factor * rec["dps_used"]
    r = refine(n, edges, X0, B0, t0, dps=d2)
    h = matching_digits(rec["theta"], r["theta"], d2)
    if h is None:
        return r["theta"], None, d2
    return r["theta"], int((h - 5) * backoff), d2


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
        if D2 is None or D2 <= D:
            # The higher-precision run gained nothing: the value has plateaued and
            # there is no level at which to confirm.  Blaming PSLQ here would be
            # wrong, so this gets its own status rather than "unstable".
            return dict(degree=d, poly=rel, status="precision_plateau", ladder=tried,
                        confirmed_at=D2)
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
