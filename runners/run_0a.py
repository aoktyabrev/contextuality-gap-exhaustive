"""Block 0.a -- calibration.  PREREGISTRATION §3.

Gate 0.a: any |Delta_ours - Delta_reference| > tau_gate = 1e-6 on A1'''/A2'''/A3''
blocks blocks 0.b and 0.c.
"""
import sys, os, json, math, csv, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np

from quadc5.g6 import decode_g6, edges_of, adj_from_edges, encode_g6, iso_equal
from quadc5.alpha import alpha_bitmask
from quadc5.theta import theta_scs_direct, theta_cvxpy
from quadc5.sweep import sweep

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
SRC = os.path.join(ROOT, "sources")
TAU_AN, TAU_HI, TAU_BULK, TAU_GATE, TAU_PAPER = 1e-12, 1e-7, 1e-5, 1e-6, 5e-6
SEED = 20260819
report = {"tolerances": dict(tau_an=TAU_AN, tau_hi=TAU_HI, tau_bulk=TAU_BULK,
                             tau_gate=TAU_GATE, tau_paper=TAU_PAPER), "checks": []}
FAILS = []


def rec(name, predicted, obtained, tol, ok, note=""):
    verdict = "PASS" if ok else "FAIL"
    report["checks"].append(dict(name=name, predicted=predicted, obtained=obtained,
                                 tol=tol, verdict=verdict, note=note))
    print(f"{verdict} {name:38s} pred={predicted} got={obtained} tol={tol} {note}")
    if not ok:
        FAILS.append(name)


def cyc(n):
    return adj_from_edges(n, [(i, (i + 1) % n) for i in range(n)])


def theta_cyc(n):
    return n * math.cos(math.pi / n) / (1 + math.cos(math.pi / n))


# ---------------------------------------------------------------- 3.2 SDP calibration
print("=== 0.a / SDP calibration on the analytic family ===")
sdpcal = []
for n in (5, 7, 9):
    ex = theta_cyc(n)
    for label, solver in (("SCSdirect", None), ("CLARABEL", "CLARABEL")):
        E = edges_of(n, cyc(n))
        t = (theta_scs_direct(n, E, eps=1e-9)["theta"] if solver is None
             else theta_cvxpy(n, E, solver=solver)["theta"])
        sdpcal.append(dict(family=f"C{n}", solver=label, exact=ex, got=t, err=abs(t - ex)))
for n in range(5, 10):
    for label, solver in (("SCSdirect", None), ("CLARABEL", "CLARABEL")):
        Ek = [(i, j) for i in range(n) for j in range(i + 1, n)]
        t = (theta_scs_direct(n, Ek, eps=1e-9)["theta"] if solver is None
             else theta_cvxpy(n, Ek, solver=solver)["theta"])
        sdpcal.append(dict(family=f"K{n}", solver=label, exact=1.0, got=t, err=abs(t - 1.0)))
        t = (theta_scs_direct(n, [], eps=1e-9)["theta"] if solver is None
             else theta_cvxpy(n, [], solver=solver)["theta"])
        sdpcal.append(dict(family=f"E{n}", solver=label, exact=float(n), got=t, err=abs(t - n)))
report["sdp_calibration"] = sdpcal
for label in ("SCSdirect", "CLARABEL"):
    mx = max(d["err"] for d in sdpcal if d["solver"] == label)
    rec(f"SDPcal max err [{label}]", f"<= {TAU_HI}", f"{mx:.3e}", TAU_HI, mx <= TAU_HI)

# A1' analytic identity 5cos(pi/5)/(1+cos(pi/5)) == sqrt(5)
d = abs(theta_cyc(5) - math.sqrt(5))
rec("A1' identity C5 formula = sqrt5", "0", f"{d:.3e}", TAU_AN, d <= TAU_AN)

# ---------------------------------------------------------------- A1  n = 5
print("\n=== 0.a / A1  n=5 ===")
C5 = cyc(5)
a5 = alpha_bitmask(5, C5)
rec("A1'' alpha(C5)", 2, a5, "exact", a5 == 2)
t5 = theta_cvxpy(5, edges_of(5, C5), solver="CLARABEL")["theta"]
rec("A1 theta(C5)", f"{math.sqrt(5):.12f}", f"{t5:.12f}", TAU_HI, abs(t5 - math.sqrt(5)) <= TAU_HI)
d5 = t5 - a5
rec("A1''' Delta(C5)", f"{math.sqrt(5)-2:.12f}", f"{d5:.12f}", TAU_GATE,
    abs(d5 - (math.sqrt(5) - 2)) <= TAU_GATE, "GATE")

# ---------------------------------------------------------------- A2  n = 7
print("\n=== 0.a / A2  n=7 (exhaustive over 853) ===")
p7 = sweep(os.path.join(SRC, "mckay_graph7c.g6"), RES, "n7", eps=1e-8, chunk=200, procs=7)
rows7 = list(csv.DictReader(open(p7)))
rec("A2 connected graphs n=7", 853, len(rows7), "exact", len(rows7) == 853)
rows7.sort(key=lambda r: -float(r["delta"]))
best7 = rows7[0]
rec("A2' argmax Delta n=7 is C7 (up to isomorphism)", "C7", best7["graph6"],
    "isomorphism", iso_equal(best7["graph6"], 7, cyc(7)),
    "graph6 encodes a labelling; compared as graphs, not as strings")
t7 = theta_cvxpy(7, edges_of(7, cyc(7)), solver="CLARABEL")["theta"]
rec("A2'' theta(C7)", f"{theta_cyc(7):.10f}", f"{t7:.10f}", TAU_HI,
    abs(t7 - theta_cyc(7)) <= TAU_HI)
