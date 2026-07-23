# Pool B — the immobilisation / leach-resistance pool

**Status 2026-07-20:** 40 rows · 4 sources · 22 leachability indices + 10 ingress diffusivities +
6 structure-only · **122 tests passing**

Pool B exists because of **F20**: solid-state NMR and adsorption capacity are near-disjoint in
this literature, and the NMR — the only descriptor that tracks cation uptake — lives almost
entirely in the immobilisation studies. Decision **D13** runs it in parallel with the adsorption
pool (Pool A), **never merged**.

---

## 1. What is in the pool

| Source | rows | nuclides | target | descriptor |
|---|---|---|---|---|
| **Kim 2026** | 6 | Sr | leachability index (2 left-censored) | EXAFS CN |
| **Nevin 2026** | 10 | Cs, Sr | leachability index (+6 structure-only) | full Q⁴(mAl), ARI |
| **Kurumisawa 2021** | 10 | Cs | **ingress** diffusivity | — (activator-solution NMR only) |
| **Jang 2016** | 14 | Cs, Sr | leachability index | pore structure |

The two diffusivity *kinds* are kept rigorously apart — see §3.

---

## 2. The four schema traps, and why each is real

Every one of these was triggered by real data in the pool, not anticipated in the abstract.

**Trap 1 — the target is inverted.** A high capacity is good; a high leach rate is *bad*. The
leachability index (LI) is the well-behaved target because **higher LI = better retention**,
matching Pool A's sign convention — but `De` and CLF run the other way. `HIGHER_IS_BETTER` states
the direction for every type, and `pooling_warning()` refuses to merge opposing directions.

**Trap 2 — loading is a control variable.** In Pool A the capacity is measured; here the
radionuclide is *doped in at synthesis* (1/2/3 wt%, or 10 g/L in the activator). It must never be
used as a target.

**Trap 3 — below-detection is information.** Kim's KSr1 and KSr2 leached *below* the ICP-OES
limit — they are the **best-performing samples in the study**, yet a naive reader records them as
null and drops them, deleting the top of the distribution. `Censoring.LEFT` keeps them with their
bound.

**Trap 4 — LI is logarithmic.** LI = −log₁₀(De), so a *mean* LI over leaching intervals is a
geometric mean of De and does not invert to a single diffusivity. **This is now confirmed against
three independent papers:**

| paper | check | result |
|---|---|---|
| Kim 2026 | 12 of 13 Table-2 cells vs −log₁₀(De) | ✅ (13th is a typo, §4) |
| Nevin 2026 | 4 of 4 Table-2 cells | ✅ 18.66/19.11/13.27/13.22 |
| Jang 2016 | F1 Cs: mean(−log₁₀ Deₙ) = **10.02** vs published 10.0 | ✅ (−log₁₀ of the mean = 9.46, wrong by 0.5) |

---

## 3. A twelve-order-of-magnitude naming collision (F24)

Kurumisawa and Kim/Nevin both report "the diffusion coefficient of Cs". **They are not the same
quantity:**

- **effective** (Kim, Nevin, Jang) — nuclide doped in, diffuses **OUT** during leaching:
  10⁻¹⁶ to 10⁻¹⁹ cm²/s
- **ingress** (Kurumisawa) — cured specimen immersed in Cs solution, nuclide diffuses **IN**:
  4×10⁻⁸ cm²/s

Same name, opposite experiment, **twelve orders apart**. `RetentionType` keeps them as distinct
members and `pooling_warning()` raises an explicit *CATEGORY ERROR* if both appear together.
Merging them would not bias a model — it would destroy it.

---

## 4. Two source defects caught by audit

**Kim Table 2, cell NaSr1 @ 2 h — a published typo.** Prints `8.88 E-16 (15.5)`, but
−log₁₀(8.88e-16) = **15.05**. Kim's own column average of 15.5 equals mean(15.05, 15.94) exactly;
a true 15.5 would average to 15.7. Verified at 430 dpi. Recorded in `KNOWN_SOURCE_ERRATA` with a
test that fails if anyone "corrects" it.

**The master workbook dropped half of Nevin's Table 2.** It carried only the two Sr rows and
silently omitted both Cs rows (LI 13.3, 13.2) — undetectable without reading the source. The
adapter carries all four.

---

## 5. Results that already hold

- **Sr is retained better than Cs in every matrix measured** — all 7 Jang specimens, both Nevin
  loadings, ~6 orders of magnitude in Nevin's K–A–S–H gel. At fixed composition, nuclide identity
  dominates structure. This is the single most robust immobilisation result in the pool.
- **All 22 measured LI values clear the ANSI/ANS 16.1 acceptance floor of 6.0** — every
  alkali-activated matrix in the pool is a regulatory-grade wasteform for both nuclides.
- **Pore structure tracks retention weakly** (corr(porosity, Cs LI) = −0.27 across Jang's
  geopolymers) — consistent with Jang's own conclusion that critical pore *diameter* matters more
  than total porosity.

---

## 6. The honest limitation, unchanged

Pool B still has **NMR paired with composition in only 4 rows** (Nevin, one formulation at
Si/Al = 3). Kurumisawa's NMR is of the activator solution, not the gel; Jang has no NMR; Kim has
EXAFS but no Q⁴ deconvolution.

> **Pool A has composition without NMR. Pool B has NMR without composition. Growing Pool B to 40
> rows did not change that** — it added leach targets and pore structure, both valuable, but not
> the paired NMR-plus-composition that M4/M5 need.

The gating acquisitions remain **Geddes 2025 (Q8)** and **Komljenović 2020 (Q9)** — the two
identified papers that may carry NMR, composition and a retention/binding measure together. See
`docs/acquisition-worklist.md`.
