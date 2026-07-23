# Data registry

Every data asset. **`usage` is binding** — widening it requires a recorded decision.

## Originally provided

### ✅ `raw.data_xlsx` — verified

- **Path:** `data/raw/Data.xlsx`
- **Shape:** 672 × 13
- **Description:** Fly-ash/GGBFS concrete mix designs with compressive strength (kg/m3 dosages, curing temp/time, age). One of the two traceable upstream sources of Physical_Data compressive-strength values.
- **Usage:** Provenance source only. Not used as a modelling table.
- **Findings:** F4

### ✅ `raw.n_data_xls` — verified

- **Path:** `data/raw/N data.xls`
- **Shape:** 186 × 10
- **Description:** Second concrete strength dataset (fly ash, NaOH molarity, sand, copper slag, rubber aggregate). Legacy BIFF format.
- **Usage:** Provenance source only.
- **Findings:** F4

### 🟡 `raw.physical_data` — partial

- **Path:** `data/raw/Physical_Data.csv`
- **Shape:** 867 × 11
- **Description:** Compiled fly-ash/slag CONCRETE dataset. Only 92 distinct mix designs underlie the 867 rows (the rest are replicate specimens). Metakaolin column is constant zero. Si_Al and Density were transplanted from the GEOMIND paper.
- **Usage:** Comp_Strength usable with grouped CV by mix design. Si_Al, Density and Metakaolin columns are DROPPED and must never be reinstated as features.
- **Findings:** F1, F2, F4

### ✅ `raw.master_v2` — verified

- **Path:** `data/raw/GEOMIND_R_MASTER_DATABASE_v2.xlsx`
- **Shape:** 867 × 30
- **Description:** Superset of Physical_Data with 19 extra radionuclide columns (Sr/Cs loading, diffusion coefficients, NMR Q4). Disagrees with Physical_Data in 22 cells with no changelog; extra columns are largely null (15,597 empty cells).
- **Usage:** RESOLVED (F12): the 22 "disagreements" are rounding only, all in Comp_Strength rows 843-866. N data.xls genuinely carries 6 dp and 18 of 24 v2 values appear VERBATIM upstream, so v2 preserves original precision and Physical_Data rounded it. Difference <=0.005 MPa - immaterial. Physical_Data stays canonical (cleaner, no nulls); v2's 19 extra columns remain unused as they are ~96% empty.
- **Findings:** F4, F12

### 🟡 `raw.functional_data` — partial

- **Path:** `data/raw/Functional_Data.csv`
- **Shape:** 28 × 10
- **Description:** Hand-compiled Cs/Sr adsorption capacities from 6 papers. Source-audited row by row against the primary PDFs; 10 of 31 expanded rows failed.
- **Usage:** Only the 21 audited-clean rows enter the pool. Quarantines and relabels are enforced in code (_from_literature_compilation), not by convention.
- **Findings:** F3, F7

### ✅ `raw.metadata` — verified

- **Path:** `data/raw/Metadata.csv`
- **Shape:** 19 × 4
- **Description:** Column dictionary for the concrete dataset. cp1256-encoded, not UTF-8.
- **Usage:** Superseded by docs/data-dictionary.md.
- **Findings:** F5

### ✅ `master.geomind_samples` — verified

- **Path:** `GEOMIND_RADIOACTIVE_MASTER.xlsx :: GEOMIND_Samples`
- **Shape:** 10 × 26
- **Description:** The GEOMIND paper's 10 publicly released samples, full 26-column schema (11 precursor mass fractions + molar quantities + 4 target properties). Schema confirmed identical to the authors' published CSV.
- **Usage:** Ground truth for M3a chemistry validation. -1 is an infeasibility sentinel.

### ✅ `master.validation_samples` — verified

- **Path:** `GEOMIND_RADIOACTIVE_MASTER.xlsx :: Validation_Samples`
- **Shape:** 45 × 6
- **Description:** Paper Table S5 - 15 test samples x 3 property types (target/predicted/experimental).
- **Usage:** M3a reproduction target.

### ❌ `master.feasibility_ranges` — rejected

- **Path:** `GEOMIND_RADIOACTIVE_MASTER.xlsx :: Feasibility_Ranges`
- **Shape:** 9 × 5
- **Description:** Claims Source="GEOMIND (2026)" but its Si/Al and porosity constants are verbatim from this project's own retired heuristic tool (git tag v1.0.0). Applied to the paper's own samples it rejects 7 of 9 feasible and accepts the 1 infeasible.
- **Usage:** NEVER USE for the chemical domain. Only the viscosity class boundaries (0.2/2/100/1314 Pa.s) are independently confirmed by the paper text.
- **Findings:** F6

### ♻️ `master.adsorption_isotherms` — duplicate

