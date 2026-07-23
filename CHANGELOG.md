# Changelog

All notable changes to this project are documented here. Versions follow
[semantic versioning](https://semver.org/); each tagged release is archived on Zenodo under the
concept DOI [10.5281/zenodo.21510123](https://doi.org/10.5281/zenodo.21510123).

## [1.1.0] — 2026-07-23

**DOI:** [10.5281/zenodo.21511375](https://doi.org/10.5281/zenodo.21511375)

### Added
- **CC BY 4.0 licence for data, figures and documentation** (`LICENSE-DATA`), alongside
  AGPL-3.0-or-later for the software. Both require attribution.
- **Source-data workbook** — `geomind.source_data` regenerates, from the live pipeline, the exact
  values behind every figure panel plus both audited pools
  (`data/source-data/GEOMIND-R-source-data.xlsx`, 10 sheets).
- `paper.md` / `paper.bib` for a Journal of Open Source Software submission.
- Author affiliations, ORCIDs and contact addresses in `CITATION.cff`, `.zenodo.json`, `NOTICE.md`
  and the README.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, installation and runnable usage examples.
- Continuous integration running the suite on Python 3.10–3.12 and re-verifying the published
  numbers from a clean checkout.

### Fixed
- **Reproducibility from a fresh clone.** `data/processed/*.csv` and a 91-row
  `data/warehouse/audit_summary.csv` are now committed; previously a clone silently produced a
  short Pool A and an empty audit trail. `load_audit_summary()` falls back to the committed CSV
  when the 31 MB warehouse database is absent.

### Removed
- Private working notes (`notes.md`) from version control.

## [1.0.0] — 2026-07-23

**DOI:** [10.5281/zenodo.21510124](https://doi.org/10.5281/zenodo.21510124)

First public release, under AGPL-3.0-or-later.

### Added
- Audited, provenance-tracked meta-analysis database: Pool A (adsorption, 141 rows) and Pool B
  (immobilisation, 54 rows), kept deliberately separate.
- The framework-aluminium descriptor result, evidenced on three independent levels.
- A within-class forward model, K_D = 2812·[Al^IV] − 9258 mL/g, leave-one-out R² = 0.81, behind an
  explicit domain guard.
- The cross-laboratory pooling result (leave-one-out R² < 0) and the Langmuir saturation screen
  (θ = 1 − R_L).
- The **Virtual Lab**: a local Gradio application and a self-contained Colab notebook mirror,
  generated from tested modules and verified against them.
- 91-table veracity audit trail and a 37-finding register.
