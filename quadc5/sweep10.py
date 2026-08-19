"""Filtered sweep over a geng stream (Stage 1, block 1.c).

Per graph: decode -> alpha (exact, batched) -> chi(Gbar).  If chi(Gbar) == alpha the
sandwich alpha <= theta <= chi(Gbar) (SOURCES.md S1.2) forces theta = alpha and Delta
= 0 with no SDP.  Everything else goes to the SDP.

Chunks are written as they complete, so an interrupted run costs at most one chunk,
and a re-run skips parts already on disk.
"""
from __future__ import annotations
import os, csv, time
import numpy as np

from .g6 import decode_g6, edges_of, complement
from .alpha import alpha_batch
from .chrom import chromatic_number
from .theta import theta_scs_direct
from . import gengstream

FIELDS = ["graph6", "n", "edges", "alpha", "theta", "delta", "filtered",
          "chi_comp", "solve_time", "status", "pr"]


def run_part(args):
    n, res, mod, out_dir, tag, eps, buf = args
    path = os.path.join(out_dir, f"{tag}_part_{res:05d}.csv")
    done = path + ".done"
    # A part counts as finished only if BOTH its data file and its marker exist;
    # a marker without data means the data was lost and the part must be redone.
    if os.path.exists(done) and os.path.exists(path):
        with open(done) as fh:
            a, b, c = fh.read().split()
        return int(a), int(b), float(c)
    if os.path.exists(done):
        os.remove(done)
    t0 = time.perf_counter()
    n_tot = n_sdp = 0
    fh = open(path, "w", newline="")
    w = csv.writer(fh)
    batch = []

    def flush(batch):
        nonlocal n_sdp
        if not batch:
            return
        A = np.array([a for _, a in batch], dtype=np.int32)
        alphas = alpha_batch(A, n)
        rows = []
        for k, (code, adj) in enumerate(batch):
            a = int(alphas[k])
            chi = chromatic_number(n, complement(n, adj))
            E = edges_of(n, adj)
            if chi == a:                      # sandwich collapses: Delta = 0, no SDP
                rows.append([code, n, len(E), a, float(a), 0.0, 1, chi, 0.0, "sandwich", 0.0])
            else:
                r = theta_scs_direct(n, E, eps=eps)
                n_sdp += 1
                rows.append([code, n, len(E), a, r["theta"], r["theta"] - a, 0, chi,
                             r["t"], r["status"], r["pr"]])
        w.writerows(rows)

    for code in gengstream.stream(n, res=res, mod=mod):
        n, adj = decode_g6(code)
        batch.append((code, adj))
        n_tot += 1
        if len(batch) >= buf:
            flush(batch)
            batch = []
    flush(batch)
    fh.close()
    el = time.perf_counter() - t0
    with open(done, "w") as f:
        f.write(f"{n_tot} {n_sdp} {el:.3f}")
    return n_tot, n_sdp, el
