"""Arbitrary-precision refinement of the Lovasz theta optimum (Stage 2, block 2.a).

The SDP of SOURCES.md S1.2 and its dual are characterised by

    Tr X = 1,   X_ij = 0 for (i,j) in E,   1^T X 1 = t,
    B_ij = 1 for i = j and for non-edges,  B_ij free on edges,
    (t*I - B) X = 0                                   (complementary slackness)

which is a polynomial system.  Seeded from a double-precision solution it is solved
by Gauss-Newton in mpmath, so the number of correct digits doubles per iteration.

The value produced here is a SEARCH INPUT ONLY.  Nothing in Stage 2's result depends
on trusting it: the result is the exact certificate built in quadc5/numfield.py.
"""
from __future__ import annotations
from mpmath import mp, matrix, mpf, norm


def _layout(n, edges):
    E = set((min(i, j), max(i, j)) for (i, j) in edges)
    free = [(i, i) for i in range(n)]
    free += [(i, j) for i in range(n) for j in range(i + 1, n) if (i, j) not in E]
    ed = sorted(E)
    return E, free, ed


def _assemble(x, n, free, ed):
    """x -> (X, B, t) as mpmath matrices."""
    X = matrix(n, n)
    for k, (i, j) in enumerate(free):
        X[i, j] = x[k]
        X[j, i] = x[k]
    nf = len(free)
    B = matrix(n, n)
    Eset = set(ed)
    for i in range(n):
        for j in range(n):
            if i == j or (min(i, j), max(i, j)) not in Eset:
                B[i, j] = mpf(1)
    for k, (i, j) in enumerate(ed):
        B[i, j] = x[nf + k]
        B[j, i] = x[nf + k]
    t = x[nf + len(ed)]
    return X, B, t


def _residual(x, n, free, ed):
    X, B, t = _assemble(x, n, free, ed)
    M = matrix(n, n)
    for i in range(n):
        for j in range(n):
            M[i, j] = (t if i == j else mpf(0)) - B[i, j]
    MX = M * X
    F = [sum(X[i, i] for i in range(n)) - 1,
         sum(X[i, j] for i in range(n) for j in range(n)) - t]
    for i in range(n):
        for j in range(n):
            F.append(MX[i, j])
    return matrix(F), X, M


def _jacobian(x, n, free, ed):
    nf, ne = len(free), len(ed)
    nx = nf + ne + 1
    X, B, t = _assemble(x, n, free, ed)
    M = matrix(n, n)
    for i in range(n):
        for j in range(n):
            M[i, j] = (t if i == j else mpf(0)) - B[i, j]
    rows = 2 + n * n
    J = matrix(rows, nx)
    # row 0: d(Tr X)/dx ; row 1: d(sum X - t)/dx
    for k, (i, j) in enumerate(free):
        if i == j:
            J[0, k] = mpf(1)
            J[1, k] = mpf(1)
        else:
            J[1, k] = mpf(2)
    J[1, nf + ne] = mpf(-1)
    # rows 2.. : d(M X)_{pq} / dx
    def rc(p, q):
        return 2 + p * n + q
    for k, (i, j) in enumerate(free):          # X entries
        for q in range(n):
            if i == j:
                for p in range(n):
                    J[rc(p, q), k] += M[p, i] * (mpf(1) if q == i else mpf(0))
            else:
                for p in range(n):
                    if q == j:
                        J[rc(p, q), k] += M[p, i]
                    if q == i:
                        J[rc(p, q), k] += M[p, j]
    for k, (i, j) in enumerate(ed):            # dual edge entries: M = tI - B
        for q in range(n):
            for p in range(n):
                v = mpf(0)
                if p == i:
                    v -= X[j, q]
                if p == j:
                    v -= X[i, q]
                if v != 0:
                    J[rc(p, q), nf + k] += v
    for p in range(n):                          # t
        for q in range(n):
            J[rc(p, q), nf + ne] = X[p, q]
    return J


def refine(n, edges, X0, B0, t0, dps=120, iters=40, tol_exp=None):
    """Gauss-Newton refinement.  X0/B0 are numpy arrays, t0 a float."""
    mp.dps = dps
    E, free, ed = _layout(n, edges)
    x = matrix(len(free) + len(ed) + 1, 1)
    for k, (i, j) in enumerate(free):
        x[k] = mpf(repr(float(X0[i, j])))
    for k, (i, j) in enumerate(ed):
        x[len(free) + k] = mpf(repr(float(B0[i, j])))
    x[len(free) + len(ed)] = mpf(repr(float(t0)))
    lam = mpf(10) ** (-(dps // 2))
    hist = []
    for it in range(iters):
        F, X, M = _residual(x, n, free, ed)
        r = norm(F)
        hist.append(r)
        if r < mpf(10) ** (-(dps - 10)):
            break
        J = _jacobian(x, n, free, ed)
        JT = J.T
        A = JT * J
        for d in range(A.rows):
            A[d, d] += lam
        try:
            dx = mp.lu_solve(A, -(JT * F))
        except Exception:
            break
        x = x + dx
        if norm(dx) < mpf(10) ** (-(dps - 5)):
            break
    F, X, M = _residual(x, n, free, ed)
    t = x[len(free) + len(ed)]
    return dict(theta=t, X=X, M=M, residual=norm(F), iterations=len(hist),
                history=hist, dps=dps)
