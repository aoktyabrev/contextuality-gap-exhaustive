"""Certify Delta(G) > 0 exactly, without needing the exact value of theta.

A primal feasible X with 1^T X 1 > alpha proves theta(G) > alpha, and alpha is an
integer computed exactly, so Delta > 0 follows.  The certificate is built by rounding a
numerical optimum to rationals and then shrinking it towards I/n:

    X' = (1 - eps) * X_rounded + eps * I / n

Shrinking preserves both invariants that matter -- I/n is diagonal, so the zeros on the
edges survive, and its trace is 1, so the trace stays 1 -- while pulling the spectrum
away from zero, which repairs the small negative eigenvalues that rounding introduces.
Everything is then verified in exact rational arithmetic.

This is much cheaper than certifying theta itself and is all that is needed to settle
whether a graph belongs in the "quantum" list.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runners"))
from fractions import Fraction as F
import numpy as np

from quadc5.g6 import decode_g6, edges_of
from quadc5.alpha import alpha_bitmask
from quadc5.numfield import NumField, psd_schur, psd_minors
from quadc5.theta import theta_cvxpy, theta_scs_direct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def rational_field():
    """Q as a degree-1 NumField, so the exact PSD machinery applies unchanged."""
    return NumField([F(0), F(1)], (F(-1), F(1)))


def build(code, X, alpha, denom, eps):
    n, adj = decode_g6(code)
    E = set(edges_of(n, adj))
    K = rational_field()
    e = F(eps).limit_denominator(10 ** 9)
    M = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            if (min(i, j), max(i, j)) in E:
                v = F(0)
            else:
                v = F(round(float(X[i, j]) * denom), denom)
            M[i][j] = M[j][i] = v
    # exact trace normalisation, then shrink towards I/n
    tr = sum(M[i][i] for i in range(n))
    if tr != 1:
        M[0][0] += 1 - tr
    for i in range(n):
        for j in range(n):
            M[i][j] = (1 - e) * M[i][j] + (e / n if i == j else F(0))
    Kel = [[K.from_rational(M[i][j]) for j in range(n)] for i in range(n)]
    tr2 = sum(M[i][i] for i in range(n))
    s = sum(M[i][j] for i in range(n) for j in range(n))
    zero_ok = all(M[i][j] == 0 for (i, j) in E)
    ok1, rank, msg = psd_schur(K, Kel, n)
    ok2, msg2 = psd_minors(K, Kel, n) if n <= 10 else (None, "skipped")
    return dict(n=n, alpha=alpha, trace=tr2, sum=s, zero_on_edges=zero_ok,
                psd_schur=ok1, psd_minors=ok2, rank=rank,
                proves_positive=bool(zero_ok and tr2 == 1 and ok1 and ok2 and s > alpha),
                margin=float(s) - alpha, denom=denom, eps=str(e))


def certify_positive(code, dps=60, verbose=True):
    n, adj = decode_g6(code)
    E = edges_of(n, adj)
    alpha = alpha_bitmask(n, adj)
    sols = {"CLARABEL": theta_cvxpy(n, E, solver="CLARABEL"),
            "CVXOPT": theta_cvxpy(n, E, solver="CVXOPT"),
            "SCS(1e-11)": theta_scs_direct(n, E, eps=1e-11)}
    vals = {k: v["theta"] - alpha for k, v in sols.items()}
    if verbose:
        print(f"  {code}: alpha={alpha}; Delta by solver: " +
              ", ".join(f"{k}={v:.6e}" for k, v in vals.items()))
    X = sols["CLARABEL"]["X"]
    X = (X + X.T) / 2
    for denom in (10 ** 6, 10 ** 8, 10 ** 10, 10 ** 12):
        for eps in (1e-9, 1e-8, 1e-7, 1e-6, 1e-5):
            r = build(code, X, alpha, denom, eps)
            if r["proves_positive"]:
                r.update(graph6=code, solver_deltas={k: float(v) for k, v in vals.items()})
                if verbose:
                    print(f"    CERTIFIED  1^T X 1 - alpha = {r['margin']:.6e} exactly "
                          f"(denominator 1e{len(str(denom))-1}, eps={eps:g}, "
                          f"PSD by Schur and by all {2**r['n']-1} principal minors)")
                return r
    if verbose:
        print("    NOT CERTIFIED with the denominators and shrinkages tried")
    return dict(graph6=code, alpha=alpha, proves_positive=False,
                solver_deltas={k: float(v) for k, v in vals.items()})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("codes", nargs="+")
    ap.add_argument("--out", default=os.path.join(RES, "report_3a_positive.json"))
    a = ap.parse_args()
    res = [certify_positive(c) for c in a.codes]
    json.dump(res, open(a.out, "w"), indent=1, default=str)
    ok = sum(r["proves_positive"] for r in res)
    print(f"\ncertified positive: {ok} of {len(res)}; wrote {a.out}")
