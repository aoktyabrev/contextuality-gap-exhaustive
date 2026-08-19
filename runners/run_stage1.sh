#!/usr/bin/env bash
# QUADC5 Stage 1 (n = 10), end to end.  Every block gates the next.
#   bash runners/run_stage1.sh [SEED]
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python
SEED="${1:-20260819}"

if [ ! -x build/nauty2_9_3/geng ]; then
  echo "### building nauty (geng)"
  mkdir -p build && tar xzf sources/nauty2_9_3.tar.gz -C build
  ( cd build/nauty2_9_3 && ./configure >/dev/null && make -j8 geng >/dev/null )
fi

echo "### gate R -- estimators on random inputs"
$PY tests/test_estimators.py

echo "### 1.a -- the generator and its gate"
$PY runners/run_1a.py

echo "### 1.c -- exhaustive sweep over n=10 (resumable; ~26 min on 7 procs)"
$PY runners/run_1c.py --n 10 --mod 224 --procs 7 --seed "$SEED"

echo "### 1.b -- filters, external cross-check against geng -P, and the gate"
$PY runners/run_1b.py --n 10 --mod 224 --procs 7 --seed "$SEED" --tau-zero 1e-5

echo "### 1.d -- exact certificates for the n=10 top-5 and the n=9 rank-2 thread"
$PY runners/certify.py 'ICRb`yiu?' 'ICQeR`[Mg' 'ICRbcqhNO' 'ICQ`fP[r_' 'ICRbdO{xG' \
    --out results/certificates_n10_top5.json
$PY runners/certify.py 'HCrb`qi' --out results/certificate_n9_rank2.json

echo "### 1.e / 1.f -- the series over n = 5..10 and the invariants"
$PY runners/run_1ef.py --seed "$SEED"

echo "### d* over the n=10 top-50"
$PY runners/run_0d.py --n 10 --top 50 --restarts 150 --procs 5 --seed "$SEED"

echo "### done -- results/ holds every CSV and JSON quoted in REPORT_STAGE1.md"
