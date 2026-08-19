"""Independence number, two independent routes (PREREGISTRATION §R1).

Route A: exact bitmask enumeration over all 2^n vertex subsets.
Route B: networkx max_weight_clique on the complement.
Route A also has a batched numpy form used for the n=9 sweep.
"""
from __future__ import annotations
import numpy as np


def alpha_bitmask(n: int, adj) -> int:
    """Route A, single graph: largest S with no internal edge."""
    best = 0
    for S in range(1 << n):
        pc = bin(S).count("1")
        if pc <= best:
            continue
        m = S
        ok = True
        while m:
            b = m & -m
            v = b.bit_length() - 1
            if adj[v] & S:
                ok = False
                break
            m ^= b
        if ok:
            best = pc
    return best


def alpha_networkx(n: int, adj) -> int:
    """Route B: alpha(G) = omega(complement(G))."""
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(n))
    for i in range(n):
        for j in range(i + 1, n):
            if (adj[i] >> j) & 1:
                G.add_edge(i, j)
    clique, _ = nx.clique.max_weight_clique(nx.complement(G), weight=None)
    return len(clique)


_POPCNT = {}


def _tables(n: int):
    if n not in _POPCNT:
        subsets = np.arange(1 << n, dtype=np.int32)
        pc = np.zeros(1 << n, dtype=np.int8)
        for i in range(n):
            pc += ((subsets >> i) & 1).astype(np.int8)
        bits = np.array([[(S >> i) & 1 for i in range(n)] for S in range(1 << n)], dtype=bool)
        _POPCNT[n] = (subsets, pc, bits)
    return _POPCNT[n]


def alpha_batch(adj_mat: np.ndarray, n: int) -> np.ndarray:
    """Route A, batched. adj_mat: (N, n) int32 bitmasks. Returns (N,) int8.

    For every subset S, OR together the neighbourhoods of the vertices in S;
    S is independent iff that OR has no bit inside S.
    """
    subsets, pc, bits = _tables(n)
    N = adj_mat.shape[0]
    ors = np.zeros((N, 1 << n), dtype=np.int32)
    for i in range(n):
        sel = bits[:, i]
        ors[:, sel] |= adj_mat[:, i:i + 1]
    indep = (ors & subsets[None, :]) == 0
    return (indep * pc[None, :]).max(axis=1).astype(np.int8)
