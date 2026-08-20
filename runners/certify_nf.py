"""Block 2.c/2.d -- exact primal+dual certificates over a number field of arbitrary
degree.  PREREGISTRATION_STAGE2 4.

A candidate minimal polynomial p and its real root theta are INPUTS.  What is verified:

    primal  X symmetric, Tr X = 1, X_ij = 0 on every edge, 1^T X 1 = theta, X psd
            -> theta(G) >= theta
    dual    B = 1 on the diagonal and on non-edges, (theta*I - B) psd
            -> theta(G) <= theta

Both PSD tests are run twice by independent methods (pivoted Schur complement, and all
principal minors).  Everything is exact; the high-precision numerics only propose the
entries, they never enter the verdict.
"""
import sys, os, json, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runners"))
from fractions import Fraction as F
import sympy as sp
from mpmath import mp, mpf, pslq, nstr

from quadc5.g6 import decode_g6, edges_of
from quadc5.alpha import alpha_bitmask
from quadc5.numfield import NumField, psd_schur, psd_minors, solve_exact
from run_2a import theta_hi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


def field_from_poly(coeffs_low_first, numeric_theta, dps):
    """Build K = Q(theta) picking the real root of p closest to `numeric_theta`,
    with a certified rational isolating interval from sympy's CRootOf."""
    x = sp.symbols("x")
    poly = sp.Poly(sum(int(c) * x ** k for k, c in enumerate(coeffs_low_first)), x)
    poly = poly.monic() if poly.LC() != 1 else poly
    roots = sp.real_roots(poly.as_expr(), x)
    mp.dps = dps
    best, bi = None, None
    for i, r in enumerate(roots):
        v = mpf(str(sp.N(r, 50)))
        d = abs(v - numeric_theta)
        if best is None or d < best:
            best, bi = d, i
    cr = sp.CRootOf(poly.as_expr(), sp.real_roots(poly.as_expr()).index(roots[bi])) \
        if False else roots[bi]
    iv = cr._get_interval()
    lo, hi = F(int(iv.a.numerator), int(iv.a.denominator)), F(int(iv.b.numerator), int(iv.b.denominator))
    cs = [F(int(c)) for c in sp.Poly(poly, x).all_coeffs()[::-1]]
    K = NumField(cs, (lo, hi))
    return K, poly, best


def recognise(K, value, theta_num, dps, maxcoeff=10 ** 40):
    """value ~ sum_k c_k theta^k with rational c_k; PSLQ on [value, 1, th, th^2, ...]."""
    mp.dps = dps
    vec = [value] + [theta_num ** k for k in range(K.d)]
    rel = pslq(vec, maxcoeff=maxcoeff, maxsteps=10 ** 6, tol=mpf(10) ** (-(dps - 30)))
    if rel is None or rel[0] == 0:
        return None
    m = -int(rel[0])
    return K.from_coeffs([F(int(rel[k + 1]), m) for k in range(K.d)])


