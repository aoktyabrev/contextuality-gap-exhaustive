"""Exact chromatic number for small graphs (used only in the sandwich test R2)."""
from __future__ import annotations


def _colorable(n, adj, k):
    color = [-1] * n
    order = sorted(range(n), key=lambda v: -bin(adj[v]).count("1"))

    def bt(idx, used):
        if idx == n:
            return True
        v = order[idx]
        forbidden = 0
        for u in range(n):
            if (adj[v] >> u) & 1 and color[u] >= 0:
                forbidden |= 1 << color[u]
        for c in range(min(used + 1, k)):
            if (forbidden >> c) & 1:
                continue
            color[v] = c
            if bt(idx + 1, max(used, c + 1)):
                return True
            color[v] = -1
        return False

    return bt(0, 0)


def chromatic_number(n: int, adj) -> int:
    for k in range(1, n + 1):
        if _colorable(n, adj, k):
            return k
    return n
