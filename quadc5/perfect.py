"""Perfect-graph recognition by induced odd holes and antiholes (brief 0.b).

For n <= 9 the only odd lengths >= 5 that fit are 5, 7, 9, so it suffices to
look for induced cycles of those lengths in G (holes) and in the complement
(antiholes).

Soundness -- "perfect => Delta = 0" -- is NOT taken on trust here.  It is
verified against the full SDP on every connected graph at n=8 and n=9
(PREREGISTRATION §4.2, gate B-sound).
"""
from __future__ import annotations
from itertools import combinations
from .g6 import complement


def _induced_is_cycle(adj, S_list) -> bool:
    """S_list: list of vertices. True iff the induced subgraph is a single cycle."""
    S = 0
    for v in S_list:
        S |= 1 << v
    k = len(S_list)
    for v in S_list:
        if bin(adj[v] & S).count("1") != 2:
            return False
    # 2-regular + connected == one cycle of length k
    start = S_list[0]
    seen = 1 << start
    stack = [start]
    cnt = 1
    while stack:
        v = stack.pop()
        nb = adj[v] & S & ~seen
        while nb:
            b = nb & -nb
            u = b.bit_length() - 1
            seen |= b
            cnt += 1
            stack.append(u)
            nb ^= b
    return cnt == k


def induced_cycles_of_length(n: int, adj, k: int):
    """All vertex sets inducing a k-cycle, as sorted tuples."""
    out = []
    for S in combinations(range(n), k):
        if _induced_is_cycle(adj, list(S)):
            out.append(S)
    return out


def has_odd_hole(n: int, adj, lengths=(5, 7, 9)) -> bool:
    for k in lengths:
        if k > n:
            break
        if induced_cycles_of_length(n, adj, k):
            return True
    return False


def is_perfect(n: int, adj) -> bool:
    """No induced odd hole and no induced odd antihole of length >= 5."""
    if has_odd_hole(n, adj):
        return False
    return not has_odd_hole(n, complement(n, adj))
