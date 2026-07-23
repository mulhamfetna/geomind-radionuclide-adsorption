# Data Dictionary

Describes the **model-ready tables** emitted by `python -m src.geomind.data.clean` into
`data/processed/` (regenerable; not committed). Decisions trace to
[`reports/m2-data-quality-report.md`](../reports/m2-data-quality-report.md).

---

## `physical.csv` — 849 × 10

Fly-ash / slag **concrete** compressive-strength data. **This is not the paper's material
system** (see the material-system warning below).

| Column | Meaning | Unit | Notes |
|---|---|---|---|
| `FlyAsh` | fly ash content | kg m⁻³ | 4 distinct values |
| `GGBFS` | ground granulated blast-furnace slag | kg m⁻³ | 2 distinct values |
| `NaOH_M` | NaOH molar concentration | mol L⁻¹ | 4 distinct values (8–14) |
| `Na2SiO3` | sodium silicate content | kg m⁻³ | 5 distinct values |
| `CopperSlag` | copper slag content | kg m⁻³ | 6 distinct values |
| `RecycledAgg` | recycled aggregate content | kg m⁻³ | 6 distinct values |
| `Curing_Days` | curing age at test | days | 5 distinct values (3–90) |
| `Comp_Strength` | **target** — compressive strength | MPa | 11–102; the only high-cardinality column |
| `provenance` | source file the strength value traces to | — | `Data.xlsx` (655) · `N_data.xls` (185) · `ambiguous` (5) · `UNTRACED` (4) |
| `material_system` | constant `fly_ash_slag_concrete` | — | guards against silently mixing systems |

### ⚠️ Columns deliberately removed

| Removed | Why |
|---|---|
| `Si_Al` | **F1** — 9 of its 11 values match the GEOMIND paper exactly to 3 dp; broadcast one-per-mix across 91/92 mixes; absent from both source files. **Transplanted from the paper, not measured.** Using it would learn a join artefact. |
| `Density` | **F1** — all 10 of the paper's published density values appear here; same broadcast pattern; absent from both source files. |
| `Metakaolin` | **F2** — constant `0` across all 867 rows. Carries no information, and shows the paper's primary precursor is absent from this dataset. |

**18 exact duplicate rows** were removed (867 → 849).

### Interpretation limits

- Only **92 distinct mix designs** underlie these rows; most rows are replicate specimens.
  Effective sample size ≈ 92, not 849. **Cross-validation must group by mix design**, or estimates
  will be optimistically biased by leakage between replicates.
- There is **no viscosity** and no fresh/consolidated density split, so the paper's four-property
  target space cannot be reproduced here.

---

## `adsorption.csv` — 28 × 12

Cs/Sr adsorption capacities — the M4/M5 target. **Small and partly duplicated.**

| Column | Meaning | Unit |
|---|---|---|
| `Sorbent_Type` | sorbent identifier (e.g. `Na-MK`, `FA-Geopolymer`) | — |
| `Si_Al` | silica/alumina molar ratio of the sorbent | — |
| `NaOH_M` | activator concentration | mol L⁻¹ |
| `Temp_K` | experiment temperature | K |
| `Qmax_Cs_mg_g` | **target** — max Cs adsorption capacity | mg g⁻¹ |
| `Qmax_Sr_mg_g` | **target** — max Sr adsorption capacity | mg g⁻¹ |
| `b_L_mg` | Langmuir affinity constant | L mg⁻¹ |
| `E_kJ_mol` | Dubinin–Radushkevich mean sorption energy | kJ mol⁻¹ |
| `R2_Langmuir` | Langmuir fit quality | — |
| `provenance` | source publication | — |
| `cs_value_repeated` | 🚩 this `Qmax_Cs` value occurs verbatim elsewhere | bool |
| `sr_value_repeated` | 🚩 this `Qmax_Sr` value occurs verbatim elsewhere | bool |

`Si_Al` **is** legitimate here — it is a genuine property of each published sorbent, taken from its
source paper. This is unrelated to the transplanted `Si_Al` removed from `physical.csv`.

### ⚠️ Usable evidence is far below 28 rows

- `Qmax_Cs`: 24 rows → **16 distinct values** (15 flagged repeated)
- `Qmax_Sr`: **7 rows** → 6 distinct values (2 flagged)
- Whole blocks repeat verbatim: rows 3–5 vs 9–11 share identical Qmax/b/E/R² despite different
  sorbents; rows 12–18 repeat one triplet across `NaOH_M` 8/10/12, so **that variation is not
  reflected in the target at all**.

Rows are **flagged, not deleted** — silent deletion could discard genuine replicates. Modelling
code **must** respect the flags and must not treat repeated rows as independent samples.

**Sources:** El-Naggar 2018 · Hamed 2025 · Lei 2021 · Niu 2022 · Tian 2019 · Zheng 2023 —
to be reconciled against [`papers/MANIFEST.md`](../papers/MANIFEST.md).

---

## `geomind_reference.csv` — 10 × 27

The paper's **own published samples** — verified identical in schema to
`Geopolymer-AI/GEOMIND → data/geopolymers_23_07.csv`. Used for **M3a faithful replication**.

| Group | Columns |
|---|---|
| Precursor mass fractions | `M1(%)`…`M5(%)`, `S1(%)`, `S3(%)`, `SNa(%)`, `S3'(%)`, `KOH(%)`, `NaOH(%)` — 11, sum to 1 |
| Molar quantities | `Si_met`, `Si_sol`, `M_sol`, `M_MOH`, `Si`, `Al`, `M` (mol) |
| Molar fractions & ratios | `Si(mol%)`, `Al(mol%)`, `M(mol%)`, `Si/M_Sol`, `Si/Al`, `Solid/Liquid` |
| **Targets** | `mixture_density(g/cm³)`, `viscosity(Pa.s)`, `material_density(g/cm³)`, `compressive_strength(MPa)` |
| Added | `provenance` = `doi:10.1039/d5dd00383k` |

**`-1` is an infeasibility sentinel, not missing data.** One of the ten rows carries it. Never
impute it, never let it enter a mean.

---

## Not carried forward

| File | Reason |
|---|---|
| `GEOMIND_R_MASTER_DATABASE_v2.xlsx` | Disagrees with `Physical_Data` in **22 cells** with no changelog; its 19 radionuclide columns are largely null (15,597 null cells). **Unresolved — needs a decision on which version is authoritative.** |
| `Data.xlsx`, `N data.xls` | Retained as provenance sources only. |
| `*.xlsx` twins of the CSVs | Byte-identical; CSV is authoritative. |
| `Metadata.csv` | cp1256-encoded; superseded by this document. |
