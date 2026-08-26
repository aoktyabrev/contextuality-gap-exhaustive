"""Stability is not accuracy: the measurement behind the companion note (Paper B).

For each graph it records, at a ladder of working precisions:

  * the residual of the Gauss-Newton refinement,
  * the agreement between consecutive precision levels ("matching digits"),
  * where the truth is known exactly (Delta = 0, so theta = alpha), the ACTUAL number
    of correct digits.

The point of the table is the column that disagrees: on a stalled refinement the
agreement between levels keeps growing while the correct-digit count stops.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import mpmath
from mpmath import mp, mpf, nstr

from quadc5.g6 import decode_g6, edges_of
from quadc5.alpha import alpha_bitmask
from quadc5.theta import theta_cvxpy
from quadc5.hiprec import refine
from quadc5.algdeg import _dual_start, matching_digits, _pslq_at, numeric_rank

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

# Two stalled cases and two healthy ones.  All four have Delta = 0, so the exact truth
# is theta = alpha and "correct digits" is measurable rather than inferred.
GRAPHS = [("GCY^fW", "stalled"), ("FCRto", "stalled"),
          ("D]{", "converged"), ("ECzw", "converged")]
LEVELS = [240, 480, 960, 1920, 3840]


def profile(code, levels):
    n, adj = decode_g6(code)
    e = edges_of(n, adj)
    a = alpha_bitmask(n, adj)
    pr = theta_cvxpy(n, e, solver="CLARABEL")
    B0, _ = _dual_start(n, e)
    runs = {}
    for d in levels:
        runs[d] = refine(n, e, pr["X"], B0, pr["theta"], dps=d)
    rows = []
    for i, d in enumerate(levels):
        mp.dps = 4 * max(levels)
        err = abs(runs[d]["theta"] - a)
        correct = None if err == 0 else int(-mpmath.log10(err))
        agree = None
        if i + 1 < len(levels):
            agree = matching_digits(runs[d]["theta"], runs[levels[i + 1]]["theta"],
                                    levels[i + 1], levels=(d, levels[i + 1]))
        mp.dps = 30
        rows.append(dict(dps=d,
                         residual=nstr(runs[d]["residual"], 4),
                         iterations=runs[d]["iterations"],
                         correct_digits=correct,
                         agrees_with_next=agree))
    # the mechanism-level test: does the residual fall with precision?
    mp.dps = 4 * max(levels)
    r0, r1 = runs[levels[0]]["residual"], runs[levels[1]]["residual"]
    converged = bool(r1 < r0 * mpf(10) ** -10)
    return dict(graph6=code, n=n, alpha=a, rank_X=numeric_rank(pr["X"]),
                converged=converged, rows=rows,
                theta_at_top=nstr(runs[levels[-1]]["theta"], 40))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "report_stability_vs_accuracy.json"))
    a = ap.parse_args()

    out = {"levels": LEVELS, "graphs": []}
    print(f"{'graph':10s} {'kind':10s} {'dps':>5} {'residual':>12} {'correct':>8} "
          f"{'agrees with next':>17}")
    print("-" * 70)
    for code, kind in GRAPHS:
        p = profile(code, LEVELS)
        p["kind_expected"] = kind
        out["graphs"].append(p)
        for r in p["rows"]:
            print(f"{code:10s} {kind:10s} {r['dps']:>5} {r['residual']:>12} "
                  f"{str(r['correct_digits']):>8} {str(r['agrees_with_next']):>17}")
        print(f"{'':10s} residual-falls-with-precision test: "
              f"{'CONVERGED' if p['converged'] else 'STALLED'}")
        print("-" * 70)

    # The consequence: hand an over-claimed digit count to an integer-relation search.
    n, adj = decode_g6("GCY^fW")
    e = edges_of(n, adj)
    pr = theta_cvxpy(n, e, solver="CLARABEL")
    B0, _ = _dual_start(n, e)
    v = refine(n, e, pr["X"], B0, pr["theta"], dps=1920)["theta"]
    claimed = matching_digits(v, refine(n, e, pr["X"], B0, pr["theta"], dps=3840)["theta"],
                              3840, levels=(1920, 3840)) - 5
    demo = {"claimed_digits": claimed, "true_digits": 359}
    for D, label in [(claimed, "over-claimed"), (350, "honest")]:
        found = {}
        for d in (1, 2, 3, 4):
            rel, _ = _pslq_at(v, D, d)
            if rel is not None:
                found = {"degree": d, "poly": rel}
                break
        demo[label] = found
        print(f"integer relation at {D} digits ({label}): "
              f"{found.get('poly')} at degree {found.get('degree')}")
    demo["truth"] = {"degree": 1, "poly": [-3, 1]}
    out["over_claimed_demo"] = demo

    json.dump(out, open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")
