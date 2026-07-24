# Changelog

All notable changes to this project are documented here. Versions follow
[semantic versioning](https://semver.org/); each tagged release is archived on Zenodo under the
concept DOI [10.5281/zenodo.21510123](https://doi.org/10.5281/zenodo.21510123).

## [1.2.0] — 2026-07-24

**Data acquisition closed.** The release that pins the evidence base ahead of journal submission.

### Added
- **Study-level meta-analysis** (`src/geomind/meta.py`, `geomind.meta`) — the unit of analysis is
  the *study*, not the sample. **k = 4 independent studies**, all in the predicted direction
  (weighted mean r̄ = +0.771, 25 samples, exact sign test p = 0.0625), with three negative controls
  that make the claim falsifiable and a full register of candidates **not** admitted. Inclusion
  criteria were fixed *before* the screen was run; 4 of the 7 rejected candidates would have
  *supported* the claim.
- **Virtual Lab — new "Evidence · Study-level meta-analysis" tab** in **both** the desktop app and
  the self-contained notebook, showing the studies, the controls, the rejection register with its
  criteria, and the honest limits.
- **Corpus manifest generator** (`src/geomind/manifest.py`) — regenerates `papers/MANIFEST.md` from
  the corpus on disk plus the source registry, linking each file to the pool rows it supports.
  Ends the manifest drift (it had tabulated 19 documents while 51 were present).
- **Pool B adapters** for Vandevenne 2018 (14 rows) and Jain 2022 (5 rows); schema fields
  `ca_si_al` (kept deliberately separate from `ca_al`) and `bet_m2_g`.
- **Findings F38–F46** (register now 46), including the batch-6/7 reports, the n = 7 ceiling
  analysis, the data-only strategy, and the laboratory campaign protocol.

### Changed
- **Pool B: 54 → 73 rows / 8 → 10 sources.** Pool A unchanged at 141.
- `PROGRESS.md` carries a pinned **"data acquisition is closed"** block with the four findings
  that justify it.
- README states the study-level result as headline finding 6 and records the acquisition closure.

### Fixed
- The CI reproducibility guard now asserts the correct Pool B size (it caught the change itself).

### Verified
- **202 tests passing**; every headline number unchanged and re-verified from a clean checkout by
  CI on Python 3.10–3.12: forward LOO-CV R² = 0.811, pooled R² = −0.092, framework r = 0.932 → 0.550.

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
