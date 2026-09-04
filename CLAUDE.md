# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

QUADC5 is a research campaign, not a product. One question per stage, closed by
`REPORT.md`. Code exists to produce the numbers that go into that report.

**Stage 0 question (closed):** exhaustive enumeration of the connected non-isomorphic
graphs on 9 vertices by the contextuality gap Δ(G) = ϑ(G) − α(G), plus the structural
question of whether the maximizer is built from overlapping induced pentagons the way the
eight-vertex maximizer is. Answer: Δ_max(9) = 2/3 exactly; pentagons persist but the
uniform two-fold cover does not. See `REPORT.md`.

**Stage 1 question (closed):** the same at n = 10, streamed through nauty's `geng` rather
than a downloaded file, plus exact certificates and the series over n = 5…10. Answer:
Δ_max(10) = 1/√2 exactly; the ×1.4 growth of the series collapses to ×1.061 at the last
step, and no structural invariant survives the whole series. See `REPORT_STAGE1.md`.

**Stage 2 question (closed):** the exact value of ϑ for the eight-vertex maximizer — the
one hole in the series, and the value whose PSLQ the source's authors withdrew as a false
positive. Answer: ϑ(`` GCQb`o ``) is the root 3.46784372984… of **x⁴ − x³ + 23x² − 155x +
158**, proved by exact primal and dual certificates over ℚ(θ); its Galois group is the
full S₄. The n=10 rank 2 did not close: no minimal polynomial of degree ≤ 48 with height
≤ 10⁹ exists. See `REPORT_STAGE2.md`.

**Stage 3 question (closed):** the cross-check against the Cabello–Danielsen–López-Tarrida–Portillo
quantum-graphs database, plus an invariant table over the top of every size. Answer: their
enumeration predates ours and **the contribution is reformulated** — exact certification and
maximization by absolute gap, not first enumeration. Counts agree exactly at n = 8 (498) and
n = 9 (16 533) and differ by **+8** at n = 10 (975 338 against 975 330). The per-graph
comparison was closed as *impossible* (the data files were never archived) and that was
**reversed on 2026-08-27**: Danielsen replied, the data live at `codetables.de/larsed/quantum_graphs/`,
sets agree name-by-name at n = 5…9 with **zero** α discrepancies over 992 398 graphs, and the
eight extra graphs at n = 10 are real — each carries an exact primal certificate ϑ > α. The
stage's own threshold hypothesis for those eight was refuted in the process. See
`REPORT_STAGE3.md` **and its dated amendment**; the body above the amendment is deliberately
not rewritten.

**Stage 4 question (closed):** does the observed maximum match what the tail of the Δ
distribution predicts? Answer: **the method is inapplicable, and that is the result** — Δ is
atomic, 60.8 % of the gapped graphs at n = 10 sitting on the single pentagon value √5 − 2, so
there is no density to fit. One stable anomaly survives every threshold, and it is at n = 9.
Nine of the ten n = 10 leaders are the nine-vertex optimum plus a vertex; C₆+K₃ does not
continue upward. Why 2/3 is reachable on nine vertices stayed open. See `REPORT_STAGE4.md`.

**Stage 5 question (closed):** the decomposition into layers by independence number,
D(n, a) = max{Δ : α(G) = a}. Answer: the gate passed on all six sizes — max over layers
reproduces every Δ_max(n) and every maximizer by graph6 code — but **both main predictions
missed**. The √5 − 2 atom does not split by layer, and 2/3 remains exactly as much of an
outlier inside its layer as outside, because layer a = 3 at n = 9 *is* 88 % of the gapped
graphs; there was almost nothing to unmix. See `REPORT_STAGE5.md`.

**Stage 6 question (closed):** the ceiling of ϑ, and n = 11 by full enumeration. Answer:
**Δ_max(11) = 0.7748885327…**, maximizer `` J?`D@pgd?{? ``, 17 edges, α = 4, and the maximum
is **unique** — one graph in the billion exceeds 0.7748, the next is 0.0202 lower. All
1 006 700 565 connected graphs covered, part-sum verified against `geng -c -u 11`; the
sandwich removed 89.98 % and 100 891 478 SDPs were solved in 71.8 h on 7 processes. **One
sealed prediction of ten hit, and it hit by coincidence** — the interval was built for layer
a = 3 and the value arrived from layer a = 4, whose own interval was exceeded. The
report is a dated running log, and the closing result sits at its `## Результат`, not at its
head. See `REPORT_STAGE6.md`.

**Stage 7 question (closed):** do the upper layers inherit from smaller sizes? Answer: the
**weak form is true and is a consequence of two published properties of ϑ**, not a new
theorem — the cone C_k(G) = {v} ∨ (G ⊔ K̄_{k−1}) shifts α and ϑ by exactly k−1 and carries Δ
across unchanged, so D(n, a) ≥ T(n, a). The inheritance boundary is a\* = 5 at both n = 9 and
n = 10. **All five sealed predictions hit** — against one of ten in Stage 6, because here a
consequence of a mechanism was predicted rather than a numerical series extrapolated. See
`REPORT_STAGE7.md`.

**Stage 7.1b question (closed):** an exact handle on Δ_max(11), which has no closed form.
Answer: a **certified rational enclosure**, Δ_max(11) ∈ [0.7748885327027013, 0.7748885327466875],
width 4.399·10⁻¹¹ — ten decimal digits fixed — with both ends explicit rationals in ℚ from
primal and dual certificates, and second place bounded strictly below the leader's lower end.
All sealed predictions hit. See `REPORT_STAGE7_1B.md`.

**Stage 8 question (closed):** does the *equality* half of inheritance hold? Answer: **no —
H7-S is refuted by certificate.** The counterexample is `` L@JC?_ASKAGPBH ``, n = 13, 19
edges, α = 5, with Δ ≥ 45375481648/55555555557 against a transfer bound of
12398216523947/16·10¹² — a strict inequality with margin 0.0419 in which **no floating-point
number appears**. The weak form is untouched. A replacement rule was sealed before any count
by it. A 2026-08-26 amendment corrected the tag on the *upper* bound — it needs a sweeping
argument to serve as a bound for T(13,5) — and the counterexample survived. See
`REPORT_STAGE8.md`.

**Stage 8-bis question (closed):** which of the two surviving inheritance formulas is right?
Answer: **outcome B, decided by the seal before the count** — the (12,5) target was not found
at ten times the budget while *every* control was found, so the instrument works and the
failure is evidence. It points **against our own** `a ≥ max(5, n − 6)` and toward
`a ≥ max(5, n − 7)`, and the two sub-cases cannot be separated with what we have. Only a full
n = 12 sweep would close it: 164 059 830 476 connected graphs, about 490 days at the measured
rate. **It will not be run** — the next step is a proof about the layers, and that is stated
as a decision, not as a "not yet". Half the rule still rests on the single (13,5) point. See
`REPORT_STAGE8BIS.md` and `OPEN_PROBLEM.md`.

**Stage 9 question (closed):** the algebraic degree of ϑ across the landscape, not just at
the top. Answer in the «Stage 9 additions» section below and in `REPORT_STAGE9.md`; the short
form is that extremal graphs are the algebraically *hardest* part of the landscape, that this
reverses how the project read its own series, and that **all three sealed hypotheses failed
their criteria** — the direction is recorded as measured but *not confirmed*.

Separate repository, own `.venv`. Nothing is imported from the earlier campaigns — not a
line of code, not a number.

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
bash runners/run_stage2.sh                        # Stage 2 end to end (~60 min)
bash runners/run_stage1.sh                        # Stage 1 end to end (~45 min)
.venv/bin/python tests/test_estimators.py         # gate R, ~5 s; blocks everything else
.venv/bin/python runners/run_0a.py                # calibration n=5,7,8; gate 0.a
.venv/bin/python runners/run_0b.py --n 8 9        # filters and their gate
.venv/bin/python runners/run_0c.py --n 9          # the sweep; --procs, --verify-top
.venv/bin/python runners/run_0d.py --n 9 --top 50 # structure; --restarts, --dstar 0
bash runners/run_stage0.sh                        # all of the above, in order
```

Stages 3–9 have no `run_stageN.sh`; they are individual runners, and several read data
already on disk rather than sweeping again.

```bash
bash scripts/verify_seals.sh                      # every preregistration vs its seal; run first
# Stage 3 — the database cross-check
.venv/bin/python runners/run_3b.py --top 10       # invariant table over the top of each size
.venv/bin/python runners/run_3c.py --top 10       # rationality vs symmetry; --dps
.venv/bin/python runners/run_db_compare.py        # per-graph vs the 2012 database; --sizes, --out
.venv/bin/python runners/certify_db_extras.py     # exact theta>alpha for the eight n=10 extras
.venv/bin/python runners/certify_positive_gap.py  # exact Delta>0 without the exact theta
# Stage 4 — the top anomaly (no new sweep; reads Stage 1-3 data)
.venv/bin/python runners/run_4a.py                # tail statistics; --round
.venv/bin/python runners/run_4bd.py               # who is on top at n=10, cheap hypotheses
.venv/bin/python runners/run_4c.py                # does C6+K3 continue upward
# Stage 5 — layers by independence number
.venv/bin/python runners/run_5a.py --procs 7      # the D(n,a) table; gate 5.a
.venv/bin/python runners/run_5bcef.py             # layer growth, crossings, atoms by layer
# Stage 6 — the ceiling of theta, and n=11
.venv/bin/python runners/run_6a.py --top 50       # fractional packing alpha*, the ceiling
.venv/bin/python runners/run_6ab.py --sizes 9 10  # the ceiling among graphs that have a gap
# the 6.c sweep is run_1c.py at --n 11: ~72 h on 7 procs, 4000 parts, resumable.
# NEVER launch it without a timestamped log — see the log-naming trap below.
# Stage 7 — inheritance of the upper layers
.venv/bin/python runners/run_7.py --trials 25     # H7 blocks 7.a-7.c; --seed, --out
.venv/bin/python runners/run_7_series.py          # series table, density, nesting
.venv/bin/python runners/certify_enclosure.py     # 7.1b: certified rational enclosure
                                                  #   --leader --second --dps --ladder --cs --out
# Stage 8 — the attack on the equality half
.venv/bin/python runners/run_8b.py --procs 7      # directed search; --restarts --steps --bis --add
.venv/bin/python runners/run_8c.py                # where the constants 5 and 6 come from
# Stage 9 — algebraic degrees
.venv/bin/python runners/run_9a_samples.py        # build the three samples FIRST; --only-c
.venv/bin/python runners/run_9a.py --procs 7      # the measurement and its three gates
.venv/bin/python runners/run_9b.py                # the three hypotheses, sealed criteria only
```

Each runner takes `--seed` (default 20260819) and writes one JSON into `results/`.
Nothing downstream of a failed gate should be run; the runners exit non-zero on failure
so `run_stage0.sh` stops on its own.

In `run_9a.py` the order of the gates is load-bearing, not cosmetic: two gates and the
Δ = 0 control sample run *before* anything unknown is measured, so that a broken
instrument is caught on graphs whose answer is already known exactly. Do not reorder it,
and do not reach for `--skip-gates` to save time.

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
- `build/nauty2_9_3/` — geng, built from the tarball in `sources/`; gitignored, rebuilt by
  `run_stage1.sh` if missing.

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

- **A log file name must carry a timestamp or a run id — never a bare name.** Writing
  `> results/run_6c_n11.log` twice destroys the first run's evidence silently, and a
  long run's log is often the *only* record of what happened: part timings, ETA drift,
  where it was restarted. This has now cost the traces of a run twice, neither time
  through an error in the mathematics. Use

  ```bash
  LOG=results/run_6c_n11_$(date +%Y%m%dT%H%M%S).log
  setsid nohup .venv/bin/python -u runners/run_1c.py ... > "$LOG" 2>&1 < /dev/null &
  ```

  `results/*.log` stays gitignored — the point is not to commit them but to stop them
  overwriting each other while the work is live. The same applies to any file a re-run
  would clobber: `run_2b.py` needed `--out` for exactly this reason.

- **Three points do not distinguish two formulas when one degenerates into the other
  over that range.** Twice now a coincidence on three consecutive sizes was taken for a
  law. The graph-count growth ratio: 85.9 was a measured one-step ratio (n = 10 → 11)
  presented as a constant of the series, and the ratios 23.5, 44.9, 85.9, 163.0 were all
  computable from counts already in hand — they double each step. The inheritance
  boundary: `a >= 5` and `a >= max(5, n - 6)` are *identically equal* at n = 9, 10, 11,
  because max(5, n-6) is 5 at all three; three complete enumerations could not tell them
  apart, and the campaign carried the wrong one through three stages until a
  counterexample at n = 13 separated them.

  Before calling a pattern on k points a law, write down at least one alternative
  formula that agrees with it on those k points and check whether any available data
  separates them. If none does, say so in the claim: "consistent with, and not
  distinguished from, X on this range." Both errors above would have been caught by that
  question and by nothing else.

## Regenerating the bulk data

`results/n9_all.csv` (29 MB, all 261 080 rows) is gitignored; the committed copy is
`results/n9_all.csv.gz`. `gunzip -k results/n9_all.csv.gz` restores what `run_0b.py`
reads. Deleting it and re-running `run_0c.py` also works — the chunk checkpoints in
`results/n9_partial_*.csv` make the sweep resumable, and a full cold run is ~6.5 min.


## Stage 1 additions

- **`geng` is the enumerator**, streamed via `quadc5/gengstream.py`, split with `res/mod`.
  **Do not pass `-l`.** McKay's published `graph{n}c.g6` files are in geng's *default*
  labelling; `-l` produces a different canonical form and 260 902 of 261 080 codes then
  fail to match. This was measured, not assumed, and it contradicts what Stage 1's own
  preregistration guessed.
- **`quadc5/qfield.py`** is exact arithmetic in Q(√d) with an exact PSD test (pivoted
  Schur complement) and exact Gaussian elimination. `runners/certify.py` uses it to prove
  a θ value: recognise the numerical optimum over a field, then verify exact feasibility,
  exact PSD, and an exact dual from complementary slackness. Soundness does not depend on
  how the candidate was found — only on the three exact checks.
- **τ_zero must scale with n.** 1e-9 was below the solver noise at n = 8/9; 1e-6 is below
  it at n = 10 (measured floor 1.9e-6 over 10⁵ provably-zero graphs, smallest genuine gap
  5.894e-4). Always measure the empty band and take the threshold inside it, and report
  the measurement next to the verdict.
- **F1 ⊆ F2 always** (perfection implies χ(Ḡ) = ω(Ḡ) = α), verified on all 11 716 571
  graphs at n = 10. The brief's "perfect graphs plus χ(Ḡ)=α" filter pair is just F2.
- **`geng -P` is the external check** on `quadc5/perfect.py`: counts matched exactly at
  n = 8, 9 and 10 (7 805 / 126 777 / 3 122 221).
- **η_d at n = 10 is expensive** — roughly 700 CPU-seconds per graph for d = 2…4 at 300
  restarts. Budget for it, or cut restarts and say so.


## Stage 2 additions

- **`quadc5/hiprec.py`** refines the theta optimum to arbitrary precision by Gauss-Newton
  on the KKT system in mpmath, seeded from CLARABEL. Digits double per iteration; 240 dps
  gives ~236 honest digits in seconds. Honest digits are *measured* (matching prefix of a
  `dps` and a `2·dps` run, minus 5), never taken from the solver's own residual.
- **`quadc5/numfield.py`** is exact arithmetic in ℚ(θ) for arbitrary degree — the degree-2
  `qfield.py` generalised. Signs are decided exactly: zero test on the coordinate vector,
  then bisection of a certified rational isolating interval until the rational interval
  hull of the value excludes zero. **No floating point in that layer.** Two independent
  PSD tests: pivoted Schur complement and all principal minors.
- **SDPA-GMP was not used** and does not need to be: GMP/MPFR headers are absent and root
  is not available, and the high-precision value is only a search input — the result is a
  certificate that does not depend on any solver. Do not spend time building it.
- **A found polynomial is never the answer.** PSLQ output is a hypothesis for the
  certificate step. This is the exact error the source's authors admitted to (S1.9), and
  the whole point of Stage 2 is not repeating it.
- **Calibrate on C₇ before touching anything unknown.** Its ϑ is a known cubic, so it
  exercises the entire degree-≥3 pipeline end to end; `runners/certify_nf.py` runs it first.


## Stage 9 additions

- **Agreement between two precision levels is evidence of STABILITY, not of accuracy.**
  This is the load-bearing one, and it corrects a Stage 2 method that had only ever
  been calibrated on non-degenerate values. Gauss–Newton on some degenerate optima
  settles on a fixed point that is *not* the optimum, and every precision level then
  reproduces that same wrong point. Measured on `GCY^fW`: the values at dps 960, 1920
  and 3840 agree with **each other** to 465 and 945 digits, while agreeing with the
  truth ϑ = α = 3 to only **359**. The honest-digit rule "matching prefix of a dps run
  and a 2·dps run, minus 5" reported 945 honest digits for a value correct to 359.

  The **residual** separates the two cleanly and by mechanism, not by a tuned
  threshold: a converged run has residual ≈ 10^−dps, so doubling dps drops it by
  hundreds of orders (3.06e-241 → 5.65e-482 for `DUW`); a stalled run returns the
  *identical* residual at every precision (1.44e-31 at both 240 and 480 for `FCRto`).
  **Verify convergence before trusting any inter-level digit count.** Where the
  residual does not scale, the value is not measurable by this instrument, and the
  honest report is to say so and count it — never to guess.

- **A check that runs at the same precision as the thing it checks is not a check.**
  The confirmation step re-runs PSLQ at higher precision to kill spurious hits. The
  first implementation hard-coded its level instead of deriving it from the level the
  search actually used; for graphs that had escalated the two coincided,
  `matching_digits` compared a value with *itself*, and the count came back as the
  full `dps` — 955 fabricated digits for a value correct to 389. **Derive the check's
  precision from the measurement's; never write it as a constant**, and make the
  self-comparison raise rather than return a number that will pass for a good one.

- **Bit-identical values from two DIFFERENT precisions are the strongest agreement
  available, not the weakest.** For a Δ = 0 graph ϑ is the integer α and the
  refinement lands on it exactly, so every level returns the same value. The first
  correction to the bug above treated that as "uninformative" — and sent 304 such
  graphs escalating to the precision ceiling, reporting 297 of them as
  `low_precision`. Two wrong corrections in one afternoon, both caught by the same
  gate. When a fix makes a *previously passing* population fail, the fix is the
  suspect, not the population.

- **The gate caught all of it, and it caught it where the answer was already known.**
  That is what the Δ = 0 control sample is for: on a Δ > 0 graph a wrong value still
  looks like a plausible algebraic number, and none of the above would have been
  visible. It surfaced only because the truth on those graphs is the exact integer α,
  computed by an independent route. **When designing a calibration sample, prefer
  inputs whose answer is known *exactly* over inputs that merely look
  representative** — and make the gate compare against that exact answer, not against
  a weaker property the answer happens to have.

- **A public text may never claim more than a non-public one.** README, release notes and
  the archive description are read by people who will never open the report, so an
  overstatement there is the one that travels. Stage 9's result was tagged `[observed]` in
  the paper — direction measured on four sizes, sealed threshold met on one, all three
  hypotheses failed — while the README's opening presented it as established and mentioned
  none of that. **When the two disagree, bring the stronger one down to the weaker**, never
  the reverse. The check is cheap and belongs in every release: read the public summary and
  the paper's abstract back to back, as one text, and treat any place the summary promises
  more as a defect.

  **Three instances in three days, and the shape is identical every time:** a fact changes,
  the edit lands where the change was noticed, and the *other* places that asserted the old
  fact keep asserting it — the database's unavailability, Stage 9's direction as fact, and
  then a sentence saying we archive data we had just decided not to redistribute. The last
  landed on the most sensitive subject there is, other people's rights. So the check is not
  "did I update the text": it is **grep for the old claim and confirm zero hits** before
  calling an edit done.

- **Correcting a claim means sweeping EVERY text in the project at once, not the document
  where it was noticed.** Fourth instance in a row, same shape: the redistribution sentence
  was fixed in `README.md` on 2026-08-27 and the identical claim sat untouched in
  `papers/paper_A` §1.2 for a week. The unit of repair is the project, not the file. The
  sweep runs over the papers, `README.md`, `SOURCES.md`, `CLAUDE.md`, the stage reports,
  `CITATION.cff`, the GitHub release notes (`gh release view <tag> --json body`) and the
  **Zenodo record description** (`curl https://zenodo.org/api/records/<id>`) — the last two
  live outside the working tree and no `grep .` will ever reach them.

  **A plain multi-word grep gives false zeros here, and it did.** These files are
  hard-wrapped, so "archived here" was split across a newline and `grep -rn "archived here"`
  reported the paper clean while the sentence was sitting in it. Flatten whitespace before
  matching — read each file, `re.sub(r"\s+", " ", text)`, then search — and search for the
  *idea* with several phrasings rather than the one wording you remember. Zero hits from a
  line-oriented grep is not evidence.

- **An audit means the whole document, not the sentence that was reported.** This has now
  cost twice. The claim that Δ_max(11) was proved sat in five places when three were named;
  the claim that the database was unretrievable sat in four. Grep for the *idea*, not for
  the wording, and read the sections that only touch it in passing — table captions,
  appendix rows, abstracts.

- **State a decision as a decision.** "Not yet computed" and "will not be computed" read
  completely differently to a reader deciding whether to wait for you. Twelve vertices is
  164 059 830 476 graphs and about 490 days at our measured rate; the honest form is that it
  will not be run and the next step is a proof about the layers, not a bigger sweep.

- **Name an absence rather than filling it.** The papers say plainly that this work is about
  the number ϑ and not about physical realisability, that d\* is a lower bound from a
  heuristic, and that we have no upper bounds on η₃ — and neither does the work we continue.
  Where a reader will expect something we do not have, the boundary of the work is itself
  worth stating; silence there reads as oversight rather than as choice.
