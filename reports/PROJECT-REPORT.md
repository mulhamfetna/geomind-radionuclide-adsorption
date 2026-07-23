# GEOMIND-R — Comprehensive Technical Report

**Project:** Geopolymer inverse design for radionuclide adsorption
**Status:** M1–M2 complete · M3a partial · M4 in progress · M6 continuous
**Report date:** 2026-07-20
**Pool:** 121 rows / 10 sources · 48 tests passing

---

# Executive summary

This project set out to replicate the GEOMIND generative model (RSC *Digital Discovery*,
`10.1039/d5dd00383k`) and extend it with adsorption capacity as a design target for Cs-137 and
Sr-90 immobilisation.

Three things happened that were not in the original plan, and they now define the work:

1. **The supplied dataset contained fabricated and misattributed values.** A systematic
   source-verification audit found that **32 % of the compiled adsorption data did not survive
   contact with its primary sources** — including europium values labelled as strontium, a sorbent
   that does not exist, and capacities attributed to a paper that tabulates none.

2. **The intended primary feature is the wrong one.** Across five independent datasets, BET
   surface area has essentially no predictive power for cation uptake (pooled r = +0.08), while
   tetrahedral aluminium concentration does (r = +0.95 in the one dataset measuring it).

3. **The project is data-limited, not method-limited.** After exhaustive scraping and mining,
   the corpus holds **55 Cs/Sr rows**. Inverse design — the original ambition — is not reachable.
   The defensible contribution is a source-verified structure–property meta-analysis.

The audit trail is itself a contribution. A literature that reuses these numbers uncritically now
has a documented case study in how badly compiled adsorption data can degrade.

---

# Part 1 — What was attempted and what changed

## 1.1 Original plan

| Milestone | Intent |
|---|---|
| M1 | Analyse the GEOMIND paper into a reproduction specification |
| M2 | Clean and document the supplied data |
| M3a | Faithfully replicate GEOMIND on its own samples |
| M3b | Validate on our larger compiled dataset |
| M4 | Add adsorption capacity as a fourth design dimension |
| M5 | Apply to Cs-137 / Sr-90 |
| M6 | Expand the corpus |

## 1.2 What actually happened

**M1 succeeded** and produced an unexpected finding: the authors published their code, trained
weights and a 10-sample subset at `github.com/Geopolymer-AI/GEOMIND`. That repository carries
**no license**, so it is legally usable only as a comprehension aid and oracle — never as source
to copy. The full 112-sample database is confidential.

**M2 became an investigation.** Profiling the supplied data surfaced defects severe enough that
cleaning could not proceed until they were resolved (Part 2).

**M3a is partially complete.** The chemistry layer is verified against the paper. The dual-VAE is
not implemented, blocked on two parameters the paper never published: the loss weights w₁–w₆
("set by trial and error") and the KL-divergence treatment.

**M3b was re-scoped.** Our data is fly-ash/slag *concrete*; the paper's is metakaolin *paste*.
Different material system, no viscosity target, and only 92 distinct mix designs behind 867 rows.
Calling it a validation of GEOMIND would have been dishonest; it is now framed as a cross-system
transfer study.

**M4 changed direction** once the feature question was answered (Part 3).

**M6 hit a hard ceiling** (Part 5).

---

# Part 2 — The data-integrity investigation

Fifteen findings, four critical. This is the project's most substantial output to date.

## 2.1 F1 — Values transplanted from the paper into unrelated data

`Si_Al` and `Density` in the 867-row concrete dataset were **copied from the GEOMIND paper's ten
published samples**.

Evidence:
- **9 of 11** unique `Si_Al` values match the paper exactly to three decimal places
- **All ten** of the paper's density values appear in the column
- **91 of 92** distinct mix designs carry a single broadcast value — a lookup, not a measurement
- Neither column exists in either upstream source file

Had these been used as features, a model would have learned an artefact of the join and reported
it as materials science. **Both columns were dropped.**

## 2.2 F6 — A fabricated feasibility domain

