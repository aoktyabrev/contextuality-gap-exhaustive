"""Block 1.c -- the n=10 sweep.  PREREGISTRATION_STAGE1 §4."""
import sys, os, csv, json, time, argparse, glob
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multiprocessing import Pool
from quadc5.sweep10 import run_part, FIELDS
from quadc5 import gengstream
from quadc5.g6 import decode_g6, edges_of
from quadc5.theta import theta_cvxpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=10)
ap.add_argument("--mod", type=int, default=56)
ap.add_argument("--procs", type=int, default=7)
ap.add_argument("--eps", type=float, default=1e-8)
ap.add_argument("--buf", type=int, default=4096)
ap.add_argument("--seed", type=int, default=20260819)
ap.add_argument("--verify-top", type=int, default=1000)
ap.add_argument("--positive-only", action="store_true",
                help="store only positive-gap rows (needed at n=11)")
a = ap.parse_args()
tag = f"n{a.n}"
os.makedirs(RES, exist_ok=True)

expected = gengstream.count(a.n)
print(f"[{tag}] geng reports {expected} connected graphs; {a.mod} parts on {a.procs} procs")
t0 = time.perf_counter()
jobs = [(a.n, r, a.mod, RES, tag, a.eps, a.buf, a.positive_only) for r in range(a.mod)]
tot = sdp = 0
with Pool(a.procs) as pool:
    for k, (nt, ns, el) in enumerate(pool.imap_unordered(run_part, jobs)):
        tot += nt
        sdp += ns
        e = time.perf_counter() - t0
        print(f"  part {k+1}/{a.mod}  cum {tot} graphs, {sdp} SDPs  {e:.0f}s "
              f"ETA {e*(a.mod-k-1)/(k+1):.0f}s", flush=True)
wall = time.perf_counter() - t0
print(f"[{tag}] swept {tot} graphs ({sdp} needed SDP = {100*sdp/tot:.2f}%) in {wall:.0f}s")
assert tot == expected, f"part sum {tot} != geng count {expected}"

# ---- collect the positive-gap rows; the Delta=0 bulk stays on disk only -----
# Streaming collection.  Holding every positive row in memory would need tens of
# gigabytes at n = 11 (about 1.0e8 rows at ~110 bytes each, several times that as
# Python objects); only a bounded top-K is kept, and the bulk file is written by
# concatenation.  Consequence, stated rather than hidden: the bulk file is NOT sorted
# for n >= 11.  The sorted deliverable is the top-K file written below.
import heapq
heap, npos = [], 0
nz = os.path.join(RES, f"{tag}_nonzero.csv")
with open(nz, "w", newline="") as fo:
    w = csv.writer(fo)
    w.writerow(FIELDS)
    for pth in sorted(glob.glob(os.path.join(RES, f"{tag}_part_*.csv"))):
        with open(pth) as fh:
            for r in csv.reader(fh):
                d = float(r[5])
                if d <= 1e-6:
                    continue
                npos += 1
                w.writerow(r)
                if len(heap) < a.verify_top:
                    heapq.heappush(heap, (d, npos, r))
                elif d > heap[0][0]:
                    heapq.heapreplace(heap, (d, npos, r))
print(f"[{tag}] {npos} graphs with Delta > 1e-6")
rows = [r for _, _, r in sorted(heap, key=lambda t: -t[0])]
from quadc5.sweep import _gzip_beside
_gzip_beside(nz)

K = min(a.verify_top, len(rows))
print(f"[{tag}] re-solving top {K} on CLARABEL ...")
top = []
for r in rows[:K]:
    n, adj = decode_g6(r[0])
    hi = theta_cvxpy(n, edges_of(n, adj), solver="CLARABEL")
    top.append(dict(graph6=r[0], n=n, edges=int(r[2]), alpha=int(r[3]),
                    theta_bulk=float(r[4]), theta_hi=hi["theta"],
                    delta_hi=hi["theta"] - int(r[3]), pr_hi=hi["pr"],
                    status_hi=hi["status"], chi_comp=int(r[7]),
                    solver_diff=abs(hi["theta"] - float(r[4]))))
top.sort(key=lambda d: -d["delta_hi"])
worst = max(d["solver_diff"] for d in top)
over = [d["graph6"] for d in top if d["solver_diff"] > 1e-7]
print(f"[{tag}] max |theta_SCS - theta_CLARABEL| over top {K}: {worst:.2e}; "
      f"{len(over)} exceed tau_hi")

with open(os.path.join(RES, f"{tag}_top{K}.csv"), "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["rank", "graph6", "n", "edges", "alpha", "theta_hi", "delta_hi",
                "theta_bulk", "solver_diff", "pr_hi", "status_hi", "chi_comp"])
    for i, d in enumerate(top):
        w.writerow([i + 1, d["graph6"], d["n"], d["edges"], d["alpha"],
                    f"{d['theta_hi']:.10f}", f"{d['delta_hi']:.10f}",
                    f"{d['theta_bulk']:.10f}", f"{d['solver_diff']:.3e}",
                    f"{d['pr_hi']:.3e}", d["status_hi"], d["chi_comp"]])
json.dump(dict(n=a.n, total=tot, expected=expected, sdp_calls=sdp,
               sdp_fraction=sdp / tot, wall_seconds=wall, procs=a.procs,
               seed=a.seed, nonzero=npos, verify_top=K,
               max_solver_diff=worst, over_tau_hi=over[:50],
               top50=[dict(rank=i + 1, **{k: v for k, v in d.items()
                                          if k in ("graph6", "edges", "alpha",
                                                   "theta_hi", "delta_hi")})
                      for i, d in enumerate(top[:50])]),
          open(os.path.join(RES, f"report_1c_n{a.n}.json"), "w"), indent=1, default=str)
print(f"[{tag}] max Delta = {top[0]['delta_hi']:.10f} at {top[0]['graph6']} "
      f"(|E|={top[0]['edges']}, alpha={top[0]['alpha']})")
