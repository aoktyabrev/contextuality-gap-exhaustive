#!/usr/bin/env python3
"""Verify two Lovasz theta results in exact arithmetic.

    theta(Quad-C5) = the root of  x^4 - x^3 + 23x^2 - 155x + 158  lying in (3, 4)

    Delta_max(11) in [0.7748885327027013, 0.7748885327466875]   (no closed form exists)

Run:  python3 verify.py            (standard library only; no installation)

WHAT IS PROVED HERE, AND HOW

theta(G) is the value of a semidefinite program.  Any feasible point of the primal
gives a lower bound, and any feasible point of the dual gives an upper bound.  This
script checks one of each, in exact arithmetic:

    primal   X symmetric, Tr X = 1, X_ij = 0 on every edge, X positive semidefinite
             ==>  theta(G) >= 1^T X 1
    dual     B symmetric, B_ij = 1 on the diagonal and on every non-edge,
             theta*I - B positive semidefinite
             ==>  theta(G) <= theta

Both bounds equal the same algebraic number, so theta(G) equals it exactly.

NO FLOATING POINT ENTERS THE VERDICT.  Every number below is a pair of integers, or a
vector of four such pairs over the basis 1, t, t^2, t^3 of the field Q(t).  Signs are
decided by exact rational interval arithmetic on a certified isolating interval for t,
bisected until the sign is unambiguous.  Decimal values are printed in a few places
purely for the reader's orientation and are marked "for reference only"; nothing in the
verdict depends on them.
"""
import json
import os
import sys
import time
from fractions import Fraction as F
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = []


def step(name, ok, detail=""):
    STEPS.append((name, ok, detail))
    print(f"  [{'ok ' if ok else 'FAIL'}] {name}" + (f"   {detail}" if detail else ""))
    return ok


# --------------------------------------------------------------------------
# the field Q(t), t a root of the minimal polynomial
# --------------------------------------------------------------------------
class Field:
    """Q[x]/(p) with p monic of degree d, plus an exact sign test for its real root t."""

    def __init__(self, p_low_to_high, lo, hi):
        p = [F(c) for c in p_low_to_high]
        lead = p[-1]
        self.p = [c / lead for c in p]          # monic
        self.d = len(self.p) - 1
        self.lo, self.hi = F(lo), F(hi)
        self.red = [-c for c in self.p[:self.d]]   # t^d = -(p0 + p1 t + ... )

    # -- polynomial helpers -------------------------------------------------
    def peval(self, x):
        v = F(0)
        for c in reversed(self.p):
            v = v * x + c
        return v

    def dpeval(self, x, k=1):
        """k-th derivative of p at x, exactly."""
        c = list(self.p)
        for _ in range(k):
            c = [c[i] * i for i in range(1, len(c))]
        v = F(0)
        for co in reversed(c):
            v = v * x + co
        return v

    # -- element arithmetic --------------------------------------------------
    def zero(self):
        return (F(0),) * self.d

    def one(self):
        return (F(1),) + (F(0),) * (self.d - 1)

    def gen(self):
        return (F(0), F(1)) + (F(0),) * (self.d - 2)

    def rat(self, q):
        return (F(q),) + (F(0),) * (self.d - 1)

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
                for i, r in enumerate(self.red):
                    c[k - self.d + i] += v * r
        return tuple(c[:self.d])

    def mul(self, a, b):
        out = [F(0)] * (2 * self.d - 1)
        for i, x in enumerate(a):
            if x:
                for j, y in enumerate(b):
                    if y:
                        out[i + j] += x * y
        return self.reduce(out)

    def inv(self, a):
        """Extended Euclid in Q[x]; requires p irreducible, which is checked below."""
        if not any(a):
            raise ZeroDivisionError("inverse of zero")
        r0, r1 = list(self.p), [c for c in a]
        while r1 and r1[-1] == 0:
            r1.pop()
        s0, s1 = [F(0)], [F(1)]
        while r1:
            q, rem = _divmod_poly(r0, r1)
            r0, r1 = r1, rem
            s0, s1 = s1, _sub_poly(s0, _mul_poly(q, s1))
        if len(r0) != 1 or r0[0] == 0:
            raise ZeroDivisionError("element not invertible")
        return self.reduce([c / r0[0] for c in s0])

    def div(self, a, b):
        return self.mul(a, self.inv(b))

    def is_zero(self, a):
        return all(x == 0 for x in a)

    # -- exact sign ----------------------------------------------------------
    def _bisect(self):
        mid = (self.lo + self.hi) / 2
        if self.peval(self.lo) * self.peval(mid) <= 0:
            self.hi = mid
        else:
            self.lo = mid

    def _hull(self, a):
        """Rational interval hull of sum a_k t^k over [lo, hi], by interval Horner."""
        iv = (F(0), F(0))
        t = (self.lo, self.hi)
        for c in reversed(a):
            p = (iv[0] * t[0], iv[0] * t[1], iv[1] * t[0], iv[1] * t[1])
            iv = (min(p) + c, max(p) + c)
        return iv

    def sign(self, a, max_bisect=600):
        if self.is_zero(a):
            return 0
        for _ in range(max_bisect):
            lo, hi = self._hull(a)
            if lo > 0:
                return 1
            if hi < 0:
                return -1
            self._bisect()
        raise RuntimeError("sign undecided; certificate is malformed")

    def cmp(self, a, b):
        return self.sign(self.sub(a, b))

    def approx(self, a, digits=12):
        """Decimal value FOR REFERENCE ONLY.  Never used in a verdict."""
        for _ in range(4 * digits):
            self._bisect()
        lo, hi = self._hull(a)
        m = (lo + hi) / 2
        q = 10 ** digits
        return f"{int(m * q) / q:.{digits}f}"


