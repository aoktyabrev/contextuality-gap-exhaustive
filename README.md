# Exact contextuality gaps for graphs up to ten vertices

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22031808.svg)](https://doi.org/10.5281/zenodo.22031808)

Every connected graph on up to ten vertices has been enumerated, the contextuality gap
Δ(G) = ϑ(G) − α(G) computed for each, and the maximum for every size determined; for each
maximizer the exact value of the Lovász theta number is **proved** by a machine-checked
primal and dual certificate rather than fitted numerically.

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

| n | Δ_max | exact value | minimal polynomial of Δ | deg | maximizer (graph6) | structure |
|--:|---|---|---|--:|---|---|
| 5 | 0.23606797749978970 | √5 − 2 | y² + 4y − 1 | 2 | `DUW` | C₅ |
| 6 | 0.23606797749978970 | √5 − 2 | y² + 4y − 1 | 2 | `EUZw` | C₅ plus a dominating vertex |
| 7 | 0.31766720739409539 | 7cos(π/7)/(1+cos(π/7)) − 3 | y³ + 16y² + 20y − 8 | 3 | `` FCp`_ `` | C₇ |
| 8 | 0.46784372984022411 | root of the quartic below | y⁴ + 11y³ + 68y² + 64y − 46 | **4** | `` GCQb`o `` | Quad-C₅ |
| 9 | 0.66666666666666667 | 2/3 | 3y − 2 | 1 | `HCRbdO{` | C₆ plus a triangle |
| 10 | 0.70710678118654752 | 1/√2 | 2y² − 1 | 2 | `` ICRb`yiu? `` | 4-regular, 20 edges |

α(G) = 2 for n ≤ 6 and 3 for 7 ≤ n ≤ 10. Graph counts swept: 21, 112, 853, 11 117,
261 080, 11 716 571 — the last verified against `geng -c 10 -u`, not taken from a table.

Δ_max is not monotone: Δ_max(6) = Δ_max(5) exactly, because the six-vertex optimum is the
five-cycle with a dominating vertex attached, which changes neither ϑ nor α. Between n = 9
and n = 10 the ratio of consecutive maxima is 1.061, against 1.35–1.47 over n = 6…9.

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
nauty tarball included in `sources/`, empties `results/`, runs all three stages, and diffs
what comes out against what is committed. It exits non-zero if any published number differs.

Requirements: Python 3.12, a C compiler for nauty, ~8 CPU cores, ~2 GB of free disk for the
intermediate sweep files. No GPU — every SDP here is at most 10×10. If a system nauty is
preferred, point `QUADC5_GENG` at its `geng` binary.

Measured on 8 cores under WSL2, from an empty directory; building the virtual
environment took 16 s and building `geng` 6 s, so the setup is not the cost — the
enumeration is:

| stage | what it does | time |
|---|---|--:|
| Stage 0 | n ≤ 9: calibration against the source paper, filters, the 261 080-graph sweep | 19 min |
| Stage 1 | n = 10: the 11 716 571-graph sweep, exact certificates, the series | 53 min |
| Stage 2 | high-precision values, minimal polynomials, exact certificates | 63 min |
| **total** | | **2 h 15 min** |

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
PREREGISTRATION*.sha256  stage was run and sealed by hash; the sealing commits are
                         dc07d1f, 2aebb12 and 053f834
SOURCES.md               every external number, quoted verbatim with a line number and an
                         access date, from dumps kept in sources/
REPORT.md                Stage 0 — n ≤ 9
REPORT_STAGE1.md         Stage 1 — n = 10, the series, the invariants
REPORT_STAGE2.md         Stage 2 — the exact eight-vertex value
REPORT_STAGE3.md         Stage 3 — comparison against the prior database, invariants
quadc5/                  the library: graph6 codec, alpha, theta, filters, structure,
                         hiprec (arbitrary-precision refinement), numfield (exact
                         arithmetic in a number field with exact sign decisions)
runners/                 one script per block, plus run_stage{0,1,2}.sh
scripts/                 clean-room verification and the results comparator
tests/                   the estimator gate: every estimator on random inputs, two routes
results/                 top-1000 tables, certificates, per-block JSON reports
sources/                 the paper, its LaTeX source, the authors' repository and Zenodo
                         archive, McKay's graph6 databases, the nauty tarball
```

The preregistrations and the three stage reports are in Russian; `SOURCES.md` quotes its
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