`Feasibility_Ranges` claimed `Source: GEOMIND (2026)`. Tested against the paper's own samples it
**rejects 7 of 9 feasible mixtures and accepts the 1 infeasible one** — anti-correlated with truth.

Its constants (`Si/Al 1.5–3.0`, `Porosity 15–65`) were traced to **this project's own retired
heuristic tool**, verbatim, at git tag `v1.0.0`. Invented numbers had been relabelled as the
paper's.

## 2.3 F7 — 32 % of the compiled data failed source audit

Every row of the hand-compiled `Functional_Data` was re-read **in context** in its primary PDF.
Ten of thirty-one expanded rows failed, in four distinct ways:

| Failure | Detail |
|---|---|
| **Wrong element** | Three rows labelled **Sr** are **europium-152/154**. The source paper studies Cs, Co and Eu — it contains no strontium at all. |
| **Non-existent sorbent** | `K-MK` is a verbatim copy of `K-MKBFS`'s values, creating an apparently independent material. |
| **Misattribution** | `Na-MK`, credited to El-Naggar 2018, actually carries values from a different paper. El-Naggar reports **only** MKBFS systems. |
| **Unverifiable** | Four rows claim Langmuir Qmax from Niu 2022, which **tabulates no capacities at all** — only ion-exchange log K. |

Sr was the scarcest target in the project. **Three of its seven rows were the wrong element.**

## 2.4 F11 — An untraceable sheet

`Sr_Immobilization_Mechanisms` is the only sheet in the master workbook with **no source column at
all**, carrying **66.7 % internal duplication** — the same signature as the fabricated rows in F7.
Labelled `FALSE / DISCARD`.

## 2.5 F12 — A conflict that wasn't

The 22 cells where `GEOMIND_R_MASTER_DATABASE_v2` disagreed with `Physical_Data` turned out to be
**rounding**, not disagreement. `N data.xls` genuinely reports six decimal places and 18 of 24 v2
values appear verbatim upstream — v2 preserved source precision, `Physical_Data` rounded it.
Difference ≤ 0.005 MPa. Resolved; v2 promoted from `suspect` to `verified`.

## 2.6 F13 — Unverifiable context sheets

Six sheets cite `Kim_2026`, `Yildirim_2024`, `Duque_Redondo_2023` — **papers we do not hold**, so
they cannot be source-verified. `Surface_Complexation` cites *"Eq. (10)–(12)"* — equations, not
sources, making those rows model output rather than measurement. FTIR is 88.9 % internally
duplicated; XRD 72.7 %.

## 2.7 F14/F15 — A high R² does not mean a meaningful capacity

Baek 2018's chabazite reports **Qmax = 1249.5 mg/g at R² = 0.99989**, while the same paper reports
equilibrium uptake of **1.184 mg/g**.

The mechanism: at low surface coverage the Langmuir isotherm is **near-linear**, so it fits almost
perfectly while the plateau is essentially unconstrained. The diagnostic is saturation:

```
θ = K·C₀ / (1 + K·C₀)
```

Chabazite reaches **θ = 0.174** — only 17 % of its fitted plateau at the highest concentration
used. The fit extrapolates ~1000× beyond any measurement.

Applying this across the pool required recovering the isotherm concentration range from **seven
separate methods sections**:

| Source | C₀max | Rows | Outcome |
|---|---|---|---|
| Baek 2018 | 2658 mg/L | 3 | 1 sound, 1 borderline, **1 artefact** |
| El-Naggar 2018 | 1000 mg/L | 6 | all sound (θ 0.886–0.926) |
| Tarnovsky 2024 | 10 mmol/L → 1329 Cs / 876 Sr | 6 | all sound (θ 0.960–0.995) |
| Hamed 2025 | 1000 mg/L | 7 | all sound (θ 0.982–0.987) |
| Lei 2021 | 170 mg/L | 2 | sound |
| Zheng 2023 | 800 mg/L | 1 | sound |
| Xiang 2021 | 500 mg/L | 1 | sound |

