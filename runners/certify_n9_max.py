"""Exact certificate for theta of the n=9 maximizer.

Primal: an integer matrix M with X = M/99 feasible for the SDP of SOURCES.md S1.2
        and 1^T X 1 = 11/3   ->  theta >= 11/3
Dual:   a rational symmetric B, equal to 1 on the diagonal and on every non-edge,
        with lambda_max(B) = 11/3  ->  theta <= 11/3
Both verified in exact rational arithmetic (all principal minors), so the value is
proved, not merely fitted -- unlike the closed form for theta(Quad-C5), which the
source reports as a PSLQ false positive (SOURCES.md S1.9).
"""
import sys, os, json, itertools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sympy as sp
from quadc5.g6 import decode_g6, edges_of
from quadc5.alpha import alpha_bitmask

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE = "HCRbdO{"
n, adj = decode_g6(CODE)
E = sorted(edges_of(n, adj))
alpha = alpha_bitmask(n, adj)
THETA = sp.Rational(11, 3)

M = sp.Matrix([[12, 4, 6, 0, 8, 0, 8, 0, 6], [4, 12, 6, 8, 0, 0, 0, 8, 6],
               [6, 6, 9, 6, 6, 0, 0, 0, 0], [0, 8, 6, 12, 4, 6, 0, 8, 0],
               [8, 0, 6, 4, 12, 6, 8, 0, 0], [0, 0, 0, 6, 6, 9, 6, 6, 0],
               [8, 0, 0, 0, 8, 6, 12, 4, 6], [0, 8, 0, 8, 0, 6, 4, 12, 6],
               [6, 6, 0, 0, 0, 0, 6, 6, 9]])


def psd_exact(A):
    for k in range(1, A.shape[0] + 1):
        for S in itertools.combinations(range(A.shape[0]), k):
            if A[list(S), list(S)].det() < 0:
                return False
    return True


out = {"graph6": CODE, "n": n, "edges": len(E), "alpha": alpha}
ok_sym = M.T == M
ok_tr = M.trace() == 99
ok_edges = all(M[i, j] == 0 for (i, j) in E)
ok_psd = psd_exact(M)
ok_val = sp.Rational(int(sum(M)), 99) == THETA
print(f"PRIMAL  symmetric={ok_sym} trace/99=1:{ok_tr} zero on edges={ok_edges} "
      f"PSD(exact)={ok_psd} sum/99={sp.Rational(int(sum(M)),99)}")
print(f"        eigenvalues of M: {sorted(M.eigenvals().items(), key=lambda kv: kv[0])}")

syms = sp.symbols("b0:%d" % len(E))
B = sp.zeros(n, n)
Eset = set(E)
for i in range(n):
    for j in range(n):
        if i == j or (min(i, j), max(i, j)) not in Eset:
            B[i, j] = 1
for k, (i, j) in enumerate(E):
    B[i, j] = syms[k]
    B[j, i] = syms[k]
sol = sp.solve([sp.Eq(v, 0) for v in ((THETA * sp.eye(n) - B) * M)], syms, dict=True)
B = B.subs(sol[0])
S = THETA * sp.eye(n) - B
ok_dual_struct = all(B[i, j] == 1 for i in range(n) for j in range(n)
                     if i == j or (min(i, j), max(i, j)) not in Eset)
ok_dual_psd = psd_exact(S)
eig = B.eigenvals()
ok_lmax = max(eig) == THETA
print(f"DUAL    structure ok={ok_dual_struct}  (11/3 I - B) PSD(exact)={ok_dual_psd}  "
      f"lambda_max={max(eig)}")
print(f"        eigenvalues of B: {dict(sorted(eig.items(), key=lambda kv: kv[0]))}")
print(f"        B on edges: {[(e, B[e[0], e[1]]) for e in E]}")

proved = all([ok_sym, ok_tr, ok_edges, ok_psd, ok_val, ok_dual_struct, ok_dual_psd, ok_lmax])
out.update(theta=str(THETA), delta=str(THETA - alpha), proved=proved,
           primal=dict(symmetric=ok_sym, trace=ok_tr, zero_on_edges=ok_edges,
                       psd_exact=ok_psd, value=ok_val,
                       eigenvalues={str(k): v for k, v in M.eigenvals().items()}),
           dual=dict(structure=ok_dual_struct, psd_exact=ok_dual_psd, lmax=ok_lmax,
                     eigenvalues={str(k): v for k, v in eig.items()},
                     edge_values={f"{i},{j}": str(B[i, j]) for (i, j) in E}))
json.dump(out, open(os.path.join(ROOT, "results", "certificate_n9_max.json"), "w"), indent=1)
print(f"\ntheta({CODE}) = {THETA} exactly, alpha = {alpha}, "
      f"Delta = {THETA - alpha}  -- PROVED: {proved}")
sys.exit(0 if proved else 1)
