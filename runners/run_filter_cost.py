"""What the sandwich filter costs and what it saves, at n = 11.  (Paper A, section 2.3.)

Soundness of the filter is settled by the sandwich inequality.  This measures the other
half: what it costs and how much solver work it removes.

The first version of this script projected a filtered run at 116 h against an observed
71.8 h and reported the 60 % gap without explaining it.  The explanation is here, and it
is not the machine and not the setup:

  * The solve-time distribution is HEAVY-TAILED.  Median 5.1 ms, 99th percentile 317 ms,
    maximum 1.87 s; the top 1 % of solves consumes 44 % of all solver time.  A mean taken
    over 300 solves is therefore an unstable estimator, and that is exactly what the first
    version used.
  * At MATCHED edge count our per-solve timings agree with the sweep's own recorded
    solve_time at a median ratio of 0.99, so neither the hardware nor the solver setup
    differs in any way that matters.

So the per-solve mean is not sampled here.  It is recovered from the sweep's own total --
71.8 h on 7 cores over 1 006 700 565 graphs, minus the filter's measured cost -- and
cross-checked against 40 000 rows of recorded solve_time drawn at random from the whole
n = 11 table.  Because the mean is recovered from the total, the filtered projection
reproduces 71.8 h BY CONSTRUCTION and is not evidence of anything; the cross-check is.
"""
import sys, os, json, time, random, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from quadc5.g6 import decode_g6, edges_of, complement
from quadc5.alpha import alpha_batch
from quadc5.chrom import chromatic_number
from quadc5.theta import theta_scs_direct
from quadc5 import gengstream

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
TOTAL_N11 = 1006700565     # geng -c -u 11, and OEIS A001349
SHARE_CLOSED = 0.8998      # from the full sweep
OBSERVED_HOURS = 71.8      # the sweep, on 7 cores
SLICES = (137, 901, 1733, 2450, 3111, 3777)