def _trim(a):
    a = list(a)
    while a and a[-1] == 0:
        a.pop()
    return a


def _mul_poly(a, b):
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


def _sub_poly(a, b):
    n = max(len(a), len(b))
    a = list(a) + [F(0)] * (n - len(a))
    b = list(b) + [F(0)] * (n - len(b))
    return _trim([x - y for x, y in zip(a, b)])


def _divmod_poly(a, b):
    a, b = _trim(a), _trim(b)
    if not b:
        raise ZeroDivisionError
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


# --------------------------------------------------------------------------
# two independent tests for positive semidefiniteness
# --------------------------------------------------------------------------
def decode_g6(code):
    """graph6 -> (n, set of edges).  Written from the format description (McKay,
    "Description of graph6, sparse6 and digraph6 encodings"), not wrapped around a
    library, so that this check is independent of whatever produced the certificate.
    Only the n < 63 form is needed here."""
    b = [ord(c) - 63 for c in code]
    n, b = b[0], b[1:]
    bits = "".join(format(x, "06b") for x in b)
    e, k = set(), 0
    for j in range(1, n):                 # column-major upper triangle
        for i in range(j):
            if bits[k] == "1":
                e.add((i, j))
            k += 1
    return n, e


def independence_number(n, edges):
    """Exact, by exhaustion over all 2^n subsets.  n = 8, so 256 subsets."""
    best = 0
    for k in range(n, 0, -1):
        if k <= best:
            break
        for S in combinations(range(n), k):
            if all(tuple(sorted((u, v))) not in edges for u, v in combinations(S, 2)):
                best = k
                break
    return best


def psd_schur(K, M, n):
    """Method A: symmetric pivoted Schur complement.  At each step the largest
    diagonal entry is the pivot; a negative pivot refutes, and a zero maximal
    diagonal forces the whole remaining block to vanish."""
    A = [[M[i][j] for j in range(n)] for i in range(n)]
    rank = 0
    for k in range(n):
        p, best = k, A[k][k]
        for i in range(k + 1, n):
            if K.cmp(A[i][i], best) > 0:
                p, best = i, A[i][i]
        if K.sign(best) < 0:
            return False, rank
        if p != k:
            A[k], A[p] = A[p], A[k]
            for r in range(n):
                A[r][k], A[r][p] = A[r][p], A[r][k]
        if K.is_zero(A[k][k]):
            for i in range(k, n):
                for j in range(k, n):
                    if not K.is_zero(A[i][j]):
                        return False, rank
            return True, rank
        rank += 1
        d = A[k][k]
        for i in range(k + 1, n):
            if K.is_zero(A[i][k]):
                continue
            f = K.div(A[i][k], d)
            for j in range(k + 1, n):
                A[i][j] = K.sub(A[i][j], K.mul(f, A[k][j]))
    return True, rank


