"""Block 4.c -- do the C6+K3 constructions continue to ten vertices?

The nine-vertex optimum is a hexagon plus a triangle, each triangle vertex joined to one
antipodal pair of the hexagon.  Three natural continuations are searched EXHAUSTIVELY
over their families, not sampled:

  C7 + K3   every assignment of a pair of cycle vertices to each triangle vertex
  C6 + K4   the same with four clique vertices on a hexagon
  C6+K3+v   the nine-vertex optimum plus a tenth vertex joined to every subset

alpha and theta are reported separately, so that what breaks is visible.
Rank is computed as the number of ten-vertex graphs with a strictly larger gap, which
needs no canonical labelling.
"""
import sys, os, csv, gzip, json, itertools, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import networkx as nx

from quadc5.g6 import decode_g6, edges_of, adj_from_edges, to_networkx
from quadc5.alpha import alpha_bitmask
from quadc5.theta import theta_scs_direct, theta_cvxpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
N9_MAX = "HCRbdO{"


def gap(n, edges):
    adj = adj_from_edges(n, edges)
    a = alpha_bitmask(n, adj)
    th = theta_scs_direct(n, edges, eps=1e-9)["theta"]
    return a, th, th - a


def family_cycle_plus_clique(m, k):
    """C_m plus K_k, each clique vertex joined to a pair of cycle vertices.
    Every assignment is tried; m + k must be 10."""
    assert m + k == 10
    cyc = [(i, (i + 1) % m) for i in range(m)]
    cli = [(m + i, m + j) for i in range(k) for j in range(i + 1, k)]
    pairs = list(itertools.combinations(range(m), 2))
    best, seen = [], set()
    for combo in itertools.product(pairs, repeat=k):
        E = list(cyc) + list(cli)
        for ci, (u, v) in enumerate(combo):
            E.append((m + ci, u)); E.append((m + ci, v))
        E = sorted(set(tuple(sorted(e)) for e in E))
        key = tuple(E)
        if key in seen:
            continue
        seen.add(key)
        adj = adj_from_edges(10, E)
        if not _connected(10, adj):
            continue
        a, th, d = gap(10, E)
        best.append((d, a, th, E))
    best.sort(key=lambda t: -t[0])
    return best


def _connected(n, adj):
    seen, st = 1, [0]
    while st:
        v = st.pop()
        nb = adj[v] & ~seen
        while nb:
            b = nb & -nb; seen |= b; st.append(b.bit_length() - 1); nb ^= b
    return seen == (1 << n) - 1


def family_plus_vertex():
    """The nine-vertex optimum plus a tenth vertex joined to every non-empty subset."""
    n9, adj9 = decode_g6(N9_MAX)
    E9 = edges_of(n9, adj9)
    out = []
    for mask in range(1, 1 << n9):
        E = list(E9) + [(v, 9) for v in range(n9) if (mask >> v) & 1]
        a, th, d = gap(10, E)
        out.append((d, a, th, sorted(v for v in range(n9) if (mask >> v) & 1)))
    out.sort(key=lambda t: -t[0])
    return out


def rank_of(delta, all_deltas):
    return int((all_deltas > delta + 1e-9).sum()) + 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    a = ap.parse_args()
    with gzip.open(os.path.join(RES, "n10_nonzero.csv.gz"), "rt") as fh:
        rd = csv.reader(fh); hdr = next(rd); di = hdr.index("delta")
        alld = np.array(sorted((float(r[di]) for r in rd), reverse=True))
    print(f"reference: {len(alld)} ten-vertex graphs with a positive gap; "
          f"max = {alld[0]:.7f}\n")
    out = {}
    for label, fn in (("C7+K3", lambda: family_cycle_plus_clique(7, 3)),
                      ("C6+K4", lambda: family_cycle_plus_clique(6, 4)),
                      ("C6+K3 plus a tenth vertex", family_plus_vertex)):
        res = fn()
        top = res[:5]
        print(f"=== {label}: {len(res)} connected members searched ===")
        for d, al, th, spec in top:
            print(f"   Delta={d:.7f}  alpha={al}  theta={th:.7f}  rank={rank_of(d, alld):>7}  {spec}")
        out[label] = dict(members=len(res),
                          best=[dict(delta=float(d), alpha=int(al), theta=float(th),
                                     rank=rank_of(d, alld), spec=str(s)) for d, al, th, s in top])
        print()
    out["reference"] = dict(n10_max=float(alld[0]), n9_max=2 / 3,
                            positive_graphs=int(len(alld)))
    json.dump(out, open(os.path.join(RES, "report_4c.json"), "w"), indent=1)
    print("wrote results/report_4c.json")
