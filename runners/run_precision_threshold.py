"""At what precision does the Quad-C5 quartic become findable?  (Paper A, section 3.3.)

The source paper reports its own integer-relation candidate for theta(Quad-C5) as a false
positive at 15-digit precision and recommends >= 30 significant digits
(SOURCES.md S1.9).  This measures where the threshold actually is.

The value is taken from the EXACT certificate proved in Stage 2, not from any solver, so
the experiment isolates precision from every other source of error.  What is varied is
only how many digits of a known-correct number the search is allowed to see.

The search is ASCENDING in degree and stops at the first relation, which is the natural
way to look for a minimal polynomial and the way that makes a spurious low-degree hit
fatal rather than merely noisy.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from math import gcd
from mpmath import mp, mpf, pslq, polyroots, nstr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

# x^4 - x^3 + 23x^2 - 155x + 158, proved in REPORT_STAGE2.md by exact primal and dual
# certificates over Q(theta).  Ascending coefficient order.
QUARTIC = [158, -155, 23, -1, 1]


def theta_exact(dps=400):
    mp.dps = dps
    roots = polyroots([1, -1, 23, -155, 158], maxsteps=200, extraprec=2 * dps)
    cands = [r.real for r in roots
             if abs(r.imag) < mpf(10) ** -(dps // 4) and 3 < r.real < 4]
    if len(cands) != 1:
        raise RuntimeError(f"expected one root in (3,4), got {len(cands)}")
    return cands[0]


def primitive(rel):
    if rel is None:
        return None
    g = 0
    for c in rel:
        g = gcd(g, abs(int(c)))
    if g == 0:
        return None
    out = [int(c) // g for c in rel]
    return [-c for c in out] if out[-1] < 0 else out


def first_relation(theta, D, degrees, maxcoeff):
    """Ascending search; returns (degree, primitive polynomial) or (None, None)."""
    for d in degrees:
        mp.dps = D
        t = +theta
        vec = [mpf(1)]
        for _ in range(d):
            vec.append(vec[-1] * t)
        rel = primitive(pslq(vec, tol=mpf(10) ** (-(D - 3)),
                             maxcoeff=maxcoeff, maxsteps=20000))
        if rel is not None and rel[-1] != 0:
            return d, rel
    return None, None


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--lo", type=int, default=16, help="mpmath's pslq needs >= 53 bits")
    ap.add_argument("--hi", type=int, default=40)
    ap.add_argument("--maxcoeff", type=int, default=10 ** 6)
    ap.add_argument("--degrees", type=int, nargs="+", default=[1, 2, 3, 4])
    ap.add_argument("--out", default=os.path.join(RES, "report_precision_threshold.json"))
    a = ap.parse_args()

    theta = theta_exact()
    mp.dps = 60
    print(f"theta = {nstr(theta, 45)}   (root of x^4-x^3+23x^2-155x+158 in (3,4))")
    print(f"ascending search over degrees {a.degrees}, coefficient bound 1e"
          f"{len(str(a.maxcoeff))-1}, tolerance 1e-(D-3)\n")
    print(f"{'digits':>7} | {'deg':>3} | first relation found")
    print("-" * 72)

    rows, threshold = [], None
    for D in range(a.lo, a.hi + 1):
        d, rel = first_relation(theta, D, a.degrees, a.maxcoeff)
        true = (rel == QUARTIC)
        if true and threshold is None:
            threshold = D
        if not true:
            threshold = None if threshold is None else threshold   # keep first run only
        rows.append(dict(digits=D, degree=d, poly=rel, is_true_quartic=bool(true)))
        print(f"{D:7d} | {str(d):>3} | {rel}" + ("   <-- TRUE QUARTIC" if true else
                                                 ("   spurious" if rel else "")))

    # the threshold is the first D from which EVERY larger D also returns the quartic
    thr = None
    for i, r in enumerate(rows):
        if r["is_true_quartic"] and all(x["is_true_quartic"] for x in rows[i:]):
            thr = r["digits"]
            break
    spurious = [r for r in rows if r["poly"] and not r["is_true_quartic"]]
    heights = [max(abs(c) for c in r["poly"]) for r in spurious]

    out = dict(
        quartic=QUARTIC, degrees=a.degrees, maxcoeff=a.maxcoeff,
        digit_range=[a.lo, a.hi], rows=rows,
        threshold_digits=thr,
        spurious_count=len(spurious),
        spurious_degrees=sorted({r["degree"] for r in spurious}),
        spurious_height_min=min(heights) if heights else None,
        spurious_height_max=max(heights) if heights else None,
        true_quartic_height=max(abs(c) for c in QUARTIC),
    )
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"\nthreshold: {thr} digits -- from here on every precision returns the quartic")
    print(f"below it: {len(spurious)} spurious relations, all of degree "
          f"{sorted({r['degree'] for r in spurious})}, "
          f"coefficient heights {min(heights)}..{max(heights)} "
          f"against the quartic's {max(abs(c) for c in QUARTIC)}")
    print(f"wrote {a.out}")
