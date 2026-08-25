"""Stage 8 block 8.b -- directed search for a counterexample to the upper half of H7.
PREREGISTRATION_STAGE8.md 2.

Looks for a connected graph in an upper layer whose Delta exceeds the transfer bound.
No enumeration.  Three independent methods; alpha exact at every step; any candidate
above threshold is immediately re-solved on a second solver before anything is claimed.
"""
import sys, os, json, math, random, argparse, time
from multiprocessing import Pool
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import networkx as nx
from quadc5.alpha import alpha_bitmask
from quadc5.theta import theta_scs_direct, theta_cvxpy
from quadc5.g6 import encode_g6, decode_g6, edges_of

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

# thresholds fixed in the preregistration, 2.1
TARGETS = [
    dict(tag="T1", n=12, a=5, thr=0.6666666667, src="(9,3)"),
    dict(tag="T2", n=12, a=6, thr=0.4678437298, src="(8,3)"),
    dict(tag="T3", n=13, a=5, thr=0.7748885327, src="(11,4)"),
    dict(tag="T4", n=13, a=6, thr=0.6666666667, src="(9,3)"),
]

# Stage 8-bis (PREREGISTRATION_STAGE8B.md): the reinforced target plus controls where a
# counterexample is KNOWN to exist from complete enumeration, so that a second failure
# can be read at all.
TARGETS_8BIS = [
    dict(tag="G",  n=12, a=5, thr=0.6666666667, src="(9,3)",  role="target"),
    dict(tag="K1", n=11, a=4, thr=0.6666666667, src="(9,3)",  role="control", known=0.7748885),
    dict(tag="K2", n=10, a=3, thr=0.6666666667, src="(9,3)",  role="control", known=0.7071068),
    dict(tag="K3", n=9,  a=2, thr=0.3431457506, src="(8,2)",  role="control", known=0.3837191),
    dict(tag="K4", n=13, a=5, thr=0.7748885327, src="(11,4)", role="control", known=0.8167587),
]
# A candidate must clear the transfer bound by a real margin, not by solver noise.
# The cone starts exactly ON the bound and SCS returns its value a few 1e-9 either
# side, so without a margin every cone start reports a false counterexample on its
# first evaluation.  1e-6 is the campaign's usual zero-threshold at these sizes: two
# orders above the measured solver agreement (~1e-8) and three below the smallest
# genuine excess seen below the boundary (0.0028).  A candidate clearing it still goes
# to a second solver and an exact certificate before anything is claimed.
MARGIN = 1e-6

MAXIMIZERS = {5: "DUW", 6: "EUZw", 7: "FCp`_", 8: "GCQb`o",
              9: "HCRbdO{", 10: "ICRb`yiu?", 11: "J?`D@pgd?{?"}


def adj_bits(n, E):
    adj = [0] * n
    for u, v in E:
        adj[u] |= 1 << v
        adj[v] |= 1 << u
    return adj


def alpha_of(n, E):
    return alpha_bitmask(n, adj_bits(n, E))


def delta_of(n, E, a, eps=1e-8):
    return theta_scs_direct(n, E, eps=eps)["theta"] - a


def connected(n, E):
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(E)
    return nx.is_connected(g)


def random_start(n, a, rng, tries=4000):
    """A connected graph on n vertices with alpha exactly a."""
    for _ in range(tries):
        p = rng.uniform(0.15, 0.6)
        g = nx.gnp_random_graph(n, p, seed=rng.randint(0, 10 ** 9))
        if not nx.is_connected(g):
            continue
        E = [tuple(sorted(e)) for e in g.edges()]
        if alpha_of(n, E) == a:
            return E
    return None


def cone_start(n, a):
    """The cone itself: it sits exactly on the transfer bound (preregistration 2.2.3)."""
    out = []
    for m, code in MAXIMIZERS.items():
        if m >= n:
            continue
        k = n - m
        mn, madj = decode_g6(code)
        am = alpha_of(mn, edges_of(mn, madj))
        if am + k - 1 != a:
            continue
        E = list(map(lambda e: tuple(sorted(e)), edges_of(mn, madj)))
        v = n - 1
        E += [(u, v) for u in range(n - 1)]
        out.append((code, m, [tuple(sorted(e)) for e in E]))
    return out


def neighbours(n, E, rng, k=1):
    """Toggle k edges at random, keeping it simple and local."""
    Es = set(E)
    for _ in range(k):
        u = rng.randrange(n); v = rng.randrange(n)
        while v == u:
            v = rng.randrange(n)
        e = (min(u, v), max(u, v))
        if e in Es:
            Es.discard(e)
        else:
            Es.add(e)
    return sorted(Es)


