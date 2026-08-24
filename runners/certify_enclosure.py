"""Stage 7.1b -- certified rational enclosure for a theta value with no closed form.
PREREGISTRATION_STAGE7_1B.md.

Numerics only propose the matrices.  The verdict is exact arithmetic in Q:

    primal  X symmetric, Tr X = 1, X_ij = 0 on edges, X psd  ->  theta >= 1^T X 1
    dual    B = 1 on diagonal and non-edges, u*I - B psd      ->  theta <= u

PSD is tested twice by independent methods (pivoted Schur complement; all 2^n - 1
principal minors) which must agree.
"""
import sys, os, json, argparse, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "runners"))
from fractions import Fraction as F
from itertools import combinations
from mpmath import mp, nstr, mpf
from quadc5.g6 import decode_g6, edges_of
from quadc5.alpha import alpha_bitmask
from run_2a import theta_hi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")


# ---------------- exact PSD, two independent methods (rationals only) -------------
def psd_schur(M, n):
    """Method A: pivoted Schur complement.  Returns (is_psd, rank)."""
    A = [row[:] for row in M]
    idx = list(range(n))
    rank = 0
    while idx:
        p = max(idx, key=lambda i: A[i][i])
        if A[p][p] < 0:
            return False, rank
        if A[p][p] == 0:
            for i in idx:
                for j in idx:
                    if A[i][j] != 0:
                        return False, rank
            return True, rank
        idx.remove(p)
        piv = A[p][p]
        for i in idx:
            if A[i][p] == 0:
                continue
            f = A[i][p] / piv
            for j in idx:
                A[i][j] -= f * A[p][j]
        rank += 1
    return True, rank


def _det(M, S):
    k = len(S)
    A = [[M[i][j] for j in S] for i in S]
    det = F(1)
    for c in range(k):
        p = None
        for r in range(c, k):
            if A[r][c] != 0:
                p = r
                break
        if p is None:
            return F(0)
        if p != c:
            A[c], A[p] = A[p], A[c]
            det = -det
        det *= A[c][c]
        inv = F(1) / A[c][c]
        for r in range(c + 1, k):
            if A[r][c] == 0:
                continue
            f = A[r][c] * inv
            for j in range(c, k):
                A[r][j] -= f * A[c][j]
    return det


def psd_minors(M, n):
    """Method B: every principal minor non-negative.  Returns (is_psd, count)."""
    cnt = 0
    for k in range(1, n + 1):
        for S in combinations(range(n), k):
            cnt += 1
            if _det(M, list(S)) < 0:
                return False, cnt
    return True, cnt


def both_psd(M, n, label, log):
    okA, rk = psd_schur(M, n)
    okB, cnt = psd_minors(M, n)
    log.append(dict(what=label, schur=okA, rank=rk, minors=okB, minors_tested=cnt,
                    agree=(okA == okB)))
    if okA != okB:
        raise SystemExit(f"PSD METHODS DISAGREE on {label} -- stop and investigate")
    return okA


