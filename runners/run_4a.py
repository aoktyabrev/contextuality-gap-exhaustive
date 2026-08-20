"""Block 4.a -- does the observed maximum match what the tail predicts at that N?

Answer, established here: the question cannot be answered the way the brief frames it,
because the distribution of Delta is heavily ATOMIC.  At n = 10 the 975 338 positive
gaps take only ~31 000 distinct values, and a single value -- sqrt(5) - 2, the pentagon
gap -- accounts for 593 000 of them.  Continuous extreme-value theory fits a density;
there is no density here, and the fitted shape parameter swings from -3 to +12 with the
threshold, flipping the verdict.  That instability is reported rather than hidden by
picking one threshold.

What survives: the same analysis on the DISTINCT values is stable for n = 9 at every
threshold tried, and a model-free gap statistic that assumes no distribution at all.
"""
import sys, os, csv, gzip, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runners"))
from collections import Counter
import numpy as np
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def deltas(n):
    if n <= 7:
        from run_3b import top_of
        return np.array(sorted((d for _, d in top_of(n, 10 ** 6)), reverse=True))
    if n == 8:
        rows = list(csv.DictReader(open(os.path.join(RES, "n8_all.csv"))))
        v = [float(r["delta"]) for r in rows if float(r["delta"]) > 1e-6]
    elif n == 9:
        p = os.path.join(RES, "n9_all.csv")
        if not os.path.exists(p):
            import subprocess
            subprocess.run(["gunzip", "-k", p + ".gz"], check=True)
        v = [float(r["delta"]) for r in csv.DictReader(open(p)) if float(r["delta"]) > 1e-6]
    else:
        with gzip.open(os.path.join(RES, "n10_nonzero.csv.gz"), "rt") as fh:
            rd = csv.reader(fh); hdr = next(rd); di = hdr.index("delta")
            v = [float(r[di]) for r in rd]
    return np.array(sorted(v, reverse=True))


def tail_verdict(v, q, drop_top=10):
    """GPD fit to exceedances over the q-quantile, top `drop_top` held out."""
    pool = v[drop_top:]
    u = np.quantile(pool, q)
    exc = pool[pool > u] - u
    if len(exc) < 20:
        return None
    xi, _, sg = stats.genpareto.fit(exc, floc=0.0)
    N, p_u = len(v), (v > u).sum() / len(v)

    def cdf_max(x):
        if x <= u:
            return 0.0
        return float(np.clip(1 - p_u * stats.genpareto.sf(x - u, xi, loc=0, scale=sg), 0, 1) ** N)

    pct = cdf_max(v[0]) * 100
    return dict(q=q, exceedances=int(len(exc)), xi=float(xi), sigma=float(sg),
                tail_endpoint=float(u - sg / xi) if xi < 0 else None,
                observed_percentile=float(pct),
                verdict="below 5th" if pct < 5 else "above 95th" if pct > 95 else "inside 5-95")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--round", type=int, default=9)
    a = ap.parse_args()
    out = {"note": "the Delta distribution is atomic; see atomicity below", "sizes": {}}

    print("=== atomicity: why continuous extreme-value theory does not apply ===")
    print(f"{'n':>2} {'values':>9} {'distinct':>9} {'frac':>7} {'largest atom':>13} {'share':>7}  value")
    for n in (7, 8, 9, 10):
        v = deltas(n)
        c = Counter(np.round(v, a.round).tolist())
        val, cnt = c.most_common(1)[0]
        rec = dict(N=int(len(v)), distinct=int(len(c)), largest_atom=int(cnt),
                   largest_atom_value=float(val), largest_atom_share=float(cnt / len(v)),
                   observed_max=float(v[0]))
        out["sizes"][str(n)] = rec
        print(f"{n:>2} {len(v):>9} {len(c):>9} {len(c)/len(v):>7.4f} {cnt:>13} "
              f"{cnt/len(v):>6.1%}  {val:.7f}")

    print("\n=== tail fit on ALL values: unstable, verdict flips with the threshold ===")
    print(f"{'n':>2} {'q':>6} {'xi':>9} {'pctile':>9}  verdict")
    for n in (8, 9, 10):
        v = deltas(n)
        out["sizes"][str(n)]["fit_all_values"] = []
        for q in (0.50, 0.80, 0.90, 0.95):
            r = tail_verdict(v, q)
            if r:
                out["sizes"][str(n)]["fit_all_values"].append(r)
                print(f"{n:>2} {q:>6.2f} {r['xi']:>+9.3f} {r['observed_percentile']:>8.2f}%  {r['verdict']}")
        print()

    print("=== tail fit on DISTINCT values ===")
    print(f"{'n':>2} {'distinct':>9} {'q':>6} {'xi':>9} {'endpoint':>10} {'pctile':>9}  verdict")
    for n in (8, 9, 10):
        v = np.array(sorted(set(np.round(deltas(n), a.round).tolist()), reverse=True))
        out["sizes"][str(n)]["distinct_count"] = int(len(v))
        out["sizes"][str(n)]["fit_distinct"] = []
        for q in (0.50, 0.80, 0.90, 0.95):
            r = tail_verdict(v, q)
            if r:
                out["sizes"][str(n)]["fit_distinct"].append(r)
                ep = f"{r['tail_endpoint']:.4f}" if r["tail_endpoint"] else "inf"
                print(f"{n:>2} {len(v):>9} {q:>6.2f} {r['xi']:>+9.3f} {ep:>10} "
                      f"{r['observed_percentile']:>8.2f}%  {r['verdict']}")
        print()

    print("=== model-free: how detached the top distinct value is ===")
    print(f"{'n':>2} {'D1':>10} {'D2':>10} {'D3':>10} {'(D1-D2)/(D2-D11)':>18}")
    for n in (7, 8, 9, 10):
        v = np.array(sorted(set(np.round(deltas(n), a.round).tolist()), reverse=True))
        k = min(10, len(v) - 1)
        ratio = (v[0] - v[1]) / (v[1] - v[k]) if v[1] != v[k] else float("inf")
        out["sizes"][str(n)]["top_gap_ratio"] = float(ratio)
        out["sizes"][str(n)]["distinct_top3"] = [float(x) for x in v[:3]]
        print(f"{n:>2} {v[0]:>10.6f} {v[1]:>10.6f} {v[2]:>10.6f} {ratio:>18.3f}")

    print("\n=== the brief's metric, printed as fixed, with the confound alongside ===")
    for n in (7, 8, 9, 10):
        v = deltas(n)
        m = float(v[0] / np.median(v[:100]))
        out["sizes"][str(n)]["max_over_median_top100"] = m
        print(f"  n={n:2d}  max/median(top100) = {m:.4f}   "
              f"top-100 is {100*min(100,len(v))/len(v):.3f}% of the population")
    json.dump(out, open(os.path.join(RES, "report_4a.json"), "w"), indent=1)
    print("\nwrote results/report_4a.json")
