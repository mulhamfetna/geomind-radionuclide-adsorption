# Submission package — COMPLETE · revision v1.4.0 released (2026-07-25)

All seven deliverables are done; both Zenodo records are published and cross-linked. A **v1.4.0**
revision release adds the reviewer-facing robustness & sensitivity evidence. **v1.3.0 stays frozen
as the submission-of-record** — the manuscript, Colab link and figures package all remain pinned to
it, so nothing the journal received has moved.

## The records

| Record | DOI (concept — cite this) | Latest version | Submitted version (frozen) | Licence |
|---|---|---|---|---|
| **Software** (code, Virtual Lab, history) | 10.5281/zenodo.21510123 | 1.4.0 → 10.5281/zenodo.21555728 | 1.3.0 → 10.5281/zenodo.21546029 | AGPL-3.0 |
| **Dataset** (audited database) | 10.5281/zenodo.21540569 | 1.3.0 → 10.5281/zenodo.21540570 | (same) | CC BY 4.0 |

Cross-linked both ways (`isSupplementTo` / `isSupplementedBy`). Manuscript Data Availability cites
the dataset DOI as the data of record.

## What v1.4.0 added

`geomind.robustness` — two complementary, reproducible analyses, surfaced in an
"Evidence · Robustness & sensitivity" tab in both the desktop Virtual Lab and the Colab notebook,
plus manuscript §3.7, a Methods note, and Supplementary S3:

1. **Analytical robustness** (data fixed, method varied) — jackknife of the core r and the forward
   slope, Spearman rank check, saturation-artefact count across thresholds, study-level mean under
   three weightings.
2. **S3 — [Al^IV] measurement-uncertainty sensitivity** — seeded Monte-Carlo errors-in-variables
   propagation of the ±1 pp precision Varon 2025 reports on the ²⁷Al tetrahedral fraction. Result
   essentially unchanged (r ≈ +0.94, slope ≈ 2800, P(r>0.8)=100%); regression dilution negligible.

## Deliverables

1. **Manuscript + DOCX** — `manuscript/manuscript-submission.docx` (local, withheld; now carries §3.7 + S3)
2. **Zenodo + zip** — software (v1.3.0 submitted, v1.4.0 latest above); release zips on the GitHub releases and Zenodo archives
3. **Public Colab (tag-pinned to the submitted version)** —
   https://colab.research.google.com/github/mulhamfetna/geomind-radionuclide-adsorption/blob/v1.3.0/notebooks/geomind_virtual_lab.ipynb
   (v1.4.0 notebook, with the robustness tab: swap `v1.3.0` → `v1.4.0` in the URL)
4. **Figures** — `manuscript/GEOMIND-R-figures-submission.zip` (600 dpi + PDF + EPS)
5. **Excel bibliography** — `manuscript/GEOMIND-R-bibliography.xlsx` (local)
6. **Vancouver DOCX bibliography** — `manuscript/GEOMIND-R-bibliography.docx` (local)
7. **Database DOI** — dataset record 10.5281/zenodo.21540569

## Regenerate any deliverable
```
python manuscript/export_figures.py        # figures
python manuscript/build_bibliography.py    # bibliography .xlsx + .docx
python -m geomind.database_export          # complete categorised database
python -m geomind.dataset_deposit          # dataset bundle for a future Zenodo version
python -m notebook_lab.bundle              # refresh the Colab bundle from the live pipeline
python -m notebook_lab.build_notebook      # rebuild notebooks/geomind_virtual_lab.ipynb
# DOCX: --resource-path=manuscript embeds the figures (701 KB output, no missing-image warnings)
pandoc manuscript/manuscript-submission.md -o manuscript/manuscript-submission.docx --standalone --resource-path=manuscript
```

State: Pool A 141 · Pool B 73 · findings 46 · **211 tests passing** · CI green.