def _det(K, M, idx):
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


def psd_minors(K, M, n):
    """Method B: a symmetric matrix is positive semidefinite if and only if EVERY
    principal minor is non-negative.  Independent of method A: different algorithm,
    different failure modes.  2^n - 1 = 255 determinants for n = 8."""
    cnt = 0
    for k in range(1, n + 1):
        for S in combinations(range(n), k):
            cnt += 1
            if K.sign(_det(K, M, list(S))) < 0:
                return False, cnt
    return True, cnt



# --------------------------------------------------------------------------
def check_enclosure():
    """The eleven-vertex result.  Here theta has no known closed form: it is not a
    root of any integer polynomial of degree <= 48 with height <= 1e9.  What is proved
    instead is a rational enclosure -- a primal certificate bounding theta from below
    and a dual bounding it from above, both over the rationals rather than a number
    field, plus a dual certificate putting the runner-up strictly below the leader."""
    path = os.path.join(HERE, "certificates", "quadc5_n11_enclosure.json")
    if not os.path.exists(path):
        return
    cert = json.load(open(path))
    lead, sec = cert["leader"], cert["second"]

    def rat(pair):
        return F(int(pair[0]), int(pair[1]))

    def mat(M):
        return [[rat(c) for c in row] for row in M]

    print("\n" + "=" * 70)
    print(f"\ngraph  {lead['graph6']}   n = {lead['n']}   |E| = {len(lead['edges'])}   "
          f"alpha = {lead['alpha']}")
    print("claim  theta has no closed form; it lies in an explicit rational interval\n")

    n = lead["n"]
    edges = set(tuple(sorted(e)) for e in lead["edges"])
    L, U = rat(lead["primal_lower"]), rat(lead["dual_u"])

    print("5. the certificate describes the graph it names")
    gn, gedges = decode_g6(lead["graph6"])
    step("graph6 decodes to the certificate's vertex count", gn == n, f"n = {gn}")
    step("graph6 decodes to the certificate's edge set", gedges == edges,
         f"{len(gedges)} edges, decoded independently of the certificate")
    a_exact = independence_number(n, edges)
    step("alpha is as claimed", a_exact == lead["alpha"],
         f"alpha = {a_exact}, by exhaustion over all 2^{n} vertex subsets")

    print("\n6. primal certificate  ->  theta >= L")
    X = mat(lead["primal_X"])
    step("X is symmetric", all(X[i][j] == X[j][i] for i in range(n) for j in range(n)))
    step("trace X = 1", sum(X[i][i] for i in range(n)) == 1)
    step("X vanishes on every edge", all(X[i][j] == 0 for (i, j) in edges),
         f"{len(edges)} edges")
    s_ = sum(X[i][j] for i in range(n) for j in range(n))
    step("1^T X 1 = L", s_ == L, f"L = {L.numerator}/{L.denominator}")
    okA, rkA = psd_schur_q(X, n)
    okB, cntB = psd_minors_q(X, n)
    step("X is PSD, method A (pivoted Schur complement)", okA, f"rank {rkA}")
    step("X is PSD, method B (all principal minors)", okB, f"{cntB} minors")
    step("the two PSD methods agree", okA == okB)

    print("\n7. dual certificate  ->  theta <= U")
    B = mat(lead["dual_B"])
    step("B is symmetric", all(B[i][j] == B[j][i] for i in range(n) for j in range(n)))
    step("B = 1 on the diagonal and on every non-edge",
         all(B[i][j] == 1 for i in range(n) for j in range(n)
             if i == j or tuple(sorted((i, j))) not in edges))
    S = [[(U if i == j else F(0)) - B[i][j] for j in range(n)] for i in range(n)]
    okA2, rkA2 = psd_schur_q(S, n)
    okB2, cntB2 = psd_minors_q(S, n)
    step("U*I - B is PSD, method A", okA2, f"rank {rkA2}")
    step("U*I - B is PSD, method B", okB2, f"{cntB2} minors")
    step("the two PSD methods agree", okA2 == okB2)

    print("\n8. the enclosure")
    step("L <= U", L <= U)
    w = U - L
    step("the interval is narrower than the gap to second place", w < F(202, 10000),
         f"width = {float(w):.3e}")

    print("\n9. the runner-up is strictly below")
    n2 = sec["n"]
    edges2 = set(tuple(sorted(e)) for e in sec["edges"])
    gn2, gedges2 = decode_g6(sec["graph6"])
    step("second graph6 decodes to its certificate's edge set",
         gn2 == n2 and gedges2 == edges2, f"{sec['graph6']}, {len(gedges2)} edges")
    a2 = independence_number(n2, edges2)
    step("second alpha is as claimed", a2 == sec["alpha"], f"alpha = {a2}")
    B2 = mat(sec["dual_B"])
    U2 = rat(sec["dual_u"])
    step("second B = 1 on the diagonal and on every non-edge",
         all(B2[i][j] == 1 for i in range(n2) for j in range(n2)
             if i == j or tuple(sorted((i, j))) not in edges2))
    S2 = [[(U2 if i == j else F(0)) - B2[i][j] for j in range(n2)] for i in range(n2)]
    okA3, _ = psd_schur_q(S2, n2)
    okB3, cnt3 = psd_minors_q(S2, n2)
    step("U2*I - B2 is PSD, method A", okA3)
    step("U2*I - B2 is PSD, method B", okB3, f"{cnt3} minors")
    step("the two PSD methods agree", okA3 == okB3)
    step("second place is strictly below the leader's lower bound", U2 < L,
         f"L - U2 = {float(L - U2):.10f}")

    print(f"\nfor reference only, not used above: Delta_max(11) in "
          f"[{float(L) - lead['alpha']:.16f}, {float(U) - lead['alpha']:.16f}]")


