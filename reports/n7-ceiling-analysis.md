# Can we increase n beyond 7? — an exhaustive analysis

**Prepared:** 2026-07-24 · Pool A: 141 rows · Pool B: 73 rows

The forward model is fit on **n = 7** (Varon's metakaolin geopolymers, Sr, one protocol). That is
the single biggest weakness in the work. This report tests every route to a larger n that the
existing corpus could support, and answers what it would actually take.

**Answer: n cannot be increased from the literature. Not by one row. The ceiling is structural,
and only new laboratory data breaks it.**

---

## Route 1 — add the leached companion (the obvious candidate) ❌

`varon_leached2026` supplies **7 more (Al^IV, K_D) pairs** from the *same laboratory, same protocol,
same material class*. On paper this doubles n to 14. It fails, decisively.

**The fresh model does not predict the leached samples:**

| specimen | Al^IV | observed K_D | fresh model predicts | residual |
|---|---|---|---|---|
| K-0.5-16 | 3.38 | 1350 | 245 | **+1105** |
| K-1.2-8 | 3.61 | 150 | 892 | −742 |
| K-1.5-16 | 3.67 | 450 | 1060 | −610 |
| Na-1.2-16 | 3.20 | 130 | −261 | +391 |

**Transfer R² = −0.988** — the fresh model is worse than useless on leached material. And *within*
the leached set the descriptor is flat (slope 580 vs 2812; in-sample R² = 0.07).

**Merging makes the model worse, not better:**

| training set | LOO-CV R² |
|---|---|
| fresh only, n = 7 | **+0.811** ← what we ship |
| leached only, n = 7 | −1.234 |
| combined n = 14, *grouped* LOO (leave one specimen out, both states) | **+0.684** |

*(A naive row-wise LOO on the combined set gives +0.677 but is invalid: the 14 rows are 7 specimens
× 2 states, so leaving out one row leaves its paired twin in training.)*

**Why this matters beyond the arithmetic.** F27 showed that *removing* Al^IV from a specimen lowers
its K_D (Δ-vs-Δ, r = +0.94) — the causal test. This analysis shows the complementary limit: the
*absolute* K_D of a leached specimen is **not** predicted by its residual Al^IV. Leaching does not
simply move a sample down the same line; it produces a material with a different structure–property
relationship. The descriptor is valid within a **preparation state**, not across states.

That is F36's cross-laboratory lesson reappearing one level down — inside a single laboratory.

## Route 2 — a bigger group somewhere else in Pool A ❌

The largest single-source × single-adsorbate × single-target groups in all 141 rows:

| n | source | adsorbate | class | target |
|---|---|---|---|---|
| 7 | varon_leached2026 | Sr | geopolymer | K_D |
| **7** | **varon2025** | **Sr** | **geopolymer** | **K_D** ← the model |
| 6 | katada2024 | Cs | zeolite | capacity |
| 5 | xiang2021 | Cs | geopolymer | capacity |
| 5 | kurumisawa2021 | Cs | geopolymer | capacity |

**n = 7 is the maximum coherent group in the entire corpus.** Everything else is smaller, a
different structural class, or a different target type. And `al_iv_mmol_g` exists in *only* the two
Varon sources — no other paper in ~40 reports framework Al^IV alongside uptake.

## Route 3 — the Oulu ARI series (the only series bigger than 7) ❌

Oulu 2026 has **13** rows pairing ARI with capacity. Two disqualifications:

| adsorbate | total n | Ca-free (descriptor-valid, F19) | Ca-bearing |
|---|---|---|---|
| NH₄⁺ | 13 | n=4, r = **+0.93** | n=9, r = −0.01 |
| methylene blue | 13 | n=4, r = −0.98 | n=9, r = −0.65 |
| rhodamine 6G | 13 | n=4, r = −0.63 | n=9, r = −0.40 |

1. **The adsorbate is not Cs or Sr.** NH₄⁺ is a reasonable cation proxy; the dyes are not — and
   their *negative* correlations are a useful specificity check: the descriptor tracks
   **ion-exchange of cations**, not adsorption in general.
2. **The descriptor-valid subset is n = 4**, not 13. Using all 13 mixes Ca classes and the model
   collapses: LOO-CV R² = **−0.041** across all 13, versus **+0.556** on the 4 Ca-free samples.

## Route 4 — the GEOMIND 112-sample dataset (Q2) ❌ *for this purpose*

**This corrects an over-optimistic line in our own retrospective.** GEOMIND's four output properties
are *initial viscosity, mixture density, material density, compressive strength*. There is **no
adsorption, Cs or Sr measurement in it at all.**

Obtaining it would unblock **M3a** (faithful replication of their generative model) — it does not
add **a single row** to the n = 7 Sr model. These are two different blockers and should stop being
described as one.

---

## What would actually work: a own-laboratory campaign

This is the only route, and it is a modest one. The requirement is not "more data" — it is
**composition-varying data measured under one protocol, in one preparation state.**

**Minimum viable design (would take n from 7 → ~15–20):**

| element | specification | why |
|---|---|---|
| **Series** | 12–20 metakaolin geopolymers spanning Si/Al ≈ 1.0–2.5 in even steps | Si/Al is the composition knob that moves framework Al^IV; the current n=7 spans Al^IV 3.45–4.77 mmol g⁻¹, a narrow window |
| **Activator** | one activator family, one molarity, one L/S ratio | protocol held fixed — the condition F36 shows is non-negotiable |
| **Cure** | one temperature, one duration, one state | Route 1 above: the descriptor does not survive a change of preparation state |
| **Structure** | ²⁹Si + ²⁷Al MAS NMR on every sample → Q⁴(mAl) deconvolution → ARI and [Al^IV] | this is the measurement no published paper provides alongside uptake |
| **Uptake** | Sr batch sorption, fixed C₀, dose, pH, contact time → K_D | must be the same protocol for every sample |
| **Screen** | verify θ = b·C₀/(1+b·C₀) ≥ 0.8 if a Langmuir capacity is also fitted | our own saturation screen (F14–F17), so the new data cannot contain the artefact we criticise |
| **Keep Ca out** | Ca-free formulations | F19/F41: Ca²⁺ competes for the same sites and destroys the relationship |

**What n ≈ 15–20 buys:** the leave-one-out R² becomes meaningfully estimable rather than fragile;
the domain widens beyond a 1.3 mmol g⁻¹ window; and — most importantly — it is the **paired
composition/structure/uptake data a generative model needs**, which would reopen M4-generative and
M5 (currently blocked, per the retrospective).

**A cheaper half-step:** even **6–8 new samples** measured under our own single protocol would let
us test the descriptor in a *second independent laboratory* under controlled conditions — turning
"it holds in one lab's 7 samples" into "it reproduces." That is a smaller ask than a full campaign
and buys most of the credibility.

---

## Bottom line

| route | verdict |
|---|---|
| Add the leached companion (n → 14) | ❌ different regime; LOO-CV drops 0.811 → 0.684 |
| A larger group elsewhere in Pool A | ❌ n = 7 *is* the corpus maximum |
| Oulu ARI series (n = 13) | ❌ wrong adsorbate; descriptor-valid subset is n = 4 |
| GEOMIND 112-sample dataset | ❌ contains no adsorption data — unblocks M3a, not n |
| **Own-lab Si/Al series with NMR + Sr uptake** | ✅ **the only route — and n ≈ 15–20 is enough** |

n = 7 is not a gap we failed to fill. It is the **complete** intersection of "framework Al measured"
with "Cs/Sr uptake measured" in one laboratory and protocol, across the entire published corpus. The
honest framing for the paper is that the descriptor is *established mechanistically on four
independent evidence levels* and *quantified within one well-characterised series* — with the
laboratory campaign named explicitly as the next step.
