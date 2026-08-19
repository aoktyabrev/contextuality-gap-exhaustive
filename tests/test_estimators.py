"""Repository rule: every estimator is run on random inputs, not only on the
pretty graphs where the answer is known.  PREREGISTRATION §R.

Gate R: if any of R1-R7 fails, block 0.c is not run.
"""
import sys, os, math, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np

from quadc5.g6 import (decode_g6, encode_g6, edges_of, adj_from_edges,
                       complement, is_connected)
from quadc5.alpha import alpha_bitmask, alpha_networkx, alpha_batch
from quadc5.theta import theta_scs_direct, theta_cvxpy
from quadc5.chrom import chromatic_number

FAILS = []
SEED = 20260819
TAU_HI, TAU_BULK = 1e-7, 1e-5


def check(name, ok, detail=""):
    print(("PASS " if ok else "FAIL ") + name + ("  " + detail if detail else ""))
    if not ok:
        FAILS.append((name, detail))


def random_connected(rng, n=None):
    while True:
        nn = n or rng.integers(5, 10)
        p = rng.uniform(0.1, 0.9)
        adj = [0] * nn
        for i in range(nn):
            for j in range(i + 1, nn):
                if rng.random() < p:
                    adj[i] |= 1 << j
                    adj[j] |= 1 << i
        if is_connected(nn, adj):
            return int(nn), adj


rng = np.random.default_rng(SEED)
GRAPHS = [random_connected(rng) for _ in range(500)]
print(f"# {len(GRAPHS)} random connected graphs, seed {SEED}, "
      f"n in {sorted(set(g[0] for g in GRAPHS))}")

# ---- R1: alpha by two independent routes -----------------------------------
bad = []
for n, adj in GRAPHS:
    a, b = alpha_bitmask(n, adj), alpha_networkx(n, adj)
    if a != b:
        bad.append((encode_g6(n, adj), a, b))
check("R1 alpha bitmask == alpha networkx(complement)", not bad, f"{len(bad)} mismatches {bad[:3]}")

# R1b: the batched form used for n=9 must agree with the scalar form
n9 = [g for g in GRAPHS if g[0] == 9]
if n9:
    A = np.array([g[1] for g in n9], dtype=np.int32)
    ab = alpha_batch(A, 9)
    bad = [i for i, (n, adj) in enumerate(n9) if ab[i] != alpha_bitmask(n, adj)]
    check("R1b alpha_batch == alpha_bitmask", not bad, f"{len(bad)}/{len(n9)} mismatches")

# ---- R2: sandwich alpha <= theta <= chi(complement)  (SOURCES.md S1.2) -----
bad = []
for n, adj in GRAPHS[:200]:
    a = alpha_bitmask(n, adj)
    th = theta_scs_direct(n, edges_of(n, adj), eps=1e-8)["theta"]
    chi = chromatic_number(n, complement(n, adj))
    if not (a - 1e-6 <= th <= chi + 1e-6):
        bad.append((encode_g6(n, adj), a, th, chi))
check("R2 sandwich alpha <= theta <= chi(Gbar)", not bad, f"{len(bad)} violations {bad[:2]}")

# ---- R3: two solvers agree --------------------------------------------------
worst, arg = 0.0, None
for n, adj in GRAPHS[:200]:
    E = edges_of(n, adj)
    a = theta_scs_direct(n, E, eps=1e-8)["theta"]
    b = theta_cvxpy(n, E, solver="CLARABEL")["theta"]
    if abs(a - b) > worst:
        worst, arg = abs(a - b), encode_g6(n, adj)
check("R3 SCS(direct) vs CLARABEL <= tau_bulk", worst <= TAU_BULK, f"max diff {worst:.2e} at {arg}")

# ---- R4: third solver on a subsample ---------------------------------------
worst4, arg4 = 0.0, None
for n, adj in GRAPHS[:50]:
    E = edges_of(n, adj)
    a = theta_scs_direct(n, E, eps=1e-8)["theta"]
    c = theta_cvxpy(n, E, solver="CVXOPT")["theta"]
    if abs(a - c) > worst4:
        worst4, arg4 = abs(a - c), encode_g6(n, adj)
check("R4 SCS(direct) vs CVXOPT <= tau_bulk", worst4 <= TAU_BULK, f"max diff {worst4:.2e} at {arg4}")

# ---- R5: primal feasibility of the returned X ------------------------------
worst5 = 0.0
for n, adj in GRAPHS[:200]:
    worst5 = max(worst5, theta_scs_direct(n, edges_of(n, adj), eps=1e-8)["pr"])
check("R5 primal residual <= tau_hi", worst5 <= TAU_HI, f"max residual {worst5:.2e}")

# ---- R6: invariance under relabelling (the only test that catches indexing) -
py = random.Random(SEED)
bad = []
for n, adj in GRAPHS[:150]:
    perm = list(range(n))
    py.shuffle(perm)
    padj = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                padj[perm[i]] |= 1 << perm[j]
                padj[perm[j]] |= 1 << perm[i]
    da = alpha_bitmask(n, adj) - alpha_bitmask(n, padj)
    dt = abs(theta_scs_direct(n, edges_of(n, adj), eps=1e-8)["theta"]
             - theta_scs_direct(n, edges_of(n, padj), eps=1e-8)["theta"])
    if da != 0 or dt > TAU_BULK:
        bad.append((encode_g6(n, adj), da, dt))
check("R6 alpha and theta invariant under vertex relabelling", not bad,
      f"{len(bad)} violations {bad[:2]}")

# ---- R7: analytic anchors on random sizes ----------------------------------
bad = []
for _ in range(20):
    n = int(rng.integers(3, 10))
    empty = [0] * n
    full = adj_from_edges(n, [(i, j) for i in range(n) for j in range(i + 1, n)])
    te = theta_scs_direct(n, edges_of(n, empty), eps=1e-9)["theta"]
    tf = theta_scs_direct(n, edges_of(n, full), eps=1e-9)["theta"]
    if abs(te - n) > TAU_HI or abs(tf - 1.0) > TAU_HI:
        bad.append((n, te, tf))
check("R7 theta(empty)=n and theta(complete)=1", not bad, f"{len(bad)} violations {bad[:2]}")

# ---- graph6 round trip ------------------------------------------------------
bad = [encode_g6(n, adj) for n, adj in GRAPHS
       if decode_g6(encode_g6(n, adj))[1] != adj]
check("R0 graph6 encode/decode round trip", not bad, f"{len(bad)} mismatches")

print()
if FAILS:
    print(f"GATE R FAILED: {len(FAILS)} check(s)")
    sys.exit(1)
print("GATE R PASSED")
