# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

QUADC5 is a research campaign, not a product. One question per stage, closed by
`REPORT.md`. Code exists to produce the numbers that go into that report.

**Stage 0 question:** exhaustive enumeration of the connected non-isomorphic graphs on
9 vertices by the contextuality gap Δ(G) = ϑ(G) − α(G), plus the structural question of
whether the maximizer is built from overlapping induced pentagons the way the
eight-vertex maximizer is.

Separate repository, own `.venv`. Nothing is imported from the earlier campaigns
(`/home/artem/tomloc`, `/home/artem/tomloc/DSNET`) — not a line of code, not a number.

## Standing rules — read these before writing code

They are the reason the code and the documents look the way they do. Stated in full in
`PREREGISTRATION.md` §0.

- **Rule 0 (strengthened).** No load-bearing number and no claim about someone else's
  work comes from memory — mine, yours, or the brief's. Each is either derived here or
  confirmed by a *direct dump of the source* into `sources/`, quoted with line numbers
  in `SOURCES.md`, with a link and an access date. Unreachable source ⇒ mark
  `UNVERIFIED` and keep it out of every decisive comparison. **The brief is a source
  like any other:** its `GCQb'o` was wrong (real code `` GCQb`o ``), its 261 080 was
  right — both established by download, neither taken on trust.
- **Calibration rule.** 0.a is a gate. If n=5, n=7 or n=8 fails to reproduce, 0.c is not
  run and the stage reports as blocked at 0.a.
- **Repository rule.** Every estimator runs on random inputs, by two independent routes.
  `tests/test_estimators.py` is that gate; the pretty graphs are necessary and not
  sufficient — all of them except Quad-C₅ are vertex-transitive, so an indexing bug is
  invisible on them (that is what R6 exists for).
- **Kill rule.** A triggered kill is written up as a negative result with diagnostics.
  No new quantity is introduced after the data are seen.
- **A test that cannot fail is vacuous.** Every gate names the concrete bug it must
  catch, and that is reported alongside it. See `PREREGISTRATION.md` §3.1, §4.2.
- **Preregistration.** `PREREGISTRATION.md` + `SOURCES.md`, SHA-256'd into
  `PREREGISTRATION.sha256`, committed before the first sample (commit `dc07d1f`). The
  sealed files are never edited; corrections are dated amendments in `REPORT.md`.
- **`REPORT.md` shape.** Result in half a page first, then the prediction table
  (предсказано / получено / допуск / вердикт), then sources with access dates, then
  «отклонения от брифа», plus a section on the cross-check against the authors' code.
  Not a three-hundred-line summary. Briefs and reports are in Russian; `SOURCES.md`
  quotes its English sources verbatim.

## Environment

```bash
/home/artem/QUADC5/.venv/bin/python          # 3.12: numpy, scipy, networkx, cvxpy,
                                             # clarabel, scs, cvxopt, pypdf, pandas
/home/artem/QUADC5/.venv-authors/bin/python  # the authors' declared deps, kept separate
                                             # so their run cannot touch ours
```

8 CPU cores; GPU is an RTX 4070 Ti (12 GB) under WSL2. **GPU is not used and is not
needed** — the whole n=9 sweep is ~4 minutes on 7 cores because each SDP is 9×9. Do not
add a GPU path without a measurement showing it wins.

## Commands

```bash
.venv/bin/python tests/test_estimators.py         # gate R, ~5 s; blocks everything else
.venv/bin/python runners/run_0a.py                # calibration n=5,7,8; gate 0.a
.venv/bin/python runners/run_0b.py --n 8 9        # filters and their gate
.venv/bin/python runners/run_0c.py --n 9          # the sweep; --procs, --verify-top
.venv/bin/python runners/run_0d.py --n 9 --top 50 # structure; --restarts, --dstar 0
bash runners/run_stage0.sh                        # all of the above, in order
```

Each runner takes `--seed` (default 20260819) and writes one JSON into `results/`.
Nothing downstream of a failed gate should be run; the runners exit non-zero on failure
so `run_stage0.sh` stops on its own.

## Layout

- `sources/` — PDFs, LaTeX source, the authors' repository, the Zenodo archive, McKay's
  graph6 databases. Rule 0's evidence. Never edit; re-download instead.
- `quadc5/` — the library. `g6` (graph6 codec written from the format, not wrapped
  around networkx, so cross-checks stay independent), `alpha`, `theta`, `perfect`,
  `chrom`, `structure`, `sweep`.
- `runners/` — one script per brief item; each prepends the repo root to `sys.path`.
- `tests/` — plain scripts, a `check(name, ok, detail)` helper, `FAILS` list,
  `sys.exit(1)` at the end. No pytest.
- `results/` — `n{N}_all.csv` (full sweep), `n{N}_top{K}.csv`, `report_0*.json`.
  `n{N}_partial_*.csv` are the checkpoints and are gitignored.
- `authors_run/` — a working copy of the authors' code plus what it produced here.

## Traps, established before or during the work

- **graph6 encodes a labelling, not an isomorphism class.** Comparing our own
  construction's code against McKay's canonical record tests the labelling and fails on
  a correct graph — this actually happened to A2′/A3⁗ on the first run of `run_0a.py`.
  Use `g6.iso_equal` whenever one side is a graph we built ourselves; compare strings
  only when both sides come from McKay's file or from a source's printed code.
- **The brief's τ_zero = 1e-9 is below the solvers' noise floor** (~1e-7 at n=8/9), so
  applying it literally misclassifies true zeros. Δ is sharply bimodal — the zero
  cluster tops out around 1e-7 and the next value is ~0.026 — so the classification is
  taken on a threshold inside that gap and is threshold-free there. Report both.
- **Comparing to the paper's printed 5-digit values at 1e-6 is impossible in
  principle.** The gate is applied to the authors' 8-digit CSV; the printed values get
  τ_paper = 5e-6, half the last printed digit.
- **Perfection is sufficient for Δ=0 but not necessary.** `chi(Ḡ) == α` is the stronger
  sound filter and it is sound by the *quoted* sandwich (S1.2) rather than by the strong
  perfect graph theorem, which none of our sources states. Run both, report both.
- **SCS at `eps=1e-9` costs 12× more than at `eps=1e-8`** (61 ms vs 5 ms per 9-vertex
  graph) for no gain that survives the CLARABEL re-solve. Bulk at 1e-8, verify the
  leading block with CLARABEL.
- **η_d is non-convex**; restarts give a lower bound only. `d*` resting on a
  non-exceedance is marked `indicated`, exactly as the source marks its own.

## Regenerating the bulk data

`results/n9_all.csv` (29 MB, all 261 080 rows) is gitignored; the committed copy is
`results/n9_all.csv.gz`. `gunzip -k results/n9_all.csv.gz` restores what `run_0b.py`
reads. Deleting it and re-running `run_0c.py` also works — the chunk checkpoints in
`results/n9_partial_*.csv` make the sweep resumable, and a full cold run is ~6.5 min.
