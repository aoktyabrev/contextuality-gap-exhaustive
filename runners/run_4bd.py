"""Blocks 4.b and 4.d -- who is on top at n = 10, and the cheap hypotheses.

Everything is read from results/report_3b.json and report_4a.json; nothing is re-swept.
"""
import sys, os, json, itertools, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import Counter
import networkx as nx
from scipy.stats import spearmanr

from quadc5.g6 import decode_g6, to_networkx

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
N9_MAX = "HCRbdO{"


def contains_induced(code, target_code):
    n, adj = decode_g6(code)
    G = to_networkx(n, adj)
    m, madj = decode_g6(target_code)
    T = to_networkx(m, madj)
    for S in itertools.combinations(range(n), m):
        if nx.is_isomorphic(G.subgraph(S), T):
            return True
    return False


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    a = ap.parse_args()
    tab = json.load(open(os.path.join(RES, "report_3b.json")))
    fa = json.load(open(os.path.join(RES, "report_4a.json")))
    out = {}

    print("=== 4.b -- the top-10 as families, n = 9 against n = 10 ===")
    fam = {}
    for n in ("9", "10"):
        rows = tab[n]
        f = dict(
            n=int(n),
            with_cycle_plus_clique=sum(1 for r in rows if r["cycle_plus_clique"]),
            cpc_shapes=sorted({tuple(x) for r in rows for x in r["cycle_plus_clique"]}),
            regular=sum(1 for r in rows if r["regular"]),
            vertex_transitive=sum(1 for r in rows if r["vertex_transitive"]),
            aut_orders=sorted(r["aut_order"] for r in rows),
            c5_range=[min(r["n_c5"] for r in rows), max(r["n_c5"] for r in rows)],
            edges_range=[min(r["edges"] for r in rows), max(r["edges"] for r in rows)],
            alpha=sorted({r["alpha"] for r in rows}),
            all_edges_covered=sum(1 for r in rows if r["edges_covered"] == r["edges"]),
        )
        fam[n] = f
        print(f"  n={n}: цикл+клика {f['with_cycle_plus_clique']}/10 {f['cpc_shapes']}, "
              f"регулярных {f['regular']}, |Aut| {f['aut_orders']}, C5 {f['c5_range']}, "
              f"все рёбра покрыты у {f['all_edges_covered']}/10")
    out["4b_families"] = fam

    print("\n  содержит ли лидер десятки девятивершинный оптимум как индуцированный подграф:")
    holds = []
    for r in tab["10"]:
        h = contains_induced(r["graph6"], N9_MAX)
        holds.append((r["rank"], r["graph6"], h))
        print(f"    ранг {r['rank']:>2} {r['graph6']:11s} {'да' if h else 'нет'}")
    out["4b_contains_n9_max"] = [dict(rank=x, graph6=y, contains=z) for x, y, z in holds]

    print("\n=== 4.d -- cheap hypotheses ===")
    ns = [7, 8, 9, 10]
    mm = [fa["sizes"][str(n)]["max_over_median_top100"] for n in ns]
    par = [n % 2 for n in ns]
    print(f"  чётность:  n={ns}  метрика={[round(x,4) for x in mm]}  чётность={par}")
    odd = [m for m, p in zip(mm, par) if p == 1]
    even = [m for m, p in zip(mm, par) if p == 0]
    print(f"    нечётные {[round(x,3) for x in odd]}  чётные {[round(x,3) for x in even]} "
          f"-> диапазоны {'пересекаются' if min(odd)<max(even) and min(even)<max(odd) else 'разделены'}")
    out["4d_parity"] = dict(n=ns, metric=mm, odd=odd, even=even,
                            separated=not (min(odd) < max(even) and min(even) < max(odd)))

    alphas = {n: sorted({r["alpha"] for r in tab[str(n)]}) for n in (5, 6, 7, 8, 9, 10)}
    print(f"  alpha в топ-10 по размерам: {alphas}")
    out["4d_alpha"] = {str(k): v for k, v in alphas.items()}
    varies = any(len(v) > 1 for v in alphas.values())
    print(f"    alpha варьируется внутри топ-10 хоть где-нибудь: {varies}"
          f" -> {'корреляция считается' if varies else 'коррелировать не с чем'}")

    dstar = {}
    for src in ("report_0d_n9.json", "report_0d_n10.json"):
        p = os.path.join(RES, src)
        if os.path.exists(p):
            d = json.load(open(p))
            dstar[src] = Counter(str(r.get("d_star")) for r in d["rows"][:10])
    print(f"  d* в топ-10: {dict(dstar)}")
    out["4d_dstar"] = {k: dict(v) for k, v in dstar.items()}

    json.dump(out, open(os.path.join(RES, "report_4bd.json"), "w"), indent=1, default=str)
    print("\nwrote results/report_4bd.json")
