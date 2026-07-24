# RESUME HERE — submission package status

**Paused:** 2026-07-24 · Last commit `2d17fc7` · 203 tests passing · CI green
**Target:** D1 journal submission · **Next release will be v1.3.0**

---

## Where we stopped

Building the seven submission deliverables. **Four are done, three remain.** The release has
**deliberately not been cut** — everything below should be reviewed first, because a Zenodo DOI is
permanent.

## ✅ Done

| # | Deliverable | Where it is |
|---|---|---|
| 1 | **Manuscript, updated + DOCX** | `manuscript/manuscript-submission.docx` (684 KB, 5510 words) — *local only, withheld from the repo* |
| 4 | **Figures, high quality, individual files, zipped** | `manuscript/figures-submission/` (6 figures × PNG 600 dpi + PDF + EPS + README) and `manuscript/GEOMIND-R-figures-submission.zip` (1.5 MB) |
| 5 | **Excel bibliography** | `manuscript/GEOMIND-R-bibliography.xlsx` — 31 refs; title, DOI, authors, journal, abstract, Arabic translation, role in the study, licence |
| 6 | **Vancouver DOCX bibliography** | `manuscript/GEOMIND-R-bibliography.docx` |
| 7 | **Complete categorised database** | `data/database/GEOMIND-R-complete-database.xlsx` — 20 sheets, 521 rows, **nothing dropped** |

### What went into the manuscript (local file, not in the repo)

- Abstract now states **four** independent evidence levels (was three), adding the Ca/Sr
  competition test (r = +0.99), and reports the study-level result.
- **New §3.4 passage** — the designed slag series quantifying calcium competition.
- **New §3.6** — study-level meta-analysis: the k = 4 table, three negative controls, the
  rejection register, and the honest limits.
- **New Methods §2.8** — the meta-analysis method and its pre-fixed inclusion criteria.
- **Discussion** — the n = 7 ceiling as a structural result of the field, not a shortfall of effort.
- **Data availability** — real DOIs, real counts, licences, and the fact that source publications
  are catalogued with checksums rather than redistributed.

Word count 4238 → **5584**.

## ⏳ Remaining

| # | Deliverable | What is still needed |
|---|---|---|
| 2 | **Final Zenodo link + zip of the exact same version** | Cut **v1.3.0**, let Zenodo mint the version DOI, then hand over that DOI + the release zip |
| 3 | **Public Colab link for the exact same version** | The notebook is already built and current (`notebooks/geomind_virtual_lab.ipynb`, carries the new meta-analysis tab). Needs the public Colab URL form: `https://colab.research.google.com/github/mulhamfetna/geomind-radionuclide-adsorption/blob/v1.3.0/notebooks/geomind_virtual_lab.ipynb` — **pin it to the release tag**, not to `main`, so it matches the submitted version exactly |
| 7b | **The database DOI** | The database ships inside the v1.3.0 release, so the release DOI *is* the database DOI. Decide whether that is sufficient or a separate Zenodo record is wanted |

## ⚠️ Two decisions waiting for you

**1. Abstracts — 9 of 31, and why.** Abstracts are included **only** where the publisher supplies
them via Crossref, so every word is verbatim and attributable. Automated extraction from PDFs was
trialled and **rejected**: it produced a confirmed wrong-paper match (a slag/Portland-cement
abstract attached to a zeolite ion-exchange paper). Shipping that would breach the project's own
rule about unverified data.

*Options:* (a) ship as-is, with the remaining 22 carrying their DOI; (b) I read each of the 22 PDFs
inline and verify its abstract individually — slower, accurate, and the only sound way to reach
full coverage.

**2. The bibliography files are gitignored, on purpose.** They contain verbatim publisher
abstracts, which remain publisher copyright. They are working files for your submission, **not**
part of the public deposit. Say if you want that changed for the open-access subset.

## Regenerating anything

```bash
python manuscript/export_figures.py        # figures, 600 dpi + vector, + zip
python manuscript/build_bibliography.py    # bibliography .xlsx + .docx
python -m geomind.database_export          # complete categorised database
python -m geomind.source_data              # per-figure source data
pandoc manuscript/manuscript-submission.md -o manuscript/manuscript-submission.docx --standalone
```

## State at the pause

Pool A **141** · Pool B **73** · findings **46** · audit **91** · k = **4** (r̄ = +0.771,
p = 0.0625) · forward LOO-CV R² **0.811** · pooled R² **−0.092** · **203 tests passing** ·
concept DOI [10.5281/zenodo.21510123](https://doi.org/10.5281/zenodo.21510123) (currently
resolving to v1.2.0).
