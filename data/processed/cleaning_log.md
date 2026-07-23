# M2 cleaning log

Decisions implement `reports/m2-data-quality-report.md`.

## physical
- loaded `Physical_Data.csv` (authoritative over the byte-identical .xlsx): (867, 11)
- F4 removed 18 exact duplicate rows -> 849
- **F1 dropped ['Si_Al', 'Density']** — transplanted from the paper, not measured here
- F2 dropped ['Metakaolin'] — constant zero, no information
- provenance attached by compressive-strength match: {'Data.xlsx': 655, 'N_data.xls': 185, 'ambiguous:Data.xlsx|N_data.xls': 5, 'UNTRACED': 4}
- tagged `material_system=fly_ash_slag_concrete` (NOT the paper's metakaolin pastes)

## adsorption
- loaded `Functional_Data.csv`: (28, 10)
- provenance already present: ['El-Naggar_2018', 'Hamed_2025', 'Lei_2021', 'Niu_2022', 'Tian_2019', 'Zheng_2023']
- F3 Qmax_Cs_mg_g: 24 rows but only 16 distinct values -> 15 flagged as repeated
- F3 Qmax_Sr_mg_g: 7 rows but only 6 distinct values -> 2 flagged as repeated
- ⚠️ retained all rows; repetition is FLAGGED, not removed — dropping would silently discard genuine replicates. Model code must respect these flags.

## geomind_reference
- loaded `GEOMIND_Samples`: (10, 26) (verified == the paper's published subset)
- 1 row(s) carry the -1 infeasibility sentinel (NOT missing data)

-> wrote `data/processed/physical.csv` (849, 10)

-> wrote `data/processed/adsorption.csv` (28, 12)

-> wrote `data/processed/geomind_reference.csv` (10, 27)

## Not carried forward
- `GEOMIND_R_MASTER_DATABASE_v2.xlsx` — disagrees with Physical_Data in 22 cells with no changelog; its 19 radionuclide columns are largely null. Unresolved (F4).
- `Data.xlsx`, `N data.xls` — retained as provenance sources only.
- `Metadata.csv` — cp1256; superseded by `docs/data-dictionary.md`.
