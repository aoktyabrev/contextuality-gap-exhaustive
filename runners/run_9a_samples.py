"""Stage 9, block 9.a -- build the three samples.  PREREGISTRATION_STAGE9 2.1.

Writes results/stage9_samples.json.  Nothing here computes a degree; the samples are
fixed and written down BEFORE any degree is measured, so that the choice of graphs
cannot follow from what the degrees turned out to be.
"""
import sys, os, json, csv, random, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quadc5.g6 import decode_g6, edges_of
from quadc5 import gengstream
from quadc5.theta import theta_cvxpy
from quadc5.alpha import alpha_bitmask as alpha_exact

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
SEED = 20260826
P = {5: 1, 6: 3, 7: 33, 8: 498, 9: 16533, 10: 975338, 11: 100827522}
TAU = {5: 1e-7, 6: 1e-7, 7: 1e-7, 8: 1e-7, 9: 1e-7, 10: 1e-6, 11: 1e-6}
csv.field_size_limit(1 << 30)


def _col(header, *names):
    for nm in names:
        if nm in header:
            return header.index(nm)
    raise KeyError(names)


PART_COLS = ["graph6", "n", "edges", "alpha", "theta", "delta",
             "filtered", "chi_comp", "solve_time", "status", "pr"]


def rows(path):
    """Yield (graph6, delta).  The n=10/n=11 part files carry no header row -- their
    column order is PART_COLS, the layout quadc5/sweep10.py writes."""
    with open(path) as f:
        r = csv.reader(f)
        first = next(r, None)
        if first is None:
            return
        if "graph6" in first:
            header, lead = first, None
        else:
            header, lead = PART_COLS, first
        gi = _col(header, "graph6")
        di = _col(header, "delta", "delta_hi")
        if lead is not None:
            yield lead[gi], float(lead[di])
        for row in r:
            if row:
                yield row[gi], float(row[di])


def small_all(n):
    """n = 5, 6: enumerate outright.  Cheap and independent of the stored tables."""
    out = []
    for code in gengstream.stream(n):
        nn, adj = decode_g6(code)
        e = edges_of(nn, adj)
        a = alpha_exact(nn, adj)
        t = theta_cvxpy(nn, e, solver="CLARABEL")["theta"]
        out.append((code, t - a))
    return out


def build_c_only(n, rng):
    """Sample C alone, for repairing a size without re-scanning the big tables."""
    return build(n, rng, c_only=True)


def build(n, rng, c_only=False):
    tau = TAU[n]
    N = min(100, P[n])
    if n in (5, 6):
        allrows = small_all(n)
        pos = sorted([(c, d) for c, d in allrows if d > tau], key=lambda x: (-x[1], x[0]))
        zero = [c for c, d in allrows if d <= tau]
    else:
        if n <= 9:
            src = os.path.join(RES, f"n{n}_all.csv")
            pos, zero = [], []
            for c, d in rows(src):
                (pos.append((c, d)) if d > tau else zero.append(c))
            pos.sort(key=lambda x: (-x[1], x[0]))
        else:
            if c_only:
                pos, zero = [], None
            else:
                top = os.path.join(RES, f"n{n}_top1000.csv")
                pos = sorted(list(rows(top)), key=lambda x: (-x[1], x[0]))
                zero = None                    # filled below, per size
    A = [] if c_only else [c for c, _ in pos[:N]]

    # ---- B: uniform among {delta > 0} \ A ----------------------------------
    Aset = set(A)
    if c_only:
        B = []
    elif P[n] <= N:
        B = []                                 # nothing left to draw from
    elif n <= 9:
        pool = [c for c, _ in pos if c not in Aset]
        B = rng.sample(pool, N)
    else:
        src = os.path.join(RES, f"n{n}_nonzero.csv")
        B, seen = [], 0                        # reservoir, one pass
        for c, d in rows(src):
            if d <= tau or c in Aset:
                continue
            seen += 1
            if len(B) < N:
                B.append(c)
            else:
                j = rng.randrange(seen)
                if j < N:
                    B[j] = c
        print(f"    n={n}: reservoir over {seen:,} positive rows")

    # ---- C: delta = 0 ------------------------------------------------------
    if n <= 9:
        C = rng.sample(zero, N)
    elif n == 10:
        parts = sorted(f for f in os.listdir(RES)
                       if f.startswith("n10_part_") and f.endswith(".csv"))
        pick = rng.sample(parts, min(12, len(parts)))
        pool = []
        for p in pick:
            pool += [c for c, d in rows(os.path.join(RES, p)) if d <= tau]
        C = rng.sample(pool, N)
        print(f"    n=10: sample C stratified over {len(pick)} geng slices, pool {len(pool):,}")
    else:
        # geng's res/mod split is NOT balanced: with a large mod many residues hold
        # no graphs at all.  mod = 100000 produced an empty slice and an empty C on
        # the first attempt.  Use a coarse split and walk residues until N are found.
        mod = 2000
        order = list(range(mod))
        rng.shuffle(order)
        C, used = [], []
        for res in order:
            used.append(res)
            for code in gengstream.stream(n, res=res, mod=mod):
                nn, adj = decode_g6(code)
                e = edges_of(nn, adj)
                a = alpha_exact(nn, adj)
                t = theta_cvxpy(nn, e, solver="CLARABEL")["theta"]
                if t - a <= tau:
                    C.append(code)
                    if len(C) == N:
                        break
            if len(C) == N:
                break
        print(f"    n={n}: sample C stratified, geng slices {used} of mod={mod}")
    return C if c_only else dict(A=A, B=B, C=C)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--sizes", type=int, nargs="+", default=[5, 6, 7, 8, 9, 10, 11])
    ap.add_argument("--out", default=os.path.join(RES, "stage9_samples.json"))
    ap.add_argument("--only-c", action="store_true",
                    help="rebuild only sample C for --sizes, patching --out in place")
    a = ap.parse_args()

    if a.only_c:
        out = json.load(open(a.out))
    else:
        out = {"seed": a.seed, "P": P, "tau_zero": TAU, "samples": {}}
    for n in a.sizes:
        rng = random.Random(a.seed * 1000 + n)   # per-size, so sizes are independent
        if a.only_c:
            s = out["samples"][str(n)]
            for _ in range(3):                   # burn the draws A and B consumed
                rng.random()
            s["C"] = build_c_only(n, rng)
        else:
            s = build(n, rng)
        out["samples"][str(n)] = s
        print(f"n={n:2d}  |A|={len(s['A']):3d}  |B|={len(s['B']):3d}  |C|={len(s['C']):3d}"
              + ("   (B empty: P(n) = N(n))" if not s["B"] else ""))
        with open(a.out, "w") as f:
            json.dump(out, f, indent=1)
    print(f"\nwrote {a.out}")
