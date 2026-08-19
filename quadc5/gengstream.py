"""Streaming graph generation through nauty's geng (SOURCES.md S5).

No graph file is downloaded: geng is run as a subprocess and its stdout is read
line by line.  Auxiliary lines (">A ...", ">Z ...") are suppressed with -q and,
defensively, skipped here as well.

Labelling note, established by measurement in gate 1.a and NOT assumed: McKay's
published graph{n}c.g6 files are in geng's DEFAULT output labelling.  Adding -l
("canonically label output graphs") produces a different, equally valid set of
graph6 strings that does NOT match the published files.  So -l is not used.
"""
from __future__ import annotations
import os, subprocess

GENG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "build", "nauty2_9_3", "geng")


def geng_argv(n, connected=True, res=None, mod=None, extra=(), quiet=True):
    argv = [GENG]
    if connected:
        argv.append("-c")
    if quiet:
        argv.append("-q")      # -q also suppresses the ">Z <count>" summary line
    argv.extend(extra)
    argv.append(str(n))
    if mod:
        argv.append(f"{res}/{mod}")
    return argv


def count(n, connected=True, extra=()):
    """geng -u: generate and count without emitting graphs."""
    argv = geng_argv(n, connected, extra=tuple(extra) + ("-u",), quiet=False)
    out = subprocess.run(argv, capture_output=True, text=True)
    for line in (out.stderr + out.stdout).splitlines():
        if line.startswith(">Z"):
            return int(line.split()[1])
    raise RuntimeError("no >Z line from geng: %r" % (out.stderr[-400:],))


def stream(n, connected=True, res=None, mod=None, extra=(), bufsize=1 << 20):
    """Yield graph6 strings one at a time."""
    argv = geng_argv(n, connected, res, mod, extra)
    p = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                         text=True, bufsize=bufsize)
    try:
        for line in p.stdout:
            line = line.strip()
            if line and not line.startswith(">"):
                yield line
    finally:
        p.stdout.close()
        p.wait()
