"""Blocks 5.b, 5.c, 5.e, 5.f -- growth of the layers, their crossings, atoms by layer,
and whether 2/3 is an outlier inside its own layer.

5.f repeats the Stage 4 analysis restricted to one layer, with the same threshold grid,
and the verdict is taken on stability across thresholds, exactly as there.
"""
import sys, os, csv, gzip, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runners"))
from collections import Counter, defaultdict
import numpy as np
from scipy import stats
from run_5a import positive_rows

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def tail_verdict(v, q, drop_top=10):
    pool = v[drop_top:]
    if len(pool) < 40:
        return None
    u = np.quantile(pool, q)
    exc = pool[pool > u] - u
    if len(exc) < 20:
        return None
    xi, _, sg = stats.genpareto.fit(exc, floc=0.0)
    N, p_u = len(v), (v > u).sum() / len(v)
    s = stats.genpareto.sf(v[0] - u, xi, loc=0, scale=sg) if v[0] > u else 1.0
    pct = float(np.clip(1 - p_u * s, 0, 1) ** N) * 100
    return dict(q=q, xi=float(xi), endpoint=float(u - sg / xi) if xi < 0 else None,
                pct=float(pct),
                verdict="below 5th" if pct < 5 else "above 95th" if pct > 95 else "inside")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(); a_ = ap.parse_args()
    tab = json.load(open(os.path.join(RES, "report_5a.json")))
    out = {}

    # ---- 5.b growth of each layer -------------------------------------------
    print("=== 5.b  D(n,a) и приращения по n ===")
    ns = [5, 6, 7, 8, 9, 10]
    D = {}
    for n in ns:
        for r in tab[str(n)]["layers"]:
            D[(n, r["alpha"])] = r["D"]
    growth = {}
    for a in (2, 3, 4, 5):
        seq = [(n, D.get((n, a))) for n in ns if D.get((n, a), 0) > 0]
        if len(seq) < 2:
            continue
        vals = [v for _, v in seq]
        inc = [vals[i + 1] - vals[i] for i in range(len(vals) - 1)]
        rat = [vals[i + 1] / vals[i] for i in range(len(vals) - 1)]
        growth[a] = dict(n=[n for n, _ in seq], values=vals, increments=inc, ratios=rat)
        print(f"  a={a}: n={[n for n,_ in seq]}")
        print(f"        D  = {[round(v,7) for v in vals]}")
        print(f"        ΔD = {[round(x,7) for x in inc]}   отношения {[round(x,3) for x in rat]}")
    out["5b_growth"] = growth

    # ---- 5.c crossings -------------------------------------------------------
    print("\n=== 5.c  расстояние между соседними слоями ===")
    print(f"  {'n':>2} {'D(a=2)':>10} {'D(a=3)':>10} {'D(a=4)':>10} {'3−2':>9} {'3−4':>9}")
    cross = {}
    for n in ns:
        d2, d3, d4 = D.get((n, 2), 0), D.get((n, 3), 0), D.get((n, 4), 0)
        cross[n] = dict(d2=d2, d3=d3, d4=d4, gap32=d3 - d2, gap34=d3 - d4)
        print(f"  {n:>2} {d2:>10.7f} {d3:>10.7f} {d4:>10.7f} {d3-d2:>9.5f} {d3-d4:>9.5f}")
    out["5c_gaps"] = cross

    # ---- 5.e atoms by layer --------------------------------------------------
    print("\n=== 5.e  атомы: все графы вперемешку против отдельного слоя ===")
    atoms = {}
    for n in (9, 10):
        pos = positive_rows(n)
        alld = np.array([d for _, d, _ in pos])
        call = Counter(np.round(alld, 7).tolist())
        va, ca = call.most_common(1)[0]
        rec = dict(n=n, total=len(alld), distinct=len(call),
                   biggest_atom=int(ca), biggest_value=float(va),
                   biggest_share=float(ca / len(alld)), layers={})
        print(f"  n={n}: всего {len(alld)}, различных {len(call)}, "
              f"крупнейший атом {ca} ({ca/len(alld):.1%}) на Δ={va:.7f}")
        bylayer = defaultdict(list)
        for a, d, _ in pos:
            bylayer[a].append(d)
        for a in sorted(bylayer):
            v = np.array(bylayer[a])
            c = Counter(np.round(v, 7).tolist())
            val, cnt = c.most_common(1)[0]
            rec["layers"][str(a)] = dict(count=len(v), distinct=len(c),
                                         biggest_atom=int(cnt), biggest_value=float(val),
                                         biggest_share=float(cnt / len(v)))
            print(f"     слой a={a}: {len(v):>7} графов, различных {len(c):>5}, "
                  f"крупнейший атом {cnt/len(v):>6.1%} на Δ={val:.7f}")
        atoms[str(n)] = rec
    out["5e_atoms"] = atoms

    # ---- 5.f is 2/3 an outlier inside its own layer? -------------------------
    print("\n=== 5.f  2/3 внутри слоя a=3 при n=9, та же сетка порогов ===")
    res_f = {}
    for n in (8, 9, 10):
        pos = [d for a, d, _ in positive_rows(n) if a == 3]
        v_all = np.array(sorted(pos, reverse=True))
        v_dis = np.array(sorted(set(np.round(pos, 9).tolist()), reverse=True))
        k = min(10, len(v_dis) - 1)
        gapratio = (v_dis[0] - v_dis[1]) / (v_dis[1] - v_dis[k]) if v_dis[1] != v_dis[k] else float("inf")
        row = dict(n=n, layer=3, count=len(v_all), distinct=int(len(v_dis)),
                   top3=[float(x) for x in v_dis[:3]], top_gap_ratio=float(gapratio),
                   max_over_median_top100=float(v_all[0] / np.median(v_all[:100])),
                   fits=[])
        print(f"  n={n}, слой a=3: {len(v_all)} графов, различных {len(v_dis)}, "
              f"верх {v_dis[0]:.7f}, дальше {v_dis[1]:.7f}, {v_dis[2]:.7f}")
        print(f"     отрыв (Δ1−Δ2)/(Δ2−Δ11) = {gapratio:.3f}   "
              f"max/медиана(топ-100) = {row['max_over_median_top100']:.4f}")
        for q in (0.50, 0.80, 0.90, 0.95):
            r = tail_verdict(v_dis, q)
            if r:
                row["fits"].append(r)
                ep = f"{r['endpoint']:.4f}" if r["endpoint"] else "inf"
                print(f"     порог {q:.2f}: xi={r['xi']:+7.3f} верх={ep:>8} "
                      f"процентиль={r['pct']:6.2f}%  {r['verdict']}")
        res_f[str(n)] = row
    out["5f_layer3"] = res_f
    json.dump(out, open(os.path.join(RES, "report_5bcef.json"), "w"), indent=1)
    print("\nwrote results/report_5bcef.json")
