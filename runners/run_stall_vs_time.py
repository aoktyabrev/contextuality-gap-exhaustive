"""Are slow semidefinite solves the same graphs on which high-precision refinement stalls?

This links two facts that lived in separate papers.  Paper A section 2.3: the sweep's
solve times are heavily tailed.  Paper B section 2: a class of graphs on which
Gauss-Newton refinement stops converging, read there as a degenerate optimum.

Four blocks, and the order matters because each one closes an alternative explanation.

  1  TAIL BY GAP.  Where the tail lives, at sizes where every row was kept (n = 8, 9).
  2  BANDS.  Stall rate against solve time, with Delta = 0 held FIXED -- because block 1
     shows the tail is a Delta = 0 phenomenon at those sizes, so comparing across that
     boundary would confound two things.
  3  WITHIN RANK.  The obvious competitor is the rank of the primal optimum, which
     correlates with solve time.  Block 3 fixes the rank and varies only the band.
  4  ELEVEN VERTICES.  Where the three graphs known to stall at n = 11 sit in that
     sweep's own recorded solve times.  Only three, and stated as three.

Everything is seeded, so a re-run reproduces the numbers a paper quotes.
"""
import sys, os, json, csv, random, argparse, time, bisect, statistics
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from collections import defaultdict
from mpmath import mp, mpf
from quadc5.g6 import decode_g6, edges_of
from quadc5.theta import theta_cvxpy
from quadc5.hiprec import refine
from quadc5.algdeg import _dual_start, numeric_rank

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
SEED = 20260827
# the three graphs Stage 9 found stalled at n = 11; all have Delta > 0
N11_STALLED = ["J?bBD_{uVe?", "J?bAV_{\\rz_", "J?bFB_{mnk_"]


def converges(code, dps=240):
    """The Stage 9 criterion: the residual must fall when the precision doubles."""
    n, adj = decode_g6(code)
    e = edges_of(n, adj)
    pr = theta_cvxpy(n, e, solver="CLARABEL")
    B0, _ = _dual_start(n, e)
    lo = refine(n, e, pr["X"], B0, pr["theta"], dps=dps)
    hi = refine(n, e, pr["X"], B0, pr["theta"], dps=2 * dps)
    mp.dps = 2 * dps
    return bool(hi["residual"] < lo["residual"] * mpf(10) ** -10)


def quantiles(ts):
    ts = sorted(ts); N = len(ts)
    q = lambda p: 1e3 * ts[min(int(p * N), N - 1)]
    return dict(n=N, median_ms=round(q(0.5), 2), p90_ms=round(q(0.9), 2),
                p99_ms=round(q(0.99), 2), max_ms=round(q(1.0), 2))


def load_all(n):
    z, p = [], []
    with open(os.path.join(RES, f"n{n}_all.csv")) as f:
        for r in csv.DictReader(f):
            if r["status"] != "solved":
                continue
            row = (float(r["solve_time"]), r["graph6"])
            (z if float(r["delta"]) < 1e-7 else p).append(row)
    return z, p


