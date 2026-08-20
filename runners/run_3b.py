"""Block 3.b -- the invariant table over the top-10 of every size, and the data for 3.c.

Everything here is measurement, not hypothesis testing; the two questions in 3.c are
answered from this table.
"""
import sys, os, csv, json, glob, itertools, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import networkx as nx
import numpy as np

from quadc5 import gengstream
from quadc5.g6 import decode_g6, to_networkx, edges_of, complement
from quadc5.alpha import alpha_bitmask
from quadc5.theta import theta_scs_direct, theta_cvxpy
from quadc5.perfect import induced_cycles_of_length
from quadc5.structure import induced_c5_analysis, degree_sequence

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def aut_profile(G):
    n = G.number_of_nodes()
    autos = list(nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())
    order = len(autos)
    vorb = {}
    for v in G:
        vorb.setdefault(min(a[v] for a in autos), set()).add(v)
    v_orbits = sorted(len(s) for s in vorb.values())
    eorb = {}
    for (u, v) in G.edges():
        key = min(tuple(sorted((a[u], a[v]))) for a in autos)
        eorb.setdefault(key, set()).add(tuple(sorted((u, v))))
    e_orbits = sorted(len(s) for s in eorb.values())
    return dict(aut_order=order, vertex_transitive=len(v_orbits) == 1,
                edge_transitive=len(e_orbits) == 1,
                vertex_orbits=v_orbits, edge_orbits=e_orbits,
                abelian=_is_abelian(autos, G))


def _is_abelian(autos, G):
    if len(autos) > 200:
        return None
    nodes = list(G)
    for a in autos[:40]:
        for b in autos[:40]:
            if any(a[b[v]] != b[a[v]] for v in nodes):
                return False
    return True


def cycle_plus_clique(n, adj):
    out = []
    for mask in range(1 << n):
        S = [v for v in range(n) if (mask >> v) & 1]
        C = [v for v in range(n) if not (mask >> v) & 1]
        if len(S) < 3:
            continue
        if any(bin(adj[v] & mask).count("1") != 2 for v in S):
            continue
        seen, stack, cnt = 1 << S[0], [S[0]], 1
        while stack:
            v = stack.pop()
            nb = adj[v] & mask & ~seen
            while nb:
                b = nb & -nb
                seen |= b; cnt += 1; stack.append(b.bit_length() - 1); nb ^= b
        if cnt != len(S):
            continue
        if any(not ((adj[u] >> v) & 1) for u, v in itertools.combinations(C, 2)):
            continue
        out.append((len(S), len(C)))
    return sorted(set(out))


def odd_holes(n, adj):
    """Counts of induced odd cycles of length 5, 7, 9 in G and in the complement."""
    co = complement(n, adj)
    res = {}
    for k in (5, 7, 9):
        if k <= n:
            res[f"C{k}"] = len(induced_cycles_of_length(n, adj, k))
            res[f"coC{k}"] = len(induced_cycles_of_length(n, co, k))
    return res


def profile(code, delta=None):
    n, adj = decode_g6(code)
    G = to_networkx(n, adj)
    E = edges_of(n, adj)
    al = alpha_bitmask(n, adj)
    th = theta_cvxpy(n, E, solver="CLARABEL")["theta"] if delta is None else al + delta
    c5 = induced_c5_analysis(n, adj)
    deg = dict(G.degree())
    p = dict(graph6=code, n=n, edges=len(E),
             density=len(E) / (n * (n - 1) / 2), edges_per_vertex=len(E) / n,
             alpha=al, theta=th, delta=th - al,
             degree_sequence=list(degree_sequence(n, adj)),
             regular=len(set(deg.values())) == 1,
             triangles=sum(nx.triangles(G).values()) // 3,
             n_c5=c5["n_c5"], edges_covered=c5["edges_covered"],
             mult_hist={str(k): v for k, v in c5["mult_hist"].items()},
             cycle_plus_clique=cycle_plus_clique(n, adj))
    p.update(aut_profile(G))
    p.update(odd_holes(n, adj))
    return p


def top_of(n, k=10):
    """The k largest Delta at size n, from the committed results."""
    if n <= 7:
        vals = []
        for code in gengstream.stream(n):
            nn, adj = decode_g6(code)
            a = alpha_bitmask(nn, adj)
            d = theta_scs_direct(nn, edges_of(nn, adj), eps=1e-9)["theta"] - a
            if d > 1e-6:
                vals.append((d, code))
        vals.sort(reverse=True)
        return [(c, d) for d, c in vals[:k]]
    if n == 8:
        rows = list(csv.DictReader(open(os.path.join(RES, "n8_all.csv"))))
        rows.sort(key=lambda r: -float(r["delta"]))
        return [(r["graph6"], float(r["delta"])) for r in rows[:k]]
    src = sorted(glob.glob(os.path.join(RES, f"n{n}_top*.csv")))[-1]
    rows = list(csv.DictReader(open(src)))
    rows.sort(key=lambda r: -float(r["delta_hi"]))
    return [(r["graph6"], float(r["delta_hi"])) for r in rows[:k]]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=10)
    a = ap.parse_args()
    out = {}
    for n in (5, 6, 7, 8, 9, 10):
        tops = top_of(n, a.top)
        print(f"\n=== n = {n} (top {len(tops)}) ===")
        rows = []
        for rank, (code, d) in enumerate(tops, 1):
            p = profile(code, delta=d)
            p["rank"] = rank
            rows.append(p)
            print(f"  {rank:2d} {code:11s} |E|={p['edges']:2d} a={p['alpha']} "
                  f"D={p['delta']:.7f} |Aut|={p['aut_order']:3d} "
                  f"vt={str(p['vertex_transitive'])[0]} et={str(p['edge_transitive'])[0]} "
                  f"reg={str(p['regular'])[0]} C5={p['n_c5']:2d} cpc={p['cycle_plus_clique']}")
        out[str(n)] = rows
    json.dump(out, open(os.path.join(RES, "report_3b.json"), "w"), indent=1, default=str)
    print("\nwrote results/report_3b.json")
