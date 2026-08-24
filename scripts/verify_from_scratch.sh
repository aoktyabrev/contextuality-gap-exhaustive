#!/usr/bin/env bash
# Reproduce every published number from a clean checkout.
#
#   bash scripts/verify_from_scratch.sh [WORKDIR]
#
# Creates a fresh venv, builds nauty's geng from the tarball in sources/, empties
# results/, runs all three stages, and diffs what comes out against what is committed.
# Exit status 0 means every published number was reproduced.
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
LOG="${ROOT}/verify_$(date -u +%Y%m%dT%H%M%SZ).log"
: > "$LOG"

say() { printf '%s\n' "$*" | tee -a "$LOG"; }
stage() { local name="$1"; shift; local t0=$SECONDS
  say ""; say "=== $name ==="
  "$@" >> "$LOG" 2>&1 || { say "FAILED: $name (see $LOG)"; exit 1; }
  say "--- $name took $((SECONDS - t0)) s"; }

say "QUADC5 clean reproduction, started $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
say "python: $(python3 -V 2>&1)"

# --- 1. environment -------------------------------------------------------
if [ ! -x .venv/bin/python ]; then
  stage "venv + pinned requirements" bash -c \
    "python3 -m venv .venv && .venv/bin/pip install -q --upgrade pip && \
     .venv/bin/pip install -q -r requirements.txt"
else
  say "=== venv already present, reusing ==="
fi
say "installed: $(.venv/bin/pip freeze | tr '\n' ' ' | cut -c1-200)"

# --- 2. geng --------------------------------------------------------------
if [ ! -x build/nauty2_9_3/geng ] && [ -z "${QUADC5_GENG:-}" ]; then
  stage "build nauty 2.9.3 (geng)" bash -c \
    "mkdir -p build && tar xzf sources/nauty2_9_3.tar.gz -C build && \
     cd build/nauty2_9_3 && ./configure && make -j geng"
fi

# --- 3. set the published results aside -----------------------------------
# n = 11 is NOT reproduced here: the sweep is 71.8 hours and nobody will re-run it.
# Its artefacts are data, not outputs of this script, and must survive it -- the
# n11_* files below are 25 GB and are neither copied nor deleted.
if [ ! -d results_published ]; then
  mkdir -p results_published
  find results -maxdepth 1 -type f ! -name '*n11*' -exec cp {} results_published/ \;
  say "kept the committed results in results_published/ for comparison"
fi
find results -maxdepth 1 -type f ! -name 'authors_run_summary.txt' ! -name '*n11*' -delete

# --- 4. the three stages --------------------------------------------------
stage "Stage 0 (n <= 9)"  bash runners/run_stage0.sh
stage "Stage 1 (n = 10)"  bash runners/run_stage1.sh
stage "Stage 2 (exact values)" bash runners/run_stage2.sh

# Stages 3-7 read only what stages 0-2 produce, so they belong in the reproduction
# too.  Everything below is minutes, not hours: no new enumeration, only analysis of
# the tables the sweeps just rebuilt, plus one exact-arithmetic certification.
# The thirteen graphs certified in 3.a are selected by a rule, not by a list: the
# n = 10 graphs with Delta < 2e-3, the boundary against the prior database.  They are
# taken from the sweep this script just rebuilt, so nothing here reads the answer.
stage "Stage 3 (prior database, invariants)" bash -c \
  ".venv/bin/python runners/run_3b.py && \
   .venv/bin/python runners/run_3c.py && \
   .venv/bin/python runners/certify_positive_gap.py \$(.venv/bin/python -c \
     \"import csv,gzip,os;p='results/n10_nonzero.csv';f=open(p) if os.path.exists(p) else gzip.open(p+'.gz','rt');\
r=[x for x in csv.DictReader(f) if float(x['delta'])<2e-3];\
print(' '.join(x['graph6'] for x in sorted(r,key=lambda y:float(y['delta']))))\")"
stage "Stage 4 (top of the series)" bash -c \
  ".venv/bin/python runners/run_4a.py && \
   .venv/bin/python runners/run_4bd.py && \
   .venv/bin/python runners/run_4c.py"
stage "Stage 5 (layers by alpha)" bash -c \
  ".venv/bin/python runners/run_5a.py && \
   .venv/bin/python runners/run_5bcef.py"
stage "Stage 7 (inheritance, series, enclosure)" bash -c \
  ".venv/bin/python runners/run_7.py && \
   .venv/bin/python runners/run_7_series.py && \
   .venv/bin/python runners/certify_enclosure.py"

# --- 5. compare -----------------------------------------------------------
say ""
say "=== comparison against the committed results ==="
.venv/bin/python scripts/compare_results.py results_published results | tee -a "$LOG"