a7 = alpha_bitmask(7, cyc(7))
d7 = t7 - a7
rec("A2''' Delta(C7) vs paper 0.31767", "0.31767", f"{d7:.8f}", TAU_PAPER,
    abs(d7 - 0.31767) <= TAU_PAPER, "GATE (tau_paper: 5 printed digits)")
rec("A2'''b Delta(C7) vs analytic", f"{theta_cyc(7)-3:.10f}", f"{d7:.10f}", TAU_GATE,
    abs(d7 - (theta_cyc(7) - 3)) <= TAU_GATE, "GATE")

# ---------------------------------------------------------------- A3  n = 8
print("\n=== 0.a / A3  n=8 (exhaustive over 11117) ===")
p8 = sweep(os.path.join(SRC, "mckay_graph8c.g6"), RES, "n8", eps=1e-8, chunk=400, procs=7)
rows8 = list(csv.DictReader(open(p8)))
rec("A3 connected graphs n=8", 11117, len(rows8), "exact", len(rows8) == 11117)
rows8.sort(key=lambda r: -float(r["delta"]))

# re-solve the top 50 with the high-accuracy solver
top = rows8[:50]
for r in top:
    n, adj = decode_g6(r["graph6"])
    hi = theta_cvxpy(n, edges_of(n, adj), solver="CLARABEL")
    r["theta_hi"] = hi["theta"]
    r["delta_hi"] = hi["theta"] - int(r["alpha"])
    r["pr_hi"] = hi["pr"]
top.sort(key=lambda r: -r["delta_hi"])
report["n8_top10"] = [dict(rank=i + 1, graph6=r["graph6"], alpha=int(r["alpha"]),
                           edges=int(r["edges"]), theta=r["theta_hi"],
                           delta=r["delta_hi"]) for i, r in enumerate(top[:10])]

rec("A3' argmax n=8 graph6", "GCQb`o", top[0]["graph6"], "exact string",
    top[0]["graph6"] == "GCQb`o", "GATE")
rec("A3'' max Delta n=8 vs authors CSV", "0.46784373", f"{top[0]['delta_hi']:.8f}",
    TAU_GATE, abs(top[0]["delta_hi"] - 0.46784373) <= TAU_GATE, "GATE")
rec("A3''b max Delta n=8 vs paper 0.46784", "0.46784", f"{top[0]['delta_hi']:.8f}",
    TAU_PAPER, abs(top[0]["delta_hi"] - 0.46784) <= TAU_PAPER)
rec("A3''' rank2 graph6", "GCR`r_", top[1]["graph6"], "exact string",
    top[1]["graph6"] == "GCR`r_", "GATE")
rec("A3''' rank3 graph6", "GCrb`o", top[2]["graph6"], "exact string",
    top[2]["graph6"] == "GCrb`o", "GATE")
rec("A3'''b rank2 Delta", "0.43844718", f"{top[1]['delta_hi']:.8f}", TAU_GATE,
    abs(top[1]["delta_hi"] - 0.43844718) <= TAU_GATE)

# Wagner graph, defined from the edge list in SOURCES.md S1.11, not by name
WAG = [(0,1),(1,2),(2,3),(3,4),(4,5),(5,6),(6,7),(7,0),(0,4),(1,5),(2,6),(3,7)]
wadj = adj_from_edges(8, WAG)
aw = alpha_bitmask(8, wadj)
tw = theta_cvxpy(8, WAG, solver="CLARABEL")["theta"]
dw = tw - aw
rec("A3'''' Wagner == rank3 (up to isomorphism)", top[2]["graph6"], "Wagner V8",
    "isomorphism", iso_equal(top[2]["graph6"], 8, wadj),
    "graph6 encodes a labelling; compared as graphs, not as strings")
rec("A3'''' Delta(Wagner) vs CSV", "0.41421356", f"{dw:.8f}", TAU_GATE,
    abs(dw - 0.41421356) <= TAU_GATE, "GATE")
rec("obs-8 theta(Wagner) = 2+sqrt2 (our observation, not in sources)",
    f"{2+math.sqrt(2):.10f}", f"{tw:.10f}", TAU_HI, abs(tw - (2 + math.sqrt(2))) <= TAU_HI)

# A4: ranks 4-6 as a SET
got456 = set(r["graph6"] for r in top[3:6])
exp456 = {"GCRb`w", "GCQbdo", "GCp`dO"}
rec("A4 ranks 4-6 as a set", sorted(exp456), sorted(got456), "set equality",
    got456 == exp456)

report["n8_top50"] = [dict(rank=i + 1, graph6=r["graph6"], alpha=int(r["alpha"]),
                           edges=int(r["edges"]), theta_hi=r["theta_hi"],
                           delta_hi=r["delta_hi"], theta_bulk=float(r["theta"]))
                      for i, r in enumerate(top)]
mx = max(abs(r["theta_hi"] - float(r["theta"])) for r in top)
rec("bulk vs high-accuracy solver on n=8 top50", f"<= {TAU_BULK}", f"{mx:.2e}",
    TAU_BULK, mx <= TAU_BULK)

report["gate_0a"] = "PASSED" if not FAILS else "FAILED"
report["fails"] = FAILS
json.dump(report, open(os.path.join(RES, "report_0a.json"), "w"), indent=1, default=str)
print("\n" + ("GATE 0.a PASSED" if not FAILS else f"GATE 0.a FAILED: {FAILS}"))
sys.exit(0 if not FAILS else 1)
