"""graph6 decoding/encoding to adjacency bitmasks.

Written from the format description, not from networkx, so that the reading path
is independent of the library used for cross-checks (PREREGISTRATION §R1, §R6).
Vertices are 0..n-1; adj[i] is an int bitmask of the neighbours of i.
"""
from __future__ import annotations


def decode_g6(line: str):
    """graph6 string -> (n, adj) with adj a list of int bitmasks."""
    s = line.strip()
    if s.startswith(">>graph6<<"):
        s = s[10:]
    if not s:
        raise ValueError("empty graph6 record")
    c0 = ord(s[0]) - 63
    if c0 < 0 or c0 > 62:
        raise ValueError("only n < 63 supported here; got first byte %r" % s[0])
    n = c0
    body = s[1:]
    nbits = n * (n - 1) // 2
    bits = []
    for ch in body:
        v = ord(ch) - 63
        if v < 0 or v > 63:
            raise ValueError("byte out of graph6 range: %r" % ch)
        for k in range(5, -1, -1):
            bits.append((v >> k) & 1)
    if len(bits) < nbits:
        raise ValueError("truncated graph6 record")
    adj = [0] * n
    p = 0
    # bit order: (0,1), (0,2),(1,2), (0,3),(1,3),(2,3), ...
    for j in range(1, n):
        for i in range(j):
            if bits[p]:
                adj[i] |= 1 << j
                adj[j] |= 1 << i
            p += 1
    return n, adj


def encode_g6(n: int, adj) -> str:
    """(n, adj bitmasks) -> graph6 string. Inverse of decode_g6 for n < 63."""
    if n >= 63:
        raise ValueError("only n < 63 supported here")
    bits = []
    for j in range(1, n):
        for i in range(j):
            bits.append(1 if (adj[i] >> j) & 1 else 0)
    while len(bits) % 6:
        bits.append(0)
    out = [chr(n + 63)]
    for k in range(0, len(bits), 6):
        v = 0
        for b in bits[k:k + 6]:
            v = (v << 1) | b
        out.append(chr(v + 63))
    return "".join(out)


def edges_of(n: int, adj):
    """Sorted edge list [(i,j)] with i < j."""
    return [(i, j) for i in range(n) for j in range(i + 1, n) if (adj[i] >> j) & 1]


def adj_from_edges(n: int, edges):
    adj = [0] * n
    for i, j in edges:
        adj[i] |= 1 << j
        adj[j] |= 1 << i
    return adj


def complement(n: int, adj):
    full = (1 << n) - 1
    return [(~adj[i]) & full & ~(1 << i) for i in range(n)]


def is_connected(n: int, adj) -> bool:
    if n == 0:
        return True
    seen = 1
    stack = [0]
    while stack:
        v = stack.pop()
        nb = adj[v] & ~seen
        while nb:
            b = nb & -nb
            u = b.bit_length() - 1
            seen |= b
            stack.append(u)
            nb ^= b
    return seen == (1 << n) - 1


def read_g6_file(path):
    """Yield (line, n, adj) for each record."""
    with open(path, "r") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            n, adj = decode_g6(line)
            yield line, n, adj


def to_networkx(n: int, adj):
    import networkx as nx
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges_of(n, adj))
    return G


def iso_equal(codeA: str, n: int, adj) -> bool:
    """True iff the graph6 record codeA is isomorphic to (n, adj).

    graph6 encodes a *labelled* graph, so a graph we build ourselves generally
    gets a different string than McKay's canonical record for the same
    isomorphism class.  Comparing strings there tests the labelling, not the
    graph; this compares the graph.
    """
    import networkx as nx
    nA, adjA = decode_g6(codeA)
    if nA != n:
        return False
    return nx.is_isomorphic(to_networkx(nA, adjA), to_networkx(n, adj))
