#!/usr/bin/env python3
"""Check every numeric claim in papers/*.md against the repository.  Exit 0 iff all pass.

    .venv/bin/python scripts/verify_paper_claims.py

The claims live in papers/claims.json, transcribed BY HAND from the papers.  That is the
point: the expected values come from the prose, and this script compares them against the
data.  Auto-filling them from the data would make the check vacuous.

Check kinds:
  json      numeric value at a dotted path, within an optional tolerance
  json_str  exact string form of the value at a dotted path
  text      a literal substring must occur in a named file
  agg       a named aggregate computed here from the raw per-graph data
  multi     several of the above, all of which must pass

The dotted path walks dicts and lists alike; a segment that is an integer indexes a list.
Dict keys containing dots would be ambiguous, so path segments are matched against the
literal key first and only then treated as an index.
"""
import sys, os, json, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLAIMS = os.path.join(ROOT, "papers", "claims.json")
fails, checked = [], 0
_cache = {}


def load_json(rel):
    p = os.path.join(ROOT, rel)
    if p not in _cache:
        _cache[p] = json.load(open(p))
    return _cache[p]


def dig(obj, path):
    cur = obj
    rest = path
    while rest:
        # longest literal key that matches wins, so keys like "log2|Aut|" survive
        if isinstance(cur, dict):
            hit = None
            for k in cur:
                if rest == k or rest.startswith(k + "."):
                    if hit is None or len(k) > len(hit):
                        hit = k
            if hit is None:
                raise KeyError(f"{rest!r} not in {list(cur)[:8]}")
            cur = cur[hit]
            rest = rest[len(hit):].lstrip(".")
        elif isinstance(cur, list):
            seg, _, rest = rest.partition(".")
            cur = cur[int(seg)]
        else:
            raise KeyError(f"cannot descend into {type(cur).__name__} for {rest!r}")
    return cur


def note(ok, cid, detail=""):
    global checked
    checked += 1
    if not ok:
        fails.append((cid, detail))
    return ok


def run_one(cid, ch):
    kind = ch.get("kind", "json")
    if kind == "text":
        p = os.path.join(ROOT, ch["file"])
        body = open(p, encoding="utf-8").read()
        return note(ch["needle"] in body, cid,
                    f"{ch['file']} does not contain {ch['needle']!r}")
    if kind in ("json", "json_str"):
        try:
            got = dig(load_json(ch["file"]), ch["path"])
        except Exception as e:
            return note(False, cid, f"{ch['file']}:{ch['path']} unreadable: {e}")
        exp = ch["expect"]
        if kind == "json_str" or isinstance(exp, str):
            s = json.dumps(got, ensure_ascii=False) if isinstance(got, (list, dict)) else str(got)
            return note(s == str(exp), cid, f"{ch['path']}: {s!r} != {exp!r}")
        if isinstance(exp, bool) or isinstance(got, bool):
            return note(got == exp, cid, f"{ch['path']}: {got} != {exp}")
        if isinstance(exp, dict):
            return note(got == exp, cid, f"{ch['path']}: {got} != {exp}")
        if got is None:
            return note(False, cid, f"{ch['path']}: value is null, expected {exp}")
        tol = ch.get("tol", 0)
        return note(abs(float(got) - float(exp)) <= tol, cid,
                    f"{ch['path']}: {got} != {exp} (tol {tol})")
    if kind == "agg":
        got = AGG[ch["agg"]]()
        exp = ch["expect"]
        if isinstance(exp, dict):
            return note(got == exp, cid, f"{ch['agg']}: {got} != {exp}")
        tol = ch.get("tol", 0)
        return note(abs(float(got) - float(exp)) <= tol, cid,
                    f"{ch['agg']}: {got} != {exp} (tol {tol})")
    if kind == "layer":
        # D(n, a) straight from the Stage 7 layer table -- the feeding terms of a
        # transfer bound.  Recomputed here rather than copied, because naming the wrong
        # feeding term is exactly the mistake this check exists to catch.
        tab = load_json("results/report_7.json")["blocks"]["7b"]
        hit = [r for r in tab if r["n"] == ch["n"] and r["a"] == ch["a"]]
        if not hit:
            return note(False, cid, f"D({ch['n']},{ch['a']}) absent from the layer table")
        return note(abs(hit[0]["D"] - ch["expect"]) <= ch.get("tol", 0), cid,
                    f"D({ch['n']},{ch['a']}) = {hit[0]['D']} != {ch['expect']}")
    if kind == "layer8":
        import csv
        best = {}
        with open(os.path.join(ROOT, "results", "n8_all.csv")) as f:
            for r in csv.DictReader(f):
                a, d = int(r["alpha"]), float(r["delta"])
                if d > best.get(a, -1):
                    best[a] = d
        got = best.get(ch["a"])
        if got is None:
            return note(False, cid, f"no n=8 layer a={ch['a']}")
        return note(abs(got - ch["expect"]) <= ch.get("tol", 0), cid,
                    f"D(8,{ch['a']}) = {got} != {ch['expect']}")
    if kind == "multi":
        ok = True
        for j, item in enumerate(ch["items"]):
            sub = dict(item)
            sub.setdefault("kind", "text" if "needle" in sub else
                           ("json_str" if sub.get("kind") == "str" else "json"))
            if item.get("kind") == "str":
                sub["kind"] = "json_str"
            ok &= run_one(f"{cid}[{j}]", sub)
        return ok
    return note(False, cid, f"unknown check kind {kind!r}")


