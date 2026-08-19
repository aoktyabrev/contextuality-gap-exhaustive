"""Block 0.c -- exhaustive sweep over n=9.  PREREGISTRATION §5."""
import sys, os, csv, json, argparse, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from quadc5.sweep import sweep
from quadc5.g6 import decode_g6, edges_of
from quadc5.theta import theta_cvxpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES, SRC = os.path.join(ROOT, "results"), os.path.join(ROOT, "sources")

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=9)
ap.add_argument("--seed", type=int, default=20260819)
ap.add_argument("--procs", type=int, default=7)
ap.add_argument("--verify-top", type=int, default=1000)
a = ap.parse_args()

tag = f"n{a.n}"
path = sweep(os.path.join(SRC, f"mckay_graph{a.n}c.g6"), RES, tag,
             eps=1e-8, chunk=500, procs=a.procs)
rows = list(csv.DictReader(open(path)))
for r in rows:
    r["delta"] = float(r["delta"])
rows.sort(key=lambda r: -r["delta"])
print(f"[{tag}] {len(rows)} graphs swept; max Delta (bulk) = {rows[0]['delta']:.8f}")

# high-accuracy re-solve of the leading block (brief asks for top-100; we take more
# so that the top-100 boundary itself cannot be a ranking artefact)
K = min(a.verify_top, len(rows))
print(f"[{tag}] re-solving top {K} on CLARABEL ...")
t0 = time.perf_counter()
for i, r in enumerate(rows[:K]):
    n, adj = decode_g6(r["graph6"])
    hi = theta_cvxpy(n, edges_of(n, adj), solver="CLARABEL")
    r["theta_hi"], r["pr_hi"], r["status_hi"] = hi["theta"], hi["pr"], hi["status"]
    r["delta_hi"] = hi["theta"] - int(r["alpha"])
    r["solver_diff"] = abs(hi["theta"] - float(r["theta"]))
    if (i + 1) % 200 == 0:
        print(f"   {i+1}/{K}  {time.perf_counter()-t0:.0f}s", flush=True)
top = sorted(rows[:K], key=lambda r: -r["delta_hi"])

worst = max(r["solver_diff"] for r in top)
print(f"[{tag}] max |theta_SCS - theta_CLARABEL| over top {K}: {worst:.2e}")
bad = [r for r in top if r["solver_diff"] > 1e-7]
print(f"[{tag}] {len(bad)} of {K} exceed tau_hi=1e-7 -- listed individually, not averaged")

fields = ["rank", "graph6", "n", "edges", "alpha", "theta_hi", "delta_hi",
          "theta_bulk", "solver_diff", "pr_hi", "status_hi", "perfect", "chi_comp"]
with open(os.path.join(RES, f"{tag}_top{K}.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(fields)
    for i, r in enumerate(top):
        w.writerow([i + 1, r["graph6"], r["n"], r["edges"], r["alpha"],
                    f"{r['theta_hi']:.10f}", f"{r['delta_hi']:.10f}",
                    r["theta"], f"{r['solver_diff']:.3e}", f"{r['pr_hi']:.3e}",
                    r["status_hi"], r["perfect"], r["chi_comp"]])
json.dump(dict(n=a.n, total=len(rows), seed=a.seed, verify_top=K,
               max_solver_diff=worst, n_over_tau_hi=len(bad),
               over_tau_hi=[r["graph6"] for r in bad][:50],
               top50=[dict(rank=i + 1, graph6=r["graph6"], edges=int(r["edges"]),
                           alpha=int(r["alpha"]), theta=r["theta_hi"],
                           delta=r["delta_hi"]) for i, r in enumerate(top[:50])]),
          open(os.path.join(RES, f"report_0c_n{a.n}.json"), "w"), indent=1, default=str)
print(f"[{tag}] top-{K} written; max Delta = {top[0]['delta_hi']:.10f} "
      f"at {top[0]['graph6']} (|E|={top[0]['edges']}, alpha={top[0]['alpha']})")
