"""Block 2.b -- integer-relation search for the minimal polynomial.
PREREGISTRATION_STAGE2 §3.  The polynomials found here are CANDIDATES, not answers.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sympy as sp
from mpmath import mp, mpf, pslq, nstr, mpmathify

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runners"))
from run_2a import theta_hi, matching_digits

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
CACHE = os.path.join(RES, "theta_highprec.json")


def get_theta(code, dps):
    """theta at working precision dps and 2*dps, with the honest digit count."""
    cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
    key = f"{code}@{dps}"
    if key in cache:
        mp.dps = 2 * dps + 20
        return mpmathify(cache[key]["hi"]), cache[key]["honest"]
    r1 = theta_hi(code=code, dps=dps)
    r2 = theta_hi(code=code, dps=2 * dps)
    honest = matching_digits(r1["theta"], r2["theta"], 2 * dps) - 5
    mp.dps = 2 * dps + 20
    cache[key] = dict(hi=nstr(r2["theta"], 2 * dps - 10), honest=honest,
                      residual=nstr(r2["residual"], 6))
    json.dump(cache, open(CACHE, "w"), indent=1)
    return mpmathify(cache[key]["hi"]), honest


def budget(D, d):
    """PREREGISTRATION_STAGE2 §3.1: B = floor((D - 20) / (d + 1))."""
    return max(1, (D - 20) // (d + 1))


def search(theta, D, degrees, label, extra_note=""):
    """Return the list of candidates surviving the §3.2 criteria."""
    cands, rejected = [], []
    x = sp.symbols("x")
    for d in degrees:
        B = budget(D, d)
        H = 10 ** B
        mp.dps = D + 10
        v = [theta ** k for k in range(d + 1)]
        rel = pslq(v, maxcoeff=H, maxsteps=10 ** 6, tol=mpf(10) ** (-(D - 10)))
        if rel is None:
            rejected.append(dict(degree=d, bound=f"1e{B}", why="no relation returned"))
            print(f"   deg {d:2d}  bound 1e{B:<3d}  -> none")
            continue
        # criterion 2: same relation at doubled precision and a decade wider bound
        mp.dps = 2 * D + 10
        v2 = [theta ** k for k in range(d + 1)]
        rel2 = pslq(v2, maxcoeff=10 * H, maxsteps=10 ** 6, tol=mpf(10) ** (-(D - 10)))
        stable = (rel2 is not None and
                  (list(rel2) == list(rel) or list(rel2) == [-c for c in rel]))
        poly = sp.Poly(sum(int(c) * x ** k for k, c in enumerate(rel)), x)
        mp.dps = 2 * D + 10
        resid = abs(sum(mpf(int(c)) * theta ** k for k, c in enumerate(rel)))
        small = resid < mpf(10) ** (-(D - 5))
        irred = poly.as_expr().is_polynomial() and len(sp.factor_list(poly.as_expr())[1]) == 1
        maxc = max(abs(int(c)) for c in rel)
        near_bound = maxc > 10 ** max(1, B - 1)
        ok = stable and small and irred and not near_bound
        rec = dict(degree=d, bound=f"1e{B}", relation=[int(c) for c in rel],
                   poly=str(poly.as_expr()), max_coeff=maxc,
                   stable_at_2x=bool(stable), residual=nstr(resid, 6),
                   residual_small=bool(small), irreducible=bool(irred),
                   near_bound=bool(near_bound), verdict="CANDIDATE" if ok else "NOISE")
        print(f"   deg {d:2d}  bound 1e{B:<3d}  -> {poly.as_expr()}")
        print(f"          maxcoef={maxc}  stable@2x={stable}  |p(t)|={nstr(resid,3)}  "
              f"irreducible={irred}  near-bound={near_bound}  => {rec['verdict']}")
        (cands if ok else rejected).append(rec)
    return cands, rejected


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dps", type=int, default=240)
    ap.add_argument("--codes", nargs="+",
                    default=["FCp`_", "GCQb`o", "ICQeR`[Mg"])
    ap.add_argument("--degrees", type=int, nargs="+", default=[2, 3, 4, 6, 8])
    ap.add_argument("--extra-degrees", type=int, nargs="+",
                    default=[5, 7, 9, 10, 12, 16])
    a = ap.parse_args()
    out = {}
    for code in a.codes:
        print(f"\n=== {code} ===")
        th, D = get_theta(code, a.dps)
        print(f"   honest digits D = {D}")
        mp.dps = 80
        print(f"   theta = {nstr(th, 70)}")
        c1, r1 = search(th, D, a.degrees, code)
        print(f"   -- extra degrees beyond the brief, for the negative bound --")
        c2, r2 = search(th, D, a.extra_degrees, code)
        out[code] = dict(honest_digits=D, theta=nstr(th, min(D, 200)),
                         candidates=c1 + c2, rejected=r1 + r2,
                         degrees_searched=sorted(a.degrees + a.extra_degrees),
                         budget_rule="B = floor((D-20)/(d+1)), PREREGISTRATION_STAGE2 3.1")
        print(f"   candidates: {len(c1+c2)}")
    json.dump(out, open(os.path.join(RES, "report_2b.json"), "w"), indent=1, default=str)
    print("\nwrote results/report_2b.json  (candidates are hypotheses for 2.c, not answers)")
