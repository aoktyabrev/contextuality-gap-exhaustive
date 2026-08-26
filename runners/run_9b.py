"""Stage 9, block 9.b -- the three hypotheses, judged by the sealed criteria only.

Every threshold in here is quoted from PREREGISTRATION_STAGE9 3.  Nothing is tuned
after seeing the data; where a criterion is silent the verdict is "no separation",
not a new criterion.

Block 9.c is folded in: the not-found fraction is reported per cell, never replaced
by a bound, and never dropped from the statistics -- which is what the censored
median in 3.0 exists for.

Block 9.6 (the alternative-formula rule) is applied here rather than in prose: for
any dependence on |Aut| the competitors -- rank X, vertex orbits, |E|, n -- are
scored on the same table, and the number of cells that DISCRIMINATE between them
is counted and printed.  Cells where both explanations agree do not count.
"""
import sys, os, json, argparse, math
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import defaultdict
from scipy.stats import spearmanr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
JSONL = os.path.join(RES, "stage9_degrees.jsonl")
CENSOR = 25                       # 3.0: a rank above every degree on the ladder
SIZES_AB = [8, 9, 10, 11]         # 2.1: B is empty below 8, so A-vs-B rests on four


def load():
    rows = []
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def cens(d):
    """Censored degree, 3.0.  low_precision and error are excluded, not censored."""
    if d["status"] == "hit":
        return d["degree"]
    if d["status"] in ("not_found", "pslq_unstable"):
        return CENSOR
    return None


