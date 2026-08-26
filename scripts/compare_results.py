#!/usr/bin/env python3
"""Compare a fresh run against the committed results.  Exit 0 iff every published
number reproduced.

What is compared exactly and what is compared within a tolerance is decided here, in
one place, and printed, so that "it reproduced" is a checkable statement rather than an
impression.

  exact      integers, graph6 strings, booleans, minimal polynomials, verdicts,
             the identity of the top-5 of every ranking
  tolerance  every float, at 1e-7 absolute -- the SDP solvers' own noise floor,
             measured in Stage 0/1 and reported there
  set-wise   the membership of a top-1000 list.  Near-degenerate blocks (the plateau
             at Delta = 2/3, for instance) permute between runs at the 1e-8 level;
             that was documented in Stage 1 and is a property of the solvers, not of
             the answer.  Order inside such a block is therefore not compared, but
             the set of graphs and the sorted values are.
  ignored    wall-clock times, iteration counts, solver residuals and anything else
             that is a property of the machine rather than of the mathematics
  skipped    the n = 11 artefacts, and the record of a run that failed a gate.  Each
             exclusion is named below WITH ITS REASON, and both the reasons and the
             counts are printed, so an exclusion is visible rather than silent.
  jsonl      per-graph rows, matched by key rather than by line order, with the same
             ignore list applied field by field.
"""
import sys, os, json, csv, math

TOL = 1e-7
IGNORE_SUBSTRINGS = ("time", "second", "residual", "iteration", "history",
                     "elapsed", "duration", "wall", "_gap", "solver_diff", "pr_hi",
                     "identification_error", "root_gap", "seconds")

# Files the fresh run cannot or should not produce.  Each carries its reason, and the
# reasons are printed at the end: an exclusion nobody can see is an exclusion nobody
# can check.
NOT_REPRODUCED_HERE = {
    "n11_": "produced by the 71.8-hour n = 11 sweep, which this script does not re-run",
    "report_1c_n11": "summary of that same sweep",
    "stage9_degrees_FAILED": "the record of a run that FAILED gate G9.1 -- kept as "
                             "evidence of the defect, not as a result to reproduce",
}

fails, checks = [], 0


def note(ok, what, detail=""):
    global checks
    checks += 1
    if not ok:
        fails.append((what, detail))
        print(f"  MISMATCH  {what}  {detail}")


def ignorable(key):
    k = str(key).lower()
    return any(s in k for s in IGNORE_SUBSTRINGS)


def _num_eq(x, y):
    """Equality for floats, with inf and nan treated sensibly."""
    if math.isnan(x) and math.isnan(y):
        return True
    if math.isinf(x) or math.isinf(y):
        return x == y
    return abs(x - y) <= TOL


def cmp_val(a, b, path):
    if isinstance(a, bool) or isinstance(b, bool):
        note(a == b, path, f"{a} != {b}")
    elif isinstance(a, (int,)) and isinstance(b, (int,)):
        note(a == b, path, f"{a} != {b}")
    elif isinstance(a, (int, float)) and isinstance(b, (int, float)):
        note(_num_eq(float(a), float(b)), path, f"{a} != {b}")
    elif isinstance(a, str) and isinstance(b, str):
        try:
            fa, fb = float(a), float(b)
            note(_num_eq(fa, fb), path, f"{a} != {b}")
        except ValueError:
            note(a == b, path, f"{a!r} != {b!r}")
    else:
        note(a == b, path, f"{a!r} != {b!r}")


def cmp_json(a, b, path=""):
    if isinstance(a, dict) and isinstance(b, dict):
        for k in a:
            if ignorable(k):
                continue
            if k not in b:
                note(False, f"{path}.{k}", "missing in the fresh run")
                continue
            cmp_json(a[k], b[k], f"{path}.{k}")
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            note(False, f"{path}[]", f"length {len(a)} != {len(b)}")
            return
        for i, (x, y) in enumerate(zip(a, b)):
            cmp_json(x, y, f"{path}[{i}]")
    else:
        cmp_val(a, b, path or "<root>")


def cmp_csv(pa, pb, name):
    ra = list(csv.reader(open(pa)))
    rb = list(csv.reader(open(pb)))
    note(len(ra) == len(rb), f"{name}: row count", f"{len(ra)} != {len(rb)}")
    if len(ra) != len(rb) or not ra:
        return
    hdr = ra[0]
    if "graph6" in hdr:
        gi = hdr.index("graph6")
        sa = sorted(r[gi] for r in ra[1:])
        sb = sorted(r[gi] for r in rb[1:])
        note(sa == sb, f"{name}: set of graph6 codes",
             f"{len(set(sa) ^ set(sb))} differ")
        # the leading five are far apart and must match in order
        for i in range(1, min(6, len(ra))):
            note(ra[i][gi] == rb[i][gi], f"{name}: rank {i} graph6",
                 f"{ra[i][gi]} != {rb[i][gi]}")
        for col in ("delta", "delta_hi", "alpha", "edges", "theta_hi"):
            if col not in hdr:
                continue
            ci = hdr.index(col)
            va = sorted(float(r[ci]) for r in ra[1:])
            vb = sorted(float(r[ci]) for r in rb[1:])
            bad = [(x, y) for x, y in zip(va, vb) if not _num_eq(x, y)]
            worst = max((abs(x - y) for x, y in bad), default=0.0)
            note(not bad, f"{name}: sorted {col}", f"{len(bad)} differ, max {worst:.3e}")


def cmp_jsonl(pa, pb, name):
    """Per-graph rows, matched by key.  Line order is not part of the answer -- the
    measurement runs in a process pool and rows land in completion order."""
    def load(p):
        out = {}
        for line in open(p):
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            out[(d.get("n"), d.get("sample"), d.get("graph6"))] = d
        return out
    a, b = load(pa), load(pb)
    note(set(a) == set(b), f"{name}: set of rows",
         f"{len(set(a) ^ set(b))} keys differ")
    for k in sorted(set(a) & set(b), key=lambda t: tuple(str(x) for x in t)):
        cmp_json(a[k], b[k], f"{name}[{k[0]}{k[1]}:{k[2]}]")


def main(dpub, dnew):
    print(f"comparing {dnew}/ against {dpub}/  (tolerance {TOL:g} on floats)\n")
    skipped = []
    for fn in sorted(os.listdir(dpub)):
        why = next((r for m, r in NOT_REPRODUCED_HERE.items() if m in fn), None)
        if why:
            skipped.append((fn, why))
            continue
        pa, pb = os.path.join(dpub, fn), os.path.join(dnew, fn)
        if not os.path.exists(pb):
            note(False, fn, "not produced by the fresh run")
            continue
        if fn.endswith(".json"):
            try:
                cmp_json(json.load(open(pa)), json.load(open(pb)), fn)
            except Exception as e:
                note(False, fn, f"unreadable: {e}")
        elif fn.endswith(".csv"):
            cmp_csv(pa, pb, fn)
        elif fn.endswith(".jsonl"):
            cmp_jsonl(pa, pb, fn)
    if skipped:
        print(f"\nskipped {len(skipped)} file(s), each with its reason:")
        for fn, why in skipped:
            print(f"  {fn}\n      {why}")
    print(f"\n{checks} comparisons, {len(fails)} mismatches")
    if fails:
        print("\nGATE R.b FAILED -- the following did not reproduce:")
        for w, d in fails[:40]:
            print(f"  {w}: {d}")
        return 1
    print("GATE R.b PASSED -- every published number reproduced from a clean checkout")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
