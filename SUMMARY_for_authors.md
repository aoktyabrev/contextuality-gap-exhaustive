# Summary for the authors of arXiv:2605.12828

A short account of what this repository contains, written for U. Tamer,
Ö. E. Müstecaplıoğlu, A. Dizdar and Z. Gedik, whose paper this work continues.

Repository: https://github.com/aoktyabrev/contextuality-gap-exhaustive
Concept DOI: [10.5281/zenodo.22031808](https://doi.org/10.5281/zenodo.22031808) (always the
current version). Version and release DOI: *filled in when v2.0 is archived.*

## 1. Your eight-vertex result reproduces, and its value is now proved

An independent pipeline — our own graph6 codec, an independent α, three SDP solvers —
confirms Quad-C₅ (`` GCQb`o ``) as the unique maximizer over the 11 117 connected
eight-vertex graphs. The value you left open is

> **ϑ(Quad-C₅) is the root of x⁴ − x³ + 23x² − 155x + 158 in (3, 4)**,
> ϑ = 3.46784372984022410869739188177700792442892753691289881998…, so Δ = ϑ − 3.

This is proved, not fitted: an exact primal certificate bounds ϑ from below, an exact dual
bounds it from above, both in exact arithmetic over ℚ(ϑ), with positive semidefiniteness
checked twice by independent methods. The high-precision numerics only propose the matrix
entries and take no part in the verdict — which is the point, since a numerical coincidence
is exactly what your integer-relation candidate turned out to be.

The Galois group of the quartic is the full S₄, so ℚ(ϑ) has no proper subfield other than
ℚ: unlike ϑ(C₇), which lies in the real subfield of the seventh cyclotomic field and is
therefore expressible through a cosine, this value is not cyclotomic and admits no
expression of that kind.

`verification_pack/` checks all of this in about two seconds, standard library only, no
network and no solver.

## 2. The series, now to eleven vertices

| n | Δ_max | exact value | deg | maximizer | \|E\| | α |
|--:|---|---|--:|---|--:|--:|
| 5, 6 | 0.2360679775 | √5 − 2 | 2 | `DUW`, `EUZw` | 5, 10 | 2 |
| 7 | 0.3176672074 | 7cos(π/7)/(1+cos(π/7)) − 3 | 3 | `` FCp`_ `` = C₇ | 7 | 3 |
| 8 | 0.4678437298 | the quartic above | 4 | `` GCQb`o `` | 10 | 3 |
| 9 | 0.6666666667 | 2/3 | 1 | `HCRbdO{` | 15 | 3 |
| 10 | 0.7071067812 | 1/√2 | 2 | `` ICRb`yiu? `` | 20 | 3 |
| 11 | 0.7748885327… | none exists; proved interval | > 48 | `` J?`D@pgd?{? `` | 17 | 4 |

Every size is exhaustive over connected non-isomorphic graphs — 1 006 700 565 of them at
eleven vertices, 71.8 hours on seven cores, with completeness checked against `geng -c -u 11`
and, independently, against OEIS A001349.

## 3. Two things that bear directly on your conclusions

**Sparsity.** You noted that Quad-C₅ beats W with two fewer edges. Within a single size that
tendency survives but weakly: Spearman ρ(Δ, |E|) = −0.285 at n = 9 and −0.330 at n = 10
across the top 50. Along the series it does not hold monotonically — densities run 0.500,
0.667, 0.333, 0.357, 0.417, 0.444 — but the eleven-vertex maximizer is **sparser than the
ten-vertex one**, 17 edges against 20, fewer edges on more vertices. On that step your
observation holds strongly.

**The four-pentagon structure does not continue.** The nine-vertex maximizer contains twelve
induced C₅ with uneven multiplicities; the eleven-vertex one contains eleven, all edges
covered but with multiplicities {1:2, 2:3, 3:6, 4:1, 5:5}. The level "every edge in exactly
two induced C₅" — the literal Quad-C₅ structure — holds for no graph in the top 50 at either
n = 9 or n = 10. Curiously, the eleven-vertex maximizer does contain Quad-C₅ itself as an
induced subgraph, and C₇ as well, while containing neither the nine- nor the ten-vertex
optimum.

## 4. Eleven vertices has no closed form, and that is the result

ϑ of the eleven-vertex maximizer is not a root of any integer polynomial of degree ≤ 48 with
height ≤ 10⁹ (integer-relation search at 495 verified digits). It is pinned instead by a
proved rational enclosure:

    Delta_max(11) in [0.7748885327027013, 0.7748885327466875],   width 4.4e-11

with the runner-up separated below it by its own dual certificate, so uniqueness of the
maximum does not rest on comparing solver output.

This is worth framing carefully. The generic algebraic degree of a semidefinite program's
optimum is six already for 3×3 matrices — Galois group typically S₆, no expression in
radicals — and 1400 to 2100 at 6×6 (Nie, Ranestad & Sturmfels, *Math. Program.* **122**
(2010)). Their theorems are about *generic* programs with rational data and ours is
structured, so they do not apply directly; but the moral does. The surprise in this series
is not that eleven vertices resist a closed form. It is that n ≤ 10 gave degrees 1 to 4 at
all.

## 5. An open problem, in case it interests you

The problem splits by independence number: D(n, a) = max{Δ : α = a}. A maximizer on m
vertices, coned up to n vertices by adding k−1 independent vertices and one universal
vertex, lands in layer a_m + (n−m) − 1 with Δ **exactly** unchanged — α and ϑ shift by the
same integer. The ingredients are classical (Knuth's (18.2) and (19.2), after Lovász).

So D(n, a) ≥ Δ_max(m) is exact. What is *not* proved is that nothing in the layer exceeds
it. Measured on n = 9 and n = 10, the upper layers a ≥ 5 contain nothing of their own at
all: their maxima are smaller sizes' values to the letter, exactly √5 − 2, exactly 2/3,
exactly the cubic root.

> **The open question: prove that for a ≥ a\* every graph in the layer either is such a
> cone, or has Δ no larger than the transfer.** Equivalently: find an upper bound on ϑ(G)
> in terms of n and α(G), tight in the regime where α is large relative to n.

It would turn a measured 14 % saving into a theoretical reduction of the search space —
and for twelve vertices, where a full sweep is about 490 days, it is the only route to
saying anything. We have no approach to it. Details, and a literature check that found no
off-the-shelf reduction, are in [`OPEN_PROBLEM.md`](OPEN_PROBLEM.md).

## 6. What is proved and what is not, overall

- **Proved:** every exact value in the table, by primal–dual certificates; the eleven-vertex
  enclosure and its separation from second place; that the sandwich filter is sound, which
  settles 89.98 % of the eleven-vertex space by argument rather than measurement.
- **Not proved:** that no other graph among the remaining ~10⁸ at eleven vertices is higher.
  That rests on the sweep's numerics — SCS at eps = 10⁻⁸, top 1000 re-solved on CLARABEL,
  largest disagreement 9.39·10⁻⁸.

Preregistrations for every stage were sealed by SHA-256 before that stage ran;
`bash scripts/verify_seals.sh` checks the ordering rather than asking you to take it on
trust. Across the campaign 49 of 66 sealed predictions hit. The eleven-vertex stage scored
1 of 10, and its single hit is recorded as a coincidence: the interval was built by
extrapolating one layer and the observed value arrived from another.

For full disclosure: this work was carried out with an AI assistant — specification and
predictions formulated in dialogue, computation and checks performed by it. The certificates
are machine-checkable by anyone, independently of who produced them.

Artem Oktiabrev · ORCID [0009-0003-3626-2002](https://orcid.org/0009-0003-3626-2002) ·
aoktyabrev@gmail.com
