"""Blocks 1.e and 1.f -- the series over n and the invariants.  PREREGISTRATION_STAGE1 §6."""
import sys, os, csv, json, glob, argparse, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import networkx as nx

from quadc5 import gengstream
from quadc5.g6 import decode_g6, edges_of, to_networkx
from quadc5.alpha import alpha_bitmask
from quadc5.theta import theta_scs_direct, theta_cvxpy
from quadc5.structure import induced_c5_analysis, degree_sequence, d_star

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

ap = argparse.ArgumentParser()
ap.add_argument("--restarts", type=int, default=300)
ap.add_argument("--seed", type=int, default=20260819)
ap.add_argument("--top", type=int, default=10)
a = ap.parse_args()


def sweep_small(n):
    """Brute-force max over all connected graphs on n vertices (small n only)."""
    best = None
    for code in gengstream.stream(n):
        nn, adj = decode_g6(code)
        al = alpha_bitmask(nn, adj)
        th = theta_scs_direct(nn, edges_of(nn, adj), eps=1e-9)["theta"]
        if best is None or th - al > best[1]:
            best = (code, th - al, al)
    return best[0]


def cycle_plus_clique(n, adj):
    """Every split of V into a set inducing a cycle and a complement inducing a clique.

    Exhaustive over all 2^n subsets -- for n <= 10 that is 1024 checks, so this is a
    complete answer, not a heuristic.  Reported as (cycle_len, clique_len) pairs.
    """
    out = []
    for mask in range(1 << n):
        S = [v for v in range(n) if (mask >> v) & 1]
        C = [v for v in range(n) if not (mask >> v) & 1]
        if len(S) < 3:
            continue
        if any(bin(adj[v] & mask).count("1") != 2 for v in S):
            continue
        seen, stack = 1 << S[0], [S[0]]
        cnt = 1
        while stack:
            v = stack.pop()
            nb = adj[v] & mask & ~seen
            while nb:
                b = nb & -nb
                seen |= b
                cnt += 1
                stack.append(b.bit_length() - 1)
                nb ^= b
        if cnt != len(S):
            continue
        if any(not ((adj[u] >> v) & 1) for u, v in itertools.combinations(C, 2)):
            continue
        out.append((len(S), len(C), tuple(S), tuple(C)))
    return out


def profile(code, want_dstar=True):
    n, adj = decode_g6(code)
    G = to_networkx(n, adj)
    E = edges_of(n, adj)
    al = alpha_bitmask(n, adj)
    th = theta_cvxpy(n, E, solver="CLARABEL")["theta"]
    deg = dict(G.degree())
    aut = sum(1 for _ in nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())
    vt = len(set(deg.values())) == 1 and nx.is_isomorphic(G, G) and _vertex_transitive(G)
    c5 = induced_c5_analysis(n, adj)
    cpc = cycle_plus_clique(n, adj)
    prof = dict(graph6=code, n=n, edges=len(E), alpha=al, theta=th, delta=th - al,
                density_pairs=len(E) / (n * (n - 1) / 2), edges_per_vertex=len(E) / n,
                degree_sequence=list(degree_sequence(n, adj)),
                regular=len(set(deg.values())) == 1, vertex_transitive=vt,
                aut_order=aut, n_c5=c5["n_c5"], edges_covered=c5["edges_covered"],
                D1=c5["D1"], D2=c5["D2"], D3=c5["D3"],
                cycle_plus_clique=[(s, c) for (s, c, _, _) in cpc],
                cycle_plus_clique_example=(cpc[0][2], cpc[0][3]) if cpc else None,
                triangles=sum(nx.triangles(G).values()) // 3)
    if want_dstar:
        ds = d_star(n, adj, al, dmax=min(5, n), restarts=a.restarts, seed=a.seed)
        prof["d_star"] = ds["d_star"]
        prof["d_star_indicated"] = ds["indicated"]
        prof["eta_trace"] = {str(k): float(v) for k, v in ds["eta_trace"].items()}
    return prof


def _vertex_transitive(G):
    n = G.number_of_nodes()
    orbit = {0}
    for iso in nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter():
        orbit.add(iso[0])
        if len(orbit) == n:
            return True
    return len(orbit) == n


# ---- the maximizer of each size --------------------------------------------
MAX = {}
for n in (5, 6, 7):
    MAX[n] = sweep_small(n)
    print(f"n={n}: maximizer {MAX[n]} (brute force over all connected graphs)")

for n, path, col in ((8, "n8_all.csv", None), (9, "n9_top1000.csv", "delta_hi")):
    p = os.path.join(RES, path)
    rows = list(csv.DictReader(open(p)))
    key = col or "delta"
    rows.sort(key=lambda r: -float(r[key]))
    MAX[n] = rows[0]["graph6"]
    print(f"n={n}: maximizer {MAX[n]}")

p10 = sorted(glob.glob(os.path.join(RES, "n10_top*.csv")))
if p10:
    rows = list(csv.DictReader(open(p10[-1])))
    rows.sort(key=lambda r: -float(r["delta_hi"]))
    MAX[10] = rows[0]["graph6"]
    print(f"n=10: maximizer {MAX[10]}")

series = {}
for n in sorted(MAX):
    print(f"\n--- profiling n={n} ---")
    series[n] = profile(MAX[n])
    s = series[n]
    print(f"  {s['graph6']}  |E|={s['edges']}  alpha={s['alpha']}  "
          f"Delta={s['delta']:.10f}  deg={s['degree_sequence']}")
    print(f"  density={s['density_pairs']:.3f}  regular={s['regular']}  "
          f"vertex-transitive={s['vertex_transitive']}  |Aut|={s['aut_order']}  "
          f"triangles={s['triangles']}")
    print(f"  induced C5={s['n_c5']} (D1={s['D1']} D2={s['D2']} D3={s['D3']})  "
          f"cycle+clique splits={s['cycle_plus_clique']}")
    print(f"  d*={s.get('d_star')}{' (indicated)' if s.get('d_star_indicated') else ''}"
          f"  eta={s.get('eta_trace')}")

json.dump(series, open(os.path.join(RES, "report_1ef.json"), "w"), indent=1, default=str)
print("\nwrote results/report_1ef.json")
