# The open problem: proving that the upper layers are empty

This is the main unsolved question left by the project. It is combinatorial, not
computational, and we have no approach to it.

## Setting

For a graph G write Δ(G) = ϑ(G) − α(G), and for a size n and an integer a write

    D(n, a) = max { Δ(G) : G connected on n vertices, α(G) = a }

so that Δ_max(n) = max over a of D(n, a). The problem splits by the independence number
because Δ subtracts an integer from a continuous quantity.

## What is proved

Let G\* be a graph on m vertices with α(G\*) = a_m. Define the **cone**

    C_k(G*)  =  {v}  ∨  ( G* ⊔ K̄_{k−1} )

— add k − 1 mutually non-adjacent vertices, non-adjacent to G\*, then one vertex v joined
to everything. Then C_k(G\*) is connected, lives on m + k vertices, and

    α(C_k(G*)) = α(G*) + k − 1,        ϑ(C_k(G*)) = ϑ(G*) + k − 1,

so **Δ is transferred without change**. The two facts about ϑ are classical and are not
ours: ϑ is additive under disjoint union and takes the maximum under join — Knuth,
*The Sandwich Theorem*, formulas (18.2) and (19.2), after Lovász (1979); quoted with line
numbers in `SOURCES.md` §S7. The α statement is elementary. What follows is therefore a
consequence of known properties, not a new theorem:

> **For a = a_m + (n − m) − 1 one has D(n, a) ≥ Δ_max(m), as an exact inequality between
> algebraic numbers.**

No floating point enters this. The transferred graph has Δ *exactly* equal to Δ_max(m) —
not approximately, because α and ϑ shift by the same integer and the difference is
untouched. Write T(n, a) for the largest such transferred value over all m and all layers
of smaller sizes; then D(n, a) ≥ T(n, a) always.

## What is not proved

**That nothing in the layer exceeds the transfer.** That is measured, not derived.

On n = 9 and n = 10, where the enumeration is complete, equality D(n, a) = T(n, a) holds
for every non-empty layer a ≥ 5, and fails below: layers 2, 3 and 4 exceed the transfer by
0.04 to 0.20 and so generate values of their own. The boundary is a\* = 5 at both sizes.
The agreement in the upper layers is at the 10⁻⁸ level — solver noise — which is all a
measurement can say; the exact equality is an inference from the construction plus the
measured absence of anything larger.

n = 11 is **not** evidence here: the hypothesis was formed by looking at n = 11, and
`PREREGISTRATION_STAGE7.md` excluded that data from the verdict for exactly that reason.

## The problem

> **Prove that for a ≥ a\* every graph in layer a either is a cone over a maximizer of a
> smaller size, or has Δ no larger than the transfer.**

An equivalent form, and probably the more tractable one:

> **Find an upper bound on ϑ(G) in terms of n and α(G), strong enough that
> Δ(G) = ϑ(G) − α(G) cannot exceed max over m of the transferred values.**

A bound of the shape ϑ(G) ≤ f(n, α(G)) would do it if f is tight enough in the regime
where α is large relative to n — which is exactly the upper-layer regime, and exactly where
graphs are sparse and ϑ is close to α.

## Why it matters

Right now the practical consequence — that 8.78 % of the space at n = 9 and 14.19 % at
n = 10 need not be enumerated — **rests on the measured half of the statement**. The layers
are excluded because they were computed and found to contain nothing new, which is an
observation about two sizes, not a theorem.

Proving the upper half converts this into a theoretical reduction of the search space:
layers would be excluded because it is *proved* there is nothing to find there, at any size,
without computing them.

For twelve vertices that is the only way to say anything at all. There are
**164 059 830 476** connected graphs on twelve vertices (OEIS A001349, `SOURCES.md` §S9,
which also confirms our counts at n = 8…11 exactly). At our measured throughput of
1.402·10⁷ graphs per hour on seven cores, a full sweep is **≈ 11 700 hours, about 490 days**.
It will not be run. `PREDICTION_N12_LAYERS.md` states what the upper layers must be if the
pattern holds — sealed, and derived by arithmetic from the known series rather than
extrapolated — but it remains a prediction precisely because the upper half is unproved.

## What is known about the boundary a\*

It equals 5 at n = 9 and n = 10, and also at n = 11 on data that the Stage 7 verdict
deliberately does not use. **Three points are a weak basis for a fourth.** The concrete
warning is on the record: at n = 11 layer 4 began generating its own values, overtaking
layer 3 and producing the maximizer with α = 4. Nothing forbids layer 5 from doing the same
at n = 12. Whether a\* grows with n is open, and we have no argument either way.

## Status

No approach of our own. The question is combinatorial — a bound on ϑ under a constraint on
α — and not something more computation would settle.

---

## Literature check, run after the problem was written

The statement above was written and committed (`3b80add`) before this search was made.
Result: **the problem does not reduce to a known bound.** The nearest tools are these, and
none is parameterised by α in a way that helps.

**The sandwich itself.** α(G) ≤ ϑ(G) ≤ χ_f(Ḡ) — the upper end is the fractional relaxation,
and it is what our sweep already uses as a filter. It bounds ϑ by a *chromatic* quantity of
the complement, not by n and α, and in the upper layers it is far from tight.

**Orthogonality dimension** (Knuth §28, `sources/knuth_sandwich_theorem.txt` line 1640,
after Lovász): if G has an orthogonal labeling of dimension d with no zero vectors then
ϑ(G) ≤ d. This is the quantity our campaign calls d\*, and it bounds ϑ by a representation
parameter, again not by α. Computing d\* is itself hard — η_d is non-convex, and our own
values rest on restarts and are marked *indicated* rather than proved.

**The regular case** (Knuth §24, line ~1449): for r-regular G with adjacency matrix B,
ϑ(G) ≤ n·Λ(−B)/(Λ(B)+Λ(−B)) — the Hoffman-type ratio bound. It is parameterised by n and
the spectrum, which is closer in spirit, but requires regularity. The eleven-vertex
maximizer is not regular (degrees 2, 3⁸, 4²), and upper-layer graphs are sparse and
irregular in general.

**The product bound** (Knuth line 1395): ϑ(G)ϑ(Ḡ) ≥ n, with equality for vertex-symmetric
graphs. This constrains ϑ from *below* given the complement, which is the wrong direction.

**Sparse-graph results.** For graphs of bounded maximum degree d the integrality gap of the
ϑ-based SDP is Õ(d/log^{3/2} d) (Bansal, Gupta & Guruganesh, STOC 2015, arXiv:1504.04767).
These are asymptotic approximation ratios, not bounds tight enough to decide whether a
particular layer can exceed a particular transferred value.

**Conclusion.** No off-the-shelf reduction. The problem asks for something the literature
does not seem to provide: an upper bound on ϑ under a *constraint on α* rather than on
degree, spectrum or chromatic number, and tight in the regime where α is large relative
to n. Whether that is hard or merely unasked, we do not know.