def certify(code, poly_coeffs, dps=240, verbose=True):
    n, adj = decode_g6(code)
    E = sorted(edges_of(n, adj))
    Eset = set(E)
    alpha = alpha_bitmask(n, adj)
    hp = theta_hi(code=code, dps=dps)
    th_num = hp["theta"]
    X = hp["X"]
    K, poly, root_gap = field_from_poly(poly_coeffs, th_num, dps)
    out = dict(graph6=code, n=n, edges=len(E), alpha=alpha, degree=K.d,
               minpoly=str(poly.as_expr()), root_gap=nstr(root_gap, 5),
               proved=False, stuck_at=None)
    if verbose:
        print(f"  field Q(theta), deg {K.d}, minpoly {poly.as_expr()}")

    theta = K.gen() if K.d > 1 else K.from_rational(-K.p[0])
    # --- primal ---
    M = [[None] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            if (i, j) in Eset:
                e = K.zero()
            else:
                e = recognise(K, X[i, j], th_num, dps)
                if e is None:
                    out["stuck_at"] = f"primal: entry ({i},{j}) not recognised in Q(theta)"
                    return out
            M[i][j] = M[j][i] = e
    tr = K.zero()
    for i in range(n):
        tr = K.add(tr, M[i][i])
    s = K.zero()
    for i in range(n):
        for j in range(n):
            s = K.add(s, M[i][j])
    ok_tr = tr == K.one()
    ok_edges = all(K.is_zero(M[i][j]) for (i, j) in E)
    ok_sum = K.is_zero(K.sub(s, theta))
    if not (ok_tr and ok_edges and ok_sum):
        out["stuck_at"] = (f"primal exact checks failed: trace={ok_tr} "
                           f"edges={ok_edges} sum=theta:{ok_sum}")
        return out
    p_ok, p_rank, p_msg = psd_schur(K, M, n)
    p_ok2, p_msg2 = psd_minors(K, M, n)
    if verbose:
        print(f"  PRIMAL  trace=1 {ok_tr}, zero on edges {ok_edges}, 1'X1=theta {ok_sum}; "
              f"PSD schur={p_ok} ({p_msg}); PSD minors={p_ok2} ({p_msg2})")
    if not (p_ok and p_ok2):
        out["stuck_at"] = "primal: matrix is not PSD in exact arithmetic"
        return out
    out["primal"] = dict(trace=True, zero_on_edges=True, value=True,
                         psd_schur=p_ok, psd_schur_rank=p_rank, psd_minors=p_ok2)

    # --- dual, from complementary slackness (theta I - B) M = 0 ---
    col = {e: k for k, e in enumerate(E)}
    nf = len(E)
    one, zero = K.one(), K.zero()
    B0 = [[one if (i == j or (min(i, j), max(i, j)) not in Eset) else zero
           for j in range(n)] for i in range(n)]
    A_rows, b_rows = [], []
    for i in range(n):
        for j in range(n):
            coef = [zero] * nf
            const = zero
            for k in range(n):
                tik = K.sub(theta if i == k else zero, B0[i][k])
                const = K.add(const, K.mul(tik, M[k][j]))
                key = (min(i, k), max(i, k))
                if key in Eset:
                    coef[col[key]] = K.sub(coef[col[key]], M[k][j])
            A_rows.append([K.neg(c) for c in coef])
            b_rows.append(const)
    sol, free = solve_exact(K, A_rows, b_rows, len(A_rows), nf)
    if sol is None:
        out["stuck_at"] = "dual: complementary-slackness system is inconsistent"
        return out
    B = [row[:] for row in B0]
    for e, k in col.items():
        B[e[0]][e[1]] = B[e[1]][e[0]] = sol[k]
    S = [[K.sub(theta if i == j else zero, B[i][j]) for j in range(n)] for i in range(n)]
    struct = all(B[i][j] == one for i in range(n) for j in range(n)
                 if i == j or (min(i, j), max(i, j)) not in Eset)
    d_ok, d_rank, d_msg = psd_schur(K, S, n)
    d_ok2, d_msg2 = psd_minors(K, S, n)
    if verbose:
        print(f"  DUAL    structure {struct}; PSD schur={d_ok} ({d_msg}); "
              f"PSD minors={d_ok2} ({d_msg2}); free params {len(free)}")
    out["dual"] = dict(structure=struct, psd_schur=d_ok, psd_schur_rank=d_rank,
                       psd_minors=d_ok2, free_parameters=len(free),
                       edge_values={f"{i},{j}": str([str(c) for c in B[i][j]]) for (i, j) in E})
    if not (struct and d_ok and d_ok2):
        out["stuck_at"] = "dual: theta*I - B is not PSD in exact arithmetic"
        return out
    out["proved"] = True
    mp.dps = 60
    out["theta_float"] = nstr(K.to_float(theta, 50), 45)
    out["delta_float"] = nstr(K.to_float(K.sub(theta, K.from_rational(alpha)), 50), 45)
    if verbose:
        print(f"  PROVED  theta({code}) is the root {out['theta_float']} of "
              f"{poly.as_expr()}; alpha={alpha}; Delta={out['delta_float']}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--dps", type=int, default=240)
    ap.add_argument("--out", default=os.path.join(RES, "report_2c.json"))
    a = ap.parse_args()
    JOBS = [
        ("FCp`_", [49, -49, 7, 1], "C7 -- calibration K3, already-proved cubic"),
        ("GCQb`o", [158, -155, 23, -1, 1], "the eight-vertex hole"),
    ]
    res = []
    for code, coeffs, note in JOBS:
        print(f"\n=== {code} :: {note} ===")
        r = certify(code, coeffs, dps=a.dps)
        r["note"] = note
        if not r["proved"]:
            print(f"  NOT PROVED -- stuck at: {r['stuck_at']}")
        res.append(r)
    json.dump(res, open(a.out, "w"), indent=1, default=str)
    print(f"\nproved {sum(r['proved'] for r in res)} of {len(res)}; wrote {a.out}")
