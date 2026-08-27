"""Per-graph comparison against the Cabello-Danielsen-Lopez-Tarrida-Portillo database.

Stage 3 recorded this comparison as IMPOSSIBLE: the per-graph files were not archived
anywhere and only the index page survived, so the database's counts were quotable and its
values were not (SOURCES.md S11, accessed 2026-08-20).  That is no longer true.  Lars
Eirik Danielsen replied on 2026-08-27 that the data had moved to

    https://codetables.de/larsed/quantum_graphs/

and the files are now in sources/quantum_graphs/ with checksums in
sources/quantum_graphs.sha256.

So this is no longer a comparison of two totals.  It is two independent enumerations,
fourteen years apart, matched graph by graph.  The database's columns are documented on
its own index page: id, nauty string, alpha, theta, alpha*, d, upper bound for orthogonal
rank, Q, S, intersection number, the same for the complement, chromatic number of the
complement.

One thing the script does NOT do is pick a threshold to make the counts agree.  It reports
the symmetric difference at several thresholds and, for every graph on which the two sides
disagree, whether our own sandwich filter proves the gap to be exactly zero -- which is an
argument, not a measurement, and settles the case either way.
"""
import sys, os, json, csv, gzip, argparse
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
DB = os.path.join(ROOT, "sources", "quantum_graphs")
DB_URL = "https://codetables.de/larsed/quantum_graphs/"

# The database carries no rights statement, so this repository does not redistribute it.
# It is fetched on demand instead, and the checksums it must match are committed in
# sources/quantum_graphs.sha256 -- so a reader verifies the same bytes we used without
# our having republished them.


def ensure_db():
    """Fetch the database if absent, and check it against the committed checksums."""
    import urllib.request, hashlib, bz2
    os.makedirs(DB, exist_ok=True)
    sums = {}
    with open(os.path.join(ROOT, "sources", "quantum_graphs.sha256")) as f:
        for line in f:
            h, _, name = line.strip().partition("  ")
            sums[name] = h
    for name in ("index.html", "quantum5", "quantum6", "quantum7", "quantum8",
                 "quantum9", "quantum10.bz2"):
        dst = os.path.join(DB, name)
        if not os.path.exists(dst):
            print(f"  fetching {name} from {DB_URL}")
            urllib.request.urlretrieve(DB_URL + name, dst)
        got = hashlib.sha256(open(dst, "rb").read()).hexdigest()
        if name in sums and got != sums[name]:
            raise SystemExit(f"{name}: sha256 {got} != committed {sums[name]}")
    flat = os.path.join(DB, "quantum10")
    if not os.path.exists(flat):
        with bz2.open(os.path.join(DB, "quantum10.bz2"), "rb") as z, open(flat, "wb") as o:
            o.write(z.read())
csv.field_size_limit(1 << 30)
THRESHOLDS = (1e-7, 1e-6, 1e-5)


def read_db(n):
    """graph6 -> (alpha, theta) from the database's own columns."""
    out = {}
    with open(os.path.join(DB, f"quantum{n}")) as f:
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) >= 4:
                out[p[1]] = (int(p[2]), float(p[3]))
    return out


def enumerate_small(n):
    """n = 5, 6 were computed on the fly and never tabulated; redo them here."""
    from quadc5.g6 import decode_g6, edges_of, complement
    from quadc5.alpha import alpha_bitmask
    from quadc5.chrom import chromatic_number
    from quadc5.theta import theta_cvxpy
    from quadc5 import gengstream
    out = {}
    for code in gengstream.stream(n):
        nn, adj = decode_g6(code)
        al = alpha_bitmask(nn, adj)
        th = theta_cvxpy(nn, edges_of(nn, adj), solver="CLARABEL")["theta"]
        out[code] = (al, th, th - al, chromatic_number(nn, complement(nn, adj)))
    return out


