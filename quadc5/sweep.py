"""Parallel sweep over a graph6 file with continuous checkpointing.

Chunks are written to disk as they complete, so an interrupted run costs at
most one chunk (PREREGISTRATION §5).  Re-running skips chunks already on disk.
"""
from __future__ import annotations
import os, csv, time, json
from multiprocessing import Pool

import numpy as np

from .g6 import decode_g6, edges_of
from .alpha import alpha_batch
from .theta import theta_scs_direct
from .perfect import is_perfect
from .chrom import chromatic_number
from .g6 import complement

FIELDS = ["graph6", "n", "edges", "alpha", "theta", "delta", "perfect",
          "chi_comp", "solve_time", "status", "pr"]


def _process_chunk(args):
    lines, eps, do_perfect = args
    n0, _ = decode_g6(lines[0])
    adjs = []
    for L in lines:
        n, adj = decode_g6(L)
        adjs.append(adj)
    A = np.array(adjs, dtype=np.int32)
    alphas = alpha_batch(A, n0)
    out = []
    for k, L in enumerate(lines):
        adj = adjs[k]
        E = edges_of(n0, adj)
        r = theta_scs_direct(n0, E, eps=eps)
        per = is_perfect(n0, adj) if do_perfect else ""
        chi = chromatic_number(n0, complement(n0, adj)) if do_perfect else ""
        out.append([L, n0, len(E), int(alphas[k]), r["theta"],
                    r["theta"] - int(alphas[k]), per, chi, r["t"], r["status"], r["pr"]])
    return out


def sweep(g6_path, out_dir, tag, eps=1e-8, chunk=500, procs=7, do_perfect=True,
          limit=None):
    os.makedirs(out_dir, exist_ok=True)
    lines = [l.strip() for l in open(g6_path) if l.strip()]
    if limit:
        lines = lines[:limit]
    chunks = [lines[i:i + chunk] for i in range(0, len(lines), chunk)]
    todo, done_rows = [], {}
    for ci, ch in enumerate(chunks):
        p = os.path.join(out_dir, f"{tag}_partial_{ci:05d}.csv")
        if os.path.exists(p):
            with open(p) as fh:
                rd = list(csv.reader(fh))
            if len(rd) == len(ch):
                done_rows[ci] = rd
                continue
        todo.append(ci)
    print(f"[{tag}] {len(lines)} graphs, {len(chunks)} chunks, "
          f"{len(done_rows)} already on disk, {len(todo)} to do")
    t0 = time.perf_counter()
    if todo:
        with Pool(procs) as pool:
            it = pool.imap(_process_chunk,
                           [(chunks[ci], eps, do_perfect) for ci in todo], chunksize=1)
            for k, rows in enumerate(it):
                ci = todo[k]
                p = os.path.join(out_dir, f"{tag}_partial_{ci:05d}.csv")
                with open(p, "w", newline="") as fh:
                    csv.writer(fh).writerows(rows)
                done_rows[ci] = rows
                if (k + 1) % 20 == 0 or k + 1 == len(todo):
                    el = time.perf_counter() - t0
                    frac = (k + 1) / len(todo)
                    print(f"[{tag}] {k+1}/{len(todo)} chunks  {el:.0f}s elapsed  "
                          f"ETA {el/frac-el:.0f}s", flush=True)
    rows = []
    for ci in range(len(chunks)):
        rows.extend(done_rows[ci])
    out = os.path.join(out_dir, f"{tag}_all.csv")
    with open(out, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(FIELDS)
        w.writerows(rows)
    print(f"[{tag}] wrote {out} ({len(rows)} rows) in {time.perf_counter()-t0:.0f}s")
    _gzip_beside(out)
    return out


def _gzip_beside(path):
    """Keep a committed-size .gz next to a bulk CSV.  Done here rather than by hand so
    that a clean run produces exactly the artefacts the repository holds."""
    import gzip, shutil
    if os.path.getsize(path) < 5 << 20:
        return
    with open(path, "rb") as fi, gzip.open(path + ".gz", "wb", compresslevel=9) as fo:
        shutil.copyfileobj(fi, fo)
    print(f"    wrote {os.path.basename(path)}.gz "
          f"({os.path.getsize(path + '.gz') / 1048576:.1f} MB)")
