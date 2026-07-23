# M2 — Data Quality & Provenance Report

**Milestone:** M2 · **Epic:** #2 · **Status:** 🔴 escalation required before cleaning proceeds
**Scope:** all 10 files in `data/raw/`

---

## Executive summary

Profiling `data/raw/` surfaced **one critical integrity defect** that must be resolved before any
modelling, plus several ordinary quality issues.

| # | Finding | Severity |
|---|---------|----------|
| **F1** | `Si_Al` and `Density` in the 867-row dataset appear to be **transplanted from the GEOMIND paper's 10 published samples** and broadcast onto unrelated concrete mixes | 🔴 **critical** |
| **F2** | The 867 rows contain only **92 distinct mix designs**; every input feature has 2–6 unique values; `Metakaolin` is **constant zero** | 🔴 critical |
| **F3** | `Functional_Data` (the adsorption target) contains **extensive internal value duplication** — effective sample size is far below its 28 rows | 🟠 high |
| **F4** | 18 exact duplicate rows; `v2` disagrees with `Physical_Data` in 22 cells; CSV/XLSX pairs are byte-identical redundancy | 🟡 medium |
| **F5** | `Metadata.csv` is **cp1256**-encoded; sheet names are Arabic (`ورقة2`, `ورقة3`) | 🟢 low |

---

## F1 — 🔴 `Si_Al` and `Density` are not measurements of these mixes

### Evidence

**(a) Nine of eleven `Si_Al` values are exact matches to the paper's published samples.**

```
Our 867-row Si_Al uniques : 1.31, 1.373, 1.433, 1.574, 1.627, 1.663, 1.72, 1.801, 1.95, 2.178, 2.2
Paper's 10 samples  Si/Al : 1.31, 1.373, 1.433, 1.574, 1.627, 1.663, 1.72, 1.801, 1.926, 2.178
                            ↑ 9 EXACT matches to 3 decimal places
```
Only `1.95` and `2.2` are not from the paper.

**(b) All ten of the paper's density values appear in our `Density` column.**

```
1.596, 1.767, 1.815, 1.84, 1.847, 1.876, 1.879, 1.899, 1.916, 2.009
```
— exactly the paper's `mixture_density` / `material_density` values.

**(c) The values are broadcast per mix, not measured per sample.**
Grouping the 867 rows by mix design gives **92 distinct mixes**. Of these, **91 have exactly one
`Si_Al` value and one `Density` value**. A genuine measurement would vary between replicate
specimens; a lookup value does not.

**(d) Neither column exists in either source file.**
`Data.xlsx` (672 rows) and `N data.xls` (186 rows) — the traceable sources of the compressive
strength values — contain **no density and no Si/Al column at all**. These two columns therefore
have **no upstream source**.

### Interpretation

`Si_Al` and `Density` were almost certainly **grafted onto the concrete dataset from the GEOMIND
paper**, not measured or computed from the mixes themselves. The exact-match evidence at three
decimal places across nine values makes coincidence implausible.

### Why this is critical

Any model trained on this data would learn a relationship between `Si_Al`/`Density` and
`Comp_Strength` that is **an artefact of the join, not a property of the materials**. Reporting
such a result — for example "Si/Al predicts compressive strength in our compiled dataset" — would
be reporting a fabricated correlation. If published, this is the class of error that leads to
retraction.

### Required action

**These two columns must not be used as features until their origin is established.** See
*Decisions required*, below.

---

## F2 — 🔴 The dataset is far smaller than 867 rows implies

| Column | Unique values (of 867 rows) |
|---|---|
| `Metakaolin` | **1** — constant **0**, a dead column |
| `GGBFS` | 2 |
| `FlyAsh` | 4 |
| `NaOH_M` | 4 |
| `Na2SiO3` | 5 |
| `CopperSlag` | 6 |
| `RecycledAgg` | 6 |
| `Curing_Days` | 5 |
| `Si_Al` | 11 |
| `Density` | 30 |
| `Comp_Strength` | 474 |

**Only 92 distinct mix designs exist.** The 867 rows are largely repeated input vectors with
varying compressive strength — i.e. replicate specimens, not independent formulations.

