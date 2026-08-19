"""Block 1.a -- the generator and its gate.  PREREGISTRATION_STAGE1 §2."""
import sys, os, csv, json, subprocess, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quadc5 import gengstream
from quadc5.g6 import decode_g6, edges_of
from quadc5.alpha import alpha_bitmask

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES, SRC = os.path.join(ROOT, "results"), os.path.join(ROOT, "sources")
rep, FAILS = {"checks": []}, []


def rec(name, predicted, obtained, ok, note=""):
    v = "PASS" if ok else "FAIL"
    rep["checks"].append(dict(name=name, predicted=str(predicted),
                              obtained=str(obtained), verdict=v, note=note))
    print(f"{v} {name:44s} pred={predicted} got={obtained} {note}")
    if not ok:
        FAILS.append(name)


# ---- G1 / G2 : counts -------------------------------------------------------
t0 = time.perf_counter()
c9 = gengstream.count(9)
c10 = gengstream.count(10)
rep["geng_count_time_s"] = time.perf_counter() - t0
rec("G1 geng -c 9 -u", 261080, c9, c9 == 261080)
rec("G2 geng -c 10 -u", 11716571, c10, c10 == 11716571,
    "brief's number, UNVERIFIED until now (S6)")

# ---- G3 : string identity against McKay's published file --------------------
mck = sorted(l.strip() for l in open(os.path.join(SRC, "mckay_graph9c.g6")) if l.strip())
ours = sorted(gengstream.stream(9))
rec("G3 geng default labelling == graph9c.g6 (as a set)", "same set",
    "same set" if ours == mck else "different", ours == mck)
withl = sorted(gengstream.stream(9, extra=("-l",)))
mck_set = set(mck)
rep["minus_l_differs"] = sum(1 for a in withl if a not in mck_set)
print(f"     (with -l: {rep['minus_l_differs']} of {len(withl)} strings are not in "
      f"graph9c.g6 -- -l is a DIFFERENT canonical form, so it is not used)")

# ---- G4 : the Stage 0 table, reproduced from the generated stream -----------
n9 = os.path.join(RES, "n9_all.csv")
if not os.path.exists(n9):
    subprocess.run(["gunzip", "-k", n9 + ".gz"], check=True)
old = {r["graph6"]: r for r in csv.DictReader(open(n9))}
rec("G4a same number of records", len(old), len(ours), len(old) == len(ours))
missing = [g for g in ours if g not in old]
rec("G4b every generated code is in the Stage 0 table", 0, len(missing), not missing)

# alpha recomputed from the generated stream, compared to the stored table
bad_a, worst_d = [], 0.0
for g in ours:
    n, adj = decode_g6(g)
    a = alpha_bitmask(n, adj)
    if a != int(old[g]["alpha"]):
        bad_a.append(g)
rec("G4c alpha reproduced for all 261080", 0, len(bad_a), not bad_a)
rep["gate_1a"] = "PASSED" if not FAILS else "FAILED"
rep["counts"] = dict(n9=c9, n10=c10)

# ---- B4 : external check of our perfect-graph recognition -------------------
pg = {n: gengstream.count(n, extra=("-P",)) for n in (8, 9, 10)}
rep["geng_perfect_counts"] = pg
print(f"\ngeng -c -P counts (external perfect-graph recognition): {pg}")
for n, ours_n in ((8, 7805), (9, 126777)):
    rec(f"B4 geng -P n={n} == our F1 count", ours_n, pg[n], pg[n] == ours_n,
        "our count from Stage 0 results/report_0b.json")

json.dump(rep, open(os.path.join(RES, "report_1a.json"), "w"), indent=1)
print("\n" + ("GATE 1.a PASSED" if not FAILS else f"GATE 1.a FAILED: {FAILS}"))
sys.exit(0 if not FAILS else 1)
