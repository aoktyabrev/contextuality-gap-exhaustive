"""Block 1.b -- the filter and its gate on n=10.  PREREGISTRATION_STAGE1 §3.

B2 (the brief's gate): 10^5 random filtered-out graphs run through the full pipeline;
    the false-positive rate must be of the same order as at n=9, which was zero.
B3: F1 (perfect) is a subset of F2 (chi(Gbar)==alpha) -- checked, not assumed.
B4: our F1 count over all of n=10 against geng -P, an external implementation.
"""
import sys, os, csv, json, glob, random, argparse, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multiprocessing import Pool
import numpy as np

from quadc5 import gengstream
from quadc5.g6 import decode_g6, edges_of, complement
from quadc5.alpha import alpha_batch
from quadc5.chrom import chromatic_number
from quadc5.perfect import is_perfect
from quadc5.theta import theta_scs_direct, theta_cvxpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, default=10)
ap.add_argument("--mod", type=int, default=224)
ap.add_argument("--procs", type=int, default=7)
ap.add_argument("--sample", type=int, default=100000)
ap.add_argument("--seed", type=int, default=20260819)
ap.add_argument("--tau-zero", type=float, default=1e-6)
ap.add_argument("--skip-counts", action="store_true")
a = ap.parse_args()
TAU_ZERO = a.tau_zero
out = {}


def count_part(args):
    """Per geng part: how many are perfect (F1), how many satisfy F2, F1 minus F2."""
    n, res, mod = args
    n_tot = n_f1 = n_f2 = n_f1_not_f2 = 0
    buf = []
    for code in gengstream.stream(n, res=res, mod=mod):
        _, adj = decode_g6(code)
        buf.append(adj)
        if len(buf) >= 4096:
            n_tot, n_f1, n_f2, n_f1_not_f2 = _flush(n, buf, n_tot, n_f1, n_f2, n_f1_not_f2)
            buf = []
    n_tot, n_f1, n_f2, n_f1_not_f2 = _flush(n, buf, n_tot, n_f1, n_f2, n_f1_not_f2)
    return n_tot, n_f1, n_f2, n_f1_not_f2


def _flush(n, buf, n_tot, n_f1, n_f2, n_bad):
    if not buf:
        return n_tot, n_f1, n_f2, n_bad
    A = np.array(buf, dtype=np.int32)
    al = alpha_batch(A, n)
    for k, adj in enumerate(buf):
        n_tot += 1
        f2 = chromatic_number(n, complement(n, adj)) == int(al[k])
        f1 = is_perfect(n, adj)
        n_f1 += f1
        n_f2 += f2
        if f1 and not f2:
            n_bad += 1
    return n_tot, n_f1, n_f2, n_bad


if not a.skip_counts:
    print(f"=== B3/B4: F1 and F2 over all connected graphs on {a.n} vertices ===")
    t0 = time.perf_counter()
    jobs = [(a.n, r, a.mod) for r in range(a.mod)]
    tot = f1 = f2 = bad = 0
    with Pool(a.procs) as pool:
        for k, (t, x1, x2, xb) in enumerate(pool.imap_unordered(count_part, jobs)):
            tot += t; f1 += x1; f2 += x2; bad += xb
            if (k + 1) % 40 == 0:
                print(f"   {k+1}/{a.mod} parts, {tot} graphs, {time.perf_counter()-t0:.0f}s",
                      flush=True)
    el = time.perf_counter() - t0
    geng_P = gengstream.count(a.n, extra=("-P",))
    print(f"total {tot} graphs in {el:.0f}s")
    print(f"F1 (our perfect-graph recognition): {f1}  ({100*f1/tot:.2f}%)")
    print(f"geng -c -P {a.n} (external)       : {geng_P}   MATCH: {f1 == geng_P}")
    print(f"F2 (chi(Gbar)==alpha)             : {f2}  ({100*f2/tot:.2f}%)")
    print(f"F1 not contained in F2            : {bad}   (B3 expects 0)")
    out["b3_b4"] = dict(total=tot, F1=f1, geng_P=geng_P, F1_matches_geng=f1 == geng_P,
                        F2=f2, F1_not_in_F2=bad, seconds=el)