- **Path:** `GEOMIND_RADIOACTIVE_MASTER.xlsx :: Adsorption_Isotherms`
- **Shape:** 21 × 12
- **Description:** Duplicates Functional_Data including its fabricated Na-MK and K-MK rows. Adds only 3 values beyond it (33.11/34.88/35.64) which are COBALT-60, not Cs/Sr.
- **Usage:** NOT USED - canonical asset is raw.functional_data (audited).
- **Findings:** F7, F8

### ♻️ `master.cs_isotherms` — duplicate

- **Path:** `GEOMIND_RADIOACTIVE_MASTER.xlsx :: Cs_Isotherms`
- **Shape:** 15 × 12
- **Description:** Strict subset of Adsorption_Isotherms. Adds nothing.
- **Usage:** NOT USED.
- **Findings:** F8

### ✅ `master.nmr_sr_cs` — verified

- **Path:** `GEOMIND_RADIOACTIVE_MASTER.xlsx :: NMR_Sr_Cs_Data`
- **Shape:** 10 × 10
- **Description:** Q4(mAl) speciation + Si_Al_NMR for Nevin 2026 samples (pre/post leaching). Tested against Varon's published Q4 values - ZERO matches, so NOT transplanted. Traceable to a paper we hold.
- **Usage:** Limited value for modelling - all 10 rows are ONE formulation (Si/Al = 3), pre/post leaching. No composition variation.

### ⬜ `master.other_sheets` — unmined

- **Path:** `GEOMIND_RADIOACTIVE_MASTER.xlsx :: 16 remaining sheets`
- **Shape:** —
- **Description:** Surface_Complexation (38), Thermodynamics (18+18), Magnetic_Properties (3), Sr_Leaching_Data (10), Surface_Complexation_Sr (15), MD_Simulation_Sr_Cs (18), Sr_Immobilization_Mechanisms (9), Zeolite_Comparison_Sr_Cs (8), Leaching_Model_Comparison (24), EXAFS_Sr_Structural_Parameters (8), FTIR_Sr_Characterization (18), XRD_Sr_Phases (11), Mass_Transport_Models_Sr (12), Summary_Statistics (13), GEOMIND_Parameters (55).
- **Usage:** None contain adsorption CAPACITY. Mostly leaching, thermodynamics and spectroscopy. Screened, deliberately not mined. Revisit only if the research question changes.

## Provided later

### 📦 `external.oulu` — external

- **Path:** `data/external/aam-oulu-2026/`
- **Shape:** 820
- **Description:** Oulu designed AAM study (820 files, 115 MB): synthesis, XRF, XRD, SEM, FTIR, BET-BJH, PSD, 29Si NMR, zeta potential, and adsorption for 20 compositions spanning Si/Al 1-20. Companion to doi:10.1016/j.matdes.2026.115471.
- **Usage:** Gitignored bulk (copyright + size); tracked via papers/MANIFEST.md. Tidy extract is data/raw/external/oulu2026_adsorption.csv.
- **Findings:** F9

### ⬜ `external.oulu_nmr` — unmined

- **Path:** `aam-oulu-2026 :: Si NMR AAMs & geopolymers/All data.xlsx`
- **Shape:** 2050 × 48
- **Description:** RAW 29Si spectra (Index/Intensity/Hz/ppm per sample) - NOT deconvolved Q4(mAl) populations. 48 columns = ~12 samples, fewer than the 20 compositions.
- **Usage:** SUPERSEDED by F18: our own deconvolution was rejected (Q4(3Al) = 0 is chemically impossible) and the authors' deconvolution is published in Table 2 of the same paper. The descriptor now comes from src/geomind/data/nmr_ari.py, not from these spectra. Retained as the primary record behind that transcription.

## Derived by our code

### 🔧 `derived.oulu_adsorption` — derived

- **Path:** `data/raw/external/oulu2026_adsorption.csv`
- **Shape:** 63 × 12
- **Description:** Tidy extract of the Oulu adsorption workbooks - 20 compositions x 3 adsorbates, plus BET joined from the ASAP-2020 instrument files.
- **Usage:** Adsorbates are NH4+, methylene blue and rhodamine 6G - NOT Cs/Sr. Every row carries adsorbate and is_radionuclide_analogue so the distinction cannot be lost.

### 🔧 `derived.pooled` — derived

- **Path:** `data/processed/adsorption_pooled.csv`
- **Shape:** 118 × 41
- **Description:** The pooled meta-analysis database - 9 sources normalised to one schema.
- **Usage:** MUST be stratified before modelling. capacity_type mixes Langmuir/Freundlich/ single-point/IEC/Kd; adsorbate_class mixes radionuclide/analogue/dye. pooling_warning() fires automatically.
- **Findings:** F10
