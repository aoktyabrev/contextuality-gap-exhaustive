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

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAUTY_VERSION = "2.9.3"
GENG = os.path.join(ROOT, "build", "nauty2_9_3", "geng")

_MISSING = """
geng was not found at
    {path}

QUADC5 generates the graph enumeration with nauty's geng ({ver}); no graph file is
downloaded.  Build it once, from the tarball already in sources/:

    mkdir -p build && tar xzf sources/nauty2_9_3.tar.gz -C build
    cd build/nauty2_9_3 && ./configure && make -j geng

`bash runners/run_stage1.sh` does this automatically if geng is missing.
A system nauty also works: point the QUADC5_GENG environment variable at its
binary (Debian/Ubuntu package `nauty` installs it as /usr/bin/nauty-geng).
"""


def geng_path():
    """Resolve geng, or explain how to get it.  Never raises a bare FileNotFoundError."""
    env = os.environ.get("QUADC5_GENG")
    cand = env or GENG
    if os.path.isfile(cand) and os.access(cand, os.X_OK):
        return cand
    raise RuntimeError(_MISSING.format(path=cand, ver=NAUTY_VERSION))


def geng_argv(n, connected=True, res=None, mod=None, extra=(), quiet=True):
    argv = [geng_path()]
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
