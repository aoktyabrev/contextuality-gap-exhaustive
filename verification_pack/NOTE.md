# What this checks, and why that is enough

This package proves one statement about one graph. The graph is the eight-vertex,
ten-edge graph with graph6 code `` GCQb`o `` — the Quad-C₅ graph, edges

    0-3  0-5  1-4  1-6  2-5  2-6  2-7  3-6  3-7  4-7

and the statement is:

> **θ(Quad-C₅) is the root of x⁴ − x³ + 23x² − 155x + 158 lying in (3, 4)**,
> that is θ = 3.46784372984022410869739188177700792442892753691289881998…,
> and α = 3, so Δ = θ − α = θ − 3.

`python3 verify.py` checks it in 21 steps and prints PASS or FAIL, exiting non-zero on
FAIL. Standard library only, no installation, no network, no solver. Measured with the
network switched off: **0.7 s on Python 3.12, 0.9 s on 3.11, 1.3 s on 3.9, 1.8 s on 3.7**
(an ordinary desktop; the numbers only say that nothing here is slow).

## Why a certificate rather than a computation

θ(G) is the optimum of a semidefinite program. A numerical solver returns a decimal, and
a decimal cannot distinguish an algebraic number from a nearby rational — recovering a
minimal polynomial by integer-relation search is a guess whose confidence is not a proof.

The way around it is that an SDP brackets itself. Any feasible primal point gives a lower
bound on the optimum; any feasible dual point gives an upper bound. If a primal and a
dual point are exhibited whose objective values are the *same* algebraic number, the
optimum equals that number, and the only thing that has to be trusted is arithmetic.

So the numerics here did one job only: they proposed candidate matrices. Everything that
carries the verdict is exact. A wrong proposal cannot produce a false PASS — it can only
fail one of the checks, which is what the corruption tests below confirm.

## How ℚ(θ) is represented

θ is not written as a decimal anywhere. The field is ℚ[x]/(p) with p the quartic above,
and an element is a vector of four rationals — its coordinates over the basis
1, θ, θ², θ³. Addition is componentwise; multiplication is polynomial multiplication
followed by reduction using θ⁴ = θ³ − 23θ² + 155θ − 158; inversion is the extended
Euclidean algorithm in ℚ[x]. Every coefficient in `certificates/` is an explicit
`numerator/denominator` pair of integers. There is no floating point in the file and none
in the arithmetic.

Two things have to be true for that to be a field at all, and both are checked before
anything else:

* **p is irreducible over ℚ.** The rational root theorem is applied to every candidate,
  and every factorisation into two integer quadratics is enumerated and excluded.
* **the interval (3, 4) names exactly one root.** p(3) = −46 and p(4) = 98 differ in
  sign, so a root exists there; p′(3) = 64 > 0 and p″ = 12x² − 6x + 46 has negative
  discriminant, hence p″ > 0 everywhere, hence p′ is increasing and stays positive on
  [3, 4], hence p is strictly increasing there and the root is unique. The other real
  root, near 1.257, is excluded by the interval.

Comparing two field elements needs a sign test, and that is where an implementation is
usually tempted to evaluate in floating point. Here the sign of a non-zero element is
decided exactly: the coordinates are tested for being all zero first, and if they are
not, the element's value is bounded by rational interval arithmetic over the isolating
interval, which is bisected — with the sign of p evaluated exactly at the midpoint —
until the bounding interval no longer contains zero. That terminates for every non-zero
element, and it never leaves the rationals.

## What is checked

**The graph itself.** The graph6 string is decoded by this script, from the format
description rather than through a library, and the resulting edge set must equal the one
the certificate uses; and α = 3 is established by exhausting all 2⁸ vertex subsets. So
the object being certified is tied to the name it is given, and Δ is pinned at both ends.
graph6 encodes a labelling and not an isomorphism class, which is why this check compares
edge sets rather than strings.

**Primal, giving θ(G) ≥ θ.** The matrix X is symmetric; its trace is exactly 1; it
vanishes at every one of the ten edges; 1ᵀX1 equals θ exactly; and X is positive
semidefinite. Those are precisely the constraints of the SDP

    θ(G) = max { 1ᵀX1 : X ⪰ 0, Tr X = 1, X_ij = 0 for every edge (i,j) },

so X is feasible and its objective value is a lower bound.

**Dual, giving θ(G) ≤ θ.** The matrix B equals 1 on the diagonal and at every non-edge,
and is unconstrained on edges; θ·I − B is positive semidefinite, i.e. λ_max(B) ≤ θ. By
the dual formulation θ(G) = min{ λ_max(B) } over such B, that is an upper bound.

Both bounds are the same element of ℚ(θ), so θ(G) is equal to it.

## Why two tests of positive semidefiniteness

Positive semidefiniteness is the only step where a subtle bug could plausibly hide, so it
is established twice, by algorithms that share no code path and fail differently:

* **method A, pivoted Schur complement.** The largest diagonal entry is chosen as pivot
  at each step; a negative pivot refutes immediately, and a zero maximal diagonal forces
  the entire remaining block to vanish. This is O(n³) field operations and is the natural
  exact analogue of a Cholesky factorisation.
* **method B, every principal minor.** A symmetric matrix is positive semidefinite if and
  only if all of its principal minors are non-negative — note *all*, not merely the
  leading ones, which would be the criterion for definiteness and is not sufficient here.
  For n = 8 that is 2⁸ − 1 = 255 determinants, each computed by exact elimination.

The script requires the two to agree and reports it as a separate line. Method A is fast
but relies on pivoting being done right; method B is exhaustive and slow but has almost no
structure to get wrong. A defect that fools both is far less likely than one that fools
either.

## The boundary between "numerics proposed" and "arithmetic proved"

Everything numerical happened before this package existed: an arbitrary-precision solve
produced approximate matrix entries, and an integer-relation search proposed both the
quartic and the rational coordinates. **None of that is shipped and none of it is
trusted.** What is shipped is the result of that guessing, and `verify.py` re-derives
nothing — it only asks whether the shipped integers satisfy the definition. If the
guessing had been wrong in any way, some check would fail.

That claim was tested rather than asserted. Fifteen corrupted certificates were built —
a single coefficient shifted by 1/4108, a trace-preserving perturbation of the diagonal,
a symmetric perturbation of an off-diagonal entry, a changed constant term in the
polynomial, the isolating interval moved onto the other real root, the graph6 string
replaced by that of a different eight-vertex graph, an edge dropped, α overstated, and
others — and every one produced FAIL with a non-zero exit code. In the cases designed to leave symmetry and
trace intact, the check that caught the corruption was the positive-semidefiniteness
test, and **both** methods rejected it independently.

## What is not in this package

No graph enumeration, no nauty, no SDP solver. `graph6.txt` lists the maximizers at
other sizes so that the eight-vertex number can be seen in context, but it is a table to
read, not a claim this package proves, and nothing in `verify.py` touches it. How those
graphs were found, and the certificates for the other sizes, are in the repository named
below.

## Where this came from

This package is an extract. The full study — the exhaustive enumeration that found the
graph, the certificates for the other sizes, the preregistrations and the stage reports —
is at

    https://github.com/aoktyabrev/contextuality-gap-exhaustive

archived on Zenodo with concept DOI **10.5281/zenodo.22031808** (always the current
version) and release DOI **10.5281/zenodo.22031809** (v1.0.0). The same folder you are
reading is in that repository as `verification_pack/`, from commit `31dd5cf` onward.

Prepared 2026-08-21 by Artem Oktiabrev (ORCID 0009-0003-3626-2002,
aoktyabrev@gmail.com). Nothing in `verify.py` needs any of the above: it reads only the
files next to it.

## Files

    verify.py                              the checker; run it
    certificates/quadc5_certificate.json   the primal and dual matrices over ℚ(θ),
                                           as integer numerator/denominator pairs
    certificates/minimal_polynomial.txt    the polynomial, the isolating interval, and
                                           the argument that they name one root
    graph6.txt                             the maximizers for n = 5…10 in one table
    comparison_n8.md                       our eight-vertex ranking beside the published one
    NOTE.md                                this file
    README.md                              one page: what this is and how to run it
