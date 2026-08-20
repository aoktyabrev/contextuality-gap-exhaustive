"""Block 5.a -- the layer table.

A layer (n, a) is the set of connected non-isomorphic graphs on n vertices with
alpha(G) = a.  M(n,a) = max theta over the layer, D(n,a) = M(n,a) - a, and
Delta_max(n) = max_a D(n,a), which is the gate.

A graph with Delta = 0 has theta = alpha exactly, so it can never be the maximum of a
layer that contains any positive-gap graph.  The maxima therefore come from the
positive-gap data already committed; the alpha-only pass is needed only for the counts
and the medians at n = 10, where the zero-gap graphs were not committed.
"""
import sys, os, csv, gzip, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runners"))
from collections import Counter, defaultdict
from multiprocessing import Pool
import numpy as np

from quadc5 import gengstream
from quadc5.g6 import decode_g6, edges_of
from quadc5.alpha import alpha_batch, alpha_bitmask
from quadc5.theta import theta_scs_direct

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
CACHE = os.path.join(RES, "alpha_counts.json")


def alpha_counts_part(args):
    n, res, mod = args
    c = Counter()
    buf = []
    for code in gengstream.stream(n, res=res, mod=mod):
        _, adj = decode_g6(code)
        buf.append(adj)
        if len(buf) >= 4096:
            c.update(alpha_batch(np.array(buf, dtype=np.int32), n).tolist()); buf = []
    if buf:
        c.update(alpha_batch(np.array(buf, dtype=np.int32), n).tolist())
    return dict(c)


def alpha_counts(n, procs=7, mod=224):
    """Number of connected graphs per alpha.  Cached, because it is a full pass."""
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    if str(n) in cache:
        return {int(k): v for k, v in cache[str(n)].items()}
    tot = Counter()
    if n <= 8:
        buf = []
        for code in gengstream.stream(n):
            _, adj = decode_g6(code)
            buf.append(adj)
        tot.update(alpha_batch(np.array(buf, dtype=np.int32), n).tolist())
    else:
        with Pool(procs) as pool:
            for d in pool.imap_unordered(alpha_counts_part,
                                         [(n, r, mod) for r in range(mod)]):
                tot.update({int(k): v for k, v in d.items()})
    cache[str(n)] = {str(k): int(v) for k, v in tot.items()}
    json.dump(cache, open(CACHE, "w"), indent=1)
    return dict(tot)


def positive_rows(n):
    """(alpha, delta, graph6) for every graph with Delta > 0."""
    out = []
    if n <= 7:
        for code in gengstream.stream(n):
            nn, adj = decode_g6(code)
            a = alpha_bitmask(nn, adj)
            d = theta_scs_direct(nn, edges_of(nn, adj), eps=1e-9)["theta"] - a
            if d > 1e-6:
                out.append((a, d, code))
    elif n == 8:
        for r in csv.DictReader(open(os.path.join(RES, "n8_all.csv"))):
            if float(r["delta"]) > 1e-6:
                out.append((int(r["alpha"]), float(r["delta"]), r["graph6"]))
    elif n == 9:
        p = os.path.join(RES, "n9_all.csv")
        if not os.path.exists(p):
            import subprocess; subprocess.run(["gunzip", "-k", p + ".gz"], check=True)
        for r in csv.DictReader(open(p)):
            if float(r["delta"]) > 1e-6:
                out.append((int(r["alpha"]), float(r["delta"]), r["graph6"]))
    else:
        with gzip.open(os.path.join(RES, "n10_nonzero.csv.gz"), "rt") as fh:
            rd = csv.reader(fh); hdr = next(rd)
            ai, di = hdr.index("alpha"), hdr.index("delta")
            for r in rd:
                out.append((int(r[ai]), float(r[di]), r[0]))
    return out


KNOWN_MAX = {5: ("DUW", 0.2360679775), 6: ("EUZw", 0.2360679775),
             7: ("FCp`_", 0.3176672074), 8: ("GCQb`o", 0.4678437298),
             9: ("HCRbdO{", 0.6666666667), 10: ("ICRb`yiu?", 0.7071067812)}

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=7)
    a_ = ap.parse_args()
    out, fails = {}, []
    for n in (5, 6, 7, 8, 9, 10):
        cnt = alpha_counts(n, a_.procs)
        pos = positive_rows(n)
        by = defaultdict(list)
        for a, d, g in pos:
            by[a].append((d, g))
        rows = []
        for a in sorted(cnt):
            N = cnt[a]
            lst = sorted(by.get(a, []), reverse=True)
            if lst:
                dmax, gmax = lst[0]
            else:
                dmax, gmax = 0.0, None
            npos = len(lst)
            # median of theta over the layer: theta = a + delta, and delta = 0 for the rest
            med_delta = 0.0 if npos * 2 <= N else sorted(d for d, _ in lst)[npos - (N // 2) - 1]
            rows.append(dict(alpha=a, count=int(N), positive=npos,
                             M=a + dmax, D=dmax, argmax=gmax,
                             median_theta=a + med_delta))
        best = max(rows, key=lambda r: r["D"])
        gcode, gval = KNOWN_MAX[n]
        ok = abs(best["D"] - gval) < 1e-6 and (best["argmax"] == gcode)
        if not ok:
            fails.append(n)
        out[str(n)] = dict(layers=rows, best_alpha=best["alpha"], best_D=best["D"],
                           best_graph=best["argmax"], gate_ok=bool(ok))
        print(f"\n=== n = {n} ===   гейт: {'OK' if ok else 'FAIL'} "
              f"(max_a D = {best['D']:.7f} при a = {best['alpha']}, {best['argmax']})")
        print(f"  {'a':>2} {'графов':>9} {'с Δ>0':>8} {'max ϑ':>12} {'D = maxϑ-a':>12} "
              f"{'медиана ϑ':>10}  максимизатор слоя")
        for r in rows:
            print(f"  {r['alpha']:>2} {r['count']:>9} {r['positive']:>8} {r['M']:>12.7f} "
                  f"{r['D']:>12.7f} {r['median_theta']:>10.4f}  {r['argmax'] or '—'}")
    out["gate_5a"] = "PASSED" if not fails else f"FAILED for n={fails}"
    json.dump(out, open(os.path.join(RES, "report_5a.json"), "w"), indent=1)
    print("\n" + ("ГЕЙТ 5.a ПРОЙДЕН" if not fails else f"ГЕЙТ 5.a ПРОВАЛЕН: {fails}"))
    sys.exit(0 if not fails else 1)
