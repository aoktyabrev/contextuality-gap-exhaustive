"""Exact primal+dual certificates for theta (Stage 1, block 1.d).

Method, as used for 11/3 in Stage 0 and generalised here to Q(sqrt(d)):

  primal  numerical X -> recognise every entry as (p + q*sqrt(d))/D -> check
          symmetry, trace = 1, zeros on all edges, sum = target, and PSD in exact
          arithmetic (pivoted Schur complement, quadc5/qfield.py).
  dual    B is 1 on the diagonal and on every non-edge, free on edges.  Complementary
          slackness (t*I - B) * M = 0 is a linear system over the field; solve it
          exactly, then check the structure and that (t*I - B) is PSD, which gives
          lambda_max(B) = t and hence theta <= t.

If any step fails the certificate is reported as NOT OBTAINED, naming the step.  A
numerical coincidence is never promoted to a proof (PREREGISTRATION_STAGE1 §5).
"""
import sys, os, json, math, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fractions import Fraction as F
import numpy as np

from quadc5.g6 import decode_g6, edges_of
from quadc5.theta import theta_cvxpy
from quadc5.alpha import alpha_bitmask
from quadc5.qfield import QSqrt, psd_exact, solve_exact

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def identify(x, D, d, R=60, tol=1e-4):
    """Best (p, q) with (p + q*sqrt(d))/D close to x; None if nothing is close."""
    sd = math.sqrt(d)
    best = None
    for q in range(-R, R + 1):
        p = round(x * D - q * sd)
        v = (p + q * sd) / D
        e = abs(v - x)
        if best is None or e < best[0]:
            best = (e, p, q)
    if best[0] > tol:
        return None
    return best


def build_primal(n, X, D, d, tol, R=40):
    M, worst = [], 0.0
    for i in range(n):
        row = []
        for j in range(n):
            got = identify(X[i, j], D, d, R=R, tol=tol)
            if got is None:
                return None, None
            e, p, q = got
            worst = max(worst, e)
            row.append(QSqrt(F(p, D), F(q, D), d))
        M.append(row)
    return M, worst


DEFAULT_D = tuple(range(1, 1501))


def certify(code, D_candidates=DEFAULT_D, d_candidates=(1, 2, 3, 5, 6, 7), R=40,
            tol=2e-5, verbose=True):
    """Smallest denominator first, so a spurious large-D fit is only ever reached
    after every simpler one has failed.  Soundness does not rest on the search:
    whatever it returns is accepted only if the exact feasibility, exact PSD and the
    exact dual all pass, and those together are a proof on their own."""
    n, adj = decode_g6(code)
    E = sorted(edges_of(n, adj))
    Eset = set(E)
    alpha = alpha_bitmask(n, adj)
    sol = theta_cvxpy(n, E, solver="CLARABEL")
    theta_num = sol["theta"]
    X = (sol["X"] + sol["X"].T) / 2
    out = dict(graph6=code, n=n, edges=len(E), alpha=alpha, theta_numeric=theta_num,
               proved=False, stuck_at=None)

    found = None
    for d in d_candidates:
        for D in D_candidates:
            M, worst = build_primal(n, X, D, d, tol, R)
            if M is None:
                continue
            tr = M[0][0] - M[0][0]
            for i in range(n):
                tr = tr + M[i][i]
            if not (tr - QSqrt(1, 0, d)).is_zero():
                continue
            if any(not M[i][j].is_zero() for (i, j) in E):
                continue
            s = M[0][0] - M[0][0]
            for i in range(n):
                for j in range(n):
                    s = s + M[i][j]
            if abs(s.float() - theta_num) > 1e-5:
                continue
            ok, rank, detail = psd_exact(M, n)
            if not ok:
                continue
            found = (d, D, M, s, rank, worst)
            break
        if found:
            break

    if not found:
        out["stuck_at"] = "primal: no denominator/field in the search grid gave an " \
                          "exact feasible PSD matrix"
        return out
    d, D, M, tval, rank, worst = found
    out.update(field=f"Q(sqrt({d}))" if d != 1 else "Q", denominator=D,
               theta_exact=f"({tval.a}) + ({tval.b})*sqrt({d})",
               theta_exact_float=tval.float(), primal_rank=rank,
               identification_error=worst,
               primal=dict(trace=1, zero_on_edges=True, psd_exact=True, rank=rank))
    if verbose:
        print(f"PRIMAL  field Q(sqrt({d})) denominator {D}: trace 1, zero on edges, "
              f"PSD exact, rank {rank}; 1'X1 = {tval} = {tval.float():.12f}")

    # ---- dual ---------------------------------------------------------------
    free = [(i, j) for (i, j) in E]
    nf = len(free)
    col_of = {e: k for k, e in enumerate(free)}
    one = QSqrt(1, 0, d)
    zero = QSqrt(0, 0, d)
    B0 = [[one if (i == j or (min(i, j), max(i, j)) not in Eset) else zero
           for j in range(n)] for i in range(n)]
    rows_A, rows_b = [], []
    for i in range(n):
        for j in range(n):
            coef = [zero] * nf
            const = zero
            for k in range(n):
                # entry (i,j) of (t*I - B) * M
                tik = (tval if i == k else zero) - B0[i][k]
                const = const + tik * M[k][j]
                key = (min(i, k), max(i, k))
                if key in Eset:
                    coef[col_of[key]] = coef[col_of[key]] - M[k][j]
            # sum_k coef_k * b_k + const = 0
            rows_A.append([-c for c in coef])
            rows_b.append(const)
    sol_vec, freecols = solve_exact(rows_A, rows_b, len(rows_A), nf)
    if sol_vec is None:
        out["stuck_at"] = "dual: complementary-slackness system is inconsistent"
        return out
    B = [row[:] for row in B0]
    for (i, j), k in col_of.items():
        B[i][j] = sol_vec[k]
        B[j][i] = sol_vec[k]
    S = [[(tval if i == j else zero) - B[i][j] for j in range(n)] for i in range(n)]
    okS, rankS, detS = psd_exact(S, n)
    struct = all((B[i][j] - one).is_zero() for i in range(n) for j in range(n)
                 if i == j or (min(i, j), max(i, j)) not in Eset)
    out["dual"] = dict(structure=struct, psd_exact=okS, detail=detS,
                       free_parameters=len(freecols),
                       edge_values={f"{i},{j}": str(B[i][j]) for (i, j) in E})
    if verbose:
        print(f"DUAL    structure {struct}, (t*I - B) PSD exact {okS} ({detS}), "
              f"{len(freecols)} free parameter(s)")
    if not (struct and okS):
        out["stuck_at"] = "dual: " + ("structure broken" if not struct
                                      else "t*I - B is not PSD in exact arithmetic")
        return out
    out["proved"] = True
    out["delta_exact"] = f"({tval.a - alpha}) + ({tval.b})*sqrt({d})"
    out["delta_exact_float"] = tval.float() - alpha
    if verbose:
        print(f"PROVED  theta({code}) = {tval} = {tval.float():.12f}, alpha = {alpha}, "
              f"Delta = {tval.float() - alpha:.12f}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("codes", nargs="+")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = []
    for c in a.codes:
        print(f"\n=== {c} ===")
        r = certify(c)
        if not r["proved"]:
            print(f"NOT OBTAINED -- stuck at: {r['stuck_at']}")
        res.append(r)
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, default=str)
    print(f"\nproved {sum(r['proved'] for r in res)} of {len(res)}")
