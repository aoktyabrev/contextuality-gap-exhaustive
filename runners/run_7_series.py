"""Stage 7 block 7.3 -- the series table, density, and the nesting picture,
recomputed with the final n = 11 result."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import networkx as nx
from itertools import combinations
from quadc5.g6 import decode_g6, edges_of, complement
from quadc5.alpha import alpha_bitmask
from quadc5.chrom import chromatic_number

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

MAX = [(5, "DUW"), (6, "EUZw"), (7, "FCp`_"), (8, "GCQb`o"),
       (9, "HCRbdO{"), (10, "ICRb`yiu?"), (11, "J?`D@pgd?{?")]
FORM = {5: ("sqrt(5)", 2), 6: ("sqrt(5)", 2), 7: ("root of x^3+7x^2-49x+49", 3),
        8: ("root of x^4-x^3+23x^2-155x+158", 4), 9: ("11/3", 1),
        10: ("3+sqrt(2)/2", 2), 11: (None, None)}


def load(code):
    n, adj = decode_g6(code)
    E = edges_of(n, adj)
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(E)
    return n, adj, E, g


def induced_c5(g, n):
    c = 0
    for S in combinations(range(n), 5):
        h = g.subgraph(S)
        if h.number_of_edges() == 5 and all(d == 2 for _, d in h.degree()) and nx.is_connected(h):
            c += 1
    return c


rows = []
G = {}
for n, code in MAX:
    nn, adj, E, g = load(code)
    G[n] = g
    a = alpha_bitmask(nn, adj)
    aut = len(list(nx.algorithms.isomorphism.GraphMatcher(g, g).isomorphisms_iter()))
    rows.append(dict(n=n, code=code, edges=len(E), density=len(E) / (n * (n - 1) / 2),
                     epv=len(E) / n, alpha=a, aut=aut,
                     regular=len({d for _, d in g.degree()}) == 1,
                     vt=(aut % n == 0 and nx.is_vertex_transitive(g)) if hasattr(nx, "is_vertex_transitive") else None,
                     triangles=sum(nx.triangles(g).values()) // 3,
                     c5=induced_c5(g, n), chi_comp=chromatic_number(nn, complement(nn, adj)),
                     form=FORM[n][0], degree=FORM[n][1]))

print(f"{'n':>3} {'максимизатор':>13} {'|E|':>4} {'плотн':>7} {'E/n':>6} {'a':>2} "
      f"{'|Aut|':>6} {'треуг':>6} {'C5':>4} {'chi(compl)':>10} {'степень':>8}")
for r in rows:
    print(f"{r['n']:>3} {r['code']:>13} {r['edges']:>4} {r['density']:>7.4f} {r['epv']:>6.2f} "
          f"{r['alpha']:>2} {r['aut']:>6} {r['triangles']:>6} {r['c5']:>4} {r['chi_comp']:>10} "
          f"{str(r['degree']):>8}")

print("\n=== вложенность: содержит ли максимизатор n (строка) максимизатор m (столбец) "
      "индуцированным подграфом ===")
sizes = [n for n, _ in MAX]
print("     " + "".join(f"{m:>6}" for m in sizes))
nest = {}
for n in sizes:
    line = f"{n:>3}  "
    for m in sizes:
        if m >= n:
            line += "     ."
            continue
        found = any(nx.is_isomorphic(G[n].subgraph(S), G[m]) for S in combinations(range(n), m))
        nest[(n, m)] = found
        line += f"{'да' if found else 'нет':>6}"
    print(line)

json.dump(dict(series=rows, nesting={f"{n}<-{m}": v for (n, m), v in nest.items()}),
          open(os.path.join(RES, "report_7_series.json"), "w"), indent=1, default=str)
print(f"\nwrote {os.path.join(RES, 'report_7_series.json')}")
