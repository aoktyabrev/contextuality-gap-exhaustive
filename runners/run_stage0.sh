#!/usr/bin/env bash
# QUADC5 Stage 0, end to end.  Every block is a gate for the next one.
#   bash runners/run_stage0.sh [SEED]
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
SEED="${1:-20260819}"

echo "### gate R -- estimators on random inputs"
$PY tests/test_estimators.py

echo "### 0.a -- calibration on n=5, 7, 8 (gate)"
$PY runners/run_0a.py

echo "### 0.a-code -- the authors' own script, in its own venv (optional cross-check)"
if [ -x .venv-authors/bin/python ]; then
  mkdir -p authors_run && cp -n sources/quadc5_authors_repo/* authors_run/ 2>/dev/null || true
  ( cd authors_run && ../.venv-authors/bin/python -u certification.py ) \
    > results/authors_run_asshipped.log 2>&1 || echo "   (authors' script exited non-zero; see log)"
else
  echo "   skipped: .venv-authors not present.  This step re-runs the ORIGINAL authors'"
  echo "   code and is a cross-check only -- none of the published numbers depend on it."
  echo "   To enable:  python3 -m venv .venv-authors &&" \
       ".venv-authors/bin/pip install numpy networkx cvxpy scipy matplotlib tqdm mpmath"
fi

echo "### 0.c -- exhaustive sweep over n=9"
$PY runners/run_0c.py --n 9 --seed "$SEED"

echo "### 0.c-third -- third-solver check on the leading block"
$PY runners/run_third_solver.py --n 9 --top 100

echo "### 0.b -- pre-SDP filters and gate B-sound (needs both sweeps)"
$PY runners/run_0b.py --n 8 9

echo "### exact certificate for the n=9 maximizer"
$PY runners/certify_n9_max.py

echo "### 0.d -- structure of the top-50"
$PY runners/run_0d.py --n 9 --top 50 --seed "$SEED"

echo "### done -- results/ holds every CSV and JSON quoted in REPORT.md"
