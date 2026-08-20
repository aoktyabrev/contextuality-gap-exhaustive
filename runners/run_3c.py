"""Block 3.c -- the two open questions, answered from the top-10/top-100 data.

1. Does rationality of theta track the automorphism group?
2. Is the near-stall between n = 9 and n = 10 an anomaly of 9 or of 10?

Both are reconnaissance; a negative answer was accepted in advance
(PREREGISTRATION_STAGE3 3.1, 3.2).
"""
import sys, os, csv, json, glob, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runners"))
import numpy as np
from scipy.stats import spearmanr
from mpmath import mp, mpf, pslq, nstr

from quadc5.g6 import decode_g6, edges_of
from quadc5.alpha import alpha_bitmask
from run_2a import theta_hi, matching_digits
from run_3b import top_of

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def field_degree(code, dps=120, maxdeg=6):
    """Smallest d for which an integer relation of degree d survives the budget rule
    B = floor((D-20)/(d+1)) of PREREGISTRATION_STAGE2 3.1.  None if none up to maxdeg."""
    r1 = theta_hi(code=code, dps=dps)
    r2 = theta_hi(code=code, dps=2 * dps)
    D = matching_digits(r1["theta"], r2["theta"], 2 * dps) - 5
    th = r2["theta"]
    mp.dps = D + 10
    for d in range(1, maxdeg + 1):
        B = max(1, (D - 20) // (d + 1))
        rel = pslq([th ** k for k in range(d + 1)], maxcoeff=10 ** B,
                   maxsteps=10 ** 6, tol=mpf(10) ** (-(D - 10)))
        if rel is None:
            continue
        mp.dps = 2 * D
        resid = abs(sum(mpf(int(c)) * th ** k for k, c in enumerate(rel)))
        if resid < mpf(10) ** (-(D - 5)):
            return d, [int(c) for c in rel], D, nstr(th, 40)
    return None, None, D, nstr(th, 40)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--dps", type=int, default=120)
    a = ap.parse_args()
    tab = json.load(open(os.path.join(RES, "report_3b.json")))
    out = {"q1": [], "q2": {}}

    print("=== 3.c.1 -- field degree against symmetry ===")
    for n in ("5", "6", "7", "8", "9", "10"):
        for row in tab[n]:
            code = row["graph6"]
            deg, rel, D, thv = field_degree(code, dps=a.dps)
            rec = dict(n=int(n), rank=row["rank"], graph6=code,
                       aut_order=row["aut_order"],
                       vertex_transitive=row["vertex_transitive"],
                       edge_transitive=row["edge_transitive"],
                       regular=row["regular"], edges=row["edges"],
                       field_degree=deg, minpoly=rel, honest_digits=D, theta=thv)
            out["q1"].append(rec)
            print(f"  n={n:>2} r{row['rank']:<2} {code:11s} |Aut|={row['aut_order']:3d} "
                  f"vt={str(row['vertex_transitive'])[0]} et={str(row['edge_transitive'])[0]} "
                  f"deg={deg}")
    known = [r for r in out["q1"] if r["field_degree"]]
    if len(known) >= 3:
        rho, p = spearmanr([r["aut_order"] for r in known], [r["field_degree"] for r in known])
        out["spearman_aut_vs_degree"] = dict(rho=float(rho), p=float(p), n=len(known))
        rat = [r for r in known if r["field_degree"] == 1]
        irr = [r for r in known if r["field_degree"] > 1]
        out["rational_group"] = dict(count=len(rat), aut_orders=sorted(r["aut_order"] for r in rat),
                                     vt=sum(r["vertex_transitive"] for r in rat),
                                     et=sum(r["edge_transitive"] for r in rat))
        out["irrational_group"] = dict(count=len(irr), aut_orders=sorted(r["aut_order"] for r in irr),
                                       vt=sum(r["vertex_transitive"] for r in irr),
                                       et=sum(r["edge_transitive"] for r in irr))
        overlap = set(out["rational_group"]["aut_orders"]) & set(out["irrational_group"]["aut_orders"])
        out["aut_orders_on_both_sides"] = sorted(overlap)
        print(f"\n  Spearman(|Aut|, degree) over {len(known)}: rho={rho:+.3f}, p={p:.4f}")
        print(f"  rational   ({len(rat)}): |Aut| = {out['rational_group']['aut_orders']}")
        print(f"  irrational ({len(irr)}): |Aut| = {out['irrational_group']['aut_orders']}")
        print(f"  orders occurring on BOTH sides: {sorted(overlap)}")

    print("\n=== 3.c.2 -- where the stall is ===")
    for n in (7, 8, 9, 10):
        tops = top_of(n, 100)
        d = np.array([x[1] for x in tops])
        gap12 = d[0] - d[1]
        spread = d[0] - d[-1] if len(d) > 1 else 0.0
        rec = dict(n=n, count=len(d), d1=float(d[0]), d2=float(d[1]) if len(d) > 1 else None,
                   gap_1_2=float(gap12), spread_top=float(spread),
                   detachment=float(gap12 / spread) if spread else None,
                   d100=float(d[-1]))
        out["q2"][str(n)] = rec
        print(f"  n={n:2d}: D1={d[0]:.7f} D2={d[1]:.7f} gap={gap12:.7f} "
              f"spread(top{len(d)})={spread:.7f} detachment={rec['detachment']:.4f}")
    json.dump(out, open(os.path.join(RES, "report_3c.json"), "w"), indent=1, default=str)
    print("\nwrote results/report_3c.json")