**Final: 27 sound · 1 borderline (stilbite, θ = 0.775) · 1 artefact (chabazite) · 6 unassessable.**

### A methodological error worth recording

**Three times** low K_L was used to predict an artefact, and **three times it was wrong** —
El-Naggar (6 rows), Tarnovsky (6), Hamed (7). That heuristic would have discarded **19 sound
rows**.

K_L alone is not a screen. A small K is fully compensated by a large C₀. Chabazite fails because
its K is small **and** even 2658 mg/L reaches only 17 % of its plateau. The parameter decides in
combination with the experiment, never alone.

---

# Part 3 — The scientific finding

## 3.1 Surface area does not govern cation uptake

| Source | n | corr(BET, capacity) |
|---|---|---|
| Lin 2026 | 4 | **−0.90** |
| Xiang 2021 (foams) | 5 | **−0.90** |
| Oulu (NH₄⁺) | 21 | −0.47 |
| Tarnovsky 2024 | 6 | +0.22 — inconclusive |
| **Pooled cations** | 38 | **+0.08** |
| **Dyes** | 42 | **+0.66** |

Two things matter here. First, **the pooled cation correlation is ≈ zero** — BET simply does not
predict. Second, **dyes give the opposite sign**: large organic molecules genuinely do use surface
area, while cations use charge sites. Pooling adsorbate classes flips the conclusion, which is why
the schema forbids it structurally.

## 3.2 What does govern it

Varon 2025 measured BET, ²⁷Al NMR and ²⁹Si speciation on the **same samples** as its Sr tests:

| Predictor | corr with K_D(Sr) |
|---|---|
| BET surface area | **+0.19** |
| Si/Al | −0.95 |
| **[Al^IV] (mmol/g)** | **+0.95** |

The highest-BET sample (212 m²/g) has among the **lowest** K_D; a 72 m²/g sample has the highest.

## 3.3 Reconciling an apparent contradiction

Katada 2024 found Cs capacity correlating **+0.68 with Si/Al** and **−0.81 with Al content** —
the opposite of Oulu and Varon. Both are correct:

- **Within one amorphous family** (Oulu, Varon): lowering Si/Al adds accessible framework charge.
- **Across crystalline frameworks** (Katada): topology decides which Al is *reachable*. LTA uses
  **2.7 %** of its Al sites; MOR uses **97 %**.

**The unifying variable is accessible tetrahedral aluminium.** Si/Al works within a family because
it proxies Al content there, and fails across frameworks because topology governs accessibility.

### A correction to an earlier overstatement

An earlier claim that *"six datasets confirm a negative BET correlation"* was **wrong** and is
recorded as **F9**. Cation-only per-source figures are −0.90, −0.90, −0.47 and **+0.22**, pooling
to **+0.08**. The defensible claim is the narrower one: *BET has little predictive power for
cations; Al^IV is strongly predictive in the single dataset that measured it.*

---

# Part 4 — The NMR attempt: a documented failure

The one predictive descriptor, Al^IV, exists in **7 of 121 rows**. The Oulu dataset ships raw ²⁹Si
spectra, so deconvolving them into Q⁴(mAl) populations would have extended it.

## 4.1 Pre-registration

Because deconvolution of five overlapping resonances is under-determined, acceptance criteria were
fixed **before fitting** and committed:

- **Gate 5a** — Engelhardt: NMR-derived Si/Al vs designed Si/Al, **r ≥ 0.9, no systematic bias**
- **Gate 5b** — monotonicity: Al-richness index strictly decreasing with Si/Al, **Spearman ρ = −1.0**

## 4.2 Result: both gates passed, and the fit was rejected anyway

| Gate | Result |
|---|---|
| 5a | r = **+0.985** ✅ |
| 5b | ρ = **−1.00** ✅ |

Rejected on three grounds:

