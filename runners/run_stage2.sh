#!/usr/bin/env bash
# QUADC5 Stage 2 -- close the eight-vertex hole.  Every block gates the next.
#   bash runners/run_stage2.sh
set -euo pipefail
cd "$(dirname "$0")/.."
PY=.venv/bin/python

echo "### gate R -- estimators on random inputs"
$PY tests/test_estimators.py

echo "### 2.a -- high precision and its calibration gate (four already-proved values)"
$PY runners/run_2a.py --dps 120

echo "### 2.b -- integer-relation search; the polynomials found are CANDIDATES"
$PY runners/run_2b.py --dps 240

echo "### 2.c -- exact certificates over Q(theta); the only thing that counts"
$PY runners/certify_nf.py --dps 200

echo "### 2.d -- the same for the n=10 rank 2, deeper search for the negative bound"
$PY runners/run_2b.py --dps 480 --codes 'ICQeR`[Mg' \
   --degrees 2 3 4 6 8 --extra-degrees 5 7 9 10 12 14 16 18 20 24 28 32 40 48 \
   --out results/report_2d.json

echo "### 2.e -- symmetry against the degree of the field"
$PY runners/run_2e.py

echo "### done -- results/ holds every JSON quoted in REPORT_STAGE2.md"
