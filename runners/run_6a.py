"""Block 6.a -- the fractional packing number alpha* and the ceiling theta <= alpha*.

alpha*(G) = max sum_v w_v subject to sum_{v in C} w_v <= 1 for every clique C, w >= 0.
By LP duality this equals the fractional clique cover number of G, i.e. chi_f(complement).
Maximal cliques suffice as constraints.

alpha* is rational, so a floating-point value is not an answer.  The LP is solved
numerically only to propose a candidate; what counts is an exact rational certificate:
a primal w proving alpha* >= sum w, and a dual y proving alpha* <= sum y, with the two
sums equal.  Same standard as the rest of the project.
"""
import sys, os, json, csv, glob, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runners"))
from fractions import Fraction as F
import numpy as np
import networkx as nx
from scipy.optimize import linprog

from quadc5.g6 import decode_g6, to_networkx, edges_of
from quadc5.alpha import alpha_bitmask

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def alpha_star_exact(code, maxden=10 ** 6):
    """Exact alpha* with a two-sided rational certificate.  Returns (value, detail)."""
    n, adj = decode_g6(code)
    G = to_networkx(n, adj)
    cliques = [sorted(c) for c in nx.find_cliques(G)]
    m = len(cliques)
    A = np.zeros((m, n))
    for i, c in enumerate(cliques):
        for v in c:
            A[i, v] = 1.0
    # primal: max 1^T w, A w <= 1, w >= 0
    r = linprog(-np.ones(n), A_ub=A, b_ub=np.ones(m), bounds=(0, None), method="highs")
    if not r.success:
        return None, dict(error=r.message)
    w_num = r.x
    y_num = np.asarray(r.ineqlin.marginals) * -1.0     # dual, >= 0

    def rat(vec, den):
        return [F(x).limit_denominator(den) for x in vec]

    for den in (2, 3, 4, 6, 12, 24, 60, 120, 840, 2520, maxden):
        w = rat(w_num, den)
        y = rat(y_num, den)
        if any(x < 0 for x in w) or any(x < 0 for x in y):
            continue
        # primal feasible?
        if any(sum(w[v] for v in c) > 1 for c in cliques):
            continue
        # dual feasible: every vertex covered
        cov = [sum(y[i] for i, c in enumerate(cliques) if v in c) for v in range(n)]
        if any(cv < 1 for cv in cov):
            continue
        sw, sy = sum(w), sum(y)
        if sw == sy:
            return sw, dict(denominator=den, cliques=m, certified=True,
                            primal=[str(x) for x in w], dual=[str(x) for x in y])
    return None, dict(cliques=m, certified=False,
                      numeric=float(r.x.sum()))


def chi_f_of_G(code):
    """The fractional chromatic number of G itself -- printed only to show that it is a
    different quantity from alpha*(G)."""
    n, adj = decode_g6(code)
    G = to_networkx(n, adj)
    ind = [sorted(s) for s in nx.find_cliques(nx.complement(G))]
    m = len(ind)
    A = np.zeros((n, m))
    for j, s in enumerate(ind):
        for v in s:
            A[v, j] = 1.0
    r = linprog(np.ones(m), A_ub=-A, b_ub=-np.ones(n), bounds=(0, None), method="highs")
    return F(float(r.fun)).limit_denominator(10000) if r.success else None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10)
    a_ = ap.parse_args()
    out = {"calibration": {}, "maximizers": [], "top": {}}

    print("=== калибровка (предрегистрация §1.1: ожидаются 5/2 и 7/2) ===")
    for name, code, want in (("C5", "DUW", F(5, 2)), ("C7", "FCp`_", F(7, 2))):
        v, det = alpha_star_exact(code)
        cf = chi_f_of_G(code)
        ok = (v == want)
        print(f"  {name}: alpha* = {v}  (ожидалось {want}) -> {'OK' if ok else 'FAIL'}; "
              f"сертифицировано {det.get('certified')};  для сравнения chi_f(G) = {cf}")
        out["calibration"][name] = dict(alpha_star=str(v), expected=str(want), ok=bool(ok),
                                        chi_f_of_G=str(cf), certified=det.get("certified"))

    print("\n=== максимизаторы всех шести размеров ===")
    MAXS = [(5, "DUW"), (6, "EUZw"), (7, "FCp`_"), (8, "GCQb`o"),
            (9, "HCRbdO{"), (10, "ICRb`yiu?")]
    THETA = {5: "sqrt5", 6: "sqrt5", 7: "cubic", 8: "quartic", 9: F(11, 3), 10: "3+sqrt2/2"}
    tab = json.load(open(os.path.join(RES, "report_3b.json")))
    print(f"  {'n':>2} {'граф':>11} {'alpha':>5} {'theta':>12} {'alpha*':>8} {'alpha*-theta':>13}")
    for n, code in MAXS:
        v, det = alpha_star_exact(code)
        row = [r for r in tab[str(n)] if r["graph6"] == code][0]
        th = row["theta"]
        gap = float(v) - th if v is not None else None
        print(f"  {n:>2} {code:>11} {row['alpha']:>5} {th:>12.7f} {str(v):>8} "
              f"{gap:>13.7f}")
        out["maximizers"].append(dict(n=n, graph6=code, alpha=row["alpha"], theta=th,
                                      alpha_star=str(v), gap=gap,
                                      certified=det.get("certified")))
    json.dump(out, open(os.path.join(RES, "report_6a.json"), "w"), indent=1)
    print("\nwrote results/report_6a.json (частично; топ-10 добавляется отдельным прогоном)")
