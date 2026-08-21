# Verification pack — ϑ(Quad-C₅)

A self-contained check of one statement, for the eight-vertex graph with graph6 code
`` GCQb`o `` (the Quad-C₅ graph):

> **ϑ(Quad-C₅) is the root of x⁴ − x³ + 23x² − 155x + 158 lying in (3, 4)**, and α = 3,
> so Δ = ϑ − α = ϑ − 3 = 0.4678437298402241086973918817770…

## Run it

```
python3 verify.py
```

21 checks; prints PASS or FAIL and exits non-zero on FAIL. Standard library only — no
installation, no network, no SDP solver, nothing to download. About one second (0.7 s on
Python 3.12, 1.8 s on 3.7; tested on 3.7, 3.9, 3.11 and 3.12 with networking disabled).

No floating-point value takes part in any verdict. The certificate entries are integer
numerator/denominator pairs over ℚ(ϑ), and every sign is decided by exact rational
interval arithmetic. Read `NOTE.md` for why that is a proof and not a coincidence.

To see that the script can fail: change a coefficient in `minpoly_low_to_high`, or set
`alpha` to 2, in `certificates/quadc5_certificate.json`. It exits non-zero and names the
check that broke.

## Contents

| file | |
|---|---|
| `verify.py` | the checker |
| `certificates/quadc5_certificate.json` | exact primal and dual matrices over ℚ(ϑ) |
| `certificates/minimal_polynomial.txt` | the quartic, and why (3, 4) names one root |
| `NOTE.md` | two pages: what a certificate proves, and how ℚ(ϑ) is represented |
| `graph6.txt` | maximizers for n = 5…10 with α, ϑ, Δ and minimal polynomials |
| `comparison_n8.md` | this eight-vertex ranking beside the published one |
| `README.md` | this file |

## Where this came from

An extract from a larger study — exhaustive enumeration of the contextuality gap
Δ(G) = ϑ(G) − α(G) over all connected graphs up to ten vertices, with exact certificates:

    https://github.com/aoktyabrev/contextuality-gap-exhaustive

    doi:10.5281/zenodo.22031808   concept DOI, always the current version
    doi:10.5281/zenodo.22031809   release v1.0.0

The same folder is in that repository as `verification_pack/`, from commit `31dd5cf`.

The study continues U. Tamer, Ö. E. Müstecaplıoğlu, A. Dizdar and Z. Gedik,
*The Quad-C₅ Graph: Maximum Contextuality Gap on Eight Vertices*, arXiv:2605.12828 —
please cite that paper as well.

Artem Oktiabrev · ORCID [0009-0003-3626-2002](https://orcid.org/0009-0003-3626-2002) ·
aoktyabrev@gmail.com · prepared 2026-08-21

The code in this folder is MIT-licensed; the certificates and prose are CC-BY-4.0, as in
the repository above.