def sweep_solve_times(path, k, seed=1):
    """Recorded solve_time, sampled at random byte offsets across the whole table."""
    size = os.path.getsize(path)
    rnd, out = random.Random(seed), []
    with open(path, "rb") as f:
        hdr = f.readline()
        for _ in range(k):
            f.seek(rnd.randrange(len(hdr), size - 400))
            f.readline()                       # discard the partial line
            row = f.readline().decode("utf-8", "ignore").strip().split(",")
            if len(row) >= 11:
                try:
                    out.append((int(row[2]), float(row[8])))
                except ValueError:
                    pass
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--sample", type=int, default=3000)
    ap.add_argument("--sdp", type=int, default=300)
    ap.add_argument("--rows", type=int, default=40000)
    ap.add_argument("--cores", type=int, default=7)
    ap.add_argument("--out", default=os.path.join(RES, "report_filter_cost.json"))
    a = ap.parse_args()

    # ---- 1. the filter's own cost -------------------------------------------
    codes, per = [], a.sample // len(SLICES)
    for res in SLICES:
        k = 0
        for c in gengstream.stream(a.n, res=res, mod=4000):
            codes.append(c); k += 1
            if k >= per:
                break
    adjs = [decode_g6(c)[1] for c in codes]
    t0 = time.time(); alphas = alpha_batch(np.array(adjs, dtype=np.int32), a.n)
    t_alpha = time.time() - t0
    t0 = time.time()
    chis = [chromatic_number(a.n, complement(a.n, adj)) for adj in adjs]
    t_chi = time.time() - t0
    us = lambda t: 1e6 * t / len(codes)
    us_alpha, us_chi = us(t_alpha), us(t_chi)
    us_filter = us_alpha + us_chi

    # ---- 2. our own per-solve times, for the matched-|E| cross-check ---------
    open_ = [i for i in range(len(codes)) if chis[i] != int(alphas[i])]
    mine = []
    for i in open_[:a.sdp]:
        E = edges_of(a.n, adjs[i]); t0 = time.time()
        theta_scs_direct(a.n, E, eps=1e-8)
        mine.append((len(E), time.time() - t0))

    # ---- 3. the sweep's recorded solve times ---------------------------------
    rows = sweep_solve_times(os.path.join(RES, "n11_nonzero.csv"), a.rows)
    ts = sorted(t for _, t in rows)
    q = lambda p: ts[min(int(p * len(ts)), len(ts) - 1)]
    tail_share = sum(ts[int(0.99 * len(ts)):]) / sum(ts)
    sample_mean = sum(ts) / len(ts)

    # matched-|E| ratio, medians, only where both sides have enough data
    from collections import defaultdict
    import statistics
    bys, bym = defaultdict(list), defaultdict(list)
    for e, t in rows: bys[e].append(t)
    for e, t in mine: bym[e].append(t)
    ratios = []
    for e in sorted(set(bys) & set(bym)):
        if len(bys[e]) >= 30 and len(bym[e]) >= 5:
            ratios.append(statistics.median(bym[e]) / statistics.median(bys[e]))
    matched = statistics.median(ratios) if ratios else None

    # ---- 4. the mean recovered from the sweep's own total --------------------
    core_s = OBSERVED_HOURS * a.cores * 3600
    n_solves = (1 - SHARE_CLOSED) * TOTAL_N11
    mean_sdp = 1e6 * (core_s - us_filter * 1e-6 * TOTAL_N11) / n_solves
    us_with = us_filter + (1 - SHARE_CLOSED) * mean_sdp
    h = lambda u: TOTAL_N11 * u * 1e-6 / a.cores / 3600

    print(f"filter, on {len(codes)} graphs over {len(SLICES)} geng slices")
    print(f"   alpha, batched            {us_alpha:10.1f} us/graph")
    print(f"   chi(complement), exact    {us_chi:10.1f} us/graph")
    print(f"   filter, total             {us_filter:10.1f} us/graph")
    print(f"\nsolve time, {len(ts)} rows sampled across the whole n = 11 table")
    print(f"   median                    {1e6*q(0.5):10.1f} us")
    print(f"   90th percentile           {1e6*q(0.9):10.1f} us")
    print(f"   99th percentile           {1e6*q(0.99):10.1f} us")
    print(f"   maximum seen              {1e6*q(1.0):10.1f} us")
    print(f"   top 1 % of solves take    {100*tail_share:10.1f} % of all solver time")
    print(f"   mean over these rows      {1e6*sample_mean:10.1f} us")
    print(f"\ncross-check, our timings against the sweep's at MATCHED |E|:")
    print(f"   median ratio              {matched:10.2f}   ({len(ratios)} edge counts)")
    print(f"\nmean per solve, recovered from the sweep's own total, not sampled:")
    print(f"   {mean_sdp:10.1f} us   (sampled mean above: {1e6*sample_mean:.1f} us, "
          f"{100*abs(mean_sdp-1e6*sample_mean)/mean_sdp:.0f} % apart)")
    print(f"   ratio SDP / filter        {mean_sdp/us_filter:10.1f}x")
    print(f"\nprojection on {a.cores} cores over {TOTAL_N11:,} graphs:")
    print(f"   with the filter    {h(us_with):8.1f} h   <- reproduces the observed "
          f"{OBSERVED_HOURS} h BY CONSTRUCTION")
    print(f"   without the filter {h(mean_sdp):8.1f} h   ESTIMATE, no such run was made")
    print(f"   factor             {mean_sdp/us_with:8.1f}x")

    json.dump(dict(
        n=a.n, sample=len(codes), rows_sampled=len(ts),
        us_alpha=round(us_alpha, 1), us_chi=round(us_chi, 1),
        us_filter=round(us_filter, 1),
        solve_median_us=round(1e6 * q(0.5), 1),
        solve_p90_us=round(1e6 * q(0.9), 1),
        solve_p99_us=round(1e6 * q(0.99), 1),
        solve_max_us=round(1e6 * q(1.0), 1),
        top1pct_share_of_time=round(tail_share, 3),
        sampled_mean_us=round(1e6 * sample_mean, 1),
        matched_edge_ratio=None if matched is None else round(matched, 2),
        mean_sdp_from_total_us=round(mean_sdp, 1),
        ratio_sdp_over_filter=round(mean_sdp / us_filter, 1),
        share_closed_full_sweep=SHARE_CLOSED,
        hours_with_filter=round(h(us_with), 1),
        hours_without_filter_ESTIMATE=round(h(mean_sdp), 1),
        factor=round(mean_sdp / us_with, 1),
        observed_run_hours=OBSERVED_HOURS),
        open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")
