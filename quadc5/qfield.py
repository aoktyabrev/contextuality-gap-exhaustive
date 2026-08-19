"""Exact arithmetic in Q(sqrt(d)) and an exact PSD test.

Numbers are pairs (a, b) of Fractions meaning a + b*sqrt(d).  Everything here is
exact: no floating point enters, so a PSD verdict is a proof, not a measurement.
d = 1 recovers plain Q, so the same code certifies the rational cases.
"""
from __future__ import annotations
from fractions import Fraction as F


class QSqrt:
    __slots__ = ("a", "b", "d")

    def __init__(self, a=0, b=0, d=5):
        self.a = F(a); self.b = F(b); self.d = int(d)

    def __repr__(self):
        if self.b == 0:
            return str(self.a)
        return f"({self.a} + {self.b}*sqrt({self.d}))"

    def _co(self, o):
        return o if isinstance(o, QSqrt) else QSqrt(o, 0, self.d)

    def __add__(self, o):
        o = self._co(o); return QSqrt(self.a + o.a, self.b + o.b, self.d)
    __radd__ = __add__

    def __neg__(self):
        return QSqrt(-self.a, -self.b, self.d)

    def __sub__(self, o):
        return self + (-self._co(o))

    def __rsub__(self, o):
        return self._co(o) + (-self)

    def __mul__(self, o):
        o = self._co(o)
        return QSqrt(self.a * o.a + self.d * self.b * o.b,
                     self.a * o.b + self.b * o.a, self.d)
    __rmul__ = __mul__

    def inv(self):
        nrm = self.a * self.a - self.d * self.b * self.b
        if nrm == 0:
            raise ZeroDivisionError("non-invertible in Q(sqrt(%d))" % self.d)
        return QSqrt(self.a / nrm, -self.b / nrm, self.d)

    def __truediv__(self, o):
        return self * self._co(o).inv()

    def is_zero(self):
        return self.a == 0 and self.b == 0

    def sign(self):
        """Exact sign of a + b*sqrt(d).  No floating point."""
        a, b, d = self.a, self.b, self.d
        if b == 0:
            return (a > 0) - (a < 0)
        if a == 0:
            return (b > 0) - (b < 0)
        if a > 0 and b > 0:
            return 1
        if a < 0 and b < 0:
            return -1
        # opposite signs: compare a^2 with d*b^2
        lhs, rhs = a * a, d * b * b
        if lhs == rhs:
            return 0
        bigger_is_a = lhs > rhs
        return (1 if bigger_is_a else -1) * (1 if a > 0 else -1)

    def __eq__(self, o):
        o = self._co(o); return self.a == o.a and self.b == o.b

    def float(self):
        import math
        return float(self.a) + float(self.b) * math.sqrt(self.d)


def psd_exact(Mat, n):
    """Exact PSD test by symmetric pivoted Schur complement.

    Returns (is_psd, rank, detail).  Correct for any symmetric matrix: at each
    step the largest diagonal entry is the pivot; a negative pivot refutes PSD,
    and a zero maximal diagonal forces the whole remaining block to vanish.
    """
    A = [[Mat[i][j] for j in range(n)] for i in range(n)]
    rank = 0
    idx = list(range(n))
    for k in range(n):
        p, best = k, A[k][k]
        for i in range(k + 1, n):
            if A[i][i].sign() > best.sign() or (
                    A[i][i].sign() == best.sign() and (A[i][i] - best).sign() > 0):
                p, best = i, A[i][i]
        if best.sign() < 0:
            return False, rank, f"negative pivot {best} at step {k}"
        if p != k:
            A[k], A[p] = A[p], A[k]
            for r in range(n):
                A[r][k], A[r][p] = A[r][p], A[r][k]
            idx[k], idx[p] = idx[p], idx[k]
        if A[k][k].is_zero():
            for i in range(k, n):
                for j in range(k, n):
                    if not A[i][j].is_zero():
                        return False, rank, "zero diagonal with nonzero off-diagonal"
            return True, rank, "psd, rank %d" % rank
        rank += 1
        d = A[k][k]
        for i in range(k + 1, n):
            f = A[i][k] / d
            if f.is_zero():
                continue
            for j in range(k + 1, n):
                A[i][j] = A[i][j] - f * A[k][j]
    return True, rank, "psd, full rank %d" % rank


def solve_exact(A, b, nrow, ncol):
    """Exact Gaussian elimination over Q(sqrt(d)).

    A is nrow x ncol, b is length nrow.  Returns (solution, free_columns) with the
    free columns set to zero, or (None, None) if the system is inconsistent.
    """
    Aug = [[A[i][j] for j in range(ncol)] + [b[i]] for i in range(nrow)]
    piv_of_col = {}
    r = 0
    for c in range(ncol):
        p = None
        for i in range(r, nrow):
            if not Aug[i][c].is_zero():
                p = i
                break
        if p is None:
            continue
        Aug[r], Aug[p] = Aug[p], Aug[r]
        d = Aug[r][c]
        Aug[r] = [x / d for x in Aug[r]]
        for i in range(nrow):
            if i != r and not Aug[i][c].is_zero():
                f = Aug[i][c]
                Aug[i] = [Aug[i][j] - f * Aug[r][j] for j in range(ncol + 1)]
        piv_of_col[c] = r
        r += 1
        if r == nrow:
            break
    for i in range(r, nrow):
        if all(Aug[i][j].is_zero() for j in range(ncol)) and not Aug[i][ncol].is_zero():
            return None, None
    zero = A[0][0] - A[0][0]
    sol = [zero for _ in range(ncol)]
    for c, rr in piv_of_col.items():
        sol[c] = Aug[rr][ncol]
    free = [c for c in range(ncol) if c not in piv_of_col]
    return sol, free