def run_search(method, tgt, restarts, steps, rng, budget, log):
    n, a, thr = tgt["n"], tgt["a"], tgt["thr"]
    best = dict(delta=-1.0, edges=None, graph6=None)
    evals = 0
    starts = []
    if method == "cone":
        starts = [e for _, _, e in cone_start(n, a)]
        if not starts:
            log.append(f"{tgt['tag']}/cone: no cone lands in layer {a}; method skipped")
            return best, 0
    for r in range(restarts):
        if evals >= budget:
            break
        if method == "cone":
            E = list(starts[r % len(starts)])
        else:
            E = random_start(n, a, rng)
            if E is None:
                continue
        cur = delta_of(n, E, a); evals += 1
        T0 = 0.05
        for s in range(steps):
            if evals >= budget:
                break
            E2 = neighbours(n, E, rng, k=1 if rng.random() < 0.8 else 2)
            if not E2 or not connected(n, E2):
                continue
            if alpha_of(n, E2) != a:
                continue
            d2 = delta_of(n, E2, a); evals += 1
            if d2 > cur:
                E, cur = E2, d2
            elif method == "anneal":
                T = T0 * (1.0 - s / steps) + 1e-4
                if rng.random() < math.exp((d2 - cur) / T):
                    E, cur = E2, d2
            if cur > best["delta"]:
                best = dict(delta=cur, edges=list(E), graph6=None)
            if cur > thr + MARGIN:
                log.append(f"{tgt['tag']}/{method}: CANDIDATE Delta={cur:.10f} "
                           f"> {thr} + {MARGIN}")
                return best, evals
    return best, evals


def one_pair(job):
    """One (target, method) pair.  The twelve pairs are independent, so they run in
    parallel; the sealed per-pair budget is untouched by that."""
    tgt, method, restarts, steps, seed = job
    rng = random.Random(seed + hash((tgt["tag"], method)) % 10 ** 6)
    log = []
    ts = time.time()
    best, evals = run_search(method, tgt, restarts, steps, rng, restarts * steps, log)
    row = dict(target=tgt["tag"], role=tgt.get("role", "target"),
               known=tgt.get("known"), n=tgt["n"], a=tgt["a"], threshold=tgt["thr"],
               method=method, best_delta=best["delta"], evaluations=evals,
               seconds=time.time() - ts,
               exceeded=best["delta"] > tgt["thr"] + MARGIN,
               gap_to_threshold=best["delta"] - tgt["thr"], log=log)
    if best["edges"]:
        row["best_edges"] = [list(e) for e in best["edges"]]
        if row["exceeded"]:
            row["clarabel_delta"] = theta_cvxpy(tgt["n"], best["edges"],
                                                solver="CLARABEL")["theta"] - tgt["a"]
    return row


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--restarts", type=int, default=100)
    ap.add_argument("--steps", type=int, default=3000)
    ap.add_argument("--procs", type=int, default=7)
    ap.add_argument("--seed", type=int, default=20260819)
    ap.add_argument("--out", default=os.path.join(RES, "report_8b.json"))
    ap.add_argument("--bis", action="store_true",
                    help="Stage 8-bis: reinforced target plus controls")
    ap.add_argument("--target-restarts", type=int, default=1000,
                    help="restarts for the 8-bis target (10x budget)")
    args = ap.parse_args()
    methods = ["hill", "anneal", "cone"]
    if args.bis:
        jobs = []
        for t in TARGETS_8BIS:
            for m in methods:
                if t["tag"] == "K4" and m == "cone":
                    continue          # K4 tests cold starts only, preregistration 1
                r = args.target_restarts if t["role"] == "target" else args.restarts
                jobs.append((t, m, r, args.steps, args.seed))
    else:
        jobs = [(t, m, args.restarts, args.steps, args.seed) for t in TARGETS for m in methods]
    budget = args.restarts * args.steps
    print(f"{len(jobs)} pairs, budget {budget} theta-evaluations each "
          f"({len(jobs)*budget} total), {args.procs} processes", flush=True)
    rep = {"budget_per_pair": budget, "total_budget": sum(j[2] * j[3] for j in jobs),
           "methods": methods, "margin": MARGIN, "bis": args.bis, "targets": []}
    t0 = time.time()
    with Pool(args.procs) as pool:
        for row in pool.imap_unordered(one_pair, jobs):
            rep["targets"].append(row)
            print(f"{row['target']} n={row['n']} a={row['a']} {row['method']:6s}: "
                  f"best Delta={row['best_delta']:.10f} vs thr {row['threshold']:.10f} "
                  f"({row['gap_to_threshold']:+.2e})  {row['evaluations']} evals  "
                  f"{row['seconds']:.0f}s  {'EXCEEDED' if row['exceeded'] else 'no'}",
                  flush=True)
            json.dump(rep, open(args.out, "w"), indent=1)
    rep["wall_seconds"] = time.time() - t0
    rep["any_exceeded"] = any(r["exceeded"] for r in rep["targets"])
    json.dump(rep, open(args.out, "w"), indent=1)
    print(f"\nwrote {args.out}; any threshold exceeded: {rep['any_exceeded']}")