**`Metakaolin` is identically zero.** Metakaolin is *the* primary aluminosilicate precursor in
GEOMIND (M1–M5). Our data contains none: it is a **fly-ash / slag concrete** dataset with
aggregates, a materially different material system from the paper's metakaolin geopolymer pastes.
This independently confirms the feature-space gap recorded in the README.

**Effective statistical power** is therefore closer to ~92 independent formulations than 867 —
comparable to the paper's own 112, not an order of magnitude larger.

---

## F3 — 🟠 The adsorption dataset has extensive internal duplication

`Functional_Data` (28 rows) is the basis of M4/M5. Its usable content is much smaller:

- **Split targets:** `Qmax_Cs` is present in 24 rows, `Qmax_Sr` in only **7**. They are almost
  mutually exclusive.
- **Verbatim repeated blocks:**
  - rows 3–5 (`K-MK`, Si/Al 1.76) and rows 9–11 (`K-MKBFS`, Si/Al 2.40) carry **identical**
    `Qmax`, `b`, `E`, `R²` (42.23 / 48.05 / 61.54) despite different sorbents and Si/Al.
  - rows 12–18 (`MU-PMK80`) repeat the same triplet (59.59 / 59.35 / 57.74) across
    `NaOH_M` = 8, 10, 12 — **the NaOH variation is not reflected in the target at all**.
  - rows 24–25 share `Qmax_Cs` = 152.84; rows 26–27 share `Qmax_Sr` = 279.20.

**Measured consequence:** the 24 rows carrying `Qmax_Cs` contain only **16 distinct values**, and
`Qmax_Sr` has just **7 rows** in total. So the usable adsorption evidence is roughly
**16 Cs + ≤7 Sr independent measurements**, not 28. This is **far too small to train a generative
target**, and confirms the dependency flagged on #5: **M6 (corpus expansion) is a prerequisite for
M4, not a parallel track.**

**Positive:** provenance here *is* sound — every row carries a `Source`
(El-Naggar 2018, Hamed 2025, Tian 2019, Zheng 2023, Lei 2021, Niu 2022). These 6 sources should be
reconciled against `papers/MANIFEST.md`.

---

## F4 — 🟡 Redundancy and version disagreement

- `Functional_Data.csv` ≡ `Functional_Data.xlsx` and `Physical_Data.csv` ≡ `Physical_Data.xlsx` —
  **byte-identical duplicates**. Declare the CSV authoritative; retain XLSX as archive only.
- **18 exact duplicate rows** in `Physical_Data` (36 rows involved).
- `GEOMIND_R_MASTER_DATABASE_v2` shares all 11 `Physical_Data` columns but **disagrees in 22 cells**,
  with no changelog explaining which is correct. It adds 19 radionuclide columns (Sr/Cs loading,
  diffusion coefficients, NMR Q⁴ speciation) that are largely null (15,597 null cells).
- **Traceability that does hold:** of 474 distinct `Comp_Strength` values, 344 appear in
  `Data.xlsx` and 127 in `N data.xls` — only **4** are in neither. The strength data *is*
  substantially traceable. Note 672 + 186 = 858 ≠ 867, so the merge was not a plain concatenation.

## F5 — 🟢 Encoding

`Metadata.csv` is **cp1256** (Windows Arabic), not UTF-8 — it fails a naive `read_csv`. Sheet names
are Arabic. Both are trivially fixable and are handled by the ingestion layer.

---

## F6 — 🔴 `Feasibility_Ranges` is mislabelled and unusable *(found during M3a)*

The sheet claims `Source: GEOMIND (2026)` and purports to give the chemical feasibility domain.
Tested against the paper's **own** published samples it is **anti-correlated with ground truth**:

| | Result |
|---|---|
| Genuinely **feasible** samples it **rejects** | **7 of 9** |
| The genuinely **infeasible** sample it **accepts** | **1 of 1** |

Rows rejected on `Si/Al` and/or `Si/M` include samples the authors synthesised and measured.

**Origin traced.** Its `Si/Al 1.5–3.0` and `Porosity 15–65` values are **verbatim constants from
this project's own retired heuristic tool** — confirmed present in `geopolymer_design.py` at git
tag `v1.0.0`:

