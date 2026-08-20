"""Block 2.e -- symmetry against the degree of the field theta lives in.
Reconnaissance; a negative answer was accepted in advance (PREREGISTRATION_STAGE2 6).
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import networkx as nx
import sympy as sp
from scipy.stats import spearmanr

from quadc5.g6 import decode_g6, to_networkx, edges_of

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(ROOT, "results")
x = sp.symbols("x")

# every graph in this campaign whose theta is now known exactly, plus the one that is not
ROWS = [
    ("n=5 maximizer",  "DUW",        2, x**2 - 5,                       "sqrt5"),
    ("n=6 maximizer",  "EUZw",       2, x**2 - 5,                       "sqrt5"),
    ("n=7 maximizer",  "FCp`_",      3, x**3 + 7*x**2 - 49*x + 49,      "cubic, cyclotomic"),
    ("n=8 maximizer",  "GCQb`o",     4, x**4 - x**3 + 23*x**2 - 155*x + 158, "quartic"),
    ("n=9 maximizer",  "HCRbdO{",    1, x - sp.Rational(11, 3),         "11/3"),
    ("n=9 rank 2",     "HCrb`qi",    2, x**2 - 5*x + 5,                 "(5+sqrt5)/2"),
    ("n=10 maximizer", "ICRb`yiu?",  2, 2*x**2 - 12*x + 17,             "3+sqrt2/2"),
    ("n=10 rank 3",    "ICRbcqhNO",  1, x - sp.Rational(11, 3),         "11/3"),
    ("n=10 rank 4",    "ICQ`fP[r_",  1, x - sp.Rational(11, 3),         "11/3"),
    ("n=10 rank 5",    "ICRbdO{xG",  1, x - sp.Rational(11, 3),         "11/3"),
    ("n=10 rank 2",    "ICQeR`[Mg",  None, None,                        "not obtained"),
]


def aut_and_orbit(code):
    n, adj = decode_g6(code)
    G = to_networkx(n, adj)
    aut, orb = 0, set()
    for iso in nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter():
        aut += 1
        orb.add(iso[0])
    return n, len(edges_of(n, adj)), aut, len(orb) == n


if __name__ == "__main__":
    out = []
    print(f"{'graph':16s} {'code':11s} {'n':>2s} {'|E|':>3s} {'|Aut|':>5s} {'v-tr':>5s} "
          f"{'deg':>4s} {'Galois':>7s}  value")
    for label, code, deg, poly, note in ROWS:
        n, m, aut, vt = aut_and_orbit(code)
        gal = ""
        if poly is not None and deg and deg >= 2:
            G, alt = sp.polys.numberfields.galoisgroups.galois_group(sp.Poly(poly, x))
            gal = str(G.order())
        elif deg == 1:
            gal = "1"
        print(f"{label:16s} {code:11s} {n:2d} {m:3d} {aut:5d} {str(vt):>5s} "
              f"{str(deg) if deg else '>16':>4s} {gal:>7s}  {note}")
        out.append(dict(label=label, graph6=code, n=n, edges=m, aut_order=aut,
                        vertex_transitive=vt, field_degree=deg,
                        galois_order=gal or None, minpoly=str(poly) if poly else None,
                        note=note))

    known = [r for r in out if r["field_degree"]]
    rho, p = spearmanr([r["aut_order"] for r in known], [r["field_degree"] for r in known])
    rho2, p2 = spearmanr([r["aut_order"] / r["n"] for r in known],
                         [r["field_degree"] for r in known])
    print(f"\nSpearman(|Aut|, field degree) over the {len(known)} graphs with an exact value: "
          f"rho = {rho:+.3f}, p = {p:.3f}")
    print(f"Spearman(|Aut|/n, field degree):                       rho = {rho2:+.3f}, p = {p2:.3f}")
    same_aut = {}
    for r in known:
        same_aut.setdefault(r["aut_order"], set()).add(r["field_degree"])
    spread = {a: sorted(d) for a, d in same_aut.items() if len(d) > 1}
    print(f"automorphism orders that occur with more than one field degree: {spread}")
    out_json = dict(rows=out, spearman_aut_vs_degree=dict(rho=float(rho), p=float(p)),
                    spearman_autpern_vs_degree=dict(rho=float(rho2), p=float(p2)),
                    same_aut_different_degree=spread)
    json.dump(out_json, open(os.path.join(RES, "report_2e.json"), "w"), indent=1, default=str)
    print("\nwrote results/report_2e.json")
