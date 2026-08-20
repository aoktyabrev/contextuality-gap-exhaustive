"""Block 2.a -- high precision and its calibration gate.  PREREGISTRATION_STAGE2 §2."""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from mpmath import mp, mpf, sqrt, cos, pi, nstr

from quadc5.g6 import decode_g6, edges_of, adj_from_edges
from quadc5.theta import theta_cvxpy
from quadc5.hiprec import refine

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def dual_start(n, edges):
    """Double-precision dual solution: min t s.t. t I - B >= 0, B fixed off edges."""
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


def theta_hi(code=None, n=None, edges=None, dps=120):
    if code is not None:
        n, adj = decode_g6(code)
        edges = edges_of(n, adj)
    pr = theta_cvxpy(n, edges, solver="CLARABEL")
    B0, t0 = dual_start(n, edges)
    return refine(n, edges, pr["X"], B0, pr["theta"], dps=dps)


def matching_digits(a, b, dps):
    """Length of the common decimal prefix of two mpf values."""
    mp.dps = dps
    if a == b:
        return dps
    d = abs(a - b)
    if d == 0:
        return dps
    import mpmath
    return int(mpmath.floor(-mpmath.log10(d / max(abs(a), mpf(1)))))


def exact_refs():
    """The four already-proved values (SOURCES.md S9)."""
    return {
        "DUW": ("C5", lambda: sqrt(5), 2),
        "FCp`_": ("C7", lambda: 7 * cos(pi / 7) / (1 + cos(pi / 7)), 3),
        "HCRbdO{": ("n=9 max", lambda: mpf(11) / 3, 1),
        "ICRb`yiu?": ("n=10 max", lambda: 3 + sqrt(2) / 2, 2),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dps", type=int, default=120)
    a = ap.parse_args()
    out = {"dps": a.dps, "calibration": [], "targets": []}
    FAILS = []

    print(f"=== GATE 2.a -- calibration on four already-proved values (dps {a.dps} and {2*a.dps}) ===")
    for code, (name, exact_fn, deg) in exact_refs().items():
        r1 = theta_hi(code=code, dps=a.dps)
        r2 = theta_hi(code=code, dps=2 * a.dps)
        mp.dps = 2 * a.dps
        ex = exact_fn()
        honest = matching_digits(r1["theta"], r2["theta"], 2 * a.dps) - 5
        vs_exact = matching_digits(r2["theta"], ex, 2 * a.dps)
        ok = vs_exact >= 60 and honest >= 60
        FAILS.append(code) if not ok else None
        print(f"{'PASS' if ok else 'FAIL'} {name:9s} {code:11s} deg={deg}  "
              f"honest digits (run vs 2x run) = {honest}, digits vs exact = {vs_exact}")
        mp.dps = 70
        print(f"      got   {nstr(r2['theta'], 65)}")
        print(f"      exact {nstr(ex, 65)}")
        out["calibration"].append(dict(code=code, name=name, degree=deg,
                                       honest_digits=honest, digits_vs_exact=vs_exact,
                                       value=nstr(r2["theta"], 80), verdict="PASS" if ok else "FAIL"))

    print(f"\n=== targets ===")
    for code in ["GCQb`o", "ICQeR`[Mg"]:
        r1 = theta_hi(code=code, dps=a.dps)
        r2 = theta_hi(code=code, dps=2 * a.dps)
        honest = matching_digits(r1["theta"], r2["theta"], 2 * a.dps) - 5
        mp.dps = 2 * a.dps
        print(f"{code:11s} honest digits = {honest}, residual = {nstr(r2['residual'],4)}")
        mp.dps = 90
        print(f"      {nstr(r2['theta'], 85)}")
        out["targets"].append(dict(code=code, honest_digits=honest,
                                   value=nstr(r2["theta"], 120),
                                   residual=nstr(r2["residual"], 6)))

    out["gate_2a_K1_K2"] = "PASSED" if not FAILS else "FAILED"
    json.dump(out, open(os.path.join(RES, "report_2a.json"), "w"), indent=1, default=str)
    print("\n" + ("GATE 2.a (K1,K2) PASSED" if not FAILS else f"GATE 2.a FAILED: {FAILS}"))
    sys.exit(0 if not FAILS else 1)