```
'1.5 <= si_al <= 3.0'   in v1.0.0:geopolymer_design.py  -> True
'min(porosity, 65)'     in v1.0.0:geopolymer_design.py  -> True
'base_porosity = 15'    in v1.0.0:geopolymer_design.py  -> True
```

So invented constants from the abandoned tool were labelled as coming from the paper — **the same
pattern as F1**, in the opposite direction.

**Partially sound:** the viscosity rows (0.2 / 2 / 100 / 1314 Pa·s) *do* match the paper's stated
class boundaries and are safe to use.

**Actions taken.** `src/geomind/feasibility.py` deliberately does **not** read this sheet; it uses
the paper-verified viscosity thresholds plus a clearly-labelled *provisional* envelope fitted to
the nine feasible samples, with a `provisional=True` flag on every verdict.
`tests/test_feasibility.py` contains a regression guard asserting the sheet's inaccuracy, so nobody
wires it in later. **Gap G3 remains open.**

---

## What is sound and usable

- ✅ `Comp_Strength` — substantially traceable to two source files.
- ✅ `Functional_Data` source attribution — 6 named publications.
- ✅ `GEOMIND_Samples` (10 × 26) — verified to match the paper's published subset exactly.
- ✅ `Validation_Samples` (45 × 6) — verified to be Table S5 (15 samples × 3 property types).

---

## Impact on the roadmap

| Milestone | Impact |
|---|---|
| **M3a** (faithful replication) | ✅ **Unaffected** — uses the paper's own verified samples. Proceed. |
| **M3b** (extended validation) | 🔴 **At risk.** Rests on the 867 rows. With `Metakaolin` = 0, no viscosity, only 92 distinct mixes and two unsourced columns, this is *not* a validation of GEOMIND — it is a different material system. Must be re-scoped. |
| **M4 / M5** (adsorption) | 🔴 **Blocked on M6.** ~13 independent measurements cannot support a generative target. |
| **M6** (corpus expansion) | ⬆️ **Promote to immediate priority** — it is the critical path to M4/M5. |

---

## Decisions required

1. **F1 — where did `Si_Al` and `Density` come from?** If they were joined from the paper, they
   must be dropped from any model and the join documented as an error. If there is a legitimate
   derivation, it must be written down and reproducible. *I cannot resolve this without you.*
2. **F4 — is `Physical_Data` or `v2` authoritative** for the 22 disagreeing cells?
3. **M3b re-scope** — options: (a) recast it honestly as *"applying the GEOMIND architecture to a
   different material system (fly-ash concrete)"*, which is defensible and interesting; (b) drop it
   until the confidential 112-sample dataset is obtained; (c) request the real dataset from the
   authors (already recommended as action A1 in the M1 spec).
4. **Promote M6 ahead of M4?** Recommended.

---

*Generated during M2 profiling. All figures reproducible via `src/geomind/data/profile.py`.*

---

## F7 — 🔴 Two provenance errors found by re-extracting the source PDFs *(M6 backlog mining)*

Mining the held papers doubled as an audit of the hand-compiled `Functional_Data`. Two of its
rows do not survive contact with their sources.

### F7a — **Europium values are labelled as strontium**

`Functional_Data` records, for sorbent `MU-PMK80` (source `Hamed_2025`):

| T (K) | our label | value |
|---|---|---|
| 298 | **Sr** | 18.58 |
| 313 | **Sr** | 19.98 |
| 333 | **Sr** | 21.55 |

The source paper (*Magnetic ternary nanocomposite from ultra-purified metakaolin*, held locally)
reports for MU-P MK80:

| nuclide | 298 / 313 / 333 K |
|---|---|
| Cs-134 | 59.59 / 59.35 / 57.74 |
| Co-60 | 33.11 / 34.88 / 35.64 |
| **Eu-152+154** | **18.58 / 19.98 / 21.55** ← exact match |

**That paper does not study strontium at all.** Our "Sr" values are **europium-152/154**.

Eu³⁺ is a trivalent lanthanide; Sr²⁺ is a divalent alkaline earth. They have different charge,
ionic radius and sorption mechanism. **Three of the seven Sr rows in the entire compilation are
the wrong element** — and Sr was already the scarcest target.