# ------------------------------------------------------------------ primal ------
def primal_lower(n, edges, Xf, D, c, log):
    """Round, symmetrise, zero the edges, add (c/D)I, normalise the trace."""
    E = set(map(tuple, (tuple(sorted(e)) for e in edges)))
    R = [[F(int(mp.nint(Xf[i, j] * D)), D) for j in range(n)] for i in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            s = (R[i][j] + R[j][i]) / 2
            if (i, j) in E:
                s = F(0)
            R[i][j] = R[j][i] = s
    eps = F(c, D)
    for i in range(n):
        R[i][i] += eps
    t = sum(R[i][i] for i in range(n))
    X = [[R[i][j] / t for j in range(n)] for i in range(n)]
    # exact feasibility
    assert all(X[i][j] == X[j][i] for i in range(n) for j in range(n))
    assert sum(X[i][i] for i in range(n)) == 1
    assert all(X[i][j] == 0 for (i, j) in E)
    if not both_psd(X, n, f"primal X (D=1e{len(str(D))-1}, c={c})", log):
        return None
    return sum(X[i][j] for i in range(n) for j in range(n))


# -------------------------------------------------------------------- dual ------
def dual_matrix(n, edges, Mf, theta, D):
    """hiprec returns M = theta*I - B, not B.  Recover B, then round its edge
    entries; the diagonal and every non-edge are exactly 1 by construction."""
    E = set(map(tuple, (tuple(sorted(e)) for e in edges)))
    B = [[F(1) for _ in range(n)] for _ in range(n)]
    for (i, j) in E:
        bij = (theta if i == j else 0) - Mf[i, j]
        B[i][j] = B[j][i] = F(int(mp.nint(bij * D)), D)
    return B, E


def dual_upper(n, B, u, log, label):
    M = [[(u if i == j else F(0)) - B[i][j] for j in range(n)] for i in range(n)]
    return both_psd(M, n, label, log)


def bisect_upper(n, B, lo, hi, log, tag, max_steps=60, tol=F(1, 10 ** 12)):
    """lo: known-not-PSD (or unknown), hi: known PSD.  Return the tightest PSD u."""
    assert dual_upper(n, B, hi, log, f"{tag} u=hi"), "starting upper bound is not PSD"
    steps = 0
    while hi - lo > tol and steps < max_steps:
        mid = (lo + hi) / 2
        if dual_upper(n, B, mid, log, f"{tag} step{steps}"):
            hi = mid
        else:
            lo = mid
        steps += 1
    return hi, steps


# -------------------------------------------------------------------- main ------
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--leader", default="J?`D@pgd?{?")
    ap.add_argument("--second", default="J?`@f?kUDG_")
    ap.add_argument("--dps", type=int, default=300)
    ap.add_argument("--ladder", type=int, nargs="+", default=[6, 9, 12, 15, 18])
    ap.add_argument("--cs", type=int, nargs="+", default=[1, 2, 4, 8, 16])
    ap.add_argument("--out", default=os.path.join(RES, "report_7_1b.json"))
    a = ap.parse_args()
    rep = {"psd_log": [], "ladder": []}

    mp.dps = a.dps
    n, adj = decode_g6(a.leader)
    edges = edges_of(n, adj)
    alpha = alpha_bitmask(n, adj)
    print(f"лидер {a.leader}: n={n} |E|={len(edges)} alpha={alpha}")
    t0 = time.time()
    hi = theta_hi(code=a.leader, dps=a.dps)
    print(f"  hiprec dps={a.dps} за {time.time()-t0:.1f} с, residual={nstr(hi['residual'],4)}")
    Xf, Bf, thnum = hi["X"], hi["M"], hi["theta"]

    L = U = None
    steps_used = 0
    for k in a.ladder:
        D = 10 ** k
        for c in a.cs:
            steps_used += 1
            print(f"  примал D=1e{k}, c={c} ...", flush=True)
            v = primal_lower(n, edges, Xf, D, c, rep["psd_log"])
            if v is not None:
                L = v
                break
        if L is None:
            continue
        B, E = dual_matrix(n, edges, Bf, thnum, D)
        u_hi = F(int(mp.nint(thnum * D)) + 2 * max(a.cs) * 11, D)
        u_lo = F(int(mp.nint(thnum * D)) - 2 * max(a.cs) * 11, D)
        U, bs = bisect_upper(n, B, u_lo, u_hi, rep["psd_log"], f"dual D=1e{k}")
        w = float(U - L)
        rep["ladder"].append(dict(D=f"1e{k}", c=c, L=str(L), U=str(U), width=w,
                                  bisect_steps=bs))
        print(f"  D=1e{k}: L={float(L):.15f}  U={float(U):.15f}  ширина={w:.3e}")
        if w < 1e-8:
            break

    gap_to_second = 0.0202024631
    rep["leader"] = dict(graph6=a.leader, alpha=alpha, L=str(L), U=str(U),
                         L_float=float(L), U_float=float(U), width=float(U - L),
                         delta_lo=str(L - alpha), delta_hi=str(U - alpha),
                         delta_lo_float=float(L) - alpha, delta_hi_float=float(U) - alpha,
                         gate_width_below_gap=float(U - L) < gap_to_second,
                         ladder_steps=steps_used)
    print(f"\nЛИДЕР доказано: Delta in [{float(L)-alpha:.15f}, {float(U)-alpha:.15f}]")
    print(f"  ширина {float(U-L):.3e}; гейт (< {gap_to_second}): "
          f"{'ВЗЯТ' if float(U-L) < gap_to_second else 'НЕ ВЗЯТ'}")

    # ---- second place: dual only
    n2, adj2 = decode_g6(a.second)
    edges2 = edges_of(n2, adj2)
    alpha2 = alpha_bitmask(n2, adj2)
    hi2 = theta_hi(code=a.second, dps=a.dps)
    D = 10 ** a.ladder[min(2, len(a.ladder) - 1)]
    B2, _ = dual_matrix(n2, edges2, hi2["M"], hi2["theta"], D)
    u_hi2 = F(int(mp.nint(hi2["theta"] * D)) + 400, D)
    u_lo2 = F(int(mp.nint(hi2["theta"] * D)) - 400, D)
    U2, bs2 = bisect_upper(n2, B2, u_lo2, u_hi2, rep["psd_log"], "dual second")
    rep["second"] = dict(graph6=a.second, alpha=alpha2, U=str(U2), U_float=float(U2),
                         delta_hi=str(U2 - alpha2), delta_hi_float=float(U2) - alpha2,
                         bisect_steps=bs2)
    gap = L - U2
    rep["separation"] = dict(L_minus_U2=str(gap), float=float(gap),
                             strict=(gap > 0))
    print(f"ВТОРОЕ доказано: Delta <= {float(U2)-alpha2:.15f}")
    print(f"РАЗДЕЛЕНИЕ: L - U2 = {float(gap):.10f}  ({'строгое' if gap>0 else 'НЕТ'})")
    rep["psd_all_agree"] = all(e["agree"] for e in rep["psd_log"])
    rep["psd_tests"] = len(rep["psd_log"])
    print(f"проверок PSD: {len(rep['psd_log'])}, методы согласны везде: {rep['psd_all_agree']}")
    json.dump(rep, open(a.out, "w"), indent=1)
    print(f"wrote {a.out}")
