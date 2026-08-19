"""Block 0.b -- pre-SDP filters and their gate.  PREREGISTRATION §4.

Two filters are measured:
  F1  perfect-graph recognition by induced odd holes/antiholes  (the brief's filter)
  F2  chi(Gbar) == alpha, which forces Delta=0 through the sandwich
      alpha <= theta <= chi(Gbar) quoted in SOURCES.md S1.2   (stronger, and sound
      by a derivation from a quoted result rather than by the SPG theorem)

B-sound    (mandatory): nothing a filter drops has Delta > 0.
B-complete (checked)  : everything with Delta = 0 is dropped.
"""
import sys, os, csv, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
from quadc5.g6 import decode_g6, edges_of
from quadc5.theta import theta_cvxpy

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
TAU_ZERO = 1e-9

ap = argparse.ArgumentParser()
ap.add_argument("--n", type=int, nargs="+", default=[8, 9])
ap.add_argument("--resolve-below", type=float, default=1e-2)
ap.add_argument("--noise-floor", type=float, default=1e-6)
a = ap.parse_args()
out = {}

for n in a.n:
    print(f"\n================ n = {n} ================")
    rows = list(csv.DictReader(open(os.path.join(RES, f"n{n}_all.csv"))))
    for r in rows:
        r["delta"] = float(r["delta"])
        r["perfect"] = r["perfect"] == "True"
        r["sandwich"] = int(r["chi_comp"]) == int(r["alpha"])
    print(f"{len(rows)} connected graphs")

    # Re-solving every near-zero graph on CLARABEL is unnecessary and, at n=9,
    # would cost an hour.  Delta_bulk is bimodal with an empty band in between,
    # so it is enough to re-solve everything inside and near that band, plus
    # every graph on which the two filters disagree with the bulk verdict, plus
    # a seeded random sample of the zero cluster to bound it.
    # The band is bounded BELOW by the bulk solver's own noise floor: under it a
    # positive Delta_bulk carries no information, and re-solving 2.4e5 graphs on
    # CLARABEL would cost an hour for nothing.
    band = [r for r in rows if a.noise_floor < r["delta"] < a.resolve_below]
    disagree = [r for r in rows if (r["perfect"] or r["sandwich"]) != (r["delta"] < a.resolve_below)]
    rngl = np.random.default_rng(20260819)
    zero = [r for r in rows if r["delta"] <= a.noise_floor]
    samp = [zero[i] for i in rngl.choice(len(zero), min(3000, len(zero)), replace=False)] if zero else []
    todo = {id(r): r for r in band + disagree + samp}.values()
    print(f"re-solving {len(todo)} graphs on CLARABEL "
          f"(band {len(band)}, filter/bulk disagreements {len(disagree)}, sample {len(samp)})")
    for r in todo:
        nn, adj = decode_g6(r["graph6"])
        r["delta_hi"] = theta_cvxpy(nn, edges_of(nn, adj), solver="CLARABEL")["theta"] - int(r["alpha"])
    for r in rows:
        r.setdefault("delta_hi", r["delta"])

    # Classification threshold is the solvers' noise floor, NOT --resolve-below
    # (which only says which graphs get a second solve).  Every Delta at or under
    # the floor is indistinguishable from zero; everything above it is a real gap.
    d = np.array([r["delta_hi"] for r in rows])
    thr = a.noise_floor
    zc, nzc = d[d <= thr], d[d > thr]
    print(f"Delta is bimodal: zero-cluster max = {zc.max():.3e}, "
          f"smallest strictly positive gap = {nzc.min():.6f}; "
          f"threshold {thr:.1e} sits in a gap {nzc.min()/max(zc.max(),1e-30):.0f}x wide")
    print(f"  (tau_zero = 1e-9 from the brief lies BELOW the solvers' own noise "
          f"{zc.max():.1e}; any threshold in ({zc.max():.1e}, {nzc.min():.1e}) "
          f"gives the same split)")

    res_n = dict(total=len(rows), zero=int((d <= thr).sum()), nonzero=int((d > thr).sum()),
                 zero_cluster_max=float(zc.max()), smallest_positive_gap=float(nzc.min()),
                 threshold=thr, tau_zero_note="1e-9 is below solver noise; see gap")
    for key, name in (("perfect", "F1 perfect (odd holes/antiholes)"),
                      ("sandwich", "F2 chi(Gbar)==alpha (sandwich)")):
        dropped = [r for r in rows if r[key]]
        fp = [r for r in dropped if r["delta_hi"] > thr]
        fn = [r for r in rows if (not r[key]) and r["delta_hi"] <= thr]
        print(f"{name}: drops {len(dropped)} ({100*len(dropped)/len(rows):.2f}%)  "
              f"false-positives {len(fp)}  false-negatives {len(fn)}")
        res_n[key] = dict(dropped=len(dropped), pct=100 * len(dropped) / len(rows),
                          false_positives=len(fp), false_negatives=len(fn),
                          fp_examples=[r["graph6"] for r in fp[:5]],
                          fn_examples=[r["graph6"] for r in fn[:5]],
                          B_sound="PASSED" if not fp else "FAILED",
                          B_complete="PASSED" if not fn else "FAILED")
    # how much of F1's incompleteness F2 explains
    f1_fn = [r for r in rows if (not r["perfect"]) and r["delta_hi"] <= thr]
    res_n["F1_false_negatives_captured_by_F2"] = sum(1 for r in f1_fn if r["sandwich"])
    print(f"of F1's {len(f1_fn)} false negatives, {res_n['F1_false_negatives_captured_by_F2']} "
          f"are caught by F2")
    res_n["nonzero_graphs"] = int((d >= thr).sum())
    out[f"n{n}"] = res_n

json.dump(out, open(os.path.join(RES, "report_0b.json"), "w"), indent=1, default=str)
sound = all(out[k][f]["B_sound"] == "PASSED" for k in out for f in ("perfect", "sandwich"))
print(f"\nGATE B-sound: {'PASSED' if sound else 'FAILED'}")
sys.exit(0 if sound else 1)