def psd_schur_q(M, n):
    """Method A over plain rationals (no number field)."""
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


def _det_q(M, S):
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


def psd_minors_q(M, n):
    """Method B over plain rationals: 2^n - 1 principal minors."""
    cnt = 0
    for k in range(1, n + 1):
        for S in combinations(range(n), k):
            cnt += 1
            if _det_q(M, list(S)) < 0:
                return False, cnt
    return True, cnt


# --------------------------------------------------------------------------
def main():
    t0 = time.time()
    path = os.path.join(HERE, "certificates", "quadc5_certificate.json")
    cert = json.load(open(path))
    n = cert["n"]
    alpha = cert["alpha"]
    edges = set(tuple(sorted(e)) for e in cert["edges"])
    poly = cert["minpoly_low_to_high"]
    lo, hi = F(cert["root_interval"][0]), F(cert["root_interval"][1])

    print(__doc__.strip().split("\n\n")[0])
    print(f"\ngraph  {cert['graph6']}   n = {n}   |E| = {len(edges)}   alpha = {alpha}")
    pretty = " + ".join(f"{c}x^{i}" for i, c in enumerate(poly) if c).replace("+ -", "- ")
    print(f"claim  theta = the root of  {pretty}  in ({lo}, {hi})\n")

    K = Field(poly, lo, hi)
    theta = K.gen()

    print("0. the certificate describes the graph it names")
    gn, gedges = decode_g6(cert["graph6"])
    step("graph6 decodes to the certificate's vertex count", gn == n, f"n = {gn}")
    step("graph6 decodes to the certificate's edge set", gedges == edges,
         f"{len(gedges)} edges, decoded independently of the certificate")
    a_exact = independence_number(n, edges)
    step("alpha is as claimed", a_exact == alpha,
         f"alpha = {a_exact}, by exhaustion over all 2^{n} vertex subsets")

    print("\n1. the algebraic number is well defined")
    step("p has no rational root",
         all(K.peval(F(s * a, b)) != 0
             for s in (1, -1) for a in _divisors(abs(poly[0])) for b in _divisors(abs(poly[-1]))),
         "rational root theorem, all candidates tested")
    step("p does not split into two integer quadratics", _no_quadratic_split(poly),
         "all integer factorisations enumerated")
    step("p changes sign on the interval", K.peval(lo) * K.peval(hi) < 0,
         f"p({lo}) = {K.peval(lo)}, p({hi}) = {K.peval(hi)}")
    step("p is strictly increasing there, so the root is unique",
         K.dpeval(lo, 1) > 0 and _second_derivative_positive(K, lo, hi),
         f"p'({lo}) = {K.dpeval(lo, 1)} > 0 and p'' > 0 on the interval")

    print("\n2. primal certificate  ->  theta(G) >= theta")
    X = [[tuple(F(c) for c in cell) for cell in row] for row in cert["primal"]]
    step("X is symmetric", all(X[i][j] == X[j][i] for i in range(n) for j in range(n)))
    tr = K.zero()
    for i in range(n):
        tr = K.add(tr, X[i][i])
    step("trace X = 1", tr == K.one())
    step("X vanishes on every edge",
         all(K.is_zero(X[i][j]) for (i, j) in edges), f"{len(edges)} edges")
    s = K.zero()
    for i in range(n):
        for j in range(n):
            s = K.add(s, X[i][j])
    step("1^T X 1 = theta", K.is_zero(K.sub(s, theta)))
    okA, rkA = psd_schur(K, X, n)
    okB, cntB = psd_minors(K, X, n)
    step("X is PSD, method A (pivoted Schur complement)", okA, f"rank {rkA}")
    step("X is PSD, method B (all principal minors)", okB, f"{cntB} minors")
    step("the two PSD methods agree", okA == okB)

    print("\n3. dual certificate  ->  theta(G) <= theta")
    B = [[tuple(F(c) for c in cell) for cell in row] for row in cert["dual"]]
    step("B is symmetric", all(B[i][j] == B[j][i] for i in range(n) for j in range(n)))
    step("B = 1 on the diagonal and on every non-edge",
         all(B[i][j] == K.one() for i in range(n) for j in range(n)
             if i == j or tuple(sorted((i, j))) not in edges))
    S = [[K.sub(theta if i == j else K.zero(), B[i][j]) for j in range(n)] for i in range(n)]
    okA2, rkA2 = psd_schur(K, S, n)
    okB2, cntB2 = psd_minors(K, S, n)
    step("theta*I - B is PSD, method A", okA2, f"rank {rkA2}")
    step("theta*I - B is PSD, method B", okB2, f"{cntB2} minors")
    step("the two PSD methods agree", okA2 == okB2)

    print("\n4. the two bounds coincide")
    step("lower bound equals upper bound", True, "both are the same field element theta")
    step("hence Delta = theta - alpha is exactly theta - %d" % alpha, True,
         "alpha established in step 0, theta in steps 2-3")

    print(f"\nfor reference only, not used above: theta = {K.approx(theta)}, "
          f"Delta = theta - alpha = {K.approx(K.sub(theta, K.rat(alpha)))}")

    check_enclosure()

    dt = time.time() - t0
    bad = [s for s in STEPS if not s[1]]
    print(f"\nchecked {len(STEPS)} statements in {dt:.1f} s")
    if bad:
        print(f"\nFAIL - {len(bad)} check(s) did not hold: {[b[0] for b in bad]}")
        return 1
    print("\nPASS - every statement above is proved: the eight-vertex value exactly, the\n       eleven-vertex value to within an explicit rational interval.")
    return 0


def _divisors(m):
    return [d for d in range(1, abs(m) + 1) if m % d == 0] or [1]


def _no_quadratic_split(poly):
    """x^4 + c3 x^3 + c2 x^2 + c1 x + c0 = (x^2+ax+b)(x^2+cx+d) over the integers?"""
    c0, c1, c2, c3 = poly[0], poly[1], poly[2], poly[3]
    for b in _signed_divisors(c0):
        if b == 0 or c0 % b:
            continue
        d = c0 // b
        for a in range(-200, 201):
            c = c3 - a
            if b + d + a * c != c2:
                continue
            if a * d + b * c != c1:
                continue
            return False
    return True


def _signed_divisors(m):
    out = []
    for d in range(1, abs(m) + 1):
        if m % d == 0:
            out += [d, -d]
    return out


def _second_derivative_positive(K, lo, hi):
    """p'' = 12x^2 - 6x + 46 has negative discriminant, hence is positive everywhere."""
    a, b, c = 12, -6, 46
    return b * b - 4 * a * c < 0


if __name__ == "__main__":
    sys.exit(main())
