"""Exact proof that the eight graphs the database omits at n = 10 really are quantum.

The per-graph comparison (runners/run_db_compare.py) finds our set identical to the
database's at n = 5..9 and eight graphs larger at n = 10.  Those eight are not solver
noise -- their gaps run from 2.8e-3 to 8.3e-3 and none is closed by the sandwich, since
chi(complement) exceeds alpha for every one.  But "our solver says so" is not the standard
this project uses for a claim about someone else's data.

So each of the eight gets a PRIMAL certificate and nothing else is needed: an explicit
rational X with X symmetric, Tr X = 1, X_ij = 0 on every edge and X >= 0, whose 1^T X 1
exceeds alpha.  That proves theta >= 1^T X 1 > alpha, hence Delta > 0, in exact rational
arithmetic with no floating point in the decisive step.  Positive semidefiniteness is
checked twice by independent methods, as everywhere else here.

An upper bound is not built and is not wanted: the claim is only that the gap is
positive, not what it equals.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fractions import Fraction as F
from mpmath import mp

from quadc5.g6 import decode_g6, edges_of
from quadc5.alpha import alpha_bitmask
from quadc5.theta import theta_cvxpy
from quadc5.hiprec import refine
from quadc5.algdeg import _dual_start
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
from certify_enclosure import primal_lower

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

EIGHT = ["I?`e`qqUo", "I?`e`qsZO", "I?`e`qskg", "I?`edd[FW",
         "I?bebOxNG", "ICQe`pcMg", "ICQe`psMg", "ICvdq~sNo"]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--codes", nargs="+", default=EIGHT)
    ap.add_argument("--dps", type=int, default=200)
    ap.add_argument("--ladder", type=int, nargs="+", default=[6, 9, 12, 15])
    ap.add_argument("--cs", type=int, nargs="+", default=[1, 2, 4, 8, 16, 32])
    ap.add_argument("--out", default=os.path.join(RES, "report_db_extras_certified.json"))
    a = ap.parse_args()

    log, rows, ok_all = [], [], True
    for code in a.codes:
        n, adj = decode_g6(code)
        e = edges_of(n, adj)
        al = alpha_bitmask(n, adj)
        pr = theta_cvxpy(n, e, solver="CLARABEL")
        B0, _ = _dual_start(n, e)
        hi = refine(n, e, pr["X"], B0, pr["theta"], dps=a.dps)
        mp.dps = a.dps
        best = None
        for k in a.ladder:
            D = 10 ** k
            for c in a.cs:
                got = primal_lower(n, e, hi["X"], D, c, log)
                if got is None:
                    continue
                L, X = got
                if L > al:                       # strictly above alpha: Delta > 0
                    best = dict(D=D, c=c, L=L, X=X)
                    break
            if best:
                break
        row = dict(graph6=code, n=n, alpha=al,
                   numeric_delta=round(float(pr["theta"]) - al, 9))
        if best:
            L = best["L"]
            row.update(certified=True, denominator=f"1e{len(str(best['D']))-1}",
                       eps_c=best["c"],
                       primal_lower=f"{L.numerator}/{L.denominator}",
                       primal_lower_float=float(L),
                       proved_gap=f"{(L - al).numerator}/{(L - al).denominator}",
                       proved_gap_float=float(L - al))
            print(f"PROVED  {code:12s} alpha={al}  1^T X 1 = {float(L):.9f} > {al}  "
                  f"gap >= {float(L-al):.3e}")
        else:
            ok_all = False
            row.update(certified=False)
            print(f"FAILED  {code:12s} no primal certificate on this ladder")
        rows.append(row)

    out = dict(claim="each of these graphs has Delta > 0, proved by an exact primal "
                     "certificate; the database of quantum graphs omits them at n = 10",
               source_of_the_list="runners/run_db_compare.py",
               all_certified=ok_all, graphs=rows)
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"\n{sum(1 for r in rows if r['certified'])}/{len(rows)} certified")
    print(f"wrote {a.out}")
    sys.exit(0 if ok_all else 1)