1. **Q⁴(3Al) fitted to exactly 0.0 in all four validation samples.** Chemically impossible —
   Q⁴(4Al) and Q⁴(2Al) are both well populated, so the intermediate environment cannot be empty.
   Intensity is being pushed to the outer peaks, **despite R² ≥ 0.998**.
2. **Systematic bias.** NMR/designed Si/Al ratios: 0.41, 0.57, 0.72, 0.89 — every value low, gap
   widening. The registered criterion required *no systematic bias*.
3. **Gate 3 failed outright** for Ca-bearing spectra (R² 0.69–0.97), two degenerate at 100 %
   intensity in one peak.

## 4.3 The methodological lesson

**Both registered criteria are computed from the same fitted populations.** Q⁴(3Al) ≡ 0 shifts
intensity outward roughly symmetrically, preserving *both* the lumped Engelhardt ratio *and* the
monotonic ordering.

**Two criteria derived from one fit are not two independent tests.** Gate 5b was designed to be
independent and was not independent enough. The problem was caught by an unregistered chemical
sanity check, not by either formal gate.

**Gate 2 was also vacuous**: least-squares fitting the baseline wings forces their residual mean to
≈ 0 by construction. It could not have failed.

Nothing was relaxed, dropped, or reinterpreted after seeing the numbers.

---

# Part 5 — Corpus expansion and its ceiling

## 5.1 Systematic sweep

A 101-agent adversarially-verified sweep established the headline constraint:

> **No large, ready-made open dataset of Cs/Sr adsorption on geopolymers exists.**

The only tier-1 open deposit found was the Oulu dataset already in hand — which contains **no Cs or
Sr at all**. JAEA-SDB, the largest standing sorption database, covers Cs and Sr but contains
**zero geopolymers**.

## 5.2 Mining yield

| Batch | Papers | With capacity data | Hit rate |
|---|---|---|---|
| Local backlog | 8 | 3 | 38 % |
| Downloads batch 2 | 5 | 1 | 20 % |
| Downloads batch 3 | 5 | 2 | 40 % |

The recurring cause: **"geopolymer + Cs" retrieves waste-form immobilisation studies** — leaching,
diffusivity, durability — not sorption. Future queries must require isotherm vocabulary and
exclude leachability-index terms.

## 5.3 Sources ingested

10 sources, 121 rows: Oulu (63) · literature compilation (21, post-audit) · Varon (7, K_D) ·
Katada (6) · Tarnovsky (6) · Lin (6) · Xiang (5) · Baek (3) · Zhang (2) · Tian ESPR (2).

---

# Part 6 — Infrastructure built

## 6.1 Warehouse — every source mined, nothing left unlooked-at

**22,271 records** from every tabular file, plus **816 non-tabular assets catalogued**. Zero tables
untriaged. A worthless sheet is still ingested and labelled, because *"we looked and it was
worthless"* is knowledge while *"we never looked"* is a hole.

Three orthogonal label axes, each a closed vocabulary:

| Axis | Question | Values |
|---|---|---|
| **Veracity** | Is it true? | VERIFIED_TRUE · PROBABLE · UNVERIFIED · REDUNDANT · FALSE |
| **Utility** | Is it useful? | CORE · SUPPORTING · CONTEXT · DISCARD |
| **Granularity** | What *is* it? | OBSERVATION · RAW_SIGNAL · REFERENCE |

The third axis was added after the first build reported *"21,136 records cleared for modelling"* —
which was wrong. ~18,000 were **spectrum points**, not training rows. Corrected: **3,391
modellable observations**.

## 6.2 Schema — traps encoded, not documented

`CapacityType` distinguishes five quantities the field conflates: Langmuir Qmax, Freundlich max,
single-point uptake, ion-exchange capacity (meq/g), and K_d (mL/g). **K_d is not a capacity** and
cannot enter the mg/g pool.

`AdsorbateClass` separates radionuclide / analogue / dye so NH₄⁺ can never silently become a Cs
target. `pooling_warning()` fires automatically when a pool mixes them.

Unit conversions are separate named functions because **mmol/g ≠ meq/g for divalent Sr** — a
factor-of-two error waiting to happen.

