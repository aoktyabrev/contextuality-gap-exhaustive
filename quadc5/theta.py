"""Lovasz theta.

SDP implemented from SOURCES.md S1.2 (arXiv:2605.12828, paper.tex lines 224-232):

    theta(G) = max { 1^T X 1 : X >= 0 (PSD), Tr X = 1, X_ij = 0 for (i,j) in E }

Two paths, deliberately independent:
  * theta_cvxpy  -- CVXPY front end, any of CLARABEL / SCS / CVXOPT.
  * theta_scs_direct -- the conic problem assembled by hand and handed to the
    SCS C library, with no CVXPY canonicalisation. Used for the bulk sweep.
Both return primal feasibility residuals so that the answer carries its own
evidence (PREREGISTRATION §R5).
"""
from __future__ import annotations
import time
import numpy as np


def theta_cvxpy(n: int, edges, solver="CLARABEL", **kw):
    import cvxpy as cp
    X = cp.Variable((n, n), PSD=True)
    cons = [cp.trace(X) == 1]
    for (i, j) in edges:
        cons += [X[i, j] == 0]
    prob = cp.Problem(cp.Maximize(cp.sum(X)), cons)
    t0 = time.perf_counter()
    try:
        prob.solve(solver=solver, **kw)
        el = time.perf_counter() - t0
        Xv = X.value
        if Xv is None:
            return dict(theta=float("nan"), pr=float("nan"), status=str(prob.status), t=el)
        pr = abs(float(np.trace(Xv)) - 1.0)
        for (i, j) in edges:
            pr = max(pr, abs(float(Xv[i, j])))
        pr = max(pr, max(0.0, -float(np.linalg.eigvalsh((Xv + Xv.T) / 2)[0])))
        return dict(theta=float(prob.value), pr=pr, status=str(prob.status), t=el, X=Xv)
    except Exception as e:  # solver blow-up is data, not a crash
        return dict(theta=float("nan"), pr=float("nan"), status="ERROR:%s" % e,
                    t=time.perf_counter() - t0)


# ---------------------------------------------------------------------------
# Direct SCS assembly.
#
# Free variables: the entries of X that are not forced to zero, i.e. the n
# diagonal entries plus one variable per NON-edge (i<j).  Let x be that vector.
#   objective   1^T X 1 = sum_i X_ii + 2 * sum_{non-edges} X_ij
#   equality    sum_i X_ii = 1
#   cone        X in S^n_+, expressed in SCS's scaled lower-triangular form:
#               svec(X)_k = X_ii on the diagonal, sqrt(2) * X_ij off it.
# SCS solves   min c^T x  s.t.  A x + s = b,  s in K,  K = zero(1) x psd(n).
# ---------------------------------------------------------------------------

def _svec_index(n):
    """Column-major lower-triangle index used by SCS: (i,j) with i>=j."""
    idx = {}
    k = 0
    for j in range(n):
        for i in range(j, n):
            idx[(i, j)] = k
            k += 1
    return idx, k


def build_scs_data(n: int, edges):
    import scipy.sparse as sp
    E = set((min(i, j), max(i, j)) for (i, j) in edges)
    free = [(i, i) for i in range(n)]
    free += [(i, j) for i in range(n) for j in range(i + 1, n) if (i, j) not in E]
    m_free = len(free)
    idx, m_psd = _svec_index(n)

    c = np.zeros(m_free)
    for k, (i, j) in enumerate(free):
        c[k] = -1.0 if i == j else -2.0          # maximise -> minimise

    rows, cols, vals = [], [], []
    # row 0: trace == 1  (zero cone)
    for k, (i, j) in enumerate(free):
        if i == j:
            rows.append(0); cols.append(k); vals.append(1.0)
    # rows 1..: -svec(X) + s = 0, s in PSD cone
    r2 = np.sqrt(2.0)
    for k, (i, j) in enumerate(free):
        r = 1 + idx[(max(i, j), min(i, j))]
        rows.append(r); cols.append(k); vals.append(-(1.0 if i == j else r2))
    A = sp.csc_matrix((vals, (rows, cols)), shape=(1 + m_psd, m_free))
    b = np.zeros(1 + m_psd)
    b[0] = 1.0
    return dict(A=A, b=b, c=c, free=free, n=n,
                cone=dict(z=1, s=[n]))


def theta_scs_direct(n: int, edges, eps=1e-9, max_iters=100000):
    import scs
    d = build_scs_data(n, edges)
    t0 = time.perf_counter()
    solver = scs.SCS(dict(A=d["A"], b=d["b"], c=d["c"]), d["cone"],
                     eps_abs=eps, eps_rel=eps, max_iters=max_iters, verbose=False)
    sol = solver.solve()
    el = time.perf_counter() - t0
    x = sol["x"]
    X = np.zeros((n, n))
    for k, (i, j) in enumerate(d["free"]):
        X[i, j] = x[k]
        X[j, i] = x[k]
    theta = float(X.sum())
    pr = abs(float(np.trace(X)) - 1.0)
    for (i, j) in edges:
        pr = max(pr, abs(float(X[i, j])))
    pr = max(pr, max(0.0, -float(np.linalg.eigvalsh(X)[0])))
    return dict(theta=theta, pr=pr, status=sol["info"]["status"], t=el, X=X,
                gap=float(sol["info"].get("gap", np.nan)))