# ---- named aggregates, computed from the raw data -------------------------------
def _stage9_rows():
    p = os.path.join(ROOT, "results", "stage9_degrees.jsonl")
    return [json.loads(l) for l in open(p) if l.strip()]


def _hist():
    h = collections.Counter(r["degree"] for r in _stage9_rows() if r["status"] == "hit")
    return {str(k): v for k, v in sorted(h.items())}


AGG = {
    "stage9_rows":      lambda: len(_stage9_rows()),
    "stage9_hit":       lambda: sum(1 for r in _stage9_rows() if r["status"] == "hit"),
    "stage9_notfound":  lambda: sum(1 for r in _stage9_rows() if r["status"] == "not_found"),
    "stage9_hist":      _hist,
    "stage9_deg5":      lambda: _hist().get("5", 0),
    "stage9_share_le4": lambda: round(
        100.0 * sum(v for k, v in _hist().items() if int(k) <= 4) / sum(_hist().values()), 2),
    "seal_count":       lambda: len(re.findall(
        r"^check(?:_doc)? ", open(os.path.join(ROOT, "scripts", "verify_seals.sh")).read(),
        re.M)),
    "pack_checks":      lambda: len(re.findall(
        r"^\s*step\(", open(os.path.join(ROOT, "verification_pack", "verify.py")).read(), re.M)),
}


def main():
    claims = json.load(open(CLAIMS, encoding="utf-8"))
    by_tag = collections.Counter(c["tag"] for c in claims)
    by_paper = collections.Counter(c["paper"] for c in claims)
    print(f"{len(claims)} claims transcribed from the papers by hand")
    print(f"  by paper: {dict(by_paper)}")
    print(f"  by tag:   {dict(by_tag)}\n")
    for cl in claims:
        ok = run_one(cl["id"], cl["check"])
        if not ok:
            print(f"  MISMATCH  {cl['id']}  ({cl['paper']} §{cl['section']}) "
                  f"[{cl['tag']}] {cl['claim']}: as written {cl['as_written']!r}")
    print(f"\n{checked} comparisons, {len(fails)} mismatches")

    # A claim list compares numbers one at a time, so a false RELATION between two of
    # them -- "this fraction equals that decimal" -- is invisible to it: each side can
    # pass its own check while the equals sign between them is wrong.  That happened in
    # section 4.3.  This pass checks the printed pairs themselves.
    print()
    import subprocess
    ident = subprocess.run([sys.executable,
                            os.path.join(ROOT, "scripts", "check_printed_identities.py")],
                           capture_output=True, text=True)
    print(ident.stdout.rstrip())
    if ident.returncode != 0:
        print(ident.stderr.rstrip())

    if fails or ident.returncode != 0:
        print("\nPAPER CLAIM CHECK FAILED:")
        for cid, d in fails:
            print(f"  {cid}: {d}")
        if ident.returncode != 0:
            print("  printed fraction=decimal identities: see the table above")
        return 1
    print("\nPAPER CLAIM CHECK PASSED — every number in both papers matches the "
          "repository, and every printed fraction equals the decimal beside it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
