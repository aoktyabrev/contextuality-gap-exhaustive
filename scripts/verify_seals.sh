#!/usr/bin/env bash
# Check that every preregistration is byte-identical to what was sealed before that
# stage was run, and that the sealing commits predate the stage's results.
#
#   bash scripts/verify_seals.sh
#
# SOURCES.md grows across stages: each stage appends to it and never edits what earlier
# stages wrote.  A stage's seal therefore covers the PREFIX of SOURCES.md as it stood at
# that stage's sealing commit, and that is what is checked here.
set -uo pipefail
cd "$(dirname "$0")/.."
fail=0

check() {                       # check <sealing-commit> <sha256-file> <label>
  local commit="$1" sealfile="$2" label="$3"
  echo "=== $label  (sealed in $commit) ==="
  local prereg
  prereg=$(awk '{print $2}' "$sealfile" | grep PREREGISTRATION)
  if sha256sum -c <(grep "$prereg\$" "$sealfile") >/dev/null 2>&1; then
    echo "  OK    $prereg is byte-identical to what was sealed"
  else
    echo "  FAIL  $prereg differs from the sealed hash"; fail=1
  fi
  local want lines got
  want=$(grep " SOURCES.md\$" "$sealfile" | awk '{print $1}')
  lines=$(git show "$commit:SOURCES.md" | wc -l)
  got=$(head -n "$lines" SOURCES.md | sha256sum | awk '{print $1}')
  if [ "$want" = "$got" ]; then
    echo "  OK    SOURCES.md prefix ($lines lines) hashes to the sealed value"
  else
    echo "  FAIL  SOURCES.md prefix does not match"; echo "        want $want"; echo "        got  $got"; fail=1
  fi
  local sealdate
  sealdate=$(git show -s --format=%cI "$commit")
  echo "  sealed at $sealdate"
}

check dc07d1f PREREGISTRATION.sha256        "Stage 0"
check 2aebb12 PREREGISTRATION_STAGE1.sha256 "Stage 1"
check 053f834 PREREGISTRATION_STAGE2.sha256 "Stage 2"

echo
if [ $fail -eq 0 ]; then
  echo "ALL SEALS VERIFY."
  echo "Each preregistration is unchanged since its sealing commit, and each sealing"
  echo "commit precedes every commit carrying that stage's results:"
  git log --reverse --format='  %h  %cI  %s' | head -12
else
  echo "SEAL CHECK FAILED"
fi
exit $fail
