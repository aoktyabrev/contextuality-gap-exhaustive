"""Would the wall-clock screen have found Stage 9's declined graphs?  (Paper B section 4.1.)

Paper B recommends screening candidates by the ordinary solver's wall-clock time before
spending arbitrary precision.  The campaign that produced the recommendation never used
it: Stage 9 ran the full high-precision pipeline on all 1286 graphs and discovered the 27
stalls afterwards.  Recommending a method one has not used on one's own data is a weak
place in a methods note, so this closes it -- by testing the screen retrospectively and
reporting what it would have missed as well as what it would have caught.

Every one of the 1286 graphs is looked up in the sweep that produced it, its recorded
solve_time taken, and its percentile computed WITHIN ITS OWN SIZE against that size's
distribution of solver-reaching graphs.  Graphs the sandwich filter closed never reached a
solver at all; they are treated as the fastest possible, which is what a screen would do
with them in practice.

The number that matters is not the sensitivity but the false negatives: a stalled graph
whose solve was fast is a case the screen sends to the cheap path and gets wrong.
"""
import sys, os, json, csv, glob, random, bisect, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
csv.field_size_limit(1 << 30)
PART_COLS = ["graph6", "n", "edges", "alpha", "theta", "delta",
             "filtered", "chi_comp", "solve_time", "status", "pr"]
UNMEASURABLE = ("unconverged", "low_precision", "error")


def reference(n, want, rnd):
    """Solver-reaching solve times at size n, plus times for the graphs in `want`."""
    ref, hit = [], {}
    if n <= 6:
        # n = 5, 6 were never tabulated; redo them, which costs seconds
        from quadc5.g6 import decode_g6, edges_of, complement
        from quadc5.alpha import alpha_bitmask
        from quadc5.chrom import chromatic_number
        from quadc5.theta import theta_scs_direct
        from quadc5 import gengstream
        import time as _t
        for code in gengstream.stream(n):
            nn, adj = decode_g6(code)
            al = alpha_bitmask(nn, adj)
            chi = chromatic_number(nn, complement(nn, adj))
            if chi == al:
                st, tt = "sandwich", 0.0
            else:
                t0 = _t.time(); theta_scs_direct(nn, edges_of(nn, adj), eps=1e-8)
                st, tt = "solved", _t.time() - t0
                ref.append(tt)
            if code in want:
                hit[code] = (tt, st)
        return sorted(ref), hit
    if n <= 9:
        with open(os.path.join(RES, f"n{n}_all.csv")) as f:
            for r in csv.DictReader(f):
                t, st = float(r["solve_time"]), r["status"]
                if st == "solved":
                    ref.append(t)
                if r["graph6"] in want:
                    hit[r["graph6"]] = (t, st)
    elif n == 10:
        for p in sorted(glob.glob(os.path.join(RES, "n10_part_*.csv"))):
            with open(p) as f:
                for row in csv.reader(f):
                    if not row or row[0] == "graph6":
                        continue
                    t, st = float(row[8]), row[9]
                    if st == "solved" and rnd.random() < 0.05:   # 5 % reference sample
                        ref.append(t)
                    if row[0] in want:
                        hit[row[0]] = (t, st)
    else:
        path = os.path.join(RES, "n11_nonzero.csv")
        size = os.path.getsize(path)
        with open(path, "rb") as f:
            hdr = f.readline()
            for _ in range(40000):
                f.seek(rnd.randrange(len(hdr), size - 400)); f.readline()
                row = f.readline().decode("utf-8", "ignore").strip().split(",")
                if len(row) >= 11:
                    try:
                        ref.append(float(row[8]))
                    except ValueError:
                        pass
        with open(path) as f:
            for line in f:
                code = line.split(",", 1)[0]
                if code in want:
                    p = line.rstrip("\n").split(",")
                    hit[code] = (float(p[8]), p[9])
    return sorted(ref), hit


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(RES, "report_screen_retrospective.json"))
    a = ap.parse_args()
    rnd = random.Random(20260827)

    rows = [json.loads(l) for l in open(os.path.join(RES, "stage9_degrees.jsonl")) if l.strip()]
    by_n = defaultdict(list)
    for r in rows:
        by_n[r["n"]].append(r)

    scored, missing = [], []
    for n in sorted(by_n):
        want = {r["graph6"] for r in by_n[n]}
        ref, hit = reference(n, want, rnd)
        N = len(ref)
        print(f"n = {n:2d}: {len(want):3d} graphs, reference distribution {N:,} solves")
        for r in by_n[n]:
            g = r["graph6"]
            if g not in hit:
                missing.append(dict(n=n, graph6=g, sample=r["sample"], status=r["status"]))
                continue
            t, st = hit[g]
            pc = 0.0 if st != "solved" else 100.0 * bisect.bisect_left(ref, t) / N
            scored.append(dict(n=n, graph6=g, sample=r["sample"], status=r["status"],
                               declined=r["status"] in UNMEASURABLE,
                               solve_ms=round(1e3 * t, 3), reached_solver=(st == "solved"),
                               percentile=round(pc, 2)))

    declined = [s for s in scored if s["declined"]]
    print(f"\n{len(scored)} graphs scored, {len(missing)} without a recorded time "
          f"(n = 11 sample C: that run kept positive rows only)")
    print(f"declined by the instrument, among the scored: {len(declined)}")

    print(f"\n{'screen':>18} {'caught':>7} {'of':>4} {'sensitivity':>12} "
          f"{'graphs screened':>16} {'share':>7}")
    out_t = {}
    for cut in (99.0, 95.0, 90.0, 75.0, 50.0):
        caught = [s for s in declined if s["percentile"] >= cut]
        screened = [s for s in scored if s["percentile"] >= cut]
        out_t[f"top_{100-cut:g}pct"] = dict(
            cut_percentile=cut, caught=len(caught), of=len(declined),
            sensitivity=round(len(caught) / len(declined), 3),
            screened=len(screened), screened_share=round(len(screened) / len(scored), 3))
        print(f"{'top ' + format(100-cut, 'g') + ' %':>18} {len(caught):>7} {len(declined):>4} "
              f"{100*len(caught)/len(declined):11.1f}% {len(screened):>16} "
              f"{100*len(screened)/len(scored):6.1f}%")

    misses = sorted((s for s in declined if s["percentile"] < 90.0),
                    key=lambda s: s["percentile"])
    print(f"\nfalse negatives below the 90th percentile: {len(misses)} of {len(declined)}")
    for s in misses:
        print(f"   n={s['n']:2d} {s['graph6']:12s} {s['solve_ms']:9.3f} ms  "
              f"percentile {s['percentile']:6.2f}  "
              f"{'reached the solver' if s['reached_solver'] else 'CLOSED BY THE FILTER'}")

    json.dump(dict(scored=len(scored), unscored=len(missing), declined=len(declined),
                   thresholds=out_t,
                   false_negatives_below_p90=[dict(n=s["n"], graph6=s["graph6"],
                                                   percentile=s["percentile"],
                                                   solve_ms=s["solve_ms"],
                                                   reached_solver=s["reached_solver"])
                                              for s in misses],
                   unscored_detail=missing[:5], per_graph=scored),
              open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")