### F7b — Niu 2022 capacities are not in the paper

Four rows are attributed to `Niu_2022` (`10.1016/j.jhazmat.2022.128373`) as **Langmuir Qmax**:
MS-GP and SC-GP at Cs **152.84** and Sr **279.20** mg/g.

Re-extraction of that paper found **no tabulated capacities of any kind** — all binding data are
plots, and the only fitted quantities are ion-exchange constants (log K = −1.275 for Cs⁺/K⁺,
−2.025 for Sr²⁺/K⁺). The identical values across two different sorbents are themselves a red flag.

**These four rows are unverifiable against their stated source.** They may be figure
digitisations (undocumented), or belong to a different paper.

### F7c — probable duplicate across sources

`Na-MK` (El-Naggar_2018) Cs = 58.96 / 61.27 / 57.60 is identical to `U-P MK100` in the magnetic
ternary paper. Same research group, so this is plausibly the same measurements republished — but
if both are ingested they become **double-counted evidence**.

### Actions

1. **Relabel F7a rows to Eu** and reclassify `adsorbate_class` — they are not a Cs/Sr target.
2. **Quarantine F7b rows** pending a source that actually contains them.
3. **Deduplicate F7c** before training.
4. **Generalise:** every remaining `literature_compilation` row should be verified against its
   source PDF. Two errors in the first six sources checked is not a reassuring rate.

---

## F7 (continued) — full source audit of `Functional_Data`, verified inline

Every compiled row was checked against its stated source PDF, reading the surrounding text — not
just searching for the number. **10 of 31 rows (32 %) did not survive.**

| Source | Rows | Verdict |
|---|---|---|
| **El-Naggar 2018** | 12 → **6** | The paper reports **only MKBFS systems**. `Na-MKBFS` (75.82/80.45/82.24) and `K-MKBFS` (42.23/48.05/61.54) verify exactly. **`Na-MK` and `K-MK` do not exist in it.** |
| **Hamed 2025** | 10 → 7 Cs + 3 **Eu** | Cs verifies. The three "Sr" rows are **Eu-152+154**; the paper studies Cs, Co and Eu — no Sr. |
| **Niu 2022** | 4 → **0** | Paper tabulates **no capacities** — only ion-exchange log K. Values unverifiable. |
| **Lei 2021** | 2 → 2 | Values verify: *"103.74 mg/g and 54.90 mg/g … best explained by **Freundlich** and **Langmuir** … respectively"*. Our Cs row was **mislabelled Langmuir** → corrected to Freundlich. |
| **Tian 2019** | 2 → 2 | 111.90 / 24.18 are **not in the article PDF** but *are* in its supplement (`wst2019209supp.docx`, "Present work"). Verified. |
| **Zheng 2023** | 1 → 1 | 87.91 mg/g, Langmuir, K_L 1.75×10⁻², R² 0.95 — exact match. |

### Two distinct failure modes

1. **`Na-MK` was a misattribution.** Its values (58.96/61.27/57.60) are `U-P MK100` from the
   magnetic-ternary paper — a *different* study by the same group, credited to El-Naggar 2018.
2. **`K-MK` was a fabricated sorbent.** Its values are a verbatim copy of `K-MKBFS`, creating an
   apparently independent material that does not exist.

### Corrections applied in `_from_literature_compilation`

- **Quarantined** (6 rows): `Na-MK`/`K-MK` Cs, and all four `Niu_2022` rows.
- **Relabelled** (3 rows): `MU-PMK80` "Sr" → **Eu**, `adsorbate_class` → `other` (no longer counted
  toward the Cs/Sr target).
- **Re-typed** (1 row): Lei Cs → `freundlich_qmax`.

Each correction is a named constant with the reason inline, so the reasoning travels with the code.

### Net effect

Pool 128 → **118 rows**; compilation 31 → **21**. Cs+Sr **52** (Cs 37, Sr 15).

**The Sr count is the real story:** it was never 7 genuine rows — 3 were europium. Newly mined
sources have since taken Sr to 15, all source-verified.

> **Standing rule:** no row enters the pool without its value being read *in context* in the source
> PDF. A number existing somewhere in a paper is not evidence that it is that sorbent's capacity
> for that adsorbate under that model.
