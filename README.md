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

**One count differs.** Ours at n = 10 is 975 338 against the database's 975 330. The
counts agree exactly at n = 8 (498) and n = 9 (16 533). All thirteen of our graphs with
Δ < 2·10⁻³ carry exact rational certificates of Δ > 0, so our side of the boundary is
not inflated by solver noise; which eight graphs account for the difference cannot be
determined, because the per-graph files are no longer retrievable from any source.
See `REPORT_STAGE3.md`.

## The series

| n | Δ_max | exact value | deg | maximizer (graph6) | \|E\| | density | α | \|Aut\| |
|--:|---|---|--:|---|--:|--:|--:|--:|
| 5 | 0.23606797749978970 | √5 − 2 | 2 | `DUW` | 5 | 0.500 | 2 | 10 |
| 6 | 0.23606797749978970 | √5 − 2 | 2 | `EUZw` | 10 | 0.667 | 2 | 10 |
| 7 | 0.31766720739409539 | 7cos(π/7)/(1+cos(π/7)) − 3 | 3 | `` FCp`_ `` | 7 | 0.333 | 3 | 14 |
| 8 | 0.46784372984022411 | root of x⁴−x³+23x²−155x+158 in (3,4), minus 3 | **4** | `` GCQb`o `` | 10 | 0.357 | 3 | 8 |
| 9 | 0.66666666666666667 | 2/3 | 1 | `HCRbdO{` | 15 | 0.417 | 3 | 12 |
| 10 | 0.70710678118654752 | 1/√2 | 2 | `` ICRb`yiu? `` | 20 | 0.444 | 3 | 16 |
| 11 | **0.7748885327…** | no closed form; proved interval below | **> 48** | `` J?`D@pgd?{? `` | 17 | 0.309 | **4** | **2** |

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

    Delta_max(11)  in  [ 0.7748885327027013 , 0.7748885327466875 ]      width 4.4e-11

    L  = 1193722133190 / 250000000003         primal certificate, theta >= L
    U  = 76398216523947 / 16000000000000      dual certificate,   theta <= U

Ten decimal places, proved in exact rational arithmetic: the 300-digit numerical solution
only proposes the matrices, and symmetry, trace = 1 and the zeros on all 17 edges are then
checked as equalities in ℚ, with positive semidefiniteness established twice — pivoted
Schur complement and all 2¹¹ − 1 = 2047 principal minors — which agreed in all 78 tests.

The runner-up carries a dual certificate of its own, `` J?`@f?kUDG_ `` with
Δ ≤ 152149953435449/32000000000000 = 0.7546860448577810, strictly below the leader's lower
bound by 0.0202024878. **Uniqueness of the maximum within the top therefore does not rest
on numerical ranking.**

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

## Inheritance: which layers need not be swept at all

Take a maximizer on m vertices, add k−1 mutually independent vertices and one universal
vertex. The result is connected, its α and its ϑ both rise by exactly k−1, and Δ is
unchanged — so every layer a of every size inherits a lower bound from smaller sizes.
Both ingredients are Knuth's (`SOURCES.md` §S7): ϑ is additive on a disjoint union (18.2)
and takes the max on a join (19.2). **The mechanism is a known property, not a finding
here.**

What is new is that above a boundary the inequality is an *equality* — the upper layers
generate nothing of their own:

| n | boundary a\* | graphs in layers a ≥ a\* | share of the sweep |
|--:|--:|---:|---:|
| 9 | 5 | 22 922 | 8.78 % |
| 10 | 5 | 1 663 003 | 14.19 % |

### Half of this is proved and half is measured

The distinction matters and the reports state it explicitly. The **lower half is exact**:
the cone shifts α and ϑ by the same integer, so Δ transfers untouched and
D(n, a) ≥ Δ_max(m) holds as an inequality between algebraic numbers, with no floating point
anywhere in it. The **upper half is measured**: that nothing in the layer *exceeds* the
transfer was observed on n = 9 and n = 10, at the 10⁻⁸ level that is all a solver can
offer, and it is not proved at any size.

So the 8.78 % and 14.19 % below are savings established by computing those layers and
finding nothing new — an observation about two sizes, not a theorem. Proving the upper half
would turn it into a reduction of the search space that holds without computing anything,
which for twelve vertices (164 059 830 476 connected graphs, about 490 days at our measured
rate) is the only way to say anything at all. That is the project's main open question:
**[`OPEN_PROBLEM.md`](OPEN_PROBLEM.md)**.

Those layers need not be enumerated: their maxima are already known from smaller sizes.

**All five of the stage's sealed predictions hit** — the analytic claim that α and ϑ both
shift by exactly k−1, equality for every non-empty layer a ≥ 5 including the ones never
computed before, the boundary landing at exactly 5 on both sizes, agreement within 10⁻⁶
(it came out exact), and that the saving would be modest rather than a serious speedup.
The weak form of the hypothesis — D(n, a) ≥ transfer bound — is violated nowhere; the
strong form holds above the boundary and fails below it, where layers 2, 3 and 4 exceed
the transfer bound by 0.04 to 0.20 and so generate values of their own.

`REPORT_STAGE7.md` has the verdict in full. **n = 11 is excluded from it**, because the
hypothesis was formed by looking at n = 11; the check runs on n = 9 and n = 10, closed
since 2026-08-18.

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
| **total** | **49 / 66** |

**The one hit at n = 11 was a coincidence, and saying otherwise would be dishonest.** The
interval [0.7475, 0.9059] was constructed by extrapolating **layer a = 3**. The observed
0.7748885 fell inside it — but came from **layer a = 4**, whose own predicted interval
[0.6748, 0.7414] was overshot by 0.033. The method got the number right for the wrong
reason. All four per-layer forecasts failed, the lower two too low and the upper two too
high: the extrapolation systematically underestimates the upper layers.

Stage 6 is the campaign's worst stage by score and its most informative one. The
preregistration named, in advance, the exact mechanism that would break it.

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

The script creates a virtual environment from pinned requirements, builds `geng` from the
nauty tarball included in `sources/`, clears `results/`, runs all three stages, and diffs
what comes out against what is committed. It exits non-zero if any published number differs.

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
| Stage 0 | n ≤ 9: calibration against the source paper, filters, the 261 080-graph sweep | 1117 s |
| Stage 1 | n = 10: the 11 716 571-graph sweep, exact certificates, the series | 3090 s |
| Stage 2 | high-precision values, minimal polynomials, exact certificates | 3670 s |
| Stage 3 | comparison against the prior database, invariants, boundary certificates | 109 s |
| Stage 4 | the top of the series, extreme-value analysis | 3305 s |
| Stage 5 | the decomposition by independence number | 269 s |
| Stage 6 | the ceiling α\*, the rational-ϑ scan | ~5 s |
| Stage 7.1 | integer-relation searches: the negative bound on the field degree at n = 11 | ~65 min |
| Stage 7 | inheritance, the series table, the eleven-vertex enclosure | 189 s |
| **total** | | **≈ 4 h 20 min** |

**Over two of those four hours go into producing negative results, and that is not a defect
of the pipeline.** Stage 4 spends an hour establishing that a continuous extreme-value tail
cannot be fitted to an atomic distribution. Stage 7.1 spends another hour on integer-relation
searches that find nothing — which is exactly what the claim "not a root of any integer
polynomial of degree ≤ 48 with height ≤ 10⁹" is made of, and it is reproduced here rather
than taken on trust. Much of Stage 2's hour goes the same way, into the negative bound for
the ten-vertex rank 2.

Timings are stable across independent runs: a second clean room gave 1133 s, 3115 s and
3695 s for stages 0, 1 and 2 against the 1117 s, 3090 s and 3670 s above — under 1.5 %
apart on each.

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
covers the prefix that existed when it was taken; the script checks the prefixes.

Nauty 2.9.3 is pinned; the tarball in `sources/` has SHA-256
`9fc4edae04f88a0f5883985be3b39cf7f898fd6cc96e96b9ee25452743cc1b5b`.

## Layout

```
PREREGISTRATION*.md      predictions, tolerances and kill-criteria, written before each
PREREGISTRATION*.sha256  stage was run and sealed by hash; ten seals, all checked by
                         scripts/verify_seals.sh against their sealing commits
PREDICTION_N11.md        Delta_max(11), sealed before any eleven-vertex graph existed
PREDICTION_EDGES.md      |E| = 5(n-6), sealed at 40% coverage; refuted at 100%
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
REPORT_STAGE7_1B.md      Stage 7.1b — the certified enclosure for n = 11
quadc5/                  the library: graph6 codec, alpha, theta, filters, structure,
                         hiprec (arbitrary-precision refinement), numfield (exact
                         arithmetic in a number field with exact sign decisions)
runners/                 one script per block, plus run_stage{0,1,2}.sh
scripts/                 clean-room verification and the results comparator
verification_pack/       stand-alone five-minute check of the eight-vertex value: one
                         dependency-free script, the exact certificates, and a note
tests/                   the estimator gate: every estimator on random inputs, two routes
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
- **Precision claims are measured too.** "Verified digits" means the matching prefix of a run
  at working precision and a run at twice that, minus five — always fewer than the solver's
  own residual suggests.
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

Code is MIT; data and documents are CC BY 4.0. See `LICENSE`, `LICENSE-DATA` and
`CITATION.cff`.

Archived on Zenodo. Cite the concept DOI, which always resolves to the current version:

    Oktiabrev, A. (https://orcid.org/0009-0003-3626-2002) (2026).
    Exact contextuality gaps for graphs up to ten vertices.
    Zenodo. https://doi.org/10.5281/zenodo.22031808

The DOI for this specific release is [10.5281/zenodo.22031809](https://doi.org/10.5281/zenodo.22031809).
Please cite the paper this continues as well: arXiv:2605.12828.
