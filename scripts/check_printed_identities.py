#!/usr/bin/env python3
"""Check every printed "fraction = decimal" pair in the papers, and its rounding.

    .venv/bin/python scripts/check_printed_identities.py

THE BUG THIS CATCHES, named so the check is not vacuous.  Section 4.3 printed

    Delta <= 152 149 953 435 449 / 32 000 000 000 000 = 0.7546860448577810

The fraction is 4.75468604485778125 -- it is the dual bound on THETA, with alpha = 4
not yet subtracted -- while the decimal beside it is the bound on DELTA.  The equals
sign was false by exactly 4.  verify_paper_claims.py had a claim for the fraction and
a claim for the decimal, and both passed, because each compared a string in the paper
against the same string in README.md.  Nothing compared the fraction TO the decimal,
so the false equation lived in the gap between two passing checks.

Two verdicts per pair:
  IDENTITY  fraction == decimal, to the precision the decimal is printed at.
            A difference of a whole integer is reported as a units error, which is
            what a missing alpha looks like.
  ROUNDING  a printed LOWER bound may only be truncated DOWN, a printed UPPER bound
            may only be rounded UP.  Rounding the other way prints a claim strictly
            stronger than the certificate.  The bound's direction is taken from the
            comparator that precedes the fraction in the text.
"""
import re, sys, os, glob
from fractions import Fraction as F
from decimal import Decimal as D, getcontext

getcontext().prec = 80
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

NUM = r"\d[\d  ]*\d|\d"
PAIR = re.compile(r"([≤≥=]|\\le|\\ge)?\s*(" + NUM + r")\s*/\s*(" + NUM + r")\s*=\s*(\d+\.\d+)")


def clean(s):
    return s.replace(" ", "").replace(" ", "")


def main():
    files = sorted(glob.glob(os.path.join(ROOT, "papers", "*.md")))
    rows, bad = [], 0
    for path in files:
        raw = open(path, encoding="utf-8").read()
        flat = re.sub(r"\s+", " ", raw)
        for m in PAIR.finditer(flat):
            cmpsym, n, d, dec = m.group(1), clean(m.group(2)), clean(m.group(3)), m.group(4)
            # the bound direction: the last comparator in the 90 chars before the match
            pre = flat[max(0, m.start() - 90):m.start()]
            syms = re.findall(r"[≤≥]", pre + (cmpsym or ""))
            kind = {"≤": "upper", "≥": "lower"}.get(syms[-1], "value") if syms else "value"
            exact = F(int(n), int(d))
            ev = D(exact.numerator) / D(exact.denominator)
            pv = D(dec)
            diff = ev - pv
            places = len(dec.split(".")[1])
            unit = D(1).scaleb(-places)

            if abs(diff) >= D("0.5"):
                ident = "UNITS ERROR by %s" % (round(float(diff)))
            elif abs(diff) <= unit / 2:
                ident = "ok"
            else:
                ident = "off by %s (> half a printed unit)" % str(diff)[:14]

            if kind == "lower":
                rnd = "ok" if pv <= ev else "WRONG (lower bound rounded UP)"
            elif kind == "upper":
                rnd = "ok" if pv >= ev else "WRONG (upper bound rounded DOWN)"
            else:
                rnd = "n/a (no comparator found)"

            verdict = "PASS" if ident == "ok" and rnd.startswith(("ok", "n/a")) else "FAIL"
            if verdict == "FAIL":
                bad += 1
            rows.append((os.path.basename(path), kind, f"{n}/{d}", dec,
                         str(ev)[:22], ident, rnd, verdict))

    w = (34, 6, 34, 21, 22, 22, 32, 7)
    hdr = ("file", "type", "fraction", "printed decimal", "exact", "identity", "rounding", "verdict")
    print("  " + " | ".join(h.ljust(x) for h, x in zip(hdr, w)))
    print("  " + "-+-".join("-" * x for x in w))
    for r in rows:
        print("  " + " | ".join(str(c).ljust(x) for c, x in zip(r, w)))
    print(f"\n  {len(rows)} printed fraction=decimal pairs checked, {bad} failing.")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
