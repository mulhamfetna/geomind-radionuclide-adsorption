# Submission package — COMPLETE (2026-07-25)

All seven deliverables are done; both Zenodo records are published and cross-linked.

## The records

| Record | DOI (concept — cite this) | This version (1.3.0) | Licence |
|---|---|---|---|
| **Software** (code, Virtual Lab, history) | 10.5281/zenodo.21510123 | 10.5281/zenodo.21546029 | AGPL-3.0 |
| **Dataset** (audited database) | 10.5281/zenodo.21540569 | 10.5281/zenodo.21540570 | CC BY 4.0 |

Cross-linked both ways (`isSupplementTo` / `isSupplementedBy`). Manuscript Data Availability cites
the dataset DOI as the data of record.

## Deliverables

1. **Manuscript + DOCX** — `manuscript/manuscript-submission.docx` (local, withheld)
2. **Zenodo + zip** — software v1.3.0 above; release zip on the GitHub release and the Zenodo archive
3. **Public Colab (tag-pinned)** —
   https://colab.research.google.com/github/mulhamfetna/geomind-radionuclide-adsorption/blob/v1.3.0/notebooks/geomind_virtual_lab.ipynb
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
pandoc manuscript/manuscript-submission.md -o manuscript/manuscript-submission.docx --standalone
```

State: Pool A 141 · Pool B 73 · findings 46 · 207 tests passing · CI green.
