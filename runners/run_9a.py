"""Stage 9, block 9.a -- the mass measurement and its three gates.

Order is not cosmetic.  G9.3 and G9.2 run before any sample is measured, and the
C sample runs before A and B, so that a broken instrument is caught on graphs whose
answer is already known rather than on the graphs the stage is about.

  G9.3  |Aut| by two independent routes (repository rule)
  G9.2  regression: twelve graphs with degrees published in REPORT_STAGE2
  G9.1  sample C: degree 1 AND root equal to an independently computed alpha
  then  samples A and B

Results append to results/stage9_degrees.jsonl, one JSON per graph, so the run is
resumable and a kill never costs measured graphs.
"""
import sys, os, json, time, argparse, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from multiprocessing import Pool

from quadc5.g6 import decode_g6, edges_of
from quadc5.alpha import alpha_bitmask
from quadc5.theta import theta_cvxpy
from quadc5.hiprec import refine
from quadc5.algdeg import (theta_honest, find_minpoly, matching_digits, _dual_start,
                           higher, aut_dreadnaut, aut_networkx, vertex_orbits,
                           MIN_HONEST, DEGREES, budget)
from mpmath import mp, nstr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
JSONL = os.path.join(RES, "stage9_degrees.jsonl")

# PREREGISTRATION_STAGE9 2.6, gate G9.2.  Degrees as published in REPORT_STAGE2.md.
REGRESSION = [
    ("n=5 max",     "DUW",         2),
    ("n=6 max",     "EUZw",        2),
    ("n=7 max",     "FCp`_",       3),
    ("n=8 max",     "GCQb`o",      4),
    ("n=9 max",     "HCRbdO{",     1),
    ("n=9 rank 2",  "HCrb`qi",     2),
    ("n=10 max",    "ICRb`yiu?",   2),
    ("n=10 rank 3", "ICRbcqhNO",   1),
    ("n=10 rank 4", "ICQ`fP[r_",   1),
    ("n=10 rank 5", "ICRbdO{xG",   1),
    ("n=10 rank 2", "ICQeR`[Mg",   None),      # not found, and must stay not found
    ("n=11 max",    "J?`D@pgd?{?", None),
]


def measure(task):
    """One graph, end to end.  Runs in a worker process."""
    n_key, sample, code = task
    t_start = time.time()
    try:
        n, adj = decode_g6(code)
        edges = edges_of(n, adj)
        a = alpha_bitmask(n, adj)
        r = theta_honest(code=code, dps=240)     # escalates on its own, 2.2
        D = r["honest"]
        prec = "ok" if (D is not None and D >= MIN_HONEST) else "low_precision"

        cache = {}

        def confirm():
            """A strictly higher precision than the search used -- never the same one."""
            if "v" not in cache:
                t2, D2, d2 = higher(r)
                cache["v"] = (t2, D2)
                cache["dps"] = d2
            return cache["v"]

        if prec == "low_precision":
            m = dict(degree=None, poly=None, status="low_precision", ladder=[],
                     confirmed_at=None)
        else:
            m = find_minpoly(r["theta"], D, confirm=confirm)

        aut = aut_dreadnaut(n, adj)
        orb = vertex_orbits(n, adj)
        mp.dps = 60
        return dict(n=n, sample=sample, graph6=code, edges=len(edges), alpha=a,
                    delta=float(r["theta"]) - a, honest=D, precision=prec,
                    rank=r["rank"], aut=aut, orbits=orb,
                    dps_used=r["dps_used"], confirm_dps=cache.get("dps"),
                    plateau=r["plateau"],
                    degree=m["degree"], poly=m["poly"], status=m["status"],
                    confirmed_at=m.get("confirmed_at"),
                    theta=nstr(r["theta"], 50), seconds=round(time.time() - t_start, 1))
    except Exception as exc:
        return dict(n=n_key, sample=sample, graph6=code, status="error",
                    error=f"{type(exc).__name__}: {exc}",
                    seconds=round(time.time() - t_start, 1))


def load_done():
    done = {}
    if os.path.exists(JSONL):
        with open(JSONL) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                done[(d["n"], d["sample"], d["graph6"])] = d
    return done


def run_tasks(tasks, procs, label):
    done = load_done()
    todo = [t for t in tasks if t not in done]
    print(f"  {label}: {len(tasks)} graphs, {len(tasks)-len(todo)} already measured, "
          f"{len(todo)} to do")
    if not todo:
        return [done[t] for t in tasks]
    t0 = time.time()
    with open(JSONL, "a") as out, Pool(procs) as pool:
        for k, d in enumerate(pool.imap_unordered(measure, todo, chunksize=1), 1):
            out.write(json.dumps(d) + "\n")
            out.flush()
            done[(d["n"], d["sample"], d["graph6"])] = d
            if k % 10 == 0 or k == len(todo):
                el = time.time() - t0
                print(f"    {k}/{len(todo)}  {el/60:.1f} min elapsed, "
                      f"~{el/k*(len(todo)-k)/60:.1f} min left", flush=True)
    return [done[t] for t in tasks if t in done]