def median(xs):
    xs = sorted(xs)
    if not xs:
        return None
    k = len(xs)
    return xs[k // 2] if k % 2 else (xs[k // 2 - 1] + xs[k // 2]) / 2


def cell_stats(rows):
    used = [c for c in (cens(d) for d in rows) if c is not None]
    nf = sum(1 for d in rows if d["status"] in ("not_found", "pslq_unstable"))
    unst = sum(1 for d in rows if d["status"] == "pslq_unstable")
    low = sum(1 for d in rows if d["status"] == "low_precision")
    err = sum(1 for d in rows if d["status"] == "error")
    hits = [d["degree"] for d in rows if d["status"] == "hit"]
    dist = defaultdict(int)
    for h in hits:
        dist[h] += 1
    return dict(n_graphs=len(rows), n_used=len(used),
                med_cens=median(used), med_hits=median(hits),
                f_nf=(nf / len(used)) if used else None, n_nf=nf,
                n_unstable=unst, n_low_precision=low, n_error=err,
                deg1=sum(1 for h in hits if h == 1),
                le2=sum(1 for h in hits if h <= 2),
                le4=sum(1 for h in hits if h <= 4),
                dist={str(k): v for k, v in sorted(dist.items())})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "report_9b.json"))
    a = ap.parse_args()
    rows = load()
    by = defaultdict(list)
    for d in rows:
        by[(d["n"], d["sample"])].append(d)

    rep = {"censor_value": CENSOR, "sizes_for_AB": SIZES_AB, "cells": {}}

    print("=== 9.a / 9.c -- distribution of algebraic degrees, per cell ===")
    print(f"{'n':>3} {'выб':>4} {'графов':>7} {'med_cens':>9} {'med_hit':>8} "
          f"{'доля НН':>8} {'НН':>4} {'нест':>5} {'низкТ':>6} {'deg=1':>6} "
          f"{'<=2':>5} {'<=4':>5}   распределение степеней")
    for n in sorted({k[0] for k in by}):
        for s in ("A", "B", "C"):
            if (n, s) not in by:
                continue
            st = cell_stats(by[(n, s)])
            rep["cells"][f"{n}{s}"] = st
            fn = "  —  " if st["f_nf"] is None else f"{st['f_nf']:.3f}"
            mc = "—" if st["med_cens"] is None else f"{st['med_cens']:g}"
            mh = "—" if st["med_hits"] is None else f"{st['med_hits']:g}"
            print(f"{n:>3} {s:>4} {st['n_graphs']:>7} {mc:>9} {mh:>8} {fn:>8} "
                  f"{st['n_nf']:>4} {st['n_unstable']:>5} {st['n_low_precision']:>6} "
                  f"{st['deg1']:>6} {st['le2']:>5} {st['le4']:>5}   {st['dist']}")

    # ---- H9-A / H9-B / H9-B'  (3.1, 3.2, 3.3) ------------------------------
    print("\n=== 9.b -- H9-A / H9-B / H9-B', на четырёх размерах n = 8, 9, 10, 11 ===")
    diffs = {}
    for n in SIZES_AB:
        A, B = rep["cells"].get(f"{n}A"), rep["cells"].get(f"{n}B")
        if not A or not B or A["med_cens"] is None or B["med_cens"] is None:
            continue
        dm = B["med_cens"] - A["med_cens"]
        df = B["f_nf"] - A["f_nf"]
        diffs[n] = dict(d_med=dm, d_fnf=df,
                        medA=A["med_cens"], medB=B["med_cens"],
                        fnfA=A["f_nf"], fnfB=B["f_nf"])
        print(f"  n={n}: med_cens A={A['med_cens']:g} B={B['med_cens']:g} "
              f"(B−A = {dm:+g});  f_nf A={A['f_nf']:.3f} B={B['f_nf']:.3f} "
              f"(B−A = {df:+.3f})")

    a_ok = sum(1 for n, d in diffs.items()
               if abs(d["d_med"]) <= 1 and abs(d["d_fnf"]) <= 0.15)
    a_bad = sum(1 for n, d in diffs.items() if d["d_med"] >= 2 or d["d_fnf"] >= 0.25)
    b_ok = sum(1 for n, d in diffs.items() if d["d_med"] >= 2 or d["d_fnf"] >= 0.25)
    bp_ok = sum(1 for n, d in diffs.items() if -d["d_med"] >= 2 or -d["d_fnf"] >= 0.25)

    H9A = "ПОДТВЕРЖДЕНА" if a_ok >= 3 else ("ОПРОВЕРГНУТА" if a_bad >= 2 else "не разрешена")
    H9B = "ПОДТВЕРЖДЕНА" if b_ok >= 3 else "ОПРОВЕРГНУТА"
    H9Bp = "ПОДТВЕРЖДЕНА" if bp_ok >= 3 else "не подтверждена"
    print(f"\n  H9-A  (низкая степень — свойство задачи):        {H9A}"
          f"   [{a_ok}/4 подтв., {a_bad}/4 опроверг.]")
    print(f"  H9-B  (низкая степень — свойство экстремальности): {H9B}   [{b_ok}/4]")
    print(f"  H9-B' (экстремальность степень ПОВЫШАЕТ):          {H9Bp}   [{bp_ok}/4]")
    if H9A == "не разрешена" and H9B == "ОПРОВЕРГНУТА" and H9Bp != "ПОДТВЕРЖДЕНА":
        print("  ни A, ни B, ни B' не сработали: разделения на этом объёме выборки нет.")
        print("  Объявленная заранее мощность: при N = 100 различима разница в 2 "
              "единицы цензурированной медианы; меньшие разницы не заявляются.")
    rep["H9A"], rep["H9B"], rep["H9Bp"] = H9A, H9B, H9Bp
    rep["AB_diffs"] = diffs

    # ---- H9-C (3.4) and the competing explanations (6) ----------------------
    print("\n=== 9.b -- H9-C: степень против симметрии, ВНУТРИ каждого размера ===")
    covars = [("log2|Aut|", lambda d: math.log2(d["aut"])),
              ("rank X",    lambda d: d["rank"]),
              ("орбиты",    lambda d: d["orbits"]),
              ("|E|",       lambda d: d["edges"])]
    rho = {name: {} for name, _ in covars}
    for n in SIZES_AB:
        pool = [d for s in ("A", "B") for d in by.get((n, s), [])]
        pool = [d for d in pool if cens(d) is not None and d.get("aut")]
        y = [cens(d) for d in pool]
        line = f"  n={n} (N={len(pool)}): "
        for name, f in covars:
            try:
                r, p = spearmanr([f(d) for d in pool], y)
            except Exception:
                r, p = float("nan"), float("nan")
            rho[name][n] = dict(rho=None if r != r else round(float(r), 4),
                                p=None if p != p else float(p), N=len(pool))
            line += f"{name} ρ={r:+.3f} (p={p:.3g})   "
        print(line)

    aut = rho["log2|Aut|"]
    conf = sum(1 for n in SIZES_AB
               if aut.get(n, {}).get("rho") is not None
               and aut[n]["rho"] <= -0.30 and aut[n]["p"] < 0.05)
    weak = sum(1 for n in SIZES_AB
               if aut.get(n, {}).get("rho") is not None and abs(aut[n]["rho"]) < 0.20)
    signs = {(1 if aut[n]["rho"] > 0 else -1) for n in SIZES_AB
             if aut.get(n, {}).get("rho") is not None and abs(aut[n]["rho"]) >= 0.20}
    H9C = ("ПОДТВЕРЖДЕНА" if conf >= 3
           else ("ОПРОВЕРГНУТА" if (weak >= 3 or len(signs) > 1) else "не разрешена"))
    print(f"\n  H9-C: {H9C}   [{conf}/4 при ρ ≤ −0.30 и p < 0.05; "
          f"{weak}/4 при |ρ| < 0.20; знаки среди |ρ| ≥ 0.20: {sorted(signs)}]")
    print("  Прошлый опыт учтён: в Stage 2 ρ = −0.116 на 42 графах поперёк размеров, "
          "и знак сменился\n  относительно выборки из десяти. Здесь N = 100 и счёт "
          "внутри размеров.")
    rep["H9C"] = H9C
    rep["rho"] = rho

    # ---- 6: how many cells DISCRIMINATE |Aut| from each competitor ----------
    print("\n=== 9.6 -- правило альтернативной формулы: сколько точек РАЗЛИЧАЮТ ===")
    print("  Клетка различает два объяснения, если ровно одно из них на ней")
    print("  значимо (|ρ| ≥ 0.30 при p < 0.05), либо знаки значимых ρ противоположны.")
    disc = {}
    for name, _ in covars[1:]:
        k = 0
        for n in SIZES_AB:
            ra, rb = aut.get(n, {}), rho[name].get(n, {})
            if ra.get("rho") is None or rb.get("rho") is None:
                continue
            sa = abs(ra["rho"]) >= 0.30 and ra["p"] < 0.05
            sb = abs(rb["rho"]) >= 0.30 and rb["p"] < 0.05
            if sa != sb or (sa and sb and (ra["rho"] > 0) != (rb["rho"] > 0)):
                k += 1
        disc[name] = k
        verdict = ("неразличимы на нашем диапазоне" if k == 0
                   else f"различаются на {k} из 4 размеров")
        print(f"  |Aut| против «{name}»: {verdict}")
    rep["discriminating_cells"] = disc
    if all(v == 0 for v in disc.values()):
        print("  Ноль различающих точек: ни одно из объяснений не объявляется найденным.")

    # ---- sealed predictions (5) --------------------------------------------
    print("\n=== запечатанные предсказания ===")
    P = {}
    C = [rep["cells"][k] for k in rep["cells"] if k.endswith("C")]
    P["P9-1"] = all(c["n_graphs"] == c["deg1"] for c in C)
    P["P9-2"] = (all(rep["cells"][f"{n}A"]["med_cens"] is not None
                     and rep["cells"][f"{n}A"]["med_cens"] <= 2 for n in (9, 10, 11))
                 and all(rep["cells"][f"{n}B"]["med_cens"] is not None
                         and rep["cells"][f"{n}B"]["med_cens"] >= 4 for n in (9, 10, 11)))
    P["P9-3"] = (H9C == "ОПРОВЕРГНУТА")
    fs = [rep["cells"][f"{n}B"]["f_nf"] for n in SIZES_AB
          if rep["cells"].get(f"{n}B", {}).get("f_nf") is not None]
    P["P9-4"] = len(fs) == 4 and all(fs[i] <= fs[i + 1] for i in range(3))
    P["P9-5"] = all(rep["cells"][f"{n}A"]["deg1"] / rep["cells"][f"{n}A"]["n_graphs"] >= 0.25
                    for n in (9, 10, 11))
    P["P9-6"] = (rep["cells"].get("11A", {}).get("f_nf") or 0) >= 0.5
    for k in sorted(P):
        print(f"  {k}: {'HIT ' if P[k] else 'MISS'}")
    rep["predictions"] = P

    json.dump(rep, open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")


if __name__ == "__main__":
    main()
