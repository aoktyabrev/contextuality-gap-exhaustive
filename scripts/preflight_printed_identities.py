#!/usr/bin/env python3
"""PRE-FLIGHT, not a gate: check every printed "fraction = decimal" pair in the BUILT PDFs.

    .venv/bin/python scripts/preflight_printed_identities.py [pdf ...]

Why this is a pre-flight and not one of the release gates.  It examines the manuscripts,
and `papers/` is gitignored -- drafts are sent to named people, not published from this
repository.  On a clean clone there is therefore nothing for it to look at, EVER, not
merely today.  A check that is structurally inapplicable in the release run is not a
gate; calling it one teaches a reader to skim past its result.  It belongs where it can
actually do work: locally, on the PDF, immediately before that PDF is sent.

Why the PDF and not the markdown.  The PDF is the artefact that leaves the machine.  The
source is where the numbers are typed, but a typesetting bug can change what a reader
sees -- this build has already produced literal asterisks, a dropped macron and literal
underscores where mathematics was meant.  Checking the source would answer a weaker
question than the one that matters.

THE BUG THIS CATCHES, named so the check is not vacuous.  Section 4.3 printed

    Delta <= 152 149 953 435 449 / 32 000 000 000 000 = 0.7546860448577810

The fraction is 4.75468604485778125: it bounds theta, with alpha = 4 not yet subtracted,
while the decimal beside it bounds Delta.  The equals sign was false by exactly 4.  A
second instance, found by sweeping every printed bound rather than the one reported: an
upper bound on T(13,5) printed truncated DOWNWARDS, which states a claim strictly
stronger than the certificate behind it.

Two verdicts per pair:
  IDENTITY  fraction == decimal at the precision printed; a whole-integer difference is
            reported as a units error, which is what a missing alpha looks like.
  ROUNDING  a printed LOWER bound may only be truncated DOWN, an UPPER bound only
            rounded UP.  Direction is taken from the comparator preceding the fraction.

Exit 0 all pairs pass, 1 a pair fails, 2 nothing to check (no PDFs) -- never a silent
green on an empty input set.
"""
import re, sys, os, glob, shutil, subprocess
from fractions import Fraction as F
from decimal import Decimal as D, getcontext

getcontext().prec = 80
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# digits may be separated by ordinary or thin spaces in the typeset text, and the
# extractor sometimes closes the gaps entirely, so both forms must match
NUM = r"\d[\d    ]*\d|\d"
PAIR = re.compile(r"([≤≥=])?\s*(" + NUM + r")\s*/\s*(" + NUM + r")\s*=\s*(\d+\.\d+)")


def extract(pdf):
    """Text of a PDF.  pdftotext if present, else ghostscript's txtwrite."""
    if shutil.which("pdftotext"):
        r = subprocess.run(["pdftotext", "-layout", pdf, "-"],
                           capture_output=True, text=True)
        if r.returncode == 0:
            return r.stdout, "pdftotext"
    r = subprocess.run(["gs", "-q", "-dNOPAUSE", "-dBATCH", "-sDEVICE=txtwrite",
                        "-sOutputFile=-", pdf], capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"cannot extract text from {pdf}: {r.stderr[:200]}")
    return r.stdout, "gs txtwrite"


def clean(s):
    return re.sub(r"[\s  ]", "", s)


def main():
    pdfs = sys.argv[1:] or sorted(glob.glob(os.path.join(ROOT, "papers", "*.pdf")))
    rows, bad = [], 0
    for pdf in pdfs:
        text, how = extract(pdf)
        flat = re.sub(r"\s+", " ", text)
        for m in PAIR.finditer(flat):
            n, d, dec = clean(m.group(2)), clean(m.group(3)), m.group(4)
            pre = flat[max(0, m.start() - 90):m.start()]
            syms = re.findall(r"[≤≥]", pre + (m.group(1) or ""))
            kind = {"≤": "upper", "≥": "lower"}.get(syms[-1], "value") if syms else "value"
            exact = F(int(n), int(d))
            ev = D(exact.numerator) / D(exact.denominator)
            pv = D(dec)
            diff = ev - pv
            unit = D(1).scaleb(-len(dec.split(".")[1]))

            if abs(diff) >= D("0.5"):
                ident = "UNITS ERROR by %d" % round(float(diff))
            elif abs(diff) <= unit / 2:
                ident = "ok"
            else:
                ident = "off by %s" % str(diff)[:12]

            if kind == "lower":
                rnd = "ok" if pv <= ev else "WRONG (lower rounded UP)"
            elif kind == "upper":
                rnd = "ok" if pv >= ev else "WRONG (upper rounded DOWN)"
            else:
                rnd = "n/a (no comparator)"

            verdict = "PASS" if ident == "ok" and not rnd.startswith("WRONG") else "FAIL"
            bad += verdict == "FAIL"
            rows.append((re.sub(r"^Oktiabrev_theta_alpha_gaps_n11_|\.pdf$","",os.path.basename(pdf))[:22], kind, f"{n}/{d}", dec,
                         str(ev)[:22], ident, rnd, verdict))
        print(f"  {os.path.basename(pdf)}  ({how})")

    if not pdfs:
        print("\n  NOTHING TO CHECK — no PDFs given and none in papers/.")
        print("  Build them first: .venv/bin/python scripts/build_paper_pdf.py --edition ...")
        return 2

    w = (22, 6, 32, 21, 22, 18, 26, 7)
    hdr = ("edition", "type", "fraction", "printed decimal", "exact", "identity",
           "rounding", "verdict")
    print()
    print("  " + " | ".join(h.ljust(x) for h, x in zip(hdr, w)))
    print("  " + "-+-".join("-" * x for x in w))
    for r in rows:
        print("  " + " | ".join(str(c).ljust(x) for c, x in zip(r, w)))
    print(f"\n  {len(rows)} printed fraction=decimal pairs checked in {len(pdfs)} PDF(s), "
          f"{bad} failing.")
    if not rows:
        print("  NOTHING TO CHECK — the PDFs contain no fraction=decimal pairs.")
        return 2
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
