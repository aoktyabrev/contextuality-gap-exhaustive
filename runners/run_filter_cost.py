"""What the sandwich filter costs and what it saves, at n = 11.  (Paper A, section 2.3.)

Soundness of the filter is settled by the sandwich inequality.  This measures the other
half: how much arithmetic it costs and how much SDP work it removes.

Two things are kept apart deliberately.

  MEASURED HERE, on a sample spread over six geng slices: the per-graph cost of alpha,
  of chi(complement), and of one SDP.

  MEASURED BY THE FULL SWEEP, not by this sample: the share of graphs the filter closes,
  89.98 %.  A 3000-graph sample puts it near 93 %, which is sampling error, so the share
  is taken from the run that saw all 1 006 700 565 graphs.

The projected total for a filterless run is therefore an ESTIMATE built from a measured
per-graph cost and a measured share -- not a measurement of a run that was never made,
and it is labelled as such.
"""
import sys, os, json, time, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from quadc5.g6 import decode_g6, edges_of, complement
from quadc5.alpha import alpha_batch
from quadc5.chrom import chromatic_number
from quadc5.theta import theta_scs_direct
from quadc5 import gengstream

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
TOTAL_N11 = 1006700565          # verified against geng -c -u 11 and OEIS A001349
SHARE_CLOSED = 0.8998           # from the full sweep, README.md
SLICES = (137, 901, 1733, 2450, 3111, 3777)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=11)
    ap.add_argument("--sample", type=int, default=3000)
    ap.add_argument("--sdp", type=int, default=300)
    ap.add_argument("--cores", type=int, default=7)
    ap.add_argument("--out", default=os.path.join(RES, "report_filter_cost.json"))
    a = ap.parse_args()

    codes, per = [], a.sample // len(SLICES)
    for res in SLICES:
        k = 0
        for c in gengstream.stream(a.n, res=res, mod=4000):
            codes.append(c); k += 1
            if k >= per:
                break
    adjs = [decode_g6(c)[1] for c in codes]
    print(f"sample: {len(codes)} connected graphs at n = {a.n}, "
          f"spread over {len(SLICES)} geng slices")

    t0 = time.time(); alphas = alpha_batch(np.array(adjs, dtype=np.int32), a.n)
    t_alpha = time.time() - t0
    t0 = time.time()
    chis = [chromatic_number(a.n, complement(a.n, adj)) for adj in adjs]
    t_chi = time.time() - t0

    open_ = [i for i in range(len(codes)) if chis[i] != int(alphas[i])]
    k = min(a.sdp, len(open_))
    t0 = time.time()
    for i in open_[:k]:
        theta_scs_direct(a.n, edges_of(a.n, adjs[i]), eps=1e-8)
    t_sdp = (time.time() - t0) / k

    us = lambda t: 1e6 * t / len(codes)
    us_alpha, us_chi, us_sdp = us(t_alpha), us(t_chi), 1e6 * t_sdp
    us_filter = us_alpha + us_chi

    # projection uses the SWEEP's share, not the sample's
    us_with = us_filter + (1 - SHARE_CLOSED) * us_sdp
    us_without = us_sdp
    h = lambda u: TOTAL_N11 * u * 1e-6 / a.cores / 3600

    print(f"\n  alpha, batched          {us_alpha:9.1f} us/graph")
    print(f"  chi(complement), exact  {us_chi:9.1f} us/graph")
    print(f"  filter, total           {us_filter:9.1f} us/graph")
    print(f"  one SDP (SCS, 1e-8)     {us_sdp:9.1f} us/graph")
    print(f"  ratio SDP / filter      {us_sdp/us_filter:9.1f}x")
    print(f"\n  share closed by the filter (from the FULL sweep): {100*SHARE_CLOSED:.2f} %")
    print(f"  share closed in this sample (sampling error):     "
          f"{100*(1-len(open_)/len(codes)):.2f} %")
    print(f"\n  projected on {a.cores} cores over all {TOTAL_N11:,} graphs:")
    print(f"     with the filter     {h(us_with):8.1f} h   (observed run: 71.8 h)")
    print(f"     without the filter  {h(us_without):8.1f} h   ESTIMATE, never run")
    print(f"     factor              {us_without/us_with:8.1f}x")

    json.dump(dict(n=a.n, sample=len(codes), slices=list(SLICES),
                   us_alpha=round(us_alpha, 1), us_chi=round(us_chi, 1),
                   us_filter=round(us_filter, 1), us_sdp=round(us_sdp, 1),
                   ratio_sdp_over_filter=round(us_sdp / us_filter, 1),
                   share_closed_full_sweep=SHARE_CLOSED,
                   share_closed_in_sample=round(1 - len(open_) / len(codes), 4),
                   hours_with_filter=round(h(us_with), 1),
                   hours_without_filter_ESTIMATE=round(h(us_without), 1),
                   factor=round(us_without / us_with, 1),
                   observed_run_hours=71.8),
              open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")
