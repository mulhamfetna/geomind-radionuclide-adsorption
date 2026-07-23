# GitHub record — archived before repository recreation

Preserved because purging the leaked blobs requires deleting and recreating the
repository, which discards issues and PRs. This is the decision record; nothing is lost.

**Exported:** 2026-07-20 — 7 issues, 17 pull requests, 7 milestones

## Milestones

- **M1 — Paper analysis** — Deep analysis of GEOMIND into a precise reproduction specification
- **M2 — Data cleaning & provenance** — Clean, de-duplicate, link and document the compiled dataset
- **M3a — Faithful replication** — Reproduce GEOMIND on the paper's own 10+45 samples
- **M3b — Extended validation** — Retrain on our 867-row compilation; compare to published results
- **M4 — Adsorption dimension** — Add adsorption capacity (Qmax) as a generative design target
- **M5 — Radionuclide application** — Formulation design for Cs-137 / Sr-90 immobilisation
- **M6 — Corpus expansion** — Literature and data mining to grow the adsorption dataset

## Issues (epics)

### #1 EPIC M1 — Deep analysis of the GEOMIND paper  _(CLOSED)_
*labels:* epic, type:analysis, priority:high

Turn the paper + supplementary into a **reproduction specification** precise enough to implement from scratch.

- [ ] Extract full text and supplementary (14 pp + SI)
- [ ] Document the dual-VAE architecture: layer sizes, latent dimension, loss terms, how the two modules couple
- [ ] Document the **feasibility block** rules and thresholds
- [ ] Catalogue the formulation feature space (M1–M5, S1/S3/SNa/S3', KOH/NaOH, molar features, Si/Al, Solid/Liquid)
- [ ] Catalogue the 4 target properties and their units
- [ ] Document preprocessing/normalisation and train/val splits
- [ ] Document the training protocol and all hyperparameters
- [ ] List every figure/table/metric we must reproduce
- [ ] Deliverable: `docs/paper-analysis/reproduction-spec.md`

**Exit criterion:** someone could implement GEOMIND from the spec alone.

### #2 EPIC M2 — Data cleaning, linkage & provenance  _(CLOSED)_
*labels:* epic, type:data, priority:high

Turn the scattered compiled files into one clean, documented, traceable dataset.

Known issues found during intake:
- `Metadata.csv` is **cp1256**-encoded, not UTF-8
- Sheet names are Arabic (`ورقة2`, `ورقة3`)
- CSV/XLSX pairs are duplicates (`Functional_Data`, `Physical_Data`)
- Relationship unclear between `Data.xlsx` (672), `N data.xls` (186) and `Physical_Data` (867)

- [ ] Normalise encodings and sheet names
- [ ] De-duplicate; declare the authoritative source per table
- [ ] Reconcile the 672 / 186 / 867 row sets — are the first two sources of the third?
- [ ] Add a `provenance` field linking **every row** to an entry in `papers/MANIFEST.md`
- [ ] Fill the `_TBD_` DOIs in the manifest
- [ ] Build a data dictionary (column, meaning, unit, range, source)
- [ ] Define validation rules; produce a data-quality report
- [ ] Emit model-ready tables to `data/processed/`

**Exit criterion:** every row traceable to a publication; zero unexplained duplicates.

### #3 EPIC M3a — Faithful replication of GEOMIND  _(OPEN)_
*labels:* epic, type:model

Prove our implementation is correct by reproducing the paper **on its own data** before introducing ours.

- [ ] Implement the dual VAE + feasibility block per the M1 spec
- [ ] Train/evaluate on `GEOMIND_Samples` (10) and `Validation_Samples` (45)
- [ ] Reproduce the published metrics and figures
- [ ] Document every deviation and its likely cause

**Blocked by:** M1, M2.
**Exit criterion:** published results reproduced within a stated tolerance.

### #4 EPIC M3b — Cross-system transfer to fly-ash/slag concrete (re-scoped)  _(OPEN)_
*labels:* epic, type:model

Retrain the validated architecture on our 867-row literature compilation and compare.

⚠️ **Feature-space gap** (see README): our data lacks the paper's precursor-identity features and has **no viscosity** target, while adding aggregates the paper does not model.

- [ ] Decide and document the feature-mapping strategy
- [ ] Decide how to handle the missing viscosity target (drop it, or impute/exclude)
- [ ] Retrain on the compiled dataset
- [ ] Compare against published results — same, better, or worse, and why
- [ ] Frame results as **literature-scale meta-analysis**, never as independent experimental replication

**Blocked by:** M3a.

### #5 EPIC M4 — Add adsorption capacity as a design dimension  _(OPEN)_
*labels:* epic, type:model

Extend the generative target space with **adsorption capacity (Qmax)** — the fourth dimension.

Available today: `Functional_Data` (28 rows: Qmax_Cs, Qmax_Sr, Langmuir/D-R params) and `Adsorption_Isotherms` (21 rows).

- [ ] Integrate the adsorption tables into the processed dataset
- [ ] ⚠️ Assess data sufficiency — **28 rows is very small** for a generative target; quantify uncertainty honestly
- [ ] Extend the model to emit Qmax alongside the physical properties
- [ ] Evaluate; decide whether M6 corpus expansion is a prerequisite for credible results

**Blocked by:** M3a.

### #6 EPIC M5 — Radionuclide immobilisation design  _(OPEN)_
*labels:* epic, type:model

Apply the extended model to design formulations for **Cs-137 / Sr-90** immobilisation.

- [ ] Define design targets for each radionuclide
- [ ] Generate candidate formulations
- [ ] Validate against literature isotherms, leaching and thermodynamics sheets
- [ ] Cross-check candidates against the feasibility block

**Blocked by:** M4.

### #7 EPIC M6 — Corpus & dataset expansion (continuous)  _(OPEN)_
*labels:* epic, type:research

Systematically grow the literature corpus and the adsorption dataset — the current 28 adsorption rows are the main bottleneck for M4/M5.

- [ ] Define a systematic search protocol (databases, queries, inclusion criteria)
- [ ] Screen and log candidates
- [ ] Build a repeatable extraction pipeline into the schema from M2
- [ ] Add each new source to `papers/MANIFEST.md` with its DOI
- [ ] Track dataset growth over time

Runs in parallel with all other milestones.


## Pull requests

### PR #8 M1: GEOMIND reproduction specification  _(MERGED)_
Closes #1.

Deliverable: `docs/paper-analysis/reproduction-spec.md` — a spec precise enough to implement GEOMIND from scratch and reproduce every published number.

### Headline findings
1. **The authors published their code, trained weights, and a 10-sample subset** ([repo](https://github.com/Geopolymer-AI/GEOMIND), [Zenodo](https://doi.org/10.5281/zenodo.20286234)). We can verify our implementation against their models as an oracle.
2. 🔴 **That repo has NO LICENSE — all rights reserved.** We may study it but **must not copy any code**. Implementation must be independent. Recorded in §1.
3. **The confidential 112-sample dataset is available on request** from the corresponding author — the single highest-leverage action available to this project.
4. Our `GEOMIND_Samples` and `Validation_Samples` sheets are confirmed to match the paper's published subset and Table S5.
5. **8 gaps logged.** Blocking: **G1** loss weights `w1..w6` unpublished, **G2** KL-divergence term unspecified.
6. The paper is **internally inconsistent** on final MAEs (conclusion vs Table 4) — flag when contacting the authors.

### Verification
Architecture, hyperparameters and all result tables were transcribed directly from the paper (14 pp) and SI (7 pp); the published CSV schema was checked against our `GEOMIND_Samples` sheet.

### Research-integrity check
- [x] No result overstated; literature-derived data

### PR #9 M2: data quality & provenance — CRITICAL integrity finding  _(MERGED)_
Part of #2. **Cleaning intentionally not implemented yet** — a provenance decision is required first.

## 🔴 F1 (critical): `Si_Al` and `Density` are not measurements of these mixes

- **9 of 11** unique `Si_Al` values match the GEOMIND paper exactly to 3 decimals
- **All 10** of the paper published density values appear in our `Density` column
- **91 of 92** distinct mix designs carry a single `Si_Al`/`Density` — broadcast, not per-specimen
- Neither column exists in **either** traceable source file

Training on these would learn an **artefact of the join**, not materials science.

## Other findings
- 🔴 **F2** `Metakaolin` is constant **0** — the paper primary precursor is absent. Only **92 distinct mix designs** underlie the 867 rows.
- 🟠 **F3** adsorption data: **16 distinct Cs values + 7 Sr rows**, not 28 → **M6 must precede M4**
- 🟡 **F4** 18 duplicate rows; `v2` disagrees in 22 cells; CSV/XLSX are byte-identical
- 🟢 **F5** `Metadata.csv` is cp1256

## Sound and usable
`Comp_Strength` traceable (only 4 of 474 values untraceable) · `Functional_Data` sources named · `GEOMIND_Samples` and `Validation_Samples` verified against the paper.

## Verification
All figures reproducible: `python -m src.geomind.data.profile`

## Research-integrity check
- [x] No result overstated
- [x] No data modified — profiling only
- [x] No copyrighted material committed

### PR #10 M2: cleaning pipeline, data dictionary, M3b re-scope  _(MERGED)_
Closes #2. Implements the M2 decisions from PR #9.

## Actioned
- **F1** — dropped `Si_Al` and `Density` (transplanted from the paper, not measured)
- **F2** — dropped `Metakaolin` (constant zero)
- **F4** — removed 18 duplicate rows; CSV declared authoritative
- Row-level `provenance` attached: `Data.xlsx` 655 · `N_data.xls` 185 · ambiguous 5 · **UNTRACED 4**
- `material_system=fly_ash_slag_concrete` tag guards against silently mixing systems
- **F3** — repeated adsorption values are **flagged, not deleted** (`cs_value_repeated`, `sr_value_repeated`)

## Outputs
`physical` 867×11 → **849×10** · `adsorption` **28×12** · `geomind_reference` **10×27**

## M3b re-scoped
From *"extended validation of GEOMIND"* → **cross-system transfer study**. Our data is fly-ash/slag concrete, not metakaolin paste; with no viscosity, no metakaolin and only 92 distinct mixes, calling it a validation would be dishonest. The re-scoped question is legitimate and interesting on its own terms.

## Interpretation limits recorded
- **Group CV by mix design** — 849 rows are replicates of 92 mixes; naive CV leaks.
- **`-1` is an infeasibility sentinel**, never impute it.

## Verification
`python -m src.geomind.data.clean` runs clean; log at `data/processed/cleaning_log.md`.

## Research-integrity check
- [x] No result overstated; M3b re-scoped rather than overclaimed
- [x] Provenance attached; nothing sile

### PR #11 Add GEOMIND dataset request letter (local, unsent)  _(MERGED)_
Action **A1** from the M1 spec, kept as a local file at `docs/correspondence/2026-07-19-geomind-dataset-request.md`.

Requests the confidential 112-sample dataset (with an offer to sign a confidentiality/data-use agreement) and asks for the two blocking unknowns: **G1** loss weights `w1..w6` and **G2** the KL term. Also courteously flags the MAE inconsistency between the conclusion and Table 4.

**Not sent** — to be sent manually.

### PR #12 M3a: verified chemistry layer + feasibility controller  _(MERGED)_
Part of #3. First implementation step from the M1 spec. **No code from the authors all-rights-reserved repo is used** — only their published *numbers* act as an oracle.

## ✅ Chemistry layer verified against all 10 published samples
| Ratio | Max deviation | Mean signed error |
|---|---|---|
| Si/Al | 1.1 % | <1 % |
| Solid/Liquid | 1.9 % | <1 % |
| Si/M_Sol | 2.7 % | <1 % |

Residual scatter is explained by the source data: published fractions are rounded to 2 dp and **sum to 1.00–1.02**. An **anti-bias test** (mean signed error near zero) guards against a wrong formula hiding behind loose per-row tolerances.

**Two relationships the paper never states, recovered empirically:**
- `Si/M_Sol = n_Si_sol / n_M_total` (not `/ n_M_sol`)
- `Solid/Liquid = metakaolin mass / activator mass`

## 🔴 F6 (new, critical): `Feasibility_Ranges` is mislabelled and unusable
Tested against the paper own samples it is **anti-correlated with truth**: rejects **7 of 9 feasible**, accepts **1 of 1 infeasible**.

Its `Si/Al 1.5-3.0` and `Porosity 15-65` are **verbatim constants from the retired heuristic tool** at tag `v1.0.0` — yet labelled `Source: GEOMIND (2026)`. Same pattern as F1, opposite direction.

**Handled:** the sheet is not read. `feasibility.py` uses paper-verified viscosity classes plus a **provisional** envelope, flagged `provisional=True` on every verdict. A regression test asserts th

### PR #13 M6: ingest Oulu AAM composition-adsorption dataset  _(MERGED)_
Part of #7. Sorts the new data drop into the project.

## What arrived
- **Companion paper** — Hossain et al., *Materials & Design* 262 (2026) 115471, `doi:10.1016/j.matdes.2026.115471` (supplied as `اثبات ان الامتزاز مرتبط بالتركيب.pdf`)
- **Its full dataset** — 820 files / 115 MB: SEM, XRD, XRF, FTIR, **BET-BJH**, PSD, **Si NMR**, zeta potential, synthesis + adsorption

## Why this is the best data in the project
A **designed** composition study (Si/Al/Na/Ca varied systematically, Si/Al 1-20), **triplicate** measurements with STDs, plus full structural characterisation. Its **21 NH4+ rows exceed our entire Cs compilation** (16 distinct values), and shows a clean monotonic trend: lower Si/Al -> higher uptake, exactly as framework charge predicts.

## Honesty guard
Adsorbates are NH4+, methylene blue, rhodamine 6G — **not Cs-137/Sr-90**. NH4+ is a recognised monovalent-cation analogue for Cs+, so it informs cation exchange, but it is an analogue. Every row carries `adsorbate` and `is_radionuclide_analogue`.

## Verification
`python -m src.geomind.data.ingest_oulu` -> 63 rows, 20 compositions, 3 adsorbates. Bulk 115 MB is gitignored; only the tidy extract is committed.

### PR #14 M6: canonical adsorption schema + pooled database  _(MERGED)_
Part of #7. Builds the meta-analysis backbone so mined sources merge into one corpus safely.

## Two traps encoded in the schema, not left to documentation
1. **`capacity_type`** — Langmuir *Q*max (fitted over an isotherm) vs single-point uptake at one C0 are **different quantities**. Pooling silently would corrupt the target.
2. **`adsorbate_class`** — radionuclide / analogue / dye, so NH4+ can never quietly become a Cs target.

`pooling_warning()` fires automatically when a pool mixes them.

## Oulu conversion made auditable
Workbook reports concentration *removed* (mg/L); the paper states **dose = 1 g/L**, so `q[mg/g] = dC/dose`. Numerically 1:1 here — but written out so the basis is checkable rather than assumed.

## Current pool
94 rows, 2 sources, **0 validation issues**

| adsorbate | class | type | n |
|---|---|---|---|
| Cs | radionuclide | Qmax | 24 |
| Sr | radionuclide | Qmax | 7 |
| NH4+ | analogue | single-point | 21 |
| dyes | dye | single-point | 42 |

**Usable for the Cs/Sr target: 31 rows.** Still short — which is what the running M6 sweep is for.

## Extension point
Add a `_from_*` adapter per new source in `ADAPTERS`.

### PR #15 M6: literature sweep worklist + extended capacity typing  _(MERGED)_
Part of #7. Automated sweep: 101 agents, 643 tool calls, adversarially verified.

## 🔴 Headline (negative result)
**No large ready-made open dataset of Cs/Sr adsorption on geopolymers exists.** The only tier-1 open deposit found is the Mendeley record we already hold (Oulu) — which contains **no Cs/Sr at all**.

**Realistic yield: ~30-60 rows, not hundreds.** This constrains what M4/M5 can honestly claim and should be stated up front, not discovered by a reviewer.

## New sources
- **A1 Varon 2025** (Cleaner Materials 17:100331, CC BY-NC) — best new **Sr** source: designed Si/Al + H2O/M2O sweep with BET and NMR
- **A2 Katada 2024** (Langmuir, PMC11411716) — **open HTML table**, 6 zeolites; easiest extraction available. Shows **Si/Al alone cannot explain selectivity** — relevant to our feature design
- **B1/B2** paywalled (NaOH molarity→Kd series; 3 natural zeolites)
- **C1 JAEA-SDB** — Cs/Sr Kd at scale but **zero geopolymers**; analogue materials only

## Schema fix the sweep forced
The field reports **five** different quantities. `CapacityType` gains `FREUNDLICH_QMAX`, `ION_EXCHANGE_CAPACITY` (meq/g) and `KD` (mL/g), plus `meq_g_to_mg_g()`. **Kd is not a capacity** and must never enter the mg/g pool.

Verified: `Lin Cs 0.41 meq/g -> 54.49 mg/g`, `Sr 5.07 meq/g -> 222.12 mg/g`.

## Research-integrity note
Refuted claims are recorded alongside confirmed ones — including that JA

### PR #16 M6: extract Katada 2024 — and a finding that changes M4 feature design  _(MERGED)_
Part of #7. Extracts source **A2** (6 Cs rows) and records a result that should shape M4.

## ⚠️ Si/Al alone is the wrong feature
Across the six Na-form zeolites, Cs capacity correlates **+0.68 with Si/Al** but **−0.81 with Al content** — the opposite of "more Al → more exchange sites".

The driver is **accessibility, not site count**:

| Sorbent | Si/Al | Al (mol/kg) | Cs (mg/g) | **% Al sites used** |
|---|---|---|---|---|
| LTA 6.7 | 1.12 | 6.69 | 23.9 | **2.7 %** |
| FAU 6.1 | 1.37 | 6.08 | 73.1 | 9.0 % |
| MOR 1.5 | 9.88 | 1.48 | 191.4 | **97.3 %** |

High-Al frameworks have abundant sites Cs+ **cannot reach**.

## This does NOT contradict the Oulu trend
Oulu (lower Si/Al → more NH4+) varies composition **within one amorphous family**. Katada varies **crystalline topology**, where Si/Al is confounded with pore structure. Both are right; they vary different things.

## Consequences
1. M4 needs **accessibility descriptors** (BET, pore aperture, accessible-Al fraction), not just Si/Al.
2. **Never pool geopolymers and zeolites** into one Si/Al→capacity model — the relationship has **opposite sign**. New `sorbent_class` + `framework_code` prevent it.
3. These capacities were measured against **1000 mg/L Na** → selectivity-limited, not clean maxima. Recorded via `competing_ion`.

## Pool
100 rows / 3 sources / **0 validation issues**. Cs+Sr rows **31 → 37**.

## Licence
CC BY-NC

### PR #17 M6 round 2: two negative results (no rows added)  _(MERGED)_
Part of #7. **No rows added** — both leads investigated and rejected, with reasons recorded.

## A1 Varon 2025 — no automated retrieval path
Confirmed gold OA (CC BY-NC) but ScienceDirect **403s**, Unpaywall reports `url_for_pdf: None` for **both** locations, and HAL indexes it with **no deposited full text**. → **needs a manual download**, after which it is our best Sr source.

## Tian supplement — deliberately NOT ingested
Its 24-row table looked high-yield but:
1. the three "Present work" rows are **already in the pool** (Cs 111.90 / Sr 24.18);
2. the other ~21 sorbents are **not aluminosilicates** (Prussian blue, magnetite, yeast, dolomite…);
3. decisively, it reports **no Si/Al or composition of any kind**.

Ingesting would have grown the pool 100 → ~124 while adding **zero usable features** — padding a composition→capacity database with composition-free rows. **Row count is not progress.**

### PR #18 M6: Tarnovsky 2024 — first rows with Si/Al AND BET together  _(MERGED)_
Part of #7. **+6 Cs/Sr rows.** Found by a systematic OpenAlex sweep filtered to `is_oa` **and a real `pdf_url`** — 9 fetchable OA works surfaced. MDPI and RSC served bot-protection HTML; this one downloaded cleanly.

**Tarnovsky et al. 2024**, `doi:10.15407/hftp15.01.102` (**CC BY**) — metakaolin geopolymers with Langmuir **Cs+ AND Sr2+** isotherms plus **BET/porosity**.

| sample | class | Si/Al | BET | Cs mg/g | Sr mg/g |
|---|---|---|---|---|---|
| Kaolin | clay | 1.03 | 9 | 13.3 | 14.9 |
| GP 1 | geopolymer | 1.95 | 26 | **232.6** | 48.2 |
| GP 2 | geopolymer | 1.59 | 88 | 123.6 | 57.0 |

**These are the first rows in the pool carrying `si_al` and `bet_m2_g` together** — the composition→structure→capacity chain M4 needs.

## Unit trap handled
Capacities are **mmol/g (molar)**, not meq/g (charge). For **divalent Sr the two differ by 2×** — confusing them would silently halve every Sr value. `mmol_g_to_mg_g()` is deliberately a separate named function.

## Bug fixed
The module entrypoint sat mid-file, so adapters appended after it registered **only after `main()` had already run** — the first merge silently produced 100 rows instead of 106. Moved to end of file.

## Note
GP 1 has **3.4× the BET of nothing** — yet GP 2 has **3.4× more BET (88 vs 26) and *lower* Cs capacity**. Second independent confirmation that surface area alone does not predict capacity.

Pool: **106 rows /

### PR #19 M6: Varon 2025 — AlIV, not BET, predicts Sr sorption  _(MERGED)_
Part of #7. **+7 Sr rows** — and the M4 feature question is now answered.

## The result
Seven K-geopolymers with BET, 27Al NMR and 29Si Q4(mAl) on the **same samples** as the Sr tests:

| Predictor | corr with K_D(Sr) |
|---|---|
| **BET surface area** | **+0.19** — almost no explanatory power |
| Si/Al | −0.95 |
| **[Al-IV] mmol/g** | **+0.95** |

The **highest**-BET sample (212 m²/g) has among the **lowest** K_D (1100); a 72 m²/g sample has the **highest** (4100).

## This reconciles all four datasets
- **Within one family** (Oulu NH4+, Varon Sr): lower Si/Al → more Al → more sorption
- **Across crystalline frameworks** (Katada Cs): topology decides which Al is *reachable*; Si/Al misleads
- Tarnovsky independently: BET 88 → *lower* Cs than BET 26

**The unifying variable is accessible tetrahedral aluminium — not surface area, not Si/Al.**

## Consequences for M4
1. Primary feature should be **[Al-IV] / accessible-Al**; Si/Al secondary; **BET weak**
2. **Oulu already has 29Si NMR for all 20 compositions** — mine it next
3. BET must not be assumed predictive — four datasets now say otherwise

## Data handling
K_D is **not** a capacity. These rows carry `kd_mL_g` with `capacity_mg_g` **NULL**, so they cannot be swept into an mg/g regression. `validate()` now accepts either target.

Sample names for rows 5–7 are **inferred from context** and labelled as such; the numbers come st

### PR #20 M6: Oulu BET — surface area is negatively related to uptake  _(MERGED)_
Part of #7. BET extracted for all 20 Oulu compositions (1.0–248.6 m²/g). Rows with **both** `si_al` and `bet`: **6 → 76**.

## Result (NH4+ uptake, designed series)
| Subset | corr(BET) | corr(Si/Al) |
|---|---|---|
| All 20 | −0.50 | −0.62 |
| **Ca-free (n=8)** | **−0.97** | −0.91 |

`Si20Al1Na1`: **highest** BET (248.6) → **lowest** uptake (2.13). `Si1Al1Na1`: 8.3 m²/g → **highest** uptake (13.73).

## ⚠️ Honest limits
In the Ca-free series **BET and Si/Al are near-collinear**, and the design **fixes Al = 1**, so Al content and Si/Al are the *same axis*. This dataset **cannot separate them**. What it *does* show decisively: **high surface area does not imply high uptake**.

## Mechanism — now consistent across five datasets
Raising Si/Al increases surface area while decreasing framework charge. Cation exchange follows **charge, not area**.

→ **M4 should use accessible framework charge (Al-IV) as the primary feature. BET is not merely weak — it is actively misleading as a proxy.**

## 🔴 Bug caught (and recorded)
The BET files are ASAP-2020 **BIFF2** binaries; `BET Surface Area:` is **not contiguous** after decoding. A naive regex fails, and a loose fallback captures `single point surface area at p/p₀ = 0.30` — returning **0.3 m²/g for every sample** and a plausible-looking but **entirely false** correlation. Caught before reporting; `extract_bet()` now uses a tolerant pattern

### PR #21 M6: mine local backlog (+13 rows) — and two provenance errors found  _(MERGED)_
Part of #7. Extracted 8 held papers via parallel subagents. **+13 rows** (pool 113 → 126, 8 sources).

## New sources
| source | rows | notes |
|---|---|---|
| `lin2026` | 6 | Langmuir q_m, geopolymer granules + zeolites, 35 g/L NaCl background |
| `tian2019_espr` | 2 | zeolite A from fly ash, Cs/Sr Langmuir, BET 121 |
| `xiang2021` | 5 | metakaolin geopolymer **foams**, Cs, BET + porosity |

**Excluded deliberately:** Lin unmodelled "screening capacities"; its non-aluminosilicate benchmarks; **Nevin 2026** (diffusivity/leaching, no capacity); **Niu 2022** (figure-only).

## Sixth confirmation on BET
Xiang foam series: BET falls **53.8 → 37.8**, porosity falls **83.8 → 68.4 %**, while Cs uptake **RISES 161.8 → 192.1 mg/g**. corr(BET) = **−0.92**, corr(porosity) = **−0.96**.

## 🔴 F7 — the compiled data has provenance errors
Re-extraction doubled as an audit of the hand-typed `Functional_Data`:

- **F7a — europium labelled as strontium.** Rows recorded as `Sr` = 18.58 / 19.98 / 21.55 are **Eu-152+154**. The source paper studies Cs, Co and Eu — **no strontium at all**. That is **3 of only 7 Sr rows**, and the wrong element.
- **F7b — Niu 2022 values are not in the paper.** Four rows claim Langmuir Qmax (Cs 152.84, Sr 279.20); the paper **tabulates no capacities**, only log K. Identical values across two sorbents is itself a red flag.
- **F7c — probable duplicate**: `Na-MK` (El-Na

### PR #22 M6: screen batch 2 inline (+2 rows) — 4 of 5 are leaching studies  _(MERGED)_
Part of #7. **All inline, no subagents.**

## Re-verified the earlier subagent work against the PDFs myself
- Xiang: `qm KL RL R2 → 216.1 0.026 0.0714 0.9808` ✓
- Tian: *"maximum sorption capacities on Cs+ and Sr2+ based on Langmuir model were 2.12 and 1.93 mmol/g"* ✓
- Lin: *"up to 0.41 meq/g for Cs+ and 5.07 meq/g for Sr2+"* ✓

Attribution confirmed in context — those 13 rows stand.

## Batch 2: only 1 of 5 has sorption data
| Paper | Langmuir | leaching | Verdict |
|---|---|---|---|
| **Zhang 2021** (`10.3390/app11188407`) | 20 | 0 | ✅ ingested |
| JRNC 2025 wasteform | 1 | **101** | ❌ leaching |
| AAC immobilisation 2023 | 0 | 0 | ❌ none |
| Costa-Silva 2025 | 0 | **43** | ❌ leaching |
| O Donoghue 2025 Dalton | 1 | 1 | ❌ synthesis mechanisms |

**Zhang Table 4 (Cs):** fly-ash geomaterial **89.32 mg/g** (K_L 0.1665, R² 0.9948); slag **44.52 mg/g** (K_L 0.02126, R² 0.9954).

## Lesson
**"geopolymer + Cs/Sr" is not a sufficient query.** Much of that literature is about *immobilising* radionuclides in a waste form (leaching, diffusivity) rather than *adsorbing* them from solution. Future queries must require isotherm vocabulary and exclude leachability-index / ASTM C1308 terms.

Pool: **128 rows / 9 sources**.

### PR #23 M6: full inline source audit — 10 of 31 compiled rows removed/corrected  _(MERGED)_
Part of #7 and #2. Every `literature_compilation` row checked **inline** against its source PDF, reading surrounding context rather than just matching numbers. **32% did not survive.**

## Two distinct failure modes
1. **Misattribution** — `Na-MK` (58.96/61.27/57.60) credited to El-Naggar 2018 is actually `U-P MK100` from the magnetic-ternary paper. **El-Naggar reports only MKBFS systems**; `Na-MK`/`K-MK` do not appear in it.
2. **Fabricated sorbent** — `K-MK` is a **verbatim copy** of `K-MKBFS`, creating an apparently independent material that does not exist.

Plus from the earlier pass: three "Sr" rows are **Eu-152+154**; four `Niu_2022` rows claim Langmuir Qmax from a paper that **tabulates no capacities**.

## Verified correct
`Na-MKBFS`, `K-MKBFS`, Hamed Cs, Lei (both), Tian (values live in the **supplement**, not the article), Zheng.

**Re-typed:** Lei Cs is **Freundlich**-fitted — the paper says so explicitly: *"103.74 and 54.90 mg/g … best explained by Freundlich and Langmuir … respectively"*.

## Net effect
Pool **128 → 118**. Compilation **31 → 21**. Cs+Sr **52** (Cs 37, **Sr 15**).

**Sr was never 7 genuine rows — 3 were europium.** Newly mined sources have since taken source-verified Sr to 15.

Corrections are named constants with reasons inline, so the reasoning travels with the code.

### PR #24 Knowledge base + NMR deconvolution plan  _(MERGED)_
Two deliverables.

## 1. Unified knowledge base — machine-checked
`knowledge_base/registry.yaml` is the **single source of truth**: 17 assets, 16 sources, 10 findings, 10 decisions, 5 open questions.

Every asset carries a closed-vocabulary `status` and a **binding `usage`** constraint.

**The key design choice:** the master workbook is registered **sheet by sheet**, not as one file — `Feasibility_Ranges` (rejected), `Adsorption_Isotherms` (duplicate), `NMR_Sr_Cs_Data` (verified), `GEOMIND_Samples` (verified), plus the 16 screened-but-unmined sheets each carry their own status. **That is what stops a whole file being pulled in at once when only part of it is sound.**

`docs/knowledge-base/*.md` are **generated** — documentation cannot drift from the registry.

Validator catches: unknown statuses, missing usage constraints, dangling finding/question refs, duplicate ids, findings with no action. **Six negative tests prove it actually catches drift**, plus a test that the headline row count matches the real pooled file.

## 2. NMR deconvolution plan
`docs/nmr-deconvolution-plan.md` — 7 steps, each gated. Built around an **independent ground truth**: the Engelhardt relation gives Si/Al from fitted Q4(mAl), and we already know the true Si/Al from synthesis. **Pre-registered acceptance at r ≥ 0.9**, fixed before fitting so it cannot be relaxed retroactively.

## Correction recorded a
