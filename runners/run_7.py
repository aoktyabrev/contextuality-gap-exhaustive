"""Stage 7 -- the upper-layer inheritance hypothesis H7.
PREREGISTRATION_STAGE7.md.  Verdict blocks 7.a, 7.b, 7.c.

n = 11 is NOT used in the verdict: the hypothesis was formed from it.
"""
import sys, os, csv, json, gzip, argparse, itertools, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import numpy as np
import networkx as nx
from quadc5.g6 import decode_g6, edges_of, encode_g6
from quadc5.alpha import alpha_bitmask
from quadc5.theta import theta_cvxpy, theta_scs_direct
from quadc5 import gengstream

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
rep, FAILS = {"blocks": {}}, []
TAU = 1e-6                                    # P7-delta, fixed in the preregistration


def rec(name, ok, detail=""):
    v = "PASS" if ok else "FAIL"
    print(f"{v}  {name}   {detail}")
    if not ok:
        FAILS.append(name)
    return ok


# ---------------------------------------------------------------- 7.a analytics
def cone(n, edges, k):
    """C_k(G): add k-1 mutually independent vertices, then one universal vertex.
    Vertices 0..n-1 are G, n..n+k-2 are the independent ones, n+k-1 is universal."""
    N = n + k
    v = N - 1
    E = list(edges) + [(u, v) for u in range(N - 1)]
    return N, E


def block_7a(seed=20260819, trials=25):
    print("\n=== 7.a  analytics of the transfer construction ===")
    rng = random.Random(seed)
    out = {"alpha_ok": 0, "theta_ok": 0, "conn_ok": 0, "trials": 0,
           "max_theta_err_scs": 0.0, "max_theta_err_clarabel": 0.0}
    worst = 0.0
    for t in range(trials):
        m = rng.randint(4, 8)
        p = rng.uniform(0.25, 0.75)
        g = nx.gnp_random_graph(m, p, seed=rng.randint(0, 10 ** 9))
        if g.number_of_edges() == 0:
            g.add_edge(0, 1 % m)
        E = [tuple(sorted(e)) for e in g.edges()]
        adj = [0] * m
        for u, v in E:
            adj[u] |= 1 << v
            adj[v] |= 1 << u
        a0 = alpha_bitmask(m, adj)
        th0_s = theta_scs_direct(m, E, eps=1e-9)["theta"]
        th0_c = theta_cvxpy(m, E, solver="CLARABEL")["theta"]
        k = rng.randint(1, 4)
        N, EN = cone(m, E, k)
        adjN = [0] * N
        for u, v in EN:
            adjN[u] |= 1 << v
            adjN[v] |= 1 << u
        aN = alpha_bitmask(N, adjN)
        thN_s = theta_scs_direct(N, EN, eps=1e-9)["theta"]
        thN_c = theta_cvxpy(N, EN, solver="CLARABEL")["theta"]
        gN = nx.Graph(); gN.add_nodes_from(range(N)); gN.add_edges_from(EN)

        out["trials"] += 1
        out["alpha_ok"] += (aN == a0 + k - 1)
        out["conn_ok"] += nx.is_connected(gN)
        es, ec = abs(thN_s - (th0_s + k - 1)), abs(thN_c - (th0_c + k - 1))
        out["max_theta_err_scs"] = max(out["max_theta_err_scs"], es)
        out["max_theta_err_clarabel"] = max(out["max_theta_err_clarabel"], ec)
        out["theta_ok"] += (es < 1e-6 and ec < 1e-6)
        worst = max(worst, abs(thN_s - thN_c))
    out["max_solver_disagreement"] = worst
    T = out["trials"]
    rec("7.a-1  alpha(C_k(G)) = alpha(G) + k - 1", out["alpha_ok"] == T,
        f"{out['alpha_ok']}/{T} (exact, integer)")
    rec("7.a-2  theta(C_k(G)) = theta(G) + k - 1, two independent solvers",
        out["theta_ok"] == T,
        f"{out['theta_ok']}/{T}, max err SCS {out['max_theta_err_scs']:.2e}, "
        f"CLARABEL {out['max_theta_err_clarabel']:.2e}")
    rec("7.a-3  C_k(G) is connected", out["conn_ok"] == T, f"{out['conn_ok']}/{T}")
    rep["blocks"]["7a"] = out
    return out


# ---------------------------------------------------------------- layer tables
def layers_from_rows(rows):
    """rows -> {alpha: (Dmax, graph6, edges)}"""
    D = {}
    for g6, a, d, e in rows:
        if a not in D or d > D[a][0]:
            D[a] = (d, g6, e)
    return D


def layers_by_enumeration(m, eps=1e-9):
    D = {}
    for code in gengstream.stream(m):
        n, adj = decode_g6(code)
        E = edges_of(n, adj)
        a = alpha_bitmask(n, adj)
        th = theta_scs_direct(n, E, eps=eps)["theta"]
        d = th - a
        if d < TAU:
            d = 0.0
        if a not in D or d > D[a][0]:
            D[a] = (d, code, len(E))
    return D


