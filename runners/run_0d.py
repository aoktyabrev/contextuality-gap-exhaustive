"""Block 0.d -- structure of the top-50.  PREREGISTRATION §6.

Answers the preregistered question at three levels D1/D2/D3 fixed before the run.
"""
import sys, os, csv, json, argparse, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multiprocessing import Pool
import numpy as np
from scipy.stats import spearmanr

from quadc5.g6 import decode_g6, edges_of
from quadc5.structure import induced_c5_analysis, degree_sequence, d_star

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=9)
ap.add_argument("--top", type=int, default=50)
ap.add_argument("--restarts", type=int, default=300)
ap.add_argument("--seed", type=int, default=20260819)
ap.add_argument("--procs", type=int, default=7)
ap.add_argument("--dstar", type=int, default=1)
a = ap.parse_args()

src = [f for f in os.listdir(RES) if f.startswith(f"n{a.n}_top") and f.endswith(".csv")]
src.sort(key=lambda f: -int(f.split("top")[1].split(".")[0]))
rows = list(csv.DictReader(open(os.path.join(RES, src[0]))))[:a.top]
print(f"0.d on {len(rows)} graphs from {src[0]}")


def work(item):
    i, code, alpha = item
    n, adj = decode_g6(code)
    c5 = induced_c5_analysis(n, adj)
    out = dict(rank=i + 1, graph6=code, n=n, edges=c5["n_edges"],
               alpha=alpha, degree_sequence=list(degree_sequence(n, adj)),
               n_c5=c5["n_c5"], edges_covered=c5["edges_covered"],
               mult_hist={str(k): v for k, v in c5["mult_hist"].items()},
               max_pair_overlap=int(c5["overlap"].max(initial=0)) if c5["n_c5"] else 0,
               offdiag_overlaps=sorted(int(c5["overlap"][x, y])
                                       for x in range(c5["n_c5"])
                                       for y in range(x + 1, c5["n_c5"])),
               D1=c5["D1"], D2=c5["D2"], D3=c5["D3"],
               cycles=c5["cycles"])
    if a.dstar:
        ds = d_star(n, adj, alpha, dmax=min(5, n), restarts=a.restarts, seed=a.seed)
        out["d_star"] = ds["d_star"]
        out["d_star_indicated"] = ds["indicated"]
        out["eta_trace"] = {str(k): float(v) for k, v in ds["eta_trace"].items()}
    return out


items = [(i, r["graph6"], int(r["alpha"])) for i, r in enumerate(rows)]
t0 = time.perf_counter()
with Pool(a.procs) as pool:
    res = []
    for k, o in enumerate(pool.imap(work, items)):
        res.append(o)
        if (k + 1) % 10 == 0:
            print(f"  {k+1}/{len(items)}  {time.perf_counter()-t0:.0f}s", flush=True)
res.sort(key=lambda o: o["rank"])

deltas = [float(r["delta_hi"]) for r in rows]
ranks = [o["rank"] for o in res]
edges = [o["edges"] for o in res]
rho_rank, p_rank = spearmanr(ranks, edges)
rho_delta, p_delta = spearmanr(deltas, edges)

summary = dict(
    n=a.n, top=len(res),
    D1_count=sum(o["D1"] for o in res),
    D2_count=sum(o["D2"] for o in res),
    D3_count=sum(o["D3"] for o in res),
    maximizer=res[0],
    spearman_rank_vs_edges=dict(rho=float(rho_rank), p=float(p_rank)),
    spearman_delta_vs_edges=dict(rho=float(rho_delta), p=float(p_delta)),
    edges_min=min(edges), edges_max=max(edges),
    rows=res,
)
json.dump(summary, open(os.path.join(RES, f"report_0d_n{a.n}.json"), "w"),
          indent=1, default=str)

print(f"\n--- 0.d summary (n={a.n}, top {len(res)}) ---")
m = res[0]
print(f"maximizer {m['graph6']}  |E|={m['edges']}  alpha={m['alpha']}  "
      f"deg={m['degree_sequence']}")
print(f"  induced C5: {m['n_c5']}   edges covered: {m['edges_covered']}/{m['edges']}   "
      f"multiplicities {m['mult_hist']}")
print(f"  D1={m['D1']}  D2={m['D2']}  D3={m['D3']}   d*={m.get('d_star')}"
      f"{' (indicated)' if m.get('d_star_indicated') else ''}")
print(f"top-{len(res)}: D1 {summary['D1_count']}/{len(res)}, "
      f"D2 {summary['D2_count']}/{len(res)}, D3 {summary['D3_count']}/{len(res)}")
print(f"Spearman(rank, |E|) = {rho_rank:+.3f} (p={p_rank:.3g});  "
      f"Spearman(Delta, |E|) = {rho_delta:+.3f} (p={p_delta:.3g})")
print(f"|E| range over top-{len(res)}: {min(edges)}..{max(edges)}")
