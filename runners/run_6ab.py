"""Blocks 6.a (parts 3-4) and 6.b -- the ceiling among graphs that HAVE a gap, and
which theta values are rational.

The trivial half of the ceiling question is settled without computation: our filter F2
is chi(complement) = alpha, and alpha <= alpha* <= chi(complement) then forces
alpha* = alpha = theta.  Every graph the filter removes therefore sits exactly at its
ceiling while having zero gap.  The interesting question is the other half: among graphs
that do have a positive gap, does reaching the ceiling go with a large one?
"""
import sys, os, json, csv, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runners"))
from fractions import Fraction as F
import numpy as np
from run_6a import alpha_star_exact
from run_5a import positive_rows

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def is_rational(delta, alpha, tol=1e-9, maxden=5000):
    """theta = alpha + delta is rational iff delta is.  Candidate test only."""
    f = F(delta).limit_denominator(maxden)
    return (abs(float(f) - delta) < tol), f


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[7, 8, 9])
    ap.add_argument("--top", type=int, default=10)
    a_ = ap.parse_args()
    out = {}

    print("=== 6.a, часть 3: alpha* для топ-10 каждого размера ===")
    tab = json.load(open(os.path.join(RES, "report_3b.json")))
    tops = {}
    for n in ("5", "6", "7", "8", "9", "10"):
        rows = []
        for r in tab[n][:a_.top]:
            v, det = alpha_star_exact(r["graph6"])
            gap = float(v) - r["theta"] if v is not None else None
            rows.append(dict(rank=r["rank"], graph6=r["graph6"], alpha=r["alpha"],
                             theta=r["theta"], alpha_star=str(v), gap=gap,
                             at_ceiling=bool(gap is not None and abs(gap) < 1e-9)))
        tops[n] = rows
        gaps = [x["gap"] for x in rows if x["gap"] is not None]
        atc = sum(x["at_ceiling"] for x in rows)
        print(f"  n={n:>2}: зазор alpha*-theta от {min(gaps):.4f} до {max(gaps):.4f}; "
              f"на потолке {atc} из {len(rows)}")
    out["top10_alpha_star"] = tops

    print("\n=== 6.a, часть 4: среди графов С зазором — кто на потолке ===")
    ceil = {}
    for n in a_.sizes:
        pos = positive_rows(n)
        pos.sort(key=lambda t: -t[1])
        hits, checked = [], 0
        for rank, (al, d, code) in enumerate(pos, 1):
            v, det = alpha_star_exact(code)
            checked += 1
            if v is not None and abs(float(v) - (al + d)) < 1e-9:
                hits.append(dict(rank=rank, graph6=code, alpha=al, delta=d,
                                 alpha_star=str(v)))
        ceil[str(n)] = dict(positive=len(pos), checked=checked, at_ceiling=len(hits),
                            examples=hits[:10])
        print(f"  n={n}: из {len(pos)} графов с Δ>0 достигают потолка {len(hits)}")
        for h in hits[:5]:
            print(f"      ранг {h['rank']:>5} {h['graph6']:11s} α={h['alpha']} "
                  f"Δ={h['delta']:.7f} α*={h['alpha_star']}")
    out["ceiling_among_positive"] = ceil

    print("\n=== 6.b: рациональные theta среди графов с зазором ===")
    rat = {}
    for n in a_.sizes:
        pos = positive_rows(n)
        pos.sort(key=lambda t: -t[1])
        found = []
        for rank, (al, d, code) in enumerate(pos, 1):
            ok, f = is_rational(d, al)
            if ok:
                found.append(dict(rank=rank, graph6=code, alpha=al, delta=str(f),
                                  delta_float=d))
        rat[str(n)] = dict(positive=len(pos), rational=len(found), examples=found[:15])
        print(f"  n={n}: рациональных Δ среди {len(pos)} — {len(found)}")
        for h in found[:8]:
            print(f"      ранг {h['rank']:>5} {h['graph6']:11s} α={h['alpha']} Δ={h['delta']}")
    out["rational_theta"] = rat
    json.dump(out, open(os.path.join(RES, "report_6ab.json"), "w"), indent=1, default=str)
    print("\nwrote results/report_6ab.json")
