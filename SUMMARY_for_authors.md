# Exact contextuality gaps for graphs on 5–11 vertices

Δ(G) = ϑ(G) − α(G), maximised over all connected non-isomorphic graphs.
Continuation of U. Tamer, Ö. E. Müstecaplıoğlu, A. Dizdar & Z. Gedik,
arXiv:2605.12828.

Repository: https://github.com/aoktyabrev/contextuality-gap-exhaustive
Archive: https://doi.org/10.5281/zenodo.22031808 (concept DOI, always the current version)
This text describes v2.1, archived as https://doi.org/10.5281/zenodo.22110971

Every claim below is marked **[proved]** — exact arithmetic with verified
primal/dual certificates, no floating-point in the verdict — or **[numerical]**.

---

## 1. The series

| n | Δ_max | closed form | field degree | status |
|---|---|---|---|---|
| 5, 6 | 0.2360680 | √5 − 2 | 2 | **[proved]** |
| 7 | 0.3176672 | root of y³ + 16y² + 20y − 8 | 3 | **[proved]** |
| 8 | 0.4678437 | root of y⁴ + 11y³ + 68y² + 64y − 46 | 4 (S₄) | **[proved]** |
| 9 | 0.6666667 | 2/3 | 1 | **[proved]** |
| 10 | 0.7071068 | √2/2 | 2 | **[proved]** |
| 11 | 0.7748885 | none found | none within deg ≤ 48 | see §3 |

Equivalently for n = 8, ϑ is the root in (3,4) of x⁴ − x³ + 23x² − 155x + 158.
This is the value your integer-relation search reported as a false positive;
it lies inside the search space you specified (degree ≤ 4, coefficients well
under 10⁶), so the obstacle was the precision of ϑ, exactly as you diagnosed.

## 2. n = 11