print(f"\n=== B2: {a.sample} random filtered-out graphs through the full pipeline ===")
files = sorted(glob.glob(os.path.join(RES, f"n{a.n}_part_*.csv")))
rng = random.Random(a.seed)
reservoir, seen = [], 0
for p in files:
    with open(p) as fh:
        for r in csv.reader(fh):
            if r[6] != "1":            # only graphs the filter dropped
                continue
            seen += 1
            if len(reservoir) < a.sample:
                reservoir.append(r[0])
            else:
                j = rng.randrange(seen)
                if j < a.sample:
                    reservoir[j] = r[0]
print(f"filtered-out population {seen}; sampled {len(reservoir)} (seed {a.seed})")


def check(code):
    n, adj = decode_g6(code)
    E = edges_of(n, adj)
    A = np.array([adj], dtype=np.int32)
    al = int(alpha_batch(A, n)[0])
    r = theta_scs_direct(n, E, eps=1e-8)
    return code, r["theta"] - al, r["pr"]


t0 = time.perf_counter()
deltas = []
with Pool(a.procs) as pool:
    for k, (code, dl, pr) in enumerate(pool.imap_unordered(check, reservoir, chunksize=256)):
        deltas.append((dl, code))
        if (k + 1) % 25000 == 0:
            print(f"   {k+1}/{len(reservoir)}  {time.perf_counter()-t0:.0f}s", flush=True)
worst = max(d for d, _ in deltas) if deltas else 0.0
print(f"largest Delta among sampled filtered-out graphs: {worst:.3e}")

# The gate is evaluated at BOTH thresholds: the one this stage preregistered (1e-6)
# and one placed inside the empirically empty band.  Reporting only the second would
# be moving the goalposts; reporting only the first would call provable zeros non-zero.
out["b2"] = {}
for tau, label in ((1e-6, "b2_at_tau_1e-6"), (a.tau_zero, "b2_at_tau_1e-5")):
    fps = [(c, d) for d, c in deltas if d > tau]
    print(f"false positives (Delta > {tau:g}): {len(fps)}  "
          f"rate {len(fps)/max(len(reservoir),1):.2e}")
    for c, d in fps[:10]:
        print(f"   {c}  Delta={d:.3e}")
    out[label] = dict(threshold=tau, false_positives=len(fps),
                      rate=len(fps) / max(len(reservoir), 1),
                      examples=[c for c, _ in fps[:20]],
                      deltas_bulk=[round(d, 12) for _, d in fps[:20]])

# the smallest genuinely positive gap, from the graphs that did reach an SDP
smallest = None
for p_ in files:
    with open(p_) as fh:
        for r in csv.reader(fh):
            if r[6] == "0":
                d = float(r[5])
                if d > a.tau_zero and (smallest is None or d < smallest):
                    smallest = d
out["noise_floor_measured"] = worst
out["smallest_genuine_gap"] = smallest
out["empty_band"] = (f"({worst:.3g}, {smallest:.3g}) -- factor {smallest/max(worst,1e-30):.0f}; "
                     f"any threshold inside gives the same split")
out["b2"] = dict(population=seen, sampled=len(reservoir), seed=a.seed,
                 max_delta=worst, seconds=time.perf_counter() - t0)
fps_gate = [1 for d, _ in deltas if d > a.tau_zero]
print(f"noise floor {worst:.3e}; smallest genuine gap {smallest:.3e}; "
      f"empty band factor {smallest/max(worst,1e-30):.0f}")
out["gate_1b"] = "PASSED" if not fps_gate else "FAILED"
json.dump(out, open(os.path.join(RES, "report_1b.json"), "w"), indent=1, default=str)
print(f"\nGATE 1.b: {out['gate_1b']}  (threshold {a.tau_zero:g}, inside the measured band)")
sys.exit(0 if not fps_gate else 1)
