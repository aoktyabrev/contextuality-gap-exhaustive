"""Gate for quadc5/algdeg.py -- the Stage 9 instrument.

Two independent routes for |Aut| (repository rule), and a demonstration that the
digit-count discipline is not decoration: with an over-claimed count PSLQ returns a
WRONG ANSWER THAT LOOKS RIGHT, which is the failure mode Stage 2 exists to avoid.

    .venv/bin/python tests/test_algdeg.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from quadc5.g6 import decode_g6, edges_of
from quadc5.theta import theta_cvxpy
from quadc5.hiprec import refine
from quadc5.algdeg import (theta_honest, find_minpoly, higher, matching_digits,
                           _dual_start, _pslq_at, aut_dreadnaut, aut_networkx)
from mpmath import mpf

FAILS = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"   {detail}" if detail else ""))
    if not ok:
        FAILS.append(name)


# ---- 1. matching_digits must refuse to compare a value with itself --------------
try:
    matching_digits(mpf(3), mpf(3), 960, levels=(960, 960))
    check("matching_digits refuses a self-comparison", False, "it returned a number")
except ValueError:
    check("matching_digits refuses a self-comparison", True,
          "catches: a check running at the measurement's own precision")

check("identical values from DIFFERENT precisions are the strongest agreement",
      matching_digits(mpf(3), mpf(3), 960, levels=(480, 960)) == 960,
      "catches: treating exact agreement as uninformative")

# ---- 2. |Aut| by two independent routes ----------------------------------------
bad = []
for code in ["DUW", "EUZw", "FCp`_", "GCQb`o", "HCRbdO{", "ICRb`yiu?"]:
    n, adj = decode_g6(code)
    a1 = aut_dreadnaut(n, adj)
    a2, _ = aut_networkx(n, adj)
    if a1 != a2:
        bad.append((code, a1, a2))
check("|Aut| agrees between nauty and explicit enumeration", not bad, str(bad))

# ---- 3. known degrees reproduce ------------------------------------------------
for code, want in [("DUW", 2), ("GCQb`o", 4), ("HCRbdO{", 1)]:
    r = theta_honest(code=code, dps=240)
    m = find_minpoly(r["theta"], r["honest"], confirm=lambda: higher(r)[:2])
    check(f"degree of {code} is {want}", m["status"] == "hit" and m["degree"] == want,
          f"got {m['status']} degree {m['degree']}")

# ---- 4. the convergence test separates converged from stalled ------------------
r_ok = theta_honest(code="DUW", dps=240)
r_bad = theta_honest(code="GCY^fW", dps=240)
check("a converged refinement is accepted", r_ok["converged"] is True)
check("a stalled refinement is declined", r_bad["converged"] is False,
      "catches: inter-level agreement mistaken for accuracy")

# ---- 5. THE DEMONSTRATION: an over-claimed digit count gives a wrong answer -----
# GCY^fW has theta = alpha = 3 exactly, but Gauss-Newton stalls at 359 correct
# digits while two levels agree to 945.  Hand PSLQ that inflated count and it does
# not fail loudly -- it returns (x - 3)^3, because the CUBE of the 1e-359 error
# falls below the claimed tolerance.  A plausible wrong answer, not a blank.
n, adj = decode_g6("GCY^fW")
e = edges_of(n, adj)
pr = theta_cvxpy(n, e, solver="CLARABEL")
B0, _ = _dual_start(n, e)
v1920 = refine(n, e, pr["X"], B0, pr["theta"], dps=1920)["theta"]
spurious, _ = _pslq_at(v1920, 940, 3)
honest_rel, _ = _pslq_at(v1920, 350, 1)
check("an over-claimed digit count yields a plausible WRONG polynomial",
      spurious == [-27, 27, -9, 1],
      f"got {spurious}, which is (x-3)^3 -- degree 3 where the truth is degree 1")
check("the same value at an honest digit count gives the truth",
      honest_rel == [-3, 1], f"got {honest_rel}, i.e. x = 3 = alpha")

print()
if FAILS:
    print(f"{len(FAILS)} FAILED: {FAILS}")
    sys.exit(1)
print("all checks passed")