def read_ours(n):
    """graph6 -> (alpha, theta, delta, chi_comp) over every graph we swept at size n."""
    out = {}
    if n <= 6:
        return enumerate_small(n)
    if n <= 9:
        src, opener = os.path.join(RES, f"n{n}_all.csv"), open
    else:
        src, opener = os.path.join(RES, f"n{n}_nonzero.csv"), open
        if not os.path.exists(src):
            src, opener = src + ".gz", lambda p: gzip.open(p, "rt")
    with opener(src) as f:
        for r in csv.DictReader(f):
            out[r["graph6"]] = (int(r["alpha"]), float(r["theta"]),
                                float(r["delta"]), int(r["chi_comp"]))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", type=int, nargs="+", default=[5, 6, 7, 8, 9, 10])
    ap.add_argument("--out", default=os.path.join(RES, "report_db_compare.json"))
    a = ap.parse_args()
    ensure_db()
    rep = {"source": DB_URL,
           "accessed": "2026-08-27", "thresholds": list(THRESHOLDS), "sizes": {}}

    for n in a.sizes:
        db, ours = read_db(n), read_ours(n)
        theirs = set(db)
        row = {"db_count": len(theirs), "at_threshold": {}}
        print(f"\n=== n = {n}:  database {len(theirs):,} graphs ===")
        for tau in THRESHOLDS:
            mine = {g for g, v in ours.items() if v[2] > tau}
            only_them, only_us = theirs - mine, mine - theirs
            row["at_threshold"][f"{tau:g}"] = dict(
                ours=len(mine), only_theirs=len(only_them), only_ours=len(only_us),
                identical=(not only_them and not only_us))
            mark = "  <-- IDENTICAL SET" if not only_them and not only_us else ""
            print(f"  tau = {tau:g}:  ours {len(mine):>7,}   "
                  f"only theirs {len(only_them):>4}   only ours {len(only_us):>4}{mark}")

        # the decisive part: what are the graphs the two sides disagree on?
        tau = 1e-7
        mine = {g for g, v in ours.items() if v[2] > tau}
        diffs = []
        for g in sorted(mine - theirs):
            al, th, dl, chi = ours[g]
            diffs.append(dict(graph6=g, side="ours_only", alpha=al, delta=dl,
                              chi_comp=chi, sandwich_forces_zero=(chi == al)))
        for g in sorted(theirs - mine):
            v = ours.get(g)
            diffs.append(dict(graph6=g, side="theirs_only",
                              our_delta=None if v is None else v[2],
                              in_our_sweep=v is not None))
        row["disagreements_at_1e-7"] = diffs
        if diffs:
            forced = sum(1 for d in diffs if d.get("sandwich_forces_zero"))
            print(f"  at tau = 1e-7 the sides differ on {len(diffs)} graph(s); "
                  f"{forced} of them are forced to Delta = 0 by chi(complement) = alpha")
            for d in diffs[:12]:
                if d["side"] == "ours_only":
                    print(f"     ours only  {d['graph6']:12s} alpha={d['alpha']} "
                          f"delta={d['delta']:.3e} chi={d['chi_comp']} "
                          f"{'PROVABLY ZERO' if d['sandwich_forces_zero'] else 'genuine'}")
                else:
                    print(f"     theirs only {d['graph6']:12s} "
                          f"our delta={d['our_delta']}")

        # values, on the graphs both sides agree are quantum
        both = theirs & {g for g, v in ours.items() if v[2] > 1e-6}
        if both:
            da = sum(1 for g in both if db[g][0] != ours[g][0])
            dt = max(abs(db[g][1] - ours[g][1]) for g in both)
            worst = max(both, key=lambda g: abs(db[g][1] - ours[g][1]))
            row["values"] = dict(compared=len(both), alpha_mismatches=da,
                                 max_theta_diff=round(dt, 6), worst_graph=worst,
                                 their_theta=db[worst][1],
                                 our_theta=round(ours[worst][1], 6))
            print(f"  values on the {len(both):,} graphs both call quantum: "
                  f"alpha mismatches {da}, max |theta difference| {dt:.6f} "
                  f"(they print 4 decimals)")
        rep["sizes"][str(n)] = row

    json.dump(rep, open(a.out, "w"), indent=1)
    print(f"\nwrote {a.out}")