## 6.3 Knowledge registry

`knowledge_base/registry.yaml` is the single source of truth: 17 assets, 17 sources, 15 findings,
10 decisions. The master workbook is registered **sheet by sheet**, so a rejected sheet cannot be
pulled in with a sound one. Documentation is **generated** and cannot drift; six negative tests
prove the validator catches drift rather than merely claiming to.

---

# Part 7 — Honest assessment of what is achievable

## 7.1 Data position

| Target | Rows | Verdict |
|---|---|---|
| Cs | 40 | forward modelling marginal |
| Sr | 15 | insufficient alone |
| NH₄⁺ (analogue) | 21 | usable only as a labelled proxy |
| **Fitted capacities verified sound** | **27 of 29 assessable** | good |
| **Al^IV (the predictive feature)** | **7 of 121** | the binding constraint |

## 7.2 What is and is not reachable

| Ambition | Verdict |
|---|---|
| Faithful GEOMIND replication | ❌ blocked — needs the confidential 112 |
| Inverse design for adsorption | ❌ 55 rows is far too few |
| Forward model, Cs | ⚠️ marginal — heavy uncertainty required |
| Forward model, Sr | ❌ 15 rows |
| **Structure–property meta-analysis** | ✅ **viable now** |

## 7.3 The defensible publication

Not *"we replicated GEOMIND for radionuclides"* but:

> **What governs cation uptake in aluminosilicates? A source-verified meta-analysis showing
> surface area is not predictive, and framework charge is.**

Supported by 121 audited rows across 10 sources, with the verification methodology — and the 32 %
failure rate of a naive compilation — as a contribution in its own right.

**Required limitations disclosure:** *of 35 fitted capacities, 29 could be assessed for isotherm
saturation; 27 were confirmed as measured rather than extrapolated, one is weakly constrained, one
was excluded as an extrapolation artefact, and six could not be assessed because their sources do
not state an isotherm concentration range. Of the assessable capacities, 96 % are properly
constrained.*

---

# Part 8 — Outstanding

| # | Item | Impact |
|---|---|---|
| 1 | **Send** the GEOMIND 112-sample request | Larger than every scraping avenue combined |
| 2 | **Send** the Oulu Q⁴(mAl) request | Only external check on the failed deconvolution |
| 3 | Acquire ***Next Sustainability* 2025** | Only 1–5 M activator axis, with Cs *and* Sr *and* NMR |
| 4 | Foams 2020 figure reading | Capacities exist but are figure-derived and condition-dependent |
| 5 | ~~C₀ for the last 6 fitted rows~~ | ✅ **attempted and closed** — these papers plot their isotherms without tabulating the range; recovery needs the figure axes read manually. Closed at 29/35 screened. |

Both letters are drafted in `docs/correspondence/` and unsent.

---

# Appendix — Errors made and corrected

Recorded because the correction record is part of the method.

| # | Error | How it was caught |
|---|---|---|
| 1 | Committed 54 MB including a copyrighted PDF to git | Noticed during a later status check; history rewritten, then the repo deleted and recreated because GitHub retains PR refs |
| 2 | Claimed *"six datasets confirm a negative BET correlation"* | Re-audited per source; pooled cation r is +0.08, not negative (F9) |
| 3 | BET extraction silently returned **0.3 m²/g for every sample** — a fallback regex captured the pressure `p/p₀ = 0.3` | Every value being identical looked wrong |
| 4 | Built adapters from subagent output without reading the PDFs myself | Flagged by Mulham; re-verified inline, values held |
| 5 | Predicted artefacts from low K_L **three times**, wrong every time | The screen itself, once C₀ was recovered — 19 sound rows would have been discarded |
| 6 | Module entry point mid-file, so a new adapter registered after `main()` ran | Row count silently unchanged at 100 instead of 106 |
| 7 | Created a Gmail draft when the standing rule required a local file | Flagged by Mulham; rule added to global config |
