# Exact contextuality gaps for graphs up to eleven vertices

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22031808.svg)](https://doi.org/10.5281/zenodo.22031808)

Every connected graph on up to **eleven** vertices has been enumerated — 1 006 700 565 of
them at the last size — the contextuality gap Δ(G) = ϑ(G) − α(G) computed for each, and
the maximum for every size determined. For each maximizer the value of the Lovász theta
number is **proved**, not fitted: by an exact primal–dual certificate where a closed form
exists, and by a certified rational enclosure where none does.

### The result worth stating first

Solving a semidefinite program exactly means solving a univariate polynomial whose degree
is the *algebraic degree* of the program, and that degree is normally enormous. Already
for 3×3 matrices the generic degree is **6**, with Galois group typically the full S₆, so
the optimum admits no expression in radicals; at 6×6 the generic degrees run to
**1400–2100** (Nie, Ranestad & Sturmfels, *The Algebraic Degree of Semidefinite
Programming*, Math. Program. **122** (2010); quoted with line numbers in `SOURCES.md` §S8).

Against that background:

> The contextuality-gap maximizers for **n ≤ 10** have theta values of algebraic degree
> **1, 2, 3 or 4** — a five-vertex √5, a seven-vertex cubic, an eight-vertex quartic, a
> rational 11/3 at nine vertices, 3 + √2⁄2 at ten. At **n = 11** the degree escapes:
> the value is not a root of any integer polynomial of degree ≤ 48 with height ≤ 10⁹.
> The series does not break at eleven vertices; it **returns to typical** there.

So the surprise is not the absence of a closed form at n = 11 — that is the normal
behaviour of an 11×11 semidefinite program. The surprise is that closed forms existed at
all up to ten vertices, where the generic expectation is degrees in the hundreds.

**And the landscape has now been measured — though what the measurement licenses is
narrower than the picture it suggests, and the narrow version is the one that counts.**
Algebraic degrees were computed for 1286 graphs at n = 5…11: the top 100 by Δ at each size,
a random sample of the same size among graphs with Δ > 0, and a Δ = 0 control. The fraction
with no closed form runs 1 % → 61 % across n = 8…11 in the top 100 against 0 % → 14 % in the
random sample — the same direction on all four sizes where the comparison exists.

**But the threshold sealed before any graph was measured required that gap to reach 0.25 on
three of the four sizes, and it does so on one. The recorded verdict is therefore *not
confirmed*, and the bar is not lowered after the fact. All three sealed hypotheses of that
stage failed their criteria.** So this is a measured *direction*, not an established fact,
and the reading it invites — that the six closed forms up to n = 10 were found in the
hardest country rather than the easiest — is an interpretation of that direction and no
more. It is still the reverse of how this project read its own series until 2026-08-26,
which is why it is here at all.

**The caveat, which the claim needs to be honest.** Nie–Ranestad–Sturmfels describe
**generic** semidefinite programs with rational data. Ours is structured — zeros on every
edge, trace fixed at 1 — and is not covered by their theorems directly. The low degrees up
to n = 10 are therefore a deviation from typical that has to be explained by structure and
symmetry, not by the general theory; the general theory only says that expecting the
deviation to continue was never reasonable.

This continues **U. Tamer, Ö. E. Müstecaplıoğlu, A. Dizdar and Z. Gedik,
*The Quad-C₅ Graph: Maximum Contextuality Gap on Eight Vertices*,
[arXiv:2605.12828](https://arxiv.org/abs/2605.12828)**, which settled the eight-vertex case.
Their result is reproduced here independently and their maximizer is confirmed.

### What is new here, and what is not

**The enumeration is not new.** A. Cabello, L. E. Danielsen, A. J. López-Tarrida and
J. R. Portillo published a database of the graphs with ϑ > α for n ≤ 10, accompanying
[Amselem et al., PRL **108**, 200405 (2012)]. Its counts of such graphs are 1, 3, 33,
498, 16 533 and 975 330 for n = 5…10. The maximum by Δ can be obtained from that data by
sorting. The database was hosted at `ii.uib.no/~larsed/quantum_graphs/`, which is now
dead; only the index page survives, in the Internet Archive.

**What is new is the certification.** Every value quoted here is proved, not fitted: an
explicit primal matrix bounds ϑ from below and an explicit dual bounds it from above,
both in exact arithmetic over the relevant number field, with positive semidefiniteness
checked twice by independent methods. That includes the eight-vertex value, which the
paper above left open after reporting its integer-relation candidate as a false positive.

**That database was believed lost, and it is not.** Its published address at
`ii.uib.no/~larsed/quantum_graphs/` returns 404, and for a week this project could compare
only counts. On 2026-08-27, in answer to a direct enquiry, L. E. Danielsen supplied its
current location — **`https://codetables.de/larsed/quantum_graphs/`**. The database carries
no rights statement, so **it is not redistributed here**: what is archived here are its
SHA-256 checksums, and `runners/run_db_compare.py` fetches the files from the address above
and verifies them against those checksums before use (`SOURCES.md` §S14, §S15.4). So the
comparison below is not of two totals but of **two independent enumerations, fourteen years
apart, matched graph by graph**.

| n | database | ours (τ = 10⁻⁶) | only theirs | only ours | α mismatches |
|--:|--:|--:|--:|--:|--:|
| 5 | 1 | 1 | 0 | 0 | 0 |
| 6 | 3 | 3 | 0 | 0 | 0 |
| 7 | 33 | 33 | 0 | 0 | 0 |
| 8 | 498 | 498 | 0 | 0 | 0 |
| 9 | 16 533 | 16 533 | 0 | 0 | 0 |
| 10 | 975 330 | 975 338 | **0** | **8** | 0 |

At five sizes the sets are **identical, graph for graph** — the graph6 strings match
directly, no isomorphism testing was needed — with **zero disagreements on α across 992 398
graphs** and every ϑ agreeing within the four decimals their files print.

**The eight at n = 10 are not a threshold artefact, and that was our own hypothesis.** Their
gaps run 2.7·10⁻³ to 8.3·10⁻³, three orders above any noise floor, and χ(Ḡ) > α for all
eight, so the sandwich does not close them. Each now carries an **exact primal certificate**
proving ϑ > α. **Why they are absent from the database we do not know and do not guess.**
Lowering our cut to 10⁻⁷ instead adds 2 graphs at n = 8 and 67 at n = 9 — every one with
χ(Ḡ) = α, so those are *proved* Δ = 0 and are our own solver noise; the database excludes
them correctly. See `REPORT_STAGE3.md` and `SOURCES.md` §S14.

**This validates the computation, not the enumeration.** Their index page names its second
column `nauty-string`, so both sides rest on McKay's software and a shared omission would be
invisible to the comparison. Completeness still rests on the `geng` part-sum and on OEIS.

## The series

| n | Δ_max | exact value | deg | d\* | maximizer (graph6) | \|E\| | density | α | \|Aut\| |
|--:|---|---|--:|--:|---|--:|--:|--:|--:|
| 5 | 0.23606797749978970 | √5 − 2 | 2 | 3 | `DUW` | 5 | 0.500 | 2 | 10 |
| 6 | 0.23606797749978970 | √5 − 2 | 2 | 4 | `EUZw` | 10 | 0.667 | 2 | 10 |
| 7 | 0.31766720739409539 | 7cos(π/7)/(1+cos(π/7)) − 3 | 3 | 3 | `` FCp`_ `` | 7 | 0.333 | 3 | 14 |
| 8 | 0.46784372984022411 | root of x⁴−x³+23x²−155x+158 in (3,4), minus 3 | **4** | 3 | `` GCQb`o `` | 10 | 0.357 | 3 | 8 |
| 9 | 0.66666666666666667 | 2/3 | 1 | 4 | `HCRbdO{` | 15 | 0.417 | 3 | 12 |
| 10 | 0.70710678118654752 | 1/√2 | 2 | 4† | `` ICRb`yiu? `` | 20 | 0.444 | 3 | 16 |
| 11 | **0.7748885327…** | no closed form; proved interval below | **> 48** | — | `` J?`D@pgd?{? `` | 17 | 0.309 | **4** | **2** |

**d\* is a lower bound from a non-convex heuristic, not a proved dimension.** It is the
smallest dimension in which an orthogonal representation attaining the bound was *found*,
by minimising η_d over random restarts; a value of d\* therefore rests on a
*non-exceedance* — no representation one dimension down turned up — which is not the same
as none existing. † marks the one entry where the dimension below was shown unreachable
rather than merely not found; "—" means not computed. The authors of the work this
continues mark their own the same way: *"without an SDP upper-bound verification one cannot
rule out a 3D configuration with λmax > 3 that the heuristic failed to find […] a formal
d\* = 4 proof remains an open question"* (`SOURCES.md` §S1.9).

**This project is about the number ϑ, not about physical realisability.** Where the
dimension is known we give it, because for a reader coming from quantum information it is
the first question a table like this raises. But a certified value of ϑ says nothing about
the dimension of a system that would exhibit it, **we have no upper bounds on η₃ and
neither does the work we continue**, and nothing here should be read as a claim about
experimental accessibility. The gap is stated rather than filled.

Minimal polynomials of Δ for n ≤ 10: y²+4y−1, y²+4y−1, y³+16y²+20y−8, y⁴+11y³+68y²+64y−46,
3y−2, 2y²−1. Graph counts swept: 21, 112, 853, 11 117, 261 080, 11 716 571, 1 006 700 565 —
each verified against `geng -c <n> -u`, not taken from a table.

Δ_max is not monotone: Δ_max(6) = Δ_max(5) exactly, because the six-vertex optimum is the
five-cycle with a dominating vertex attached, which changes neither ϑ nor α. Between n = 9
and n = 10 the ratio of consecutive maxima is 1.061, against 1.35–1.47 over n = 6…9 — but
only at the very top: from rank 3 downwards the same ratio is 1.41–1.43, the historical
rate. The value that stands out is 2/3 at n = 9, which lies outside the support of a tail
fitted to the rest of its own distribution; nine of the ten leading graphs at n = 10 are
that nine-vertex optimum with a tenth vertex added. See `REPORT_STAGE4.md`.

Because Δ subtracts an integer from a continuous quantity, the problem splits by the
independence number. Writing D(n, a) for the largest ϑ − a over graphs with α = a, the
overall maximum is max over a of D(n, a). Layer a = 2 wins at n = 5, 6; layer a = 3 from
n = 7 through n = 10; and at n = 11 **layer a = 4 takes the lead**, which is why the
eleven-vertex maximizer has α = 4 while every maximizer before it had α ≤ 3.

That crossover was the mechanism `REPORT_STAGE5.md` predicted and the moment its
calibration got wrong. Stage 5 tracked the gap between layers 3 and 4 shrinking —
0.318, 0.232, 0.307, 0.156 over n = 7…10 — and stated in `PREDICTION_N11.md`, sealed
before any eleven-vertex graph existed, that layer 4 was growing faster and might overtake
at n = 11 or 12. It overtook at 11, and the sealed prediction that layer 3 would still win
failed by exactly the named cause. The model was right about the phenomenon and wrong
about the date.

## Eleven vertices

The full sweep: **1 006 700 565** connected graphs, 71.8 hours on 7 cores. Completeness is
not asserted but checked — the sum over the 4000 `res/mod` parts equals what `geng -c -u 11`
counts, graph for graph. 10.02 % of the graphs reached a semidefinite solver; the other
89.98 % were closed by the sandwich χ(Ḡ) = α ⇒ Δ = 0.

    Delta( J?`D@pgd?{? )  in  [ 0.7748885327027013 , 0.7748885327466875 ]   width 4.4e-11

    L  = 1193722133190 / 250000000003         primal certificate, theta >= L
    U  = 76398216523947 / 16000000000000      dual certificate,   theta <= U

**The enclosure is about that one named graph. That it attains Δ_max(11) — that no other
graph of the billion is higher — is measured, not proved**, and rests on the part of the
sweep that is numerical; see "What is proved and what is not" below. The two halves are
kept apart throughout, here as in the papers.

Ten decimal places, proved in exact rational arithmetic: the 300-digit numerical solution
only proposes the matrices, and symmetry, trace = 1 and the zeros on all 17 edges are then
checked as equalities in ℚ, with positive semidefiniteness established twice — pivoted
Schur complement and all 2¹¹ − 1 = 2047 principal minors — which agreed in all 78 tests.

The runner-up carries a dual certificate of its own, `` J?`@f?kUDG_ `` with α = 4: the
certificate bounds ϑ ≤ 152149953435449/32000000000000, so subtracting α gives
Δ ≤ 24149953435449/32000000000000 = 0.75468604485778125 exactly, strictly below the
leader's lower bound by 0.0202024878. **Uniqueness of the maximum within the top
therefore does not rest on numerical ranking.**

### What is proved and what is not

Stated without rounding in our own favour:

- **Proved.** The enclosure above, and that the runner-up is strictly below it.
- **Proved separately, and it covers most of the space.** The filter is sound by the
  quoted sandwich α ≤ ϑ ≤ χ(Ḡ), not by measurement, so the **89.98 %** of the billion
  graphs it resolved are settled by argument.
- **Not proved.** That none of the remaining ≈10⁸ graphs is higher. That rests on the
  sweep's numerics — SCS at eps = 10⁻⁸, the top 1000 re-solved on CLARABEL with a largest
  disagreement of 9.39·10⁻⁸ — and no certificates were built for a billion graphs, nor
  were they ever intended.

## Inheritance, and how far it goes

Take a maximizer on m vertices, add k−1 mutually independent vertices and one universal
vertex. The result is connected, its α and its ϑ both rise by exactly k−1, and Δ is
unchanged — so every layer a of every size inherits a lower bound from smaller sizes.
Both ingredients are Knuth's (`SOURCES.md` §S7): ϑ is additive on a disjoint union (18.2)
and takes the max on a join (19.2). **The mechanism is a known property, not a finding
here.**

> **This is proved and it is a theorem:** D(n, a) ≥ Δ_max(m) for a = a_m + (n − m) − 1,
> an inequality between algebraic numbers with no floating point in it.

### The equality does not hold in general — refuted 2026-08-25

The interesting question was whether the inequality is an *equality* above some boundary,
so that the upper layers generate nothing of their own. On the complete enumerations at
n = 9, 10 and 11 it looked that way, with the boundary at a\* = 5 on all three.

**It is false.** `` L@JC?_ASKAGPBH `` on 13 vertices, with α = 5 and 19 edges, has

    Delta   >= 45375481648 / 55555555557        = 0.816758669642764
    T(13,5) <= 12398216523947 / 16000000000000  = 0.7748885327466875

— strictly greater by 0.0419, both bounds from exact primal–dual certificates, compared
as fractions. Layer 5 at thirteen vertices generates a value of its own.
See `REPORT_STAGE8.md`.

**Why the earlier boundary survived three stages.** The rule that fits all sixteen known
points is a ≥ max(5, n − 6) — both a floor at 5 *and* a cap of 6 on n − a. At n = 9, 10
and 11 that expression is identically 5, so three complete enumerations could not tell it
apart from the simpler "a ≥ 5"; the two first differ at n = 12. The replacement rule is
sealed, with its own weaknesses, in `PREDICTION_INHERITANCE_RULE.md`.

### What this costs, stated plainly

Version **v2.0 of this repository stated the consequence more broadly than turned out to
be true** — as though upper layers could be skipped as a matter of method. They cannot.
The archived v2.0 record cannot be rewritten, so the correction lives here and in
`REPORT_STAGE8.md`.

The correct statement is narrower and is a fact about two sizes, not a technique:

| n | layers a ≥ 5 | graphs there | share of the sweep | status |
|--:|---|---:|---:|---|
| 9 | a = 5…8 | 22 922 | 8.78 % | verified equal by complete enumeration |
| 10 | a = 5…9 | 1 663 003 | 14.19 % | verified equal by complete enumeration |

Those two figures remain correct for those two sizes, where every layer was actually
computed. **They do not carry forward.** At n = 13 the corresponding layer is not equal
to its transfer bound, so skipping upper layers at an unswept size is not sound.

Proving *any* version of the equality — for which layers, at which sizes — is the
project's main open question: **[`OPEN_PROBLEM.md`](OPEN_PROBLEM.md)**.

**Twelve vertices will not be enumerated, and that is a decision rather than a delay.**
164 059 830 476 connected graphs at our measured 1.402·10⁷ per hour on seven cores is about
**490 days**. Nothing in this project is waiting on that number. The next step is a proof
about the layers, or a construction that reaches further without enumerating — not a bigger
sweep.

`REPORT_STAGE7.md` has the original verdict, `REPORT_STAGE8.md` its refutation.

### The replacement rule is a candidate, and half of it rests on one point

The rule that fits every known point is **a ≥ max(5, n − 6)** — a floor at 5 *and* a cap
of 6 on n − a. Sixteen points, no exceptions. That sounds stronger than it is, and the
honest accounting is this:

| constant | points where it actually decides the verdict |
|---|---:|
| the **5** | **9** |
| the **6** | **1** — the certified counterexample (13,5) |

The other fifteen points agree with the 6 without testing it: they all have n − a ≤ 6, so
the cap never binds. Counting points that *agree* rather than points that *discriminate*
is how the previous formulation survived three stages, and it is not repeated here.

**The data do not even pin the rule.** Over the family a ≥ max(c, n − d), exactly two
members fit all sixteen points: our d = 6, and d = 7. They disagree across the whole
family a = n − 7, whose first three members are (12,5), (13,6) and (14,7), all with the
same threshold 2/3.

**A directed search at ten times budget failed to separate them, and the failure leans
against our own rule.** At (12,5) — where d = 6 requires a counterexample and d = 7
forbids one — 7.12 million θ evaluations across three methods found nothing, while all
four controls, chosen where a counterexample is known to exist with a comparable excess,
were found in 10 runs out of 10. `REPORT_STAGE8BIS.md` records this as evidence *for*
d = 7 and against d = 6, with the two sub-cases it cannot separate named as such.

### What the search instrument can and cannot do, measured

Two abilities, and they are not the same one:

| ability | result |
|---|---|
| finds *an* exceedance of the transfer bound, when one exists | **10 of 10** |
| finds the layer *maximum* | **2 of 8** |

The shortfalls are systematic: at control (10,3) all three methods stalled at the same
value, 0.0400 below the true maximum. **No "best found" figure from these searches may be
read as an estimate of D(n, a).** Measured fitness stops at n = 13; at fourteen vertices
both cold-start methods failed to reach a value the cone construction supplies outright,
so that size carries no evidence either way.

### Where the 5 may come from

The floor has a candidate mechanism, and it is arithmetic rather than analogy. The odd
cycle C_{2a+1} sits in layer a at n = 2a+1, and its gap rises monotonically to a limit of
exactly ½ — 0.236, 0.318, 0.360, 0.386, 0.404, … — while transfer bounds grow without
that ceiling. The cycle beats the transfer at a = 2, 3, 4 and loses from a = 5 on:

| a | 2 | 3 | 4 | **5** | 6 | 7 |
|---|---|---|---|---|---|---|
| Δ(C_{2a+1}) − T(2a+1, a) | +0.236 | +0.082 | +0.042 | **−0.082** | −0.262 | −0.358 |

At a = 4 the layer maximizer *is* C₉ — girth 9, |Aut| = 18, Δ = 0.3600896 to the digit.
At a = 5 it is not: the layer inherits instead.

This is a candidate, not an established explanation. It makes a claim beyond the data —
odd cycles are not layer maximizers at n = 13, 15, 17, 19, sizes never enumerated — which
is why it is more than a coincidence; but it is verified only for a = 5…9, it explains
nothing about layers (10,4) and (11,4) where the generating graph is not a cycle at all,
and it says nothing whatever about the 6. `REPORT_STAGE8.md` §5 has the accounting.

## Structure across the series

**Nesting fails, and fails precisely at the top.** No maximizer contains its predecessor as
an induced subgraph: n = 9 does not contain the eight-vertex optimum, n = 10 does not
contain the nine-vertex one, n = 11 contains neither n = 9 nor n = 10. But the
eleven-vertex maximizer *does* contain both **Quad-C₅** and **C₇**, reappearing across two
sizes. Meanwhile nine of the ten leading graphs at n = 10 *are* the nine-vertex optimum
plus a vertex — and the single exception is rank 1 itself. The plateau inherits its
construction; the maximum is a new construction every time.

**Density has no trend.** 0.500, 0.667, 0.333, 0.357, 0.417, 0.444, then **0.309** at
n = 11 — the eleven-vertex maximizer has 17 edges against the ten-vertex maximizer's 20,
fewer edges on more vertices. Within a single size the "sparser is stronger" tendency the
original paper noted holds, but weakly: Spearman ρ(Δ, |E|) = −0.285 at n = 9 and −0.330 at
n = 10 across the top 50. Along the series it does not hold at all, in either direction.

**Δ is atomic, which rules out extreme-value statistics.** 61 % of the graphs with a
non-zero gap at n = 10 sit on the single value √5 − 2. A continuous tail fit has no density
to fit; `REPORT_STAGE4.md` records that as the reason the GPD/GEV route was abandoned
rather than tuned.

## Algebraic degrees across the landscape

Measured, not conjectured: **1286 graphs at n = 5…11**, in three samples per size — the
top 100 by Δ (**A**), a uniform random sample of the same size among graphs with Δ > 0
(**B**), and a Δ = 0 control (**C**). A relation was found for 1137, not found for 122,
and 27 were declined by the instrument. Sealed as `PREREGISTRATION_STAGE9.md` before the
first measurement; full account in `REPORT_STAGE9.md`.

> **Extremal graphs are algebraically harder than typical ones.** The fraction of graphs
> with no closed form runs **1 % → 61 %** across n = 8…11 in the top 100 (0.01, 0.10,
> 0.28, 0.61), against **0 % → 14 %** in a random sample of the same size (0.00, 0.00,
> 0.07, 0.14). The sign is the same on all four sizes.
>
> **The sealed threshold was not met, and it is not being lowered.** The hypothesis that
> extremality raises the degree required the gap to reach 0.25 on at least three of the
> four sizes; it does so on **one** (n = 11). The verdict recorded is therefore *not
> confirmed*. The bar was fixed in the sealed file before any graph was measured, and a
> direction that is consistent on 4 of 4 sizes is a description, not a verdict — a sign
> test on four points gives p = 0.0625, which does not clear the ordinary bar either.

**All three sealed hypotheses failed their criteria.** That low degrees are a property of
the whole problem: unresolved, 2 of 4 against a bar of 3. That they are a property of
extremality: refuted, 0 of 4. That degree tracks the automorphism group: refuted, |ρ| <
0.20 on three sizes of four with inconsistent signs. The stage's preregistration said in
advance that this closes it rather than voids it — the measurement is the deliverable.

**What the degrees look like.** 97.4 % of the relations found are degree 1, 2, 3 or 4.
The tail is thin: 6, 7, 8, 9, 10, 12, 14, 16, 20. **Degree 5 was searched for and never
occurred once.** Degrees 11, 13, 15 and the other odd values above 10 were never
searched — the ladder runs 1…10, then 12, 14, 16, 20, 24 — so their absence is a property
of the ladder, not a measurement, and nothing about the tail's parity follows.

**The sharpest cut is by layer, not by median.** At n = 11 the top-100 graphs in the
layer α = 4 are out of reach almost entirely: **45 of 47 (96 %)**, against **8 of 41
(20 %)** in the random sample at the same size and the same layer.

**The best predictor is edge count, and only at the top.** Inside sample A,
ρ(degree, |E|) = −0.30, −0.44, −0.42, −0.76 at n = 8…11, all significant; inside sample B
it is +0.09, 0.00, +0.08, −0.10, none significant. Symmetry gives nothing anywhere:
|ρ(degree, log₂|Aut|)| ≤ 0.21 at every size.

**With the limit stated in the same breath.** |E|, α and the layer n − α are nearly one
quantity — ρ(|E|, α) = −0.87 at n = 11, and layer = n − α is an identity. Holding the
layer fixed, |E| separates from α on **5 cells of 13**, all of them inside sample A and
none inside B. What the data support is: *at the top, sparser graphs are algebraically
harder, and this does not reduce entirely to the layer; in the middle of the landscape
edge count says nothing.* Anything stronger they do not support, and nothing stronger is
claimed here.

**Literature.** No measurement of the algebraic degree of ϑ across a class of graphs was
found, and no work connecting algebraic degree to the automorphism group was found; the
classical literature on symmetry reduction in semidefinite programming is about
computational cost, not about degree. Both are recorded as **results of a search on
2026-08-26**, not as claims about the literature — an empty search is not evidence that
nothing exists (`SOURCES.md` §S13).

## Two precisions agreeing is not evidence of accuracy

This may matter more than the degrees, so it is here and not in a footnote.

The campaign's rule for counting trustworthy digits, in use since Stage 2, was: run the
refinement at precision *p* and at 2*p*, take the matching prefix, subtract five. It is
sound only while the higher run is genuinely better. **It measures the stability of an
iteration, not its correctness.**

On a degenerate optimum, Gauss–Newton settles on a fixed point that is not the optimum,
and every precision level reproduces that same wrong point. For the graph `GCY^fW` the
values at 960, 1920 and 3840 digits agree **with each other** to 465 and 945 digits,
while agreeing with the truth ϑ = α = 3 to **359**. The rule reported 945 honest digits
for a value correct to 359.

**The failure is not a blank — it is a plausible wrong answer.** Hand an integer-relation
search those 940 claimed digits and at degree 1 it finds nothing, while at degree 3 it
returns

> **x³ − 9x² + 27x − 27 = (x − 3)³**

because the *cube* of the 10⁻³⁵⁹ error falls below the claimed tolerance. An integer
polynomial, an unremarkable degree, everything looking right. At an honest 350 digits the
same value gives x = 3 immediately. Both are checks in `tests/test_algdeg.py`.

**This is the same mechanism as the false positive the original paper's authors withdrew**
(`SOURCES.md` §S1.9) — stated without any accusatory edge, because we walked into it
ourselves, in our own instrument, and it took three restarts to see. It also corrects our
own Stage 2 method: there the agreement-between-levels criterion was used as a test of
correctness, and what it tests is stability.

**The residual settles it, by mechanism rather than by a tuned threshold.** A converged
run has residual ≈ 10^−dps and loses hundreds of orders per doubling of precision
(3.06·10⁻²⁴¹ → 5.65·10⁻⁴⁸² for C₅); a stalled one returns the *identical* residual at
every precision (1.44·10⁻³¹ at both 240 and 480 for `FCRto`). Convergence is now verified
before any digit count is believed, and 27 of 1286 graphs were declined on that test —
2.1 %, against a preregistered kill threshold of 40 %. The refusal is conservative: for
all 20 declined in the control sample the value is right to 8·10⁻⁸ already in double
precision; what cannot be stated is the number of honest digits, and the instrument says
so instead of inventing one.

**Three defects, all ours, and the gate caught every one.** It caught them on the Δ = 0
control sample, where the answer is the exact integer α computed by an independent route.
On a graph with Δ > 0 a wrong value still looks like a plausible algebraic number, and
none of the three would have been visible. The standing rule that came out of it: choose
a calibration sample for having an **exactly known** answer, not for looking
representative, and check against that answer rather than against some weaker property it
happens to have.

## Predictions: the scoreboard

Every stage sealed its predictions, with tolerances and kill-criteria, by SHA-256 before it
ran. Across the campaign:

| stage | hits / sealed |
|---|---:|
| 0 — n ≤ 9 | 12 / 13 |
| 1 — n = 10 | 14 / 15 |
| 2 — the eight-vertex value | 5 / 5 |
| 3 — the prior database | 4 / 5 |
| 4 — the top of the series | 1 / 4 |
| 5 — layers by α | 2 / 4 |
| 6 — n = 11 | **1 / 10** |
| 7 — inheritance | 5 / 5 |
| 7.1b — certified enclosure | 5 / 5 |
| 8 — attacking inheritance | 0 / 5 |
| 8-bis — reinforced search | 5 / 8 |
| 9 — algebraic degrees | 4 / 6 |
| **total** | **58 / 85** |

**The one hit at n = 11 was a coincidence, and saying otherwise would be dishonest.** The
interval [0.7475, 0.9059] was constructed by extrapolating **layer a = 3**. The observed
0.7748885 fell inside it — but came from **layer a = 4**, whose own predicted interval
[0.6748, 0.7414] was overshot by 0.033. The method got the number right for the wrong
reason. All four per-layer forecasts failed, the lower two too low and the upper two too
high: the extrapolation systematically underestimates the upper layers.

Stage 6 is the campaign's worst stage by score and its most informative one. The
preregistration named, in advance, the exact mechanism that would break it.

Stage 8 scored zero of five and was the campaign's best outcome to date: the prediction
it broke was that no counterexample to the inheritance conjecture existed, and the
counterexample found is exact and certified. Five predictions across stages 8 and 8-bis
were left unresolved — blocks not run, or not decidable from what the search returned —
and they are counted in the denominator rather than quietly dropped, which understates
those two stages rather than flattering them.

Stage 9's two misses are one guess: that the top of the landscape sits on a plateau of
rational values while the middle is algebraically harder. The measurement reverses it.

## The eight-vertex value

The one value the original paper left open. Its authors searched for it by integer relation and
reported their candidate as a false positive; it is settled here by proof rather than by a
better fit.

> **ϑ(Quad-C₅) is the root of  x⁴ − x³ + 23x² − 155x + 158  lying in (3, 4):**
>
> **ϑ = 3.46784372984022410869739188177700792442892753691289881998283530238038751…**
>
> equivalently Δ = ϑ − 3 is the root of y⁴ + 11y³ + 68y² + 64y − 46 in (0, 1).

The Galois group of the quartic is the full S₄, so ℚ(ϑ) has no proper subfield other than ℚ
and the degree cannot be reduced. This is why the value admits no closed form in radicals of
the kind its neighbours have: ϑ(C₇) lies in a cyclic cubic field — the real subfield of ℚ(ζ₇) —
and is therefore expressible through a cosine, while this one is not cyclotomic at all.

What is verified, in exact arithmetic over ℚ(ϑ) (`quadc5/numfield.py`, no floating point):

| | check | gives |
|---|---|---|
| primal | X symmetric, Tr X = 1, X_ij = 0 on all ten edges, **1ᵀX1 = ϑ**, X ⪰ 0 | ϑ(G) ≥ ϑ |
| dual | B = 1 on the diagonal and on every non-edge, **ϑ·I − B ⪰ 0** | ϑ(G) ≤ ϑ |

Positive semidefiniteness is checked twice by independent methods — a pivoted Schur
complement and all 255 principal minors — and both must agree. The high-precision numerics
only propose the matrix entries; they take no part in the verdict.

### A five-minute check, without cloning this repository

`verification_pack/` is a self-contained package for exactly that claim: a Python script
with no dependencies beyond the standard library, the exact primal and dual matrices as
integer numerator/denominator pairs over ℚ(ϑ), and a two-page note explaining what a
certificate proves and why numerics take no part in it.

```bash
python3 verification_pack/verify.py     # 21 checks, ~0.7 s, PASS or FAIL, non-zero exit on FAIL
```

It needs no network, no solver, no enumeration and no part of the rest of this repository,
and it runs on Python 3.7 through 3.12. Fifteen deliberately corrupted certificates were
each rejected, including five that leave the matrix symmetric and its trace intact and are
caught only by the exact positive-semidefiniteness tests. See
[`verification_pack/NOTE.md`](verification_pack/NOTE.md).

The same machinery closes ϑ for the maximizers at n = 9 and n = 10, and for three further
graphs at n = 10. It does **not** close the rank-2 graph at n = 10 (`` ICQeR`[Mg ``): at 476
verified digits no integer relation exists of degree ≤ 48 with height ≤ 10⁹, nor of degree ≤ 4
with height ≤ 10⁹¹. That bound is reported as the result for that graph.

## Reproducing this

```bash
git clone https://github.com/aoktyabrev/contextuality-gap-exhaustive && cd contextuality-gap-exhaustive
bash scripts/verify_from_scratch.sh
```

The script creates a virtual environment from pinned requirements, builds `geng` and
`dreadnaut` from the nauty tarball included in `sources/`, clears `results/`, runs every
stage that does not depend on the eleven-vertex sweep — including the algebraic-degree
measurement of Stage 9, about seventy minutes on seven cores — and diffs what comes out
against what is committed. It exits non-zero if any published number differs.

Requirements: Python 3.12, a C compiler for nauty, ~8 CPU cores, ~2 GB of free disk for the
intermediate sweep files. No GPU — every SDP here is at most 11×11. If a system nauty is
preferred, point `QUADC5_GENG` at its `geng` binary.

**n = 11 is deliberately not part of this script.** Nobody is going to re-run a
three-day sweep to check a repository, so the eleven-vertex results ship as *data*:
`results/report_1c_n11.json` (the run's summary and top 50), `results/n11_top1000.csv`
(the leading thousand graphs, each re-solved on a second solver), and the certified
enclosure in `results/report_7_1b.json`. The script leaves those files alone rather than
regenerating them.

The full table of the 100 827 522 graphs with a positive gap is **not distributed**: it is
10.9 GB raw and 3.3 GB gzipped, past what git or a GitHub release asset will hold. It is
regenerable by the command below, and available on request. Everything the repository
*claims* is derived from the top-1000 and the summary, both of which do ship.

For anyone who does want to repeat it:

```bash
LOG=results/run_n11_$(date -u +%Y%m%dT%H%M%SZ).log
setsid nohup .venv/bin/python -u runners/run_1c.py --n 11 --mod 4000 --procs 7 \
    --positive-only --verify-top 1000 > "$LOG" 2>&1 < /dev/null &
```

**71.8 hours** on 7 cores of an 8-core machine, ~25 GB of transient part files and ~15 GB
kept. `--positive-only` matters: without it the run writes about a billion rows of provable
zeros. The part files are checkpoints — an interrupted run resumes from them at no cost,
which was tested twice during ours, once deliberately and once by a reboot 63.9 hours in.
The single-threaded `geng -c -u 11` pre-count adds ~9 minutes before the sweep starts.

The certified enclosure of §"Eleven vertices" is cheap to re-derive on its own:

```bash
.venv/bin/python runners/certify_enclosure.py     # ~3 minutes, exact arithmetic only
```

Measured on 8 cores under WSL2, from an empty directory. Building the virtual environment
took 14 s and building `geng` 8 s, so the setup is not the cost — the enumeration is:

| stage | what it does | time |
|---|---|--:|
| Stage 0 | n ≤ 9: calibration against the source paper, filters, the 261 080-graph sweep | 1120 s |
| Stage 1 | n = 10: the 11 716 571-graph sweep, exact certificates, the series | 3181 s |
| Stage 2 | high-precision values, minimal polynomials, exact certificates | 3722 s |
| Stage 3 | comparison against the prior database, invariants, boundary certificates | 111 s |
| Stage 4 | the top of the series, extreme-value analysis | 3374 s |
| Stage 5 | the decomposition by independence number | 277 s |
| Stage 6 | the ceiling α\*, the rational-ϑ scan | 27 s |
| Stage 7.1 | integer-relation searches: the negative bound on the field degree at n = 11 | 3947 s |
| Stage 7 | inheritance, the series table, the eleven-vertex enclosure | 193 s |
| **total** | | **15 973 s = 4 h 26 min** |
| | | 23 833 comparisons, **0 mismatches** |

**Over two of those four hours go into producing negative results, and that is not a defect
of the pipeline.** Stage 4 spends an hour establishing that a continuous extreme-value tail
cannot be fitted to an atomic distribution. Stage 7.1 spends another hour on integer-relation
searches that find nothing — which is exactly what the claim "not a root of any integer
polynomial of degree ≤ 48 with height ≤ 10⁹" is made of, and it is reproduced here rather
than taken on trust. Much of Stage 2's hour goes the same way, into the negative bound for
the ten-vertex rank 2.

Timings are stable across independent runs. Three clean rooms gave 1133 / 1117 / 1120 s for
Stage 0, 3115 / 3090 / 3181 s for Stage 1 and 3695 / 3670 / 3722 s for Stage 2 — under 3 %
apart on each. The table above is the run on the released tag itself, not a composite.

One step is skipped in a clean checkout and says so rather than passing silently: the
cross-check that re-runs the *original authors'* code needs a second virtual environment
built from their declared dependencies (`.venv-authors`), which the script does not create.

### Checking the preregistrations

```bash
bash scripts/verify_seals.sh
```

Each stage's predictions, tolerances and kill-criteria were written and hashed before that
stage was run, and the hash was committed before any of its results existed. The script
checks that the sealed documents are byte-identical to what was sealed and prints the commit
timestamps, so the ordering — prediction first, data second — is checkable by anyone rather
than asserted. `SOURCES.md` grows across stages and is never edited in place, so each seal
covers the prefix that existed when it was taken; the script checks the prefixes. Running
`sha256sum -c` on a `.sha256` file by hand will therefore report `SOURCES.md: FAILED`,
correctly — the whole file is not what was sealed, its prefix is.

**This check needs the git history**, because it verifies each seal against the commit
that created it. A `--depth 1` clone and the source archive on Zenodo are snapshots
without that history; the script detects the shallow case and says so rather than
reporting a failure. To check the seals, clone the repository in full.

Nauty 2.9.3 is pinned; the tarball in `sources/` has SHA-256
`9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b`.

## Layout

```
PREREGISTRATION*.md      predictions, tolerances and kill-criteria, written before each
PREREGISTRATION*.sha256  stage was run and sealed by hash; ten seals, all checked by
                         scripts/verify_seals.sh against their sealing commits
PREDICTION_N11.md        Delta_max(11), sealed before any eleven-vertex graph existed
PREDICTION_EDGES.md      |E| = 5(n-6), sealed at 40% coverage; refuted at 100%
PREDICTION_INHERITANCE_RULE.md  a >= max(5, n-6), sealed after the counterexample
OPEN_PROBLEM.md          the main unsolved question, and a literature check on it
SOURCES.md               every external number, quoted verbatim with a line number and an
                         access date, from dumps kept in sources/
REPORT.md                Stage 0 — n ≤ 9
REPORT_STAGE1.md         Stage 1 — n = 10, the series, the invariants
REPORT_STAGE2.md         Stage 2 — the exact eight-vertex value
REPORT_STAGE3.md         Stage 3 — comparison against the prior database, invariants
REPORT_STAGE4.md         Stage 4 — where the top of the series is anomalous
REPORT_STAGE5.md         Stage 5 — the series split into layers by alpha
REPORT_STAGE6.md         Stage 6 — the ceiling, and the exhaustive sweep at n = 11
REPORT_STAGE7.md         Stage 7 — inheritance of the upper layers, boundary a* = 5
REPORT_STAGE8.md         Stage 8 — that boundary refuted by a certified counterexample
REPORT_STAGE8BIS.md      Stage 8-bis — reinforced search, controls, and the instrument measured
REPORT_STAGE7_1B.md      Stage 7.1b — the certified enclosure for n = 11
REPORT_STAGE9.md         Stage 9 — algebraic degrees measured across the landscape
quadc5/                  the library: graph6 codec, alpha, theta, filters, structure,
                         hiprec (arbitrary-precision refinement), numfield (exact
                         arithmetic in a number field with exact sign decisions),
                         algdeg (algebraic degree, with a convergence test on the
                         refinement before any digit count is believed)
runners/                 one script per block, plus run_stage{0,1,2}.sh
scripts/                 clean-room verification and the results comparator
verification_pack/       stand-alone five-minute check of the eight-vertex value: one
                         dependency-free script, the exact certificates, and a note
tests/                   the estimator gate: every estimator on random inputs, two routes;
                         and the algebraic-degree gate, which demonstrates that an
                         over-claimed digit count returns a plausible WRONG polynomial
results/                 top-1000 tables, certificates, per-block JSON reports
sources/                 the paper, its LaTeX source, the authors' repository and Zenodo
                         archive, McKay's graph6 databases, the nauty tarball
```

The preregistrations and the stage reports are in Russian; `SOURCES.md` quotes its
English sources verbatim, and this README and all code comments are in English.

## Method notes worth knowing before reading the code

- **The filter that makes n = 10 feasible.** χ(Ḡ) = α forces ϑ = α through the sandwich
  α ≤ ϑ ≤ χ(Ḡ), so 91.67 % of the eleven-million graphs never reach an SDP. It is sound by
  that inequality alone, not by the strong perfect graph theorem. Perfect-graph recognition
  is a strict subset of it, verified on all 11 716 571 graphs, and cross-checked against
  `geng -P`, whose counts match exactly at n = 8, 9 and 10.
- **Thresholds are measured, not assumed.** The Δ = 0 cut is placed inside an empirically
  empty band whose two edges are reported: at n = 10 the solver noise floor is 1.9·10⁻⁶,
  measured over 10⁵ provably-zero graphs, and the smallest genuine gap is 5.894·10⁻⁴.
- **Precision claims are measured too, and the measure has a precondition.** "Verified
  digits" means the matching prefix of a run at working precision and a run at twice that,
  minus five — always fewer than the solver's own residual suggests. **That is valid only
  while the refinement is still converging.** Two levels agreeing measures stability, not
  correctness: on a degenerate optimum Gauss–Newton settles on a stable wrong point and
  every level reproduces it. Convergence is checked first, by the residual falling with
  precision; where it does not fall, the value is reported as unmeasurable rather than
  guessed at. This corrects the rule as it was used in Stage 2 — see the section above.
- **graph6 encodes a labelling, not an isomorphism class.** McKay's published files are in
  `geng`'s default labelling; passing `-l` yields a different canonical form that disagrees
  with them on 260 902 of 261 080 nine-vertex codes.

## Provenance

The work was carried out with an AI assistant: the specification, the kill-criteria and the
preregistered predictions were formulated in dialogue before each stage, and the computation,
the checks and the write-up were performed by the assistant. The commit history reflects this
and has been left intact. None of it bears on whether the results are right — the certificates
are machine-checkable by anyone with a computer, independently of who produced them, and
`scripts/verify_from_scratch.sh` is there for exactly that.

## Licence and citation

Code is MIT; data and documents produced here are CC BY 4.0. See `LICENSE`,
`LICENSE-DATA` and `CITATION.cff`.

### Third-party material

`sources/` holds evidence for Rule 0 — every external number is quoted from a downloaded
copy. A rights review on 2026-08-27 (`SOURCES.md` §S15) established what may be
redistributed and what may only be *read*, and the repository now carries only the former.

| what | terms | how it is handled |
|---|---|---|
| arXiv:2605.12828 (Tamer, Müstecaplıoğlu, Dizdar, Gedik) — PDF and LaTeX | **CC BY 4.0** | included, attributed |
| The authors' code and data, Zenodo 10.5281/zenodo.20465134 | **CC BY 4.0** | included as `sources/zenodo_extract/`, attributed |
| nauty 2.9.3 (B. D. McKay, A. Piperno) | **Apache 2.0** | tarball included; `COPYRIGHT` and `LICENSE-2.0.txt` travel inside it |
| McKay's graph6 collections | no restriction stated on the source page | included; read by the Stage 0 and 1 runners |
| OEIS A001349 | **CC BY-SA 4.0** — attribution and share-alike, [oeis.org](https://oeis.org/) | included unchanged as `sources/oeis_A001349.json`; that file is under CC BY-SA 4.0, not this repository's CC BY 4.0 |
| arXiv:math/0611562, arXiv:math/9312214, arXiv:1211.5825 | arXiv non-exclusive / assumed licences, which in arXiv's own words *"limit re-use of any type from other entities or individuals"* | **not redistributed.** `SOURCES.md` carries the link, the access date, the SHA-256 and the quoted lines with their line numbers |
| The quantum-graphs database (Cabello, Danielsen, López-Tarrida, Portillo) | no rights statement on the source page | **not redistributed.** `runners/run_db_compare.py` fetches it and verifies it against the committed checksums before use |

**Nothing in Rule 0 is weakened by this.** A quotation with line numbers plus the file's
SHA-256 proves the source was read in exactly that form, and lets any reader obtain the
same bytes and check the same lines — without our republishing material we have no right
to republish.

Archived on Zenodo. Cite the concept DOI, which always resolves to the current version:

    Oktiabrev, A. (https://orcid.org/0009-0003-3626-2002) (2026).
    Exact contextuality gaps for graphs up to eleven vertices.
    Zenodo. https://doi.org/10.5281/zenodo.22031808

The DOI for this specific release (v2.2) is
[10.5281/zenodo.22309457](https://doi.org/10.5281/zenodo.22309457); v2.1 was
[10.5281/zenodo.22110971](https://doi.org/10.5281/zenodo.22110971), v2.0
[10.5281/zenodo.22092303](https://doi.org/10.5281/zenodo.22092303) and v1.0.0
[10.5281/zenodo.22031809](https://doi.org/10.5281/zenodo.22031809).
Please cite the paper this continues as well: arXiv:2605.12828.
