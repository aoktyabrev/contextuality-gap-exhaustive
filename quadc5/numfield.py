"""Exact arithmetic in a real number field Q(theta) of arbitrary degree.

Elements are coefficient vectors over the basis 1, theta, ..., theta^(d-1), with
`fractions.Fraction` coefficients.  Nothing here uses floating point: the sign of an
element is decided by an exact zero test on its coordinates followed, if it is not
zero, by rational interval arithmetic on a certified isolating interval for theta,
bisected until the value interval no longer contains zero.  That terminates for every
non-zero element and is a proof, not a measurement.

Generalises quadc5/qfield.py (degree 2) to arbitrary degree for Stage 2.
"""
from __future__ import annotations
from fractions import Fraction as F


def _trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return a


def _polymul(a, b):
    a, b = _trim(a), _trim(b)
    if not a or not b:
        return []
    out = [F(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                if y:
                    out[i + j] += x * y
    return _trim(out)


def _polysub(a, b):
    n = max(len(a), len(b))
    a = list(a) + [F(0)] * (n - len(a))
    b = list(b) + [F(0)] * (n - len(b))
    return _trim([x - y for x, y in zip(a, b)])


def _polydivmod(a, b):
    """a = q*b + r, all lists of Fractions low-order first."""
    a, b = _trim(a), _trim(b)
    if not b:
        raise ZeroDivisionError("polynomial division by zero")
    if len(a) < len(b):
        return [], a
    q = [F(0)] * (len(a) - len(b) + 1)
    r = list(a)
    while True:
        r = _trim(r)
        if not r or len(r) < len(b):
            break
        k = len(r) - len(b)
        c = r[-1] / b[-1]
        q[k] = c
        for i, y in enumerate(b):
            r[k + i] -= c * y
    return _trim(q), _trim(r)


def _ext_gcd(a, b):
    """Return (g, s, t) with s*a + t*b = g over Q[x]."""
    r0, r1 = _trim(a), _trim(b)
    s0, s1 = [F(1)], []
    t0, t1 = [], [F(1)]
    while r1:
        q, r = _polydivmod(r0, r1)
        r0, r1 = r1, r
        s0, s1 = s1, _polysub(s0, _polymul(q, s1))
        t0, t1 = t1, _polysub(t0, _polymul(q, t1))
    return r0, s0, t0


class NumField:
    """Q(theta), theta the unique real root of `minpoly` inside `interval`."""

    def __init__(self, minpoly, interval):
        """minpoly: list of Fractions low-order first (any leading coeff != 0).
        interval: (lo, hi) rationals isolating exactly one real root."""
        self.p = [F(c) for c in minpoly]
        while self.p and self.p[-1] == 0:
            self.p.pop()
        lead = self.p[-1]
        self.p = [c / lead for c in self.p]          # monic
        self.d = len(self.p) - 1
        self.lo, self.hi = F(interval[0]), F(interval[1])
        assert self._peval(self.lo) * self._peval(self.hi) < 0, "interval does not bracket a root"
        # theta^d = -(p_0 + ... + p_{d-1} theta^{d-1})
        self._red = [-c for c in self.p[:self.d]]

    # ---- basic element ops --------------------------------------------------
    def zero(self):
        return tuple([F(0)] * self.d)

    def one(self):
        return tuple([F(1)] + [F(0)] * (self.d - 1))

    def gen(self):
        if self.d == 1:
            return (self.p[0] * -1,)
        return tuple([F(0), F(1)] + [F(0)] * (self.d - 2))

    def from_rational(self, q):
        return tuple([F(q)] + [F(0)] * (self.d - 1))

    def from_coeffs(self, cs):
        cs = [F(c) for c in cs] + [F(0)] * (self.d - len(cs))
        return tuple(cs[:self.d])

    def add(self, a, b):
        return tuple(x + y for x, y in zip(a, b))

    def sub(self, a, b):
        return tuple(x - y for x, y in zip(a, b))

    def neg(self, a):
        return tuple(-x for x in a)

    def reduce(self, c):
        c = list(c)
        for k in range(len(c) - 1, self.d - 1, -1):
            v = c[k]
            if v:
                c[k] = F(0)
                for i, r in enumerate(self._red):
                    c[k - self.d + i] += v * r
        return tuple(c[:self.d] + [F(0)] * max(0, self.d - len(c)))

    def mul(self, a, b):
        return self.reduce(_polymul(list(a), list(b)))

    def inv(self, a):
        """Inverse in Q[x]/(p) by the extended Euclidean algorithm."""
        if not any(a):
            raise ZeroDivisionError("inverse of 0")
        g, _, t = _ext_gcd(self.p, list(a))
        if len(g) != 1 or g[0] == 0:
            raise ZeroDivisionError("element is not invertible (p reducible?)")
        return self.reduce([c / g[0] for c in t])

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    def is_zero(self, a):
        return all(x == 0 for x in a)

    # ---- exact sign ---------------------------------------------------------
    def _peval(self, x):
        v = F(0)
        for c in reversed(self.p):
            v = v * x + c
        return v

    def _bisect(self):
        mid = (self.lo + self.hi) / 2
        if self._peval(self.lo) * self._peval(mid) <= 0:
            self.hi = mid
        else:
            self.lo = mid

    @staticmethod
    def _ivmul(a, b):
        p = [a[0] * b[0], a[0] * b[1], a[1] * b[0], a[1] * b[1]]
        return (min(p), max(p))

    def _elem_interval(self, a):
        """Rational interval hull of sum a_k theta^k over [lo, hi], by Horner."""
        iv = (F(0), F(0))
        t = (self.lo, self.hi)
        for c in reversed(a):
            iv = self._ivmul(iv, t)
            iv = (iv[0] + c, iv[1] + c)
        return iv

    def sign(self, a, max_bisect=400):
        if self.is_zero(a):
            return 0
        for _ in range(max_bisect):
            lo, hi = self._elem_interval(a)
            if lo > 0:
                return 1
            if hi < 0:
                return -1
            self._bisect()
        raise RuntimeError("sign undecided after %d bisections" % max_bisect)

    def cmp(self, a, b):
        return self.sign(self.sub(a, b))

    def to_float(self, a, prec=60):
        from mpmath import mp, mpf
        mp.dps = prec
        th = mpf(self.lo.numerator) / self.lo.denominator
        for _ in range(4 * prec):
            self._bisect()
        th = (mpf(self.lo.numerator) / self.lo.denominator +
              mpf(self.hi.numerator) / self.hi.denominator) / 2
        v = mpf(0)
        for c in reversed(a):
            v = v * th + mpf(c.numerator) / c.denominator
        return v


def psd_schur(K, M, n):
    """Exact PSD test by symmetric pivoted Schur complement (the Stage 0/1 method)."""
    A = [[M[i][j] for j in range(n)] for i in range(n)]
    rank = 0
    for k in range(n):
        p, best = k, A[k][k]
        for i in range(k + 1, n):
            if K.cmp(A[i][i], best) > 0:
                p, best = i, A[i][i]
        if K.sign(best) < 0:
            return False, rank, "negative pivot at step %d" % k
        if p != k:
            A[k], A[p] = A[p], A[k]
            for r in range(n):
                A[r][k], A[r][p] = A[r][p], A[r][k]
        if K.is_zero(A[k][k]):
            for i in range(k, n):
                for j in range(k, n):
                    if not K.is_zero(A[i][j]):
                        return False, rank, "zero diagonal with non-zero off-diagonal"
            return True, rank, "psd, rank %d" % rank
        rank += 1
        d = A[k][k]
        for i in range(k + 1, n):
            if K.is_zero(A[i][k]):
                continue
            f = K.div(A[i][k], d)
            for j in range(k + 1, n):
                A[i][j] = K.sub(A[i][j], K.mul(f, A[k][j]))
    return True, rank, "psd, full rank %d" % rank


def det_exact(K, M, idx):
    """Exact determinant of the principal submatrix on `idx`, by fraction-free-ish
    Gaussian elimination over the field."""
    m = len(idx)
    A = [[M[i][j] for j in idx] for i in idx]
    det = K.one()
    for k in range(m):
        p = next((i for i in range(k, m) if not K.is_zero(A[i][k])), None)
        if p is None:
            return K.zero()
        if p != k:
            A[k], A[p] = A[p], A[k]
            det = K.neg(det)
        det = K.mul(det, A[k][k])
        inv = K.inv(A[k][k])
        for i in range(k + 1, m):
            if K.is_zero(A[i][k]):
                continue
            f = K.mul(A[i][k], inv)
            for j in range(k, m):
                A[i][j] = K.sub(A[i][j], K.mul(f, A[k][j]))
    return det


def psd_minors(K, M, n, limit=1 << 12):
    """Independent PSD test: every principal minor is >= 0.  Exponential; for n <= 10
    that is at most 1023 determinants."""
    from itertools import combinations
    cnt = 0
    for k in range(1, n + 1):
        for S in combinations(range(n), k):
            cnt += 1
            if cnt > limit:
                return None, "aborted after %d minors" % limit
            if K.sign(det_exact(K, M, list(S))) < 0:
                return False, "negative principal minor on %s" % (S,)
    return True, "all %d principal minors >= 0" % cnt


def solve_exact(K, A, b, nrow, ncol):
    """Exact Gaussian elimination over K.  Returns (solution, free_columns) with free
    columns set to zero, or (None, None) if the system is inconsistent."""
    Aug = [[A[i][j] for j in range(ncol)] + [b[i]] for i in range(nrow)]
    piv = {}
    r = 0
    for c in range(ncol):
        p = None
        for i in range(r, nrow):
            if not K.is_zero(Aug[i][c]):
                p = i
                break
        if p is None:
            continue
        Aug[r], Aug[p] = Aug[p], Aug[r]
        inv = K.inv(Aug[r][c])
        Aug[r] = [K.mul(x, inv) for x in Aug[r]]
        for i in range(nrow):
            if i != r and not K.is_zero(Aug[i][c]):
                f = Aug[i][c]
                Aug[i] = [K.sub(Aug[i][j], K.mul(f, Aug[r][j])) for j in range(ncol + 1)]
        piv[c] = r
        r += 1
        if r == nrow:
            break
    for i in range(r, nrow):
        if all(K.is_zero(Aug[i][j]) for j in range(ncol)) and not K.is_zero(Aug[i][ncol]):
            return None, None
    sol = [K.zero() for _ in range(ncol)]
    for c, rr in piv.items():
        sol[c] = Aug[rr][ncol]
    return sol, [c for c in range(ncol) if c not in piv]
