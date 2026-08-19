"""Structural quantities for block 0.d.

  * induced C5 subgraphs, their pairwise edge overlaps, and the multiplicity
    with which each edge is covered  (reference point: SOURCES.md S1.7)
  * degree sequence
  * eta_d and d*  (definition: SOURCES.md S1.3)
"""
from __future__ import annotations
import numpy as np
from .g6 import edges_of
from .perfect import induced_cycles_of_length


def induced_c5_analysis(n: int, adj):
    """Pentagons, their edge sets, pairwise shared-edge counts, edge multiplicities."""
    cycles = induced_cycles_of_length(n, adj, 5)
    E = edges_of(n, adj)
    Eset = set(E)
    cyc_edges = []
    for S in cycles:
        Ssub = set(S)
        es = frozenset((i, j) for (i, j) in E if i in Ssub and j in Ssub)
        cyc_edges.append(es)
    mult = {e: 0 for e in E}
    for es in cyc_edges:
        for e in es:
            mult[e] += 1
    k = len(cycles)
    overlap = np.zeros((k, k), dtype=int)
    for a in range(k):
        for b in range(k):
            overlap[a, b] = len(cyc_edges[a] & cyc_edges[b])
    mults = sorted(mult.values())
    covered = sum(1 for v in mult.values() if v > 0)
    return dict(
        n_c5=k,
        cycles=[tuple(c) for c in cycles],
        overlap=overlap,
        edge_mult=mult,
        mult_hist={m: mults.count(m) for m in sorted(set(mults))} if mults else {},
        edges_covered=covered,
        n_edges=len(E),
        # the three preregistered levels, PREREGISTRATION §6.2
        D1=k >= 1,
        D2=(k >= 2 and any(overlap[a, b] > 0 for a in range(k) for b in range(a + 1, k))),
        D3=(k >= 1 and covered == len(E) and all(v == 2 for v in mult.values())),
    )


def degree_sequence(n: int, adj):
    return tuple(sorted(bin(adj[i]).count("1") for i in range(n)))


# --------------------------------------------------------------------------
# eta_d: max lambda_max(sum_i v_i v_i^T), |v_i| = 1, v_i . v_j = 0 on edges.
# Non-convex; restarts give a LOWER bound only (SOURCES.md S1.9).
# --------------------------------------------------------------------------

def _eta_obj(x, n, d):
    V = x.reshape(n, d)
    M = V.T @ V
    try:
        w, U = np.linalg.eigh(M)
    except np.linalg.LinAlgError:      # LAPACK occasionally fails to converge
        return 0.0, np.zeros(n * d)    # report a useless point, not a crash
    u = U[:, -1]
    lam = w[-1]
    g = -2.0 * np.outer(V @ u, u)
    return -lam, g.ravel()


def eta_d(n: int, adj, d: int, restarts: int = 300, seed: int = 20260819,
          tol: float = 1e-12):
    """Best lower bound on eta_d found in `restarts` SLSQP runs."""
    from scipy.optimize import minimize
    E = edges_of(n, adj)
    rng = np.random.default_rng(seed)

    cons = []
    for i in range(n):
        def f(x, i=i):
            V = x.reshape(n, d)
            return V[i] @ V[i] - 1.0

        def jf(x, i=i):
            V = x.reshape(n, d)
            J = np.zeros((n, d))
            J[i] = 2 * V[i]
            return J.ravel()
        cons.append(dict(type="eq", fun=f, jac=jf))
    for (a, b) in E:
        def g(x, a=a, b=b):
            V = x.reshape(n, d)
            return V[a] @ V[b]

        def jg(x, a=a, b=b):
            V = x.reshape(n, d)
            J = np.zeros((n, d))
            J[a] = V[b]
            J[b] = V[a]
            return J.ravel()
        cons.append(dict(type="eq", fun=g, jac=jg))

    best = -np.inf
    best_x = None
    for _ in range(restarts):
        V0 = rng.normal(size=(n, d))
        V0 /= np.linalg.norm(V0, axis=1, keepdims=True)
        try:
            res = minimize(_eta_obj, V0.ravel(), args=(n, d), jac=True,
                           method="SLSQP", constraints=cons,
                           options=dict(maxiter=400, ftol=tol))
        except np.linalg.LinAlgError:
            continue
        V = res.x.reshape(n, d)
        err = max(
            max(abs(V[i] @ V[i] - 1.0) for i in range(n)),
            max((abs(V[a] @ V[b]) for (a, b) in E), default=0.0),
        )
        if err > 1e-8:
            continue                      # infeasible point: not a valid bound
        try:
            lam = float(np.linalg.eigvalsh(V.T @ V)[-1])
        except np.linalg.LinAlgError:
            continue
        if lam > best:
            best, best_x = lam, V.copy()
    return dict(eta=best, V=best_x, d=d, restarts=restarts)


def d_star(n: int, adj, alpha: int, dmax: int = None, restarts: int = 300,
           seed: int = 20260819, margin: float = 1e-6):
    """Smallest d with eta_d > alpha, per SOURCES.md S1.3.

    Returns (d*, indicated) where indicated=True means the value rests on a
    non-exceedance that the heuristic merely failed to find -- the same caveat
    the source attaches to its own d*=4 values (S1.9).
    """
    if dmax is None:
        dmax = n
    trace = {}
    for d in range(2, dmax + 1):
        r = eta_d(n, adj, d, restarts=restarts, seed=seed)
        trace[d] = r["eta"]
        if r["eta"] > alpha + margin:
            return dict(d_star=d, indicated=(d > 2), eta_trace=trace)
    return dict(d_star=None, indicated=True, eta_trace=trace)