def sample_recorded(path, k, seed=1):
    size = os.path.getsize(path); rnd = random.Random(seed); out = []
    with open(path, "rb") as f:
        hdr = f.readline()
        for _ in range(k):
            f.seek(rnd.randrange(len(hdr), size - 400)); f.readline()
            row = f.readline().decode("utf-8", "ignore").strip().split(",")
            if len(row) >= 11:
                try:
                    out.append(float(row[8]))
                except ValueError:
                    pass
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=9)
    ap.add_argument("--per-band", type=int, default=40)
    ap.add_argument("--per-rank", type=int, default=22)
    ap.add_argument("--rank-pool", type=int, default=150)
    ap.add_argument("--out", default=os.path.join(RES, "report_stall_vs_time.json"))
    ap.add_argument("--only", choices=("all", "n11"), default="all")
    ap.add_argument("--per-band-n11", type=int, default=25)
    a = ap.parse_args()
    t_all = time.time()

    if a.only == "n11":
        out = json.load(open(a.out))
        print("=== 6. n = 11, the band experiment on POSITIVE-gap graphs ===")
        print("   forced by the data: 93.65 % of solver-reaching graphs have Delta = 0 at")
        print("   n = 9, but only 0.063 % at n = 11, so the tail there is a positive-gap")
        print("   phenomenon and the experiment follows it.")
        path = os.path.join(RES, "n11_nonzero.csv")
        ts = sorted(sample_recorded(path, 40000))
        M = len(ts)
        cut = {"slow_top1": (ts[int(0.99 * M)], float("inf")),
               "upper_90_99": (ts[int(0.90 * M)], ts[int(0.99 * M)]),
               "median_45_55": (ts[int(0.45 * M)], ts[int(0.55 * M)]),
               "fast_bottom10": (0.0, ts[int(0.10 * M)])}
        size = os.path.getsize(path)
        rnd = random.Random(SEED)
        picked = {k: [] for k in cut}
        need = a.per_band_n11
        tries = 0
        with open(path, "rb") as f:
            hdr = f.readline()
            while any(len(v) < need for v in picked.values()) and tries < 4_000_000:
                tries += 1
                f.seek(rnd.randrange(len(hdr), size - 400)); f.readline()
                row = f.readline().decode("utf-8", "ignore").strip().split(",")
                if len(row) < 11:
                    continue
                try:
                    t = float(row[8])
                except ValueError:
                    continue
                for k, (lo_, hi_) in cut.items():
                    if len(picked[k]) < need and lo_ <= t < hi_:
                        picked[k].append((t, row[0]))
                        break
        out["n11_bands"] = {}
        print(f"\n   {'band':14s} {'median ms':>10} {'stalled':>9} {'of':>4} {'rate':>7}")
        for k, rows_ in picked.items():
            st = sum(0 if converges(g) else 1 for _, g in rows_)
            med = 1e3 * statistics.median(t for t, _ in rows_)
            out["n11_bands"][k] = dict(median_ms=round(med, 2), stalled=st, n=len(rows_),
                                       rate=round(st / len(rows_), 3))
            print(f"   {k:14s} {med:10.2f} {st:9d} {len(rows_):4d} "
                  f"{100*st/len(rows_):6.1f}%", flush=True)
        out["n11_population"] = dict(sdp_calls=100891478, positive=100827522,
                                     zero_reaching_solver=63956,
                                     zero_share_of_solver_reaching=0.00063,
                                     n9_zero_share_of_solver_reaching=0.9365)
        out["wall_minutes_n11"] = round((time.time() - t_all) / 60, 1)
        json.dump(out, open(a.out, "w"), indent=1)
        print(f"\nmerged into {a.out}  ({out['wall_minutes_n11']} min)")
        sys.exit(0)

    out = {"seed": SEED, "n": a.n}

    # ---- 1. where the tail lives ------------------------------------------
    print("=== 1. the tail, by gap, at sizes where every row was kept ===")
    out["tail_by_gap"] = {}
    for n in (8, a.n):
        z, p = load_all(n)
        out["tail_by_gap"][str(n)] = dict(zero=quantiles([t for t, _ in z]),
                                          positive=quantiles([t for t, _ in p]))
        for nm in ("zero", "positive"):
            d = out["tail_by_gap"][str(n)][nm]
            print(f"  n={n} Delta {'= 0' if nm=='zero' else '> 0'}: N={d['n']:>8,} "
                  f"median {d['median_ms']:8.2f}  p99 {d['p99_ms']:9.2f}  max {d['max_ms']:9.2f} ms")

    zero, _ = load_all(a.n)
    zero.sort(); N = len(zero)
    rnd = random.Random(SEED)
    bands = {"slow_top1": zero[int(0.99 * N):], "upper_90_99": zero[int(0.90 * N):int(0.99 * N)],
             "median_45_55": zero[int(0.45 * N):int(0.55 * N)], "fast_bottom10": zero[:int(0.10 * N)]}

    # ---- 2. stall rate by band, Delta = 0 fixed ---------------------------
    print(f"\n=== 2. stall rate by solve-time band, n = {a.n}, Delta = 0 fixed ===")
    out["bands"] = {}
    for name, pool in bands.items():
        pick = rnd.sample(pool, min(a.per_band, len(pool)))
        st = sum(0 if converges(g) else 1 for _, g in pick)
        med = 1e3 * pool[len(pool) // 2][0]
        out["bands"][name] = dict(median_ms=round(med, 2), stalled=st, n=len(pick),
                                  rate=round(st / len(pick), 3))
        print(f"  {name:14s} median {med:9.2f} ms   {st:3d}/{len(pick):<3d} = "
              f"{100*st/len(pick):5.1f} %", flush=True)

    # ---- 3. the competitor: rank of the primal optimum --------------------
    print(f"\n=== 3. rank of the primal optimum, the obvious competitor ===")
    rnd2 = random.Random(SEED)
    ranked = []
    for name, pool in bands.items():
        for t, g in rnd2.sample(pool, min(a.rank_pool, len(pool))):
            n_, adj = decode_g6(g)
            ranked.append((name, t, g, numeric_rank(
                theta_cvxpy(n_, edges_of(n_, adj), solver="CLARABEL")["X"])))
    from scipy.stats import spearmanr
    rho, pv = spearmanr([x[1] for x in ranked], [x[3] for x in ranked])
    out["rank_vs_time_rho"] = round(float(rho), 3)
    print(f"  rho(solve time, rank) = {rho:+.3f} (p = {pv:.2g}) on {len(ranked)} graphs")
    for name in bands:
        d = [x for x in ranked if x[0] == name]
        share = 100 * sum(1 for x in d if x[3] >= 3) / len(d)
        out.setdefault("rank_ge3_share", {})[name] = round(share / 100, 3)
        print(f"    {name:14s} rank >= 3 on {share:5.1f} % of the band")
    print("  the two top bands are BOTH 100 % rank >= 3, so rank cannot explain the")
    print("  difference between them; block 4 fixes the rank and varies only the band.")

    print(f"\n=== 4. stall rate at FIXED rank, slow against upper ===")
    out["within_rank"] = {}
    rnd3 = random.Random(7)
    for rk in (4, 5):
        for band in ("slow_top1", "upper_90_99"):
            pool = [x for x in ranked if x[3] == rk and x[0] == band]
            if len(pool) < 12:
                print(f"  rank {rk} {band:14s} too few ({len(pool)})"); continue
            pick = rnd3.sample(pool, min(a.per_rank, len(pool)))
            st = sum(0 if converges(x[2]) else 1 for x in pick)
            med = 1e3 * statistics.median(x[1] for x in pick)
            out["within_rank"][f"rank{rk}_{band}"] = dict(
                rank=rk, band=band, median_ms=round(med, 2), stalled=st,
                n=len(pick), rate=round(st / len(pick), 3))
            print(f"  rank {rk} {band:14s} median {med:8.2f} ms   {st:3d}/{len(pick):<3d} = "
                  f"{100*st/len(pick):5.1f} %", flush=True)

    # ---- 5. eleven vertices, the three graphs known to stall --------------
    print(f"\n=== 5. n = 11: the three graphs known to stall, in that sweep's own times ===")
    ts = sorted(sample_recorded(os.path.join(RES, "n11_nonzero.csv"), 40000))
    med11 = ts[len(ts) // 2]
    found = {}
    want = set(N11_STALLED)
    with open(os.path.join(RES, "n11_nonzero.csv")) as f:
        for line in f:
            code = line.split(",", 1)[0]
            if code in want:
                found[code] = float(line.split(",")[8])
                want.discard(code)
                if not want:
                    break
    out["n11"] = dict(median_ms=round(1e3 * med11, 2),
                      p99_ms=round(1e3 * ts[int(0.99 * len(ts))], 2), graphs={})
    for g in N11_STALLED:
        if g not in found:
            print(f"  {g:14s} not found"); continue
        t = found[g]; pc = 100 * bisect.bisect_left(ts, t) / len(ts)
        out["n11"]["graphs"][g] = dict(solve_ms=round(1e3 * t, 2), percentile=round(pc, 2))
        print(f"  {g:14s} {1e3*t:8.2f} ms   percentile {pc:6.2f}   {t/med11:6.1f}x the median")
    print("  three graphs is three graphs; this is a consistency check, not a measurement")
    print("  of the n = 11 population.")

    out["wall_minutes"] = round((time.time() - t_all) / 60, 1)
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}  ({out['wall_minutes']} min)")