def layers_from_csv(path, positive_only):
    """Streaming.  The n = 11 table is 10.9 GB and 100 827 522 rows; holding it in a
    list would need tens of gigabytes -- the same trap that nearly cost the n = 11
    sweep its own collection step.  Only the per-layer maximum is kept."""
    op = gzip.open if path.endswith(".gz") else open
    D = {}
    with op(path, "rt") as fh:
        rd = csv.reader(fh)
        head = next(rd)
        ia, idx, ie = head.index("alpha"), head.index("delta"), head.index("edges")
        for r in rd:
            a = int(r[ia])
            d = float(r[idx])
            if a not in D or d > D[a][0]:
                D[a] = (d, r[0], int(r[ie]))
    for a in list(D):
        if D[a][0] < TAU:
            D[a] = (0.0, D[a][1], D[a][2])
    return D


def block_7b(args):
    print("\n=== 7.b  D(n,a) against the transfer bound T(n,a) ===")
    D = {}
    for m in (5, 6, 7, 8):
        D[m] = layers_by_enumeration(m)
        print(f"  n={m}: layers " + ", ".join(f"a={a}:{v[0]:.7f}" for a, v in sorted(D[m].items())))
    p9 = os.path.join(RES, "n9_all.csv")
    D[9] = layers_from_csv(p9 if os.path.exists(p9) else p9 + ".gz", False)
    p10 = os.path.join(RES, "n10_nonzero.csv")
    D[10] = layers_from_csv(p10 if os.path.exists(p10) else p10 + ".gz", True)
    # n = 11, when its table is present.  Stage 8 block 8.a: recorded as fact, never as
    # verdict -- the hypothesis was formed by looking at these very numbers.
    p11 = os.path.join(RES, "n11_nonzero.csv")
    if os.path.exists(p11) or os.path.exists(p11 + ".gz"):
        D[11] = layers_from_csv(p11 if os.path.exists(p11) else p11 + ".gz", True)
    for m in sorted(set(D) & {9, 10, 11}):
        print(f"  n={m}: layers " + ", ".join(f"a={a}:{v[0]:.7f}" for a, v in sorted(D[m].items())))

    def T(n, a):
        """max_{m<n} D(m, a + m + 1 - n); the cone C_{n-m} moves layer a0 to a0+n-m-1."""
        best, arg = 0.0, None
        for m in range(4, n):
            a0 = a + m + 1 - n
            if a0 < 1 or m not in D:
                continue
            v = 0.0 if a0 == 1 else (D[m].get(a0, (0.0,))[0])
            if v > best:
                best, arg = v, (m, a0)
        return best, arg

    table = []
    for n in sorted(set(D) & {9, 10, 11}):
        for a in sorted(D[n]):
            d = D[n][a][0]
            t, arg = T(n, a)
            table.append(dict(n=n, a=a, D=d, T=t, source=arg, graph6=D[n][a][1],
                              edges=D[n][a][2], diff=d - t,
                              equal=(abs(d - t) <= TAU), empty=(d < TAU and t < TAU)))
    rep["blocks"]["7b"] = table
    print(f"\n{'n':>2} {'a':>2} {'D(n,a)':>12} {'T(n,a)':>12} {'source':>9} {'D-T':>12}  verdict")
    for r in table:
        v = "empty (0=0)" if r["empty"] else ("EQUAL" if r["equal"] else
                                              ("D>T" if r["diff"] > 0 else "D<T  !!"))
        print(f"{r['n']:>2} {r['a']:>2} {r['D']:>12.7f} {r['T']:>12.7f} "
              f"{str(r['source']):>9} {r['diff']:>+12.7f}  {v}")
    weak = [r for r in table if r["diff"] < -TAU]
    n11 = [r for r in table if r["n"] == 11]
    if n11:
        print("\n  NB: the n=11 rows are FACT, not verdict -- the hypothesis was formed\n"
              "      by looking at them (PREREGISTRATION_STAGE7 0, PREREGISTRATION_STAGE8 1).")
    rec("H7 weak form: D(n,a) >= T(n,a) everywhere", not weak,
        f"{len(weak)} violations" if weak else "no violations")
    return D, table


def block_7c(table):
    print("\n=== 7.c  inheritance boundary ===")
    out = {}
    for n in sorted({r["n"] for r in table}):
        rows = [r for r in table if r["n"] == n and not r["empty"]]
        rows.sort(key=lambda r: r["a"])
        boundary = None
        for i, r in enumerate(rows):
            if all(x["equal"] for x in rows[i:]):
                boundary = r["a"]
                break
        out[n] = dict(boundary=boundary,
                      layers={r["a"]: ("=" if r["equal"] else "!=") for r in rows})
        print(f"  n={n}: boundary a* = {boundary};  " +
              " ".join(f"a{r['a']}{out[n]['layers'][r['a']]}" for r in rows))
    rep["blocks"]["7c"] = out
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=20260819)
    ap.add_argument("--trials", type=int, default=25)
    ap.add_argument("--out", default=os.path.join(RES, "report_7.json"))
    a = ap.parse_args()
    block_7a(a.seed, a.trials)
    D, table = block_7b(a)
    block_7c(table)
    rep["fails"] = FAILS
    json.dump(rep, open(a.out, "w"), indent=1, default=str)
    print(f"\nwrote {a.out}")
    print("STAGE 7 blocks 7.a-7.c: " + ("all checks passed" if not FAILS else f"FAILED: {FAILS}"))
    sys.exit(0 if not FAILS else 1)
