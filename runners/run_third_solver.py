"""Third-solver check on the leading block of a sweep.

The brief for Stage 0 asked for the top-100 to be re-solved with a second solver; this
is the third.  It exists as a runner rather than as an ad-hoc snippet so that a clean
run produces the same artefacts the repository holds.

CVXOPT is the least accurate of the three on these problems -- its own error on the
analytic calibration family is 1.4e-7 -- so deviations of that size are the solver's,
not the answer's.  Values are never averaged; graphs exceeding tau_hi are listed.
"""
import sys, os, csv, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from quadc5.g6 import decode_g6, edges_of
from quadc5.theta import theta_cvxpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=9)
ap.add_argument("--top", type=int, default=100)
ap.add_argument("--solver", default="CVXOPT")
ap.add_argument("--tau-hi", type=float, default=1e-7)
a = ap.parse_args()

src_csv = None
for cand in sorted(os.listdir(RES)):
    if cand.startswith(f"n{a.n}_top") and cand.endswith(".csv"):
        src_csv = os.path.join(RES, cand)
if src_csv is None:
    sys.exit(f"no n{a.n}_top*.csv in results/ -- run the sweep first")

rows = list(csv.DictReader(open(src_csv)))[:a.top]
print(f"third solver ({a.solver}) on the top {len(rows)} of {os.path.basename(src_csv)}")
diffs = []
for r in rows:
    n, adj = decode_g6(r["graph6"])
    t3 = theta_cvxpy(n, edges_of(n, adj), solver=a.solver)["theta"]
    diffs.append((abs(t3 - float(r["theta_hi"])), r["graph6"]))
diffs.sort(reverse=True)
d = np.array([x[0] for x in diffs])
over = [g for v, g in diffs if v > a.tau_hi]
print(f"  vs CLARABEL: max={d.max():.2e} at {diffs[0][1]}, mean={d.mean():.2e}")
print(f"  exceeding tau_hi={a.tau_hi:g}: {len(over)} of {len(rows)} -- listed, not averaged")
json.dump(dict(n=a.n, top=len(rows), solver=a.solver, tau_hi=a.tau_hi,
               max_diff=float(d.max()), mean=float(d.mean()), over_tau_hi=over),
          open(os.path.join(RES, f"third_solver_n{a.n}_top{a.top}.json"), "w"), indent=1)
print(f"  wrote results/third_solver_n{a.n}_top{a.top}.json")