def gate_aut(samples, procs, rng):
    print("\n=== GATE G9.3 -- |Aut| by two independent routes ===")
    print("  catches: an indexing slip in one route that the other does not share;")
    print("  a capped enumeration silently reported as an exact count.")
    checks, bad, capped = [], 0, 0
    for n_s, s in sorted(samples.items(), key=lambda kv: int(kv[0])):
        n = int(n_s)
        pool = s["A"] + s["B"]
        pick = pool if n <= 9 else rng.sample(pool, min(30, len(pool)))
        for code in pick:
            nn, adj = decode_g6(code)
            a1 = aut_dreadnaut(nn, adj)
            a2, _ = aut_networkx(nn, adj)
            if a2 is None:
                capped += 1
                continue
            checks.append((code, a1, a2))
            if a1 != a2:
                bad += 1
                print(f"  FAIL {code}: dreadnaut {a1} vs networkx {a2}")
    print(f"  {len(checks)} graphs cross-checked, {bad} mismatches, "
          f"{capped} above the 200000 cap (excluded, not silently counted)")
    return bad == 0, dict(checked=len(checks), mismatches=bad, capped=capped)


def gate_regression(procs):
    print("\n=== GATE G9.2 -- regression on twelve already-published degrees ===")
    print("  catches: a wrong height budget or a broken honest-digit measure, either")
    print("  of which changes degrees silently -- every value stays 'some polynomial'.")
    tasks = [(int(code and decode_g6(code)[0]), "R", code) for _, code, _ in REGRESSION]
    got = run_tasks(tasks, procs, "regression")
    bym = {d["graph6"]: d for d in got}
    ok, rows = True, []
    for label, code, want in REGRESSION:
        d = bym.get(code, {})
        have = d.get("degree") if d.get("status") == "hit" else None
        good = (have == want)
        ok &= good
        rows.append(dict(label=label, graph6=code, expected=want, got=have,
                         status=d.get("status"), honest=d.get("honest"),
                         verdict="PASS" if good else "FAIL"))
        print(f"  {'PASS' if good else 'FAIL'} {label:12s} {code:13s} "
              f"expected {str(want):9s} got {str(have):9s} ({d.get('status')}, "
              f"D={d.get('honest')})")
    return ok, rows


def gate_C(samples, procs):
    print("\n=== GATE G9.1 -- sample C: degree 1 AND root equal to alpha ===")
    print("  catches: an edge-list transposition or the wrong seed graph.  On a graph")
    print("  with Delta > 0 a wrong value still looks plausible; on a Delta = 0 graph")
    print("  the truth is the exact integer alpha, so any such slip shows up at once.")
    print("  Degree 1 alone would be near-vacuous -- alpha is an integer by")
    print("  construction.  It is agreement with an INDEPENDENTLY computed alpha that")
    print("  makes this gate able to fail.")
    tasks = [(int(n), "C", c) for n, s in samples.items() for c in s["C"]]
    got = run_tasks(sorted(tasks), procs, "sample C")
    bad = []
    for d in got:
        if d.get("status") != "hit" or d.get("degree") != 1:
            bad.append((d["graph6"], d.get("status"), d.get("degree"), "degree"))
            continue
        p = d["poly"]                            # p[1]*x + p[0] = 0  ->  x = -p[0]/p[1]
        if p[1] * d["alpha"] + p[0] != 0:
            bad.append((d["graph6"], "root", -p[0] / p[1], d["alpha"]))
    print(f"  {len(got)} graphs, {len(bad)} failures")
    for b in bad[:20]:
        print(f"  FAIL {b}")
    return not bad, dict(checked=len(got), failures=len(bad), detail=bad[:50])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--procs", type=int, default=7)
    ap.add_argument("--samples", default=os.path.join(RES, "stage9_samples.json"))
    ap.add_argument("--seed", type=int, default=20260826)
    ap.add_argument("--skip-gates", action="store_true",
                    help="only after the gates have passed in an earlier run")
    a = ap.parse_args()

    samples = json.load(open(a.samples))["samples"]
    rng = random.Random(a.seed)
    report = {"seed": a.seed, "degrees_ladder": DEGREES, "min_honest": MIN_HONEST}
    t_all = time.time()

    if not a.skip_gates:
        ok3, det3 = gate_aut(samples, a.procs, rng)
        report["G9_3"] = dict(passed=ok3, **det3)
        if not ok3:
            print("\nG9.3 FAILED -- |Aut| is not used; H9-C reports as blocked.")

        ok2, rows2 = gate_regression(a.procs)
        report["G9_2"] = dict(passed=ok2, rows=rows2)
        if not ok2:
            print("\nG9.2 FAILED -- kill rule K9.2.  Stage blocked at 9.a.")
            json.dump(report, open(os.path.join(RES, "report_9a.json"), "w"), indent=1)
            sys.exit(1)

        ok1, det1 = gate_C(samples, a.procs)
        report["G9_1"] = dict(passed=ok1, **det1)
        if not ok1:
            print("\nG9.1 FAILED -- kill rule K9.1.  Stage blocked at 9.a.")
            json.dump(report, open(os.path.join(RES, "report_9a.json"), "w"), indent=1)
            sys.exit(1)

    print("\n=== samples A and B ===")
    tasks = sorted((int(n), s, c) for n, d in samples.items()
                   for s in ("A", "B") for c in d[s])
    run_tasks(tasks, a.procs, "A and B")

    report["wall_minutes"] = round((time.time() - t_all) / 60, 1)
    json.dump(report, open(os.path.join(RES, "report_9a.json"), "w"), indent=1)
    print(f"\n9.a done in {report['wall_minutes']} min; "
          f"per-graph rows in {JSONL}")