Exhaustive over all 1,006,700,565 connected non-isomorphic graphs; 100,891,478
reached the SDP (10.02 %); 71.8 h. Maximiser `` J?`D@pgd?{? ``, 17 edges, α = 4,
girth 4, no triangles, |Aut| = 2, eleven induced C₅.

- Δ_max(11) ∈ [0.7748885327027013, 0.7748885327466875] **[proved]**,
  bounds as explicit fractions, width 4.4·10⁻¹¹.
- Runner-up ≤ 0.7546860448577810 **[proved]** — the maximum is separated,
  not merely ranked numerically. Gap 0.0202.
- That no other graph exceeds it **[numerical]**, resting on the sweep.
  89.98 % of the space is closed by a strict argument (χ(Ḡ) = α ⇒ Δ = 0);
  the numerical part covers 10.02 %.

The graph count was checked twice and independently: against `geng -c -u 11`,
and against OEIS A001349, which also matches our counts at n = 8, 9 and 10.

## 3. No closed form at n = 11 — and why the earlier ones are the surprise

PSLQ at 495 verified digits, degrees 2…48, zero candidates; height bounds from 10¹⁵⁸
(degree 2) through 10⁹⁵ (degree 4) down to 10⁹ (degree 48). **[proved as a negative
bound]** Note what this does and does not say: a relation of degree below 48 whose
coefficients exceed those bounds is *not* excluded, and no computation at that
precision could exclude it.

Nie, Ranestad & Sturmfels (*The Algebraic Degree of Semidefinite Programming*,
Math. Program. **122** (2010)) give the context: for 3×3 matrices the typical
algebraic degree of the SDP optimum is already 6 with Galois group S₆ and no
expression in radicals; for 6×6 it runs to 1400–2100. Against that, degrees
1–4 for n ≤ 10 are the anomaly, not the break at n = 11. Their results concern
generic SDP and do not cover ours directly (ours is structured: zeros on edges,
unit trace), so the low degrees need a structural explanation. We consider this
the most interesting question the series raises.

**Since then we have measured it.** Algebraic degrees for 1286 graphs at
n = 5…11, in three samples per size: the top 100 by Δ, a uniform random sample
of the same size among graphs with Δ > 0, and a Δ = 0 control. Found 1137,
not found 122, declined by the instrument 27. 97.4 % of those found are degree
1–4; degree 5 was searched for and never occurred.

The direction is the opposite of what we had assumed. **Extremal graphs are the
algebraically hardest part of the landscape, not the easiest**: the fraction
with no closed form runs 1 % → 61 % across n = 8…11 in the top 100, against
0 % → 14 % in the random sample, the same sign on all four sizes. At n = 11 the
cut by layer is sharp — in the top 100 the graphs with α = 4 are out of reach
45 of 47 (96 %), against 8 of 41 (20 %) in the random sample at the same size
and layer.

**The sealed threshold for that hypothesis was not met and we are not lowering
it**: it required the gap to reach 0.25 on three of four sizes and it does so on
one. Recorded as *not confirmed*. All three sealed hypotheses of the stage failed
their criteria, including the one that degree tracks the automorphism group —
|ρ| < 0.20 on three sizes of four, signs inconsistent. Symmetry explains nothing
here. Edge count does, but only inside the top (ρ = −0.30…−0.76 there, nothing at
all in the random sample), and |E|, α and the layer n − α are nearly one quantity,
separating on 5 cells of 13.

So the reading of §3 above stands, but sharpened: the six closed forms up to
n = 10 were not found in easy country and lost when the ground got hard. They
were found six times running in the hardest country in this landscape.

We found no prior measurement of the algebraic degree of ϑ over a class of
graphs, and no work relating it to the automorphism group. That is the result of
a search on 2026-08-26, not a claim about the literature.

**One methodological point we would flag even if nothing else here interests
you.** The rule we had been using to count trustworthy digits — matching prefix
of a run at precision *p* and one at 2*p*, minus five — measures the *stability*
of the refinement, not its correctness. On a degenerate optimum Gauss–Newton
settles on a stable wrong point and every precision reproduces it: for one
eight-vertex graph the values at 960, 1920 and 3840 digits agree with each other
to 945 digits while agreeing with the truth ϑ = α = 3 to 359. Feeding an
integer-relation search those 940 claimed digits returns not a blank but
(x − 3)³ — an integer polynomial of degree 3 where the truth is degree 1. This is the same mechanism as the false positive you reported in your own paper, and we walked into it
in our own instrument; it took three restarts and a control sample with exactly
known answers to see. The fix is to require the residual to fall with precision
before believing any digit count.

## 4. Inheritance — and a correction to what I told you before

For a maximiser G\* on m vertices with α = a_m, the cone
C_k(G\*) = {v} ∨ (G\* ⊔ K̄_{k−1}) is connected, shifts both α and ϑ by exactly k − 1, and
therefore carries Δ unchanged. Hence **[proved]**

  D(n, a) ≥ Δ_max(m)  for a = a_m + (n − m) − 1.

Additivity of ϑ under disjoint union and join is classical (Knuth (18.2) and (19.2), after
Lovász); the application is what was new here. **That much still stands.**

**What does not stand is what I wrote to you last time about it.** I said the upper layers
generate nothing of their own, so they need not be swept — 8.78 % of the sweep at n = 9
and 14.19 % at n = 10 — and I offered a sealed n = 12 prediction as a ready check. The
equality is **false**, and we refuted it ourselves:

> `` L@JC?_ASKAGPBH `` on 13 vertices, α = 5, 19 edges: Δ ≥ 45375481648/55555555557
> = 0.816758669642764, against a transfer bound T(13,5) ≤ 12398216523947/16000000000000
> = 0.7748885327466875. Strictly greater by 0.0419, both bounds from exact primal–dual
> certificates, compared as fractions. **[proved]**

So upper layers cannot be skipped as a matter of method. The two percentages remain
correct for the two sizes where every layer was actually computed, and they do not carry
forward. The sealed n = 12 prediction loses one of its four rows. Please treat the
inheritance paragraph of my previous message as withdrawn to that extent.

**The replacement rule is a candidate, not a result.** a ≥ max(5, n − 6) fits all sixteen
known points — but the 5 is decided by nine of them and the 6 by exactly one, the
counterexample itself. Worse, the data admit exactly two rules: d = 6 and d = 7. A
directed search at ten times budget failed to separate them, and the failure leans towards
d = 7, i.e. against our own formula. Details in `REPORT_STAGE8BIS.md`.

One thing there that may interest you regardless of how it resolves: the floor at 5 has an
arithmetic candidate. The odd cycle C_{2a+1} lives in layer a at n = 2a+1 and its gap
rises monotonically to a limit of exactly ½, while transfer bounds have no such ceiling.
The cycle beats the transfer at a = 2, 3, 4 and loses from a = 5 onward — and at a = 4 the
layer maximiser *is* C₉, to the digit.

## 5. Points bearing directly on your paper

- **Quad-C₅ reappears.** The n = 11 maximiser contains Quad-C₅ and C₇ as
  induced subgraphs — while containing neither the n = 9 nor the n = 10
  maximiser. Your graph skips two sizes and returns.
- **Sparsity holds up.** The n = 11 maximiser has 17 edges against 20 at
  n = 10 — fewer edges on more vertices, density 0.444 → 0.309. Within a
  fixed n the tendency is weak (Spearman −0.285 at n = 9); along the series
  of maximisers it is pronounced.
- **The top-50 tail.** Ranks 28 and below at n = 8 lie inside a block of 377
  graphs whose Δ is indistinguishable from √5 − 2; at eight printed decimals
  they are one number, so ordering within the block is arbitrary for anyone.
  Taken as sets the lists agree at every cut that does not split the block;
  k = 27 is the natural one. Across all 11,117 graphs the largest discrepancy
  in Δ is 1.06·10⁻⁷ and α agrees everywhere.

## 6. Predictions: the honest count

Ten predictions bore on the n = 11 sweep. One held.

Eight were sealed before it began — `PREDICTION_N11.md` (commit 9b833a2,
2026-08-20 18:09 UTC) and `PREREGISTRATION_STAGE6.md` (7776955, 18:44 UTC),
both ahead of the first part of the sweep at 18:53 UTC. Two more were sealed
mid-sweep at 40 % coverage, before the leader had changed
(`PREDICTION_EDGES.md`, 0cb06ad, 2026-08-21) — and both failed, which is
itself the argument for sealing them when we did rather than at the end.

The one that held — Δ_max(11) ∈ [0.7475, 0.9059] — was a coincidence: the
interval was built for layer a = 3, and the value arrived from layer a = 4,
whose own predicted interval was overshot. The layer-extrapolation method was
refuted by exactly the mechanism its own preregistration named in advance as
its failure mode.

Across the whole campaign the count is 58 of 85. Stage 9 scored 4 of 6, and both misses were the same guess: that the top of the landscape sat on a
plateau of rational values while the middle was harder. It is the other way
round.

Preregistrations are in the repository, one commit each, never edited;
`scripts/verify_seals.sh` checks byte-identity and commit order.

---

For full disclosure: this work was carried out with an AI assistant —
specification and predictions formulated in dialogue, computation and checks
performed by it; this is stated in the repository as well. The certificates
are machine-checkable by anyone, independently of who produced them.

Artem Oktiabrev · ORCID [0009-0003-3626-2002](https://orcid.org/0009-0003-3626-2002) ·
aoktyabrev@gmail.com
