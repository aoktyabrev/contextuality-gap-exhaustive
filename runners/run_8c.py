"""Stage 8-c -- where the constants 5 and 6 come from.
PREREGISTRATION_STAGE8C.md.  Runs on data already collected; no new enumeration.
"""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import networkx as nx
from itertools import combinations
from quadc5.g6 import decode_g6, edges_of, complement
from quadc5.alpha import alpha_bitmask
from quadc5.chrom import chromatic_number

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
MAXIMIZERS = {5: "DUW", 6: "EUZw", 7: "FCp`_", 8: "GCQb`o",
              9: "HCRbdO{", 10: "ICRb`yiu?", 11: "J?`D@pgd?{?"}


def load(code):
    n, adj = decode_g6(code)
    E = [tuple(sorted(e)) for e in edges_of(n, adj)]
    g = nx.Graph(); g.add_nodes_from(range(n)); g.add_edges_from(E)
    return n, adj, E, g


def induced_cycles(g, n, k):
    c = 0
    for S in combinations(range(n), k):
        h = g.subgraph(S)
        if h.number_of_edges() == k and all(d == 2 for _, d in h.degree()) and nx.is_connected(h):
            c += 1
    return c


def invariants(code):
    n, adj, E, g = load(code)
    a = alpha_bitmask(n, adj)
    aut = len(list(nx.algorithms.isomorphism.GraphMatcher(g, g).isomorphisms_iter()))
    c5 = induced_cycles(g, n, 5)
    # edges covered by induced C5, and multiplicities
    cov = {e: 0 for e in E}
    for S in combinations(range(n), 5):
        h = g.subgraph(S)
        if h.number_of_edges() == 5 and all(d == 2 for _, d in h.degree()) and nx.is_connected(h):
            for u, v in h.edges():
                cov[tuple(sorted((u, v)))] += 1
    return dict(graph6=code, n=n, alpha=a, edges=len(E),
                density=len(E) / (n * (n - 1) / 2), aut=aut,
                triangles=sum(nx.triangles(g).values()) // 3,
                girth=(min((len(c) for c in nx.cycle_basis(g)), default=0)),
                c5=c5, c7=induced_cycles(g, n, 7),
                edges_covered_by_c5=sum(1 for v in cov.values() if v > 0),
                chi_comp=chromatic_number(n, complement(n, adj)),
                degseq=sorted(d for _, d in g.degree()))


def cone_of(m, k):
    """C_k over the m-vertex maximizer: m + k vertices, layer a_m + k - 1."""
    code = MAXIMIZERS[m]
    mn, madj = decode_g6(code)
    E = [tuple(sorted(e)) for e in edges_of(mn, madj)]
    N = mn + k
    v = N - 1
    E += [(u, v) for u in range(N - 1)]
    g = nx.Graph(); g.add_nodes_from(range(N)); g.add_edges_from(E)
    return N, E, g


if __name__ == "__main__":
    rep = {}
    d8a = json.load(open(os.path.join(RES, "report_8a.json")))
    rows = [r for r in d8a["blocks"]["7b"] if not r["empty"] and r["n"] in (9, 10, 11)]

    # ---- 8.c.2 first: the alternative-formula test, which needs no graph theory -----
    pts = [(r["n"], r["a"], r["equal"]) for r in rows] + [(13, 5, False)]
    fits = []
    for c in range(2, 9):
        for d in range(2, 12):
            f = lambda n, c=c, d=d: max(c, n - d)
            if all((a >= f(n)) == e for n, a, e in pts):
                fits.append((c, d))
    rep["alternatives"] = dict(
        family="inherit  <=>  a >= max(c, n - d)",
        fitting=[{"c": c, "d": d,
                  "predicts_12_5": "inherits" if 5 >= max(c, 12 - d) else "generates",
                  "predicts_13_6": "inherits" if 6 >= max(c, 13 - d) else "generates",
                  "threshold_at": {n: max(c, n - d) for n in (9, 10, 11, 12, 13, 14, 15)}}
                 for c, d in fits])
    print(f"формул вида max(c, n-d), согласных со всеми {len(pts)} точками: {len(fits)}")
    for c, d in fits:
        t = {n: max(c, n - d) for n in (12, 13, 14, 15)}
        print(f"  c={c} d={d}:  порог при n=12..15 = {t};  "
              f"(12,5) -> {'наследует' if 5 >= max(c,12-d) else 'ПОРОЖДАЕТ'};  "
              f"(13,6) -> {'наследует' if 6 >= max(c,13-d) else 'ПОРОЖДАЕТ'}")

    # ---- 8.c.1: structural comparison, generating vs inheriting --------------------
    print("\nструктура максимизаторов слоёв:")
    inv = []
    for r in sorted(rows, key=lambda x: (x["n"], x["a"])):
        i = invariants(r["graph6"])
        i["layer"] = [r["n"], r["a"]]
        i["role"] = "наследует" if r["equal"] else "порождает"
        i["n_minus_a"] = r["n"] - r["a"]
        inv.append(i)
        print(f"  ({i['n']},{i['alpha']}) {i['role']:10s} n-a={i['n_minus_a']} "
              f"|E|={i['edges']:2d} C5={i['c5']:3d} C7={i['c7']:3d} tri={i['triangles']:3d} "
              f"girth={i['girth']} |Aut|={i['aut']:4d} chi(comp)={i['chi_comp']}")
    rep["layer_maximizers"] = inv

    # ---- P-C-5: generating maximizers vs the cones realising their transfer --------
    print("\nP-C-5: порождающие против конусов, реализующих их границу переноса")
    cmp5 = []
    for r in sorted(rows, key=lambda x: (x["n"], x["a"])):
        if r["equal"] or not r["source"]:
            continue
        m, a0 = r["source"]
        if m not in MAXIMIZERS:
            continue
        k = r["n"] - m
        N, E, gc = cone_of(m, k)
        c5_cone = induced_cycles(gc, N, 5)
        c5_gen = next(i["c5"] for i in inv if i["layer"] == [r["n"], r["a"]])
        cmp5.append(dict(layer=[r["n"], r["a"]], cone_from=[m, a0], cone_n=N,
                         c5_generating=c5_gen, c5_cone=c5_cone,
                         generating_has_more=c5_gen > c5_cone))
        print(f"  слой ({r['n']},{r['a']}): порождающий C5={c5_gen}, "
              f"конус из ({m},{a0}) C5={c5_cone}  -> "
              f"{'порождающий БОЛЬШЕ' if c5_gen > c5_cone else 'не больше'}")
    rep["pc5"] = cmp5
    rep["pc5_verdict"] = ("порождающие НЕ содержат больше C5"
                          if not any(x["generating_has_more"] for x in cmp5)
                          else "порождающие содержат больше C5 хотя бы раз")
    print(f"\nP-C-5: {rep['pc5_verdict']}")
    json.dump(rep, open(os.path.join(RES, "report_8c.json"), "w"), indent=1, default=str)
    print(f"\nwrote {os.path.join(RES, 'report_8c.json')}")
