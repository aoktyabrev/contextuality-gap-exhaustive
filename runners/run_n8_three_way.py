"""Three-way graph-for-graph agreement at n = 8, and it checks all three sides.

Requested by U. Tamer as lead author of arXiv:2605.12828 (email of 2026-09-04): the
graph-for-graph agreement with the Amselem-Danielsen-Lopez-Tarrida-Portillo files at
n = 8, with no disagreement on the independence number, is an independent check on
*their* enumeration as much as on ours, and they asked for it to be documented as such.

Until now the repository recorded this comparison in one direction only -- the database
and our sweep -- and treated it as validation of our pipeline.  It is not only that.  At
n = 8 there are three independent enumerations of the connected graphs:

  1. the authors' own, published as all_n8_results.csv in their repository (commit
     bfacfd0), 11 117 rows, 8-digit Delta from SCS;
  2. the 2012 database, sources/quantum_graphs/quantum8, 498 rows, 4-digit theta;
  3. ours, results/n8_all.csv, 11 117 rows.

Nothing here picks a threshold to make the counts agree: the authors' file gives the
same 498 graphs at 1e-5, 1e-6 and 1e-7, so the set is threshold-free on their side and
the comparison is a set comparison, not a count comparison.

Sets are compared as graph6 STRINGS, not up to isomorphism.  That is the stronger
statement and it is available here because all three sides label with McKay's default
geng labelling; see the graph6 trap in CLAUDE.md for why the distinction matters.
"""
import sys, os, json, csv, argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")

AUTHORS_CSV = os.path.join(ROOT, "authors_run", "all_n8_results.csv")
DB_FILE = os.path.join(ROOT, "sources", "quantum_graphs", "quantum8")
OURS_CSV = os.path.join(RES, "n8_all.csv")

AUTHORS_REPO = "https://github.com/ugurtamerphys/quad-c5-contextuality"
DB_URL = "https://codetables.de/larsed/quantum_graphs/"

# The authors' file IS in this repository, under sources/zenodo_extract/: their Zenodo
# archive is CC BY 4.0 (LICENSE-DATA), so that copy may be redistributed and is the one
# used.  authors_run/ is only a scratch working copy and is gitignored.  The network is
# the last resort, for a checkout where sources/ has been pruned; either way the bytes
# are checked against the sha256 in sources/authors_run.sha256.
AUTHORS_ZENODO = ("https://zenodo.org/api/records/20465134/files/"
                  "ugurtamerphys/quad-c5-contextuality-v1.0.0.zip/content")


ZENODO_EXTRACT = os.path.join(ROOT, "sources", "zenodo_extract",
                              "ugurtamerphys-quad-c5-contextuality-bfacfd0",
                              "all_n8_results.csv")


def ensure_authors_csv():
    """Return a verified path to the authors' per-graph file.

    Preference order: the CC BY 4.0 copy committed under sources/zenodo_extract/, then
    the local scratch copy, then the network.  Whichever is used, the bytes must match
    sources/authors_run.sha256.
    """
    import hashlib, io, zipfile, urllib.request
    want = open(os.path.join(ROOT, "sources", "authors_run.sha256")).read().split()[0]
    for cand in (ZENODO_EXTRACT, AUTHORS_CSV):
        if os.path.exists(cand):
            got = hashlib.sha256(open(cand, "rb").read()).hexdigest()
            if got != want:
                raise SystemExit(f"{cand}: sha256 {got} != committed {want}")
            return cand
    if not os.path.exists(AUTHORS_CSV):
        print(f"  fetching the authors' archive from Zenodo 10.5281/zenodo.20465134")
        blob = urllib.request.urlopen(AUTHORS_ZENODO, timeout=120).read()
        with zipfile.ZipFile(io.BytesIO(blob)) as z:
            name = next(n for n in z.namelist() if n.endswith("all_n8_results.csv"))
            os.makedirs(os.path.dirname(AUTHORS_CSV), exist_ok=True)
            with open(AUTHORS_CSV, "wb") as fh:
                fh.write(z.read(name))
    got = hashlib.sha256(open(AUTHORS_CSV, "rb").read()).hexdigest()
    if got != want:
        raise SystemExit(f"all_n8_results.csv: sha256 {got} != committed {want}")
    return AUTHORS_CSV


