# The eight-vertex ranking, ours beside yours

## What was compared

Your `data/all_n8_results.csv` — all 11 117 connected graphs on eight vertices, with
α, ϑ and Δ, from the repository at

> https://github.com/ugurtamerphys/quad-c5-contextuality

and the identical copy in the Zenodo archive `10.5281/zenodo.20465134` (the six data and
code files match file-for-file between the two), downloaded 2026-08-19,

against a table computed from scratch in
https://github.com/aoktyabrev/contextuality-gap-exhaustive
(doi:10.5281/zenodo.22031808): the graphs generated with nauty's `geng`, α
by exact search, ϑ by SDP at `eps = 1e-8`, with no input from your files at any step.
Both tables cover the same 11 117 graphs, identified by graph6 string.

## Agreement on the values

Over all 11 117 graphs, the largest discrepancy in Δ is

    max |Δ_ours − Δ_yours| = 1.06e-07

which is at the level of both solvers' own tolerance and is what a comparison of two
independent numerical solves at that accuracy is expected to give. No graph differs by
more than 1e-06, and none differs in α.

## Agreement on the ranking

The first three are the same graphs in the same order:

| rank | graph6 | Δ (ours) | Δ (yours) |
|---:|---|---:|---:|
| 1 | `` GCQb`o `` | 0.46784374 | 0.46784373 |
| 2 | `` GCR`r_ ``  | 0.43844718 | 0.43844718 |
| 3 | `` GCrb`o ``  | 0.41421356 | 0.41421356 |

Below that the two lists permute, and the reason is ties rather than disagreement.
Δ takes only 15 distinct values among the top 50, and several of the blocks are wide:

| ranks | Δ | how many graphs share it |
|---|---:|---:|
| 4–6 | 0.37228133 | 3 |
| 8–9 | 0.33804446 | 2 |
| 13–21 | 0.31766722 | 9 |
| 23–25 | 0.30169434 | 3 |
| 28–50 | 0.23606798 | 23 (of 377 in total) |

Within a block the order is whatever the sort happened to do, and it is not a property of
the data. The value shared by ranks 13–21, incidentally, is the seven-vertex maximum
ϑ(C₇) − 3 reappearing on eight vertices.

Cutting at a tie-block boundary removes the effect. Taking the top *k* as a **set**, the
two rankings are identical at **every** k that does not split a block, up to the last
such k before the large final block:

    k = 1, 2, 3, 6, 7, 9, 10, 11, 12, 21, 22, 25, 26, 27

(k = 8 and k = 24 also happen to agree, by coincidence of sort order inside a block.)
The k at which they first differ is k = 4, which splits the 4–6 block.

## The top-50 cut, specifically

At k = 50 the two sets differ in 38 of 50 members, which looks alarming and is not.
Every one of those 38 graphs has

    Δ = 0.2360679775… = √5 − 2,

and at n = 8 there are **377** connected graphs whose Δ is numerically indistinguishable
from √5 − 2. The 50-graph cut lands 23 graphs deep into a block of 377 equal values, so
which 23 appear is decided by sort order, not by Δ. Your CSV prints Δ to 8 decimals, at
which all 377 are literally the same number; ours carries more digits, and those extra
digits are solver noise at the 1e-8 level, not signal. Neither list is more correct: the
"top 50" is simply not well defined at n = 8.

If a stable top-k is wanted, k = 27 is the natural cut — it is the last rank before the
√5 − 2 block begins, and the two lists agree there exactly.

## Summary

| question | answer |
|---|---|
| same 11 117 graphs? | yes |
| same α everywhere? | yes |
| largest Δ discrepancy | 1.06e-07, over all 11 117 |
| same maximizer? | yes, `` GCQb`o ``, by graph6 string |
| same top 3? | yes, same order |
| same top-k set, k ≤ 27 | yes, at every k that does not split a tie block |
| same top-50 set? | no — 38 of 50 differ, all inside one tie block of 377 |

The maximizer, its value, and the top of the list reproduce. The disagreement is confined
to the interior of a tie and carries no information about either computation.