def load_authors(path=None):
    """graph6 -> (alpha, delta).  Their published per-graph file, all 11 117 rows."""
    out = {}
    with open(path or AUTHORS_CSV) as fh:
        for r in csv.DictReader(fh):
            out[r["graph6"]] = (int(r["alpha"]), float(r["delta_scs"]))
    return out


def load_db():
    """graph6 -> (alpha, theta).  Columns per the database's own index page."""
    out = {}
    with open(DB_FILE) as fh:
        for line in fh:
            f = line.split()
            if len(f) < 4:
                continue
            out[f[1]] = (int(f[2]), float(f[3]))
    return out


def load_ours():
    out = {}
    with open(OURS_CSV) as fh:
        for r in csv.DictReader(fh):
            out[r["graph6"]] = (int(r["alpha"]), float(r["delta"]))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tau", type=float, default=1e-6)
    ap.add_argument("--out", default=os.path.join(RES, "report_n8_three_way.json"))
    ap.add_argument("--seed", type=int, default=20260819)  # unused; kept for uniformity
    args = ap.parse_args()

    csv_path = ensure_authors_csv()
    print(f"  authors' file: {os.path.relpath(csv_path, ROOT)}")
    # the database is not redistributed either; run_db_compare.py already owns the
    # fetch-and-verify for it, so reuse that rather than write a second copy of it
    from run_db_compare import ensure_db
    ensure_db()
    A, D, O = load_authors(csv_path), load_db(), load_ours()

    # The authors' set is threshold-free across three decades; report that rather than
    # asserting it, because it is the reason this is a set comparison at all.
    stability = {f"{t:g}": sum(1 for _, d in A.values() if d > t)
                 for t in (1e-5, 1e-6, 1e-7)}

    A_gap = {g for g, (_, d) in A.items() if d > args.tau}
    D_gap = set(D)
    O_gap = {g for g, (_, d) in O.items() if d > args.tau}

    def cmp(x, y):
        return {"identical": x == y, "only_first": sorted(x - y), "only_second": sorted(y - x)}

    def alpha_mismatch(x, y):
        return sorted(g for g in x if g in y and x[g][0] != y[g][0])

    worst_g, worst_v = None, 0.0
    for g in D:
        if g in A:
            v = abs((A[g][1] + A[g][0]) - D[g][1])   # their theta = alpha + delta
            if v > worst_v:
                worst_g, worst_v = g, v

    rep = {
        "stage": "F.1 -- reciprocal n=8 check, requested by the lead author of arXiv:2605.12828",
        "requested_by": "U. Tamer, email 2026-09-04",
        "tau": args.tau,
        "sources": {
            "authors": {"file": "authors_run/all_n8_results.csv", "repo": AUTHORS_REPO,
                        "commit": "bfacfd0", "rows": len(A)},
            "database": {"file": "sources/quantum_graphs/quantum8", "url": DB_URL,
                         "rows": len(D), "accessed": "2026-08-27"},
            "ours": {"file": "results/n8_all.csv", "rows": len(O)},
        },
        "authors_set_size_by_threshold": stability,
        "counts": {"authors": len(A_gap), "database": len(D_gap), "ours": len(O_gap)},
        "all_three_identical_as_graph6_strings": A_gap == D_gap == O_gap,
        "pairwise": {
            "authors_vs_database": cmp(A_gap, D_gap),
            "ours_vs_database": cmp(O_gap, D_gap),
            "ours_vs_authors": cmp(O_gap, A_gap),
        },
        "alpha_mismatches": {
            "ours_vs_authors": {"compared": len(O), "mismatches": alpha_mismatch(O, A)},
            "ours_vs_database": {"compared": len(D), "mismatches": alpha_mismatch(O, D)},
            "authors_vs_database": {"compared": len(D), "mismatches": alpha_mismatch(A, D)},
        },
        "max_abs_theta_diff_authors_vs_database": {"value": worst_v, "graph6": worst_g,
                                                   "note": "database prints 4 decimals"},
    }

    with open(args.out, "w") as fh:
        json.dump(rep, fh, indent=2)

    ok = (rep["all_three_identical_as_graph6_strings"]
          and not any(v["mismatches"] for v in rep["alpha_mismatches"].values()))
    print(json.dumps(rep["counts"]), "identical:", rep["all_three_identical_as_graph6_strings"])
    for k, v in rep["alpha_mismatches"].items():
        print(f"  alpha {k}: {len(v['mismatches'])} mismatches over {v['compared']}")
    print("wrote", args.out)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
