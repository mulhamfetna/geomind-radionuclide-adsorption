# GEOMIND-R — Framework Aluminium Governs Radionuclide Uptake in Geopolymers

[![Code: AGPL v3](https://img.shields.io/badge/code-AGPL--3.0-blue.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)
[![DOI](https://zenodo.org/badge/1309918660.svg)](https://zenodo.org/badge/latestdoi/1309918660)
[![Tests](https://img.shields.io/badge/tests-181%20passing-brightgreen.svg)](tests/)

An **audited, provenance-tracked meta-analysis database** of caesium and strontium uptake and
immobilisation in geopolymers and alkali-activated materials — with the analysis pipeline, a
validated forward model, and an interactive lab to explore it.

**Mulham Fetna** (lead author) · Dept. of Mechatronics Engineering, Faculty of Electrical and
Electronic Engineering, University of Aleppo — [ORCID 0009-0006-4432-798X](https://orcid.org/0009-0006-4432-798X)
**Dr. Abdulrazzaq Hammal** (supervisor) · Dept. of Basic Science – Chemistry, Faculty of Electrical
Engineering, University of Aleppo — [ORCID 0000-0003-1828-1376](https://orcid.org/0000-0003-1828-1376)
📬 Contact details: [Authors & contact](#authors--contact)

---

## What this work establishes

1. **Framework aluminium — not surface area — governs cation uptake.** Tetrahedral Al<sup>IV</sup>
   carries the charge-balancing exchange sites that actually bind Cs⁺/Sr²⁺. Established on three
   independent levels: **correlation** (r up to +0.95), a **within-sample causal test** (leaching
   removes Al<sup>IV</sup> and uptake falls with it, r = +0.94), and **published atomic-scale
   spectroscopy** placing Sr at Al<sup>IV</sup> sites. Specific surface area is *negatively*
   related to uptake in the same data.

2. **A forward model that predicts held-out samples.** Within one structural class and protocol,
   K_D = 2812·[Al<sup>IV</sup>] − 9258 mL/g, **leave-one-out R² = 0.81** — behind an explicit
   domain guard that refuses to pretend it generalises.

3. **The descriptor does not survive cross-laboratory pooling.** Pooled across labs, leave-one-out
   R² falls **below zero** — worse than predicting the mean. Adding more literature makes it worse,
   not better. This is a general caution for materials-informatics meta-analysis.

4. **A structural precondition.** The relationship holds in framework gels and degrades when
   Ca-bearing (C-A-S-H) gels are pooled in — descriptors are class-specific.

5. **Reusable screening methods.** A Langmuir **saturation screen** (θ = 1 − R_L) that flags
   reported capacities which are extrapolation artefacts, and a **two-pool audit framework** that
   keeps adsorption and immobilisation data separate.

> 🧪 **Try it:** the [Virtual Lab](#virtual-lab) — a local app or a one-file Colab notebook — lets
> you explore compositions and see every prediction with its confidence flag and its reasoning.

## Honest limitations — read these

- **This is a literature-scale meta-analysis, not new laboratory measurement.** Every row is
  extracted from published work and traced to its source; none of it is our own bench data.
- **The forward model is validated only within one structural class and protocol**
  (metakaolin geopolymers, Sr, [Al<sup>IV</sup>] 3.45–4.77 mmol g⁻¹). Outside that envelope it is
  extrapolation, and the tooling says so rather than hiding it.
- **The original goal — a generative inverse-design model — was not reached.** We determined
  empirically that it cannot be built from the published literature (see the pooling result above),
  and reported that finding instead of shipping a model that would have learned inter-laboratory
  noise. The full account is in [`reports/plan-vs-achieved.md`](reports/plan-vs-achieved.md).
- **The manuscript is withheld** pending journal submission and peer review. Everything needed to
  reproduce the numbers is here.

**Reference work this project set out to replicate:**
Rousseau, S.; Bouzid, A.; Rossignol, S.; Gharzouni, A. *GEOMIND: a hybrid generative artificial
intelligence model for geopolymer design and optimization.* RSC **Digital Discovery** (2026).
DOI: [10.1039/d5dd00383k](https://doi.org/10.1039/d5dd00383k) · CC-BY-NC 4.0 — cited, not
redistributed.

---

## ⚠️ Data provenance — read before citing any result

The compiled dataset in `data/raw/` is **literature-derived**, *not* newly measured laboratory
data. It was assembled by extracting published formulations and properties from the corpus in
`papers/references/`.

**This means our claims must be framed as a literature-scale meta-analysis and external
validation — never as independent experimental replication.** The paper releases only **10**
samples publicly; our compilation reaches **867** rows across a broader precursor space, which is
the basis of our contribution. Every row must carry a `provenance` field tracing it to an entry in
[`papers/MANIFEST.md`](papers/MANIFEST.md).

### Known feature-space gap — and why M3b was re-scoped

The paper's formulation space and our compiled dataset are **not** compatible:

| | GEOMIND paper | our compiled dataset |
|---|---|---|
| Material system | metakaolin geopolymer **pastes** | fly-ash / slag **concrete** with aggregates |
| Precursors | M1–M5 metakaolins, S1/S3/SNa/S3′ silicate solutions, KOH/NaOH | FlyAsh, GGBFS, Na₂SiO₃, CopperSlag, RecycledAgg |
| Targets | mixture density, **viscosity**, material density, compressive strength | compressive strength only |
| Size | 112 samples (10 public) | 849 rows, but only **92 distinct mix designs** |

M2 profiling ([report](reports/m2-data-quality-report.md)) established three decisive facts:

1. **`Metakaolin` was constant zero** — the paper's primary precursor is entirely absent.
2. **`Si_Al` and `Density` were transplanted from the paper's 10 published samples** (9 of 11 Si/Al
   values match exactly to 3 dp; broadcast one-per-mix; absent from both source files). Both
   columns have been **dropped** — using them would learn an artefact of the join.
3. **No viscosity** exists in our data, so the paper's four-target space cannot be reproduced.

**Therefore M3b makes no claim to validate GEOMIND.** It is re-scoped as a *cross-system transfer
study*: can the GEOMIND architecture be usefully applied to a different alkali-activated material
system? That is a legitimate and interesting question; "we reproduced the paper on our own data"
would not have been an honest description of it.

A faithful validation requires the authors' confidential 112-sample dataset (requested).

---

## Repository layout

```
papers/
  main/          GEOMIND paper + supplementary      (PDFs not committed)
  references/    16 supporting publications          (PDFs not committed)
  MANIFEST.md    checksummed index of the corpus     ← committed
data/
  raw/           compiled research database          ← committed
  processed/     model-ready datasets                ← committed (needed to reproduce)
  source-data/   values behind every figure (.xlsx)  ← committed
  warehouse/     audit_summary.csv (veracity trail)  ← committed (31 MB DB is not)
  interim/       cleaning intermediates              (regenerable)
docs/
  paper-analysis/  reproduction specification of GEOMIND
src/geomind/     implementation
app/             Virtual Lab — local Gradio app + tested engine service layer
notebook_lab/    self-contained notebook mirror (exporter + engine_lite + builder)
notebooks/       exploration + geomind_virtual_lab.ipynb (shareable Colab lab)
reports/         results, figures, milestone write-ups
```

Third-party PDFs are deliberately **excluded from version control** (copyright + size); the
manifest makes the corpus reproducible without redistributing it.

---

## Virtual Lab

An interactive, domain-flagged lab over the project's outcomes — Sr K_D prediction, screening
checks, the teaching sandboxes, and the reproducibility console. It is a **glass box, not an
oracle**: every prediction carries its confidence flag (🟢 validated / 🟡 exploratory /
🔴 unsupported), its reason, and its source.

- **Desktop (local):** `PYTHONPATH=src python -m app.lab` → opens `http://127.0.0.1:7860`.
- **Shareable notebook:** `notebooks/geomind_virtual_lab.ipynb` — one self-contained file. Upload
  to Colab, **Runtime ▸ Run all**; the app renders inside the session (no public tunnel, no repo
  access needed).

**Refreshing the notebook** — the `.ipynb` carries a *frozen snapshot* of the compiled data. If the
pools, registry, or figures change, regenerate the bundle and rebuild the notebook:

```bash
PYTHONPATH=src python -m notebook_lab.bundle          # re-export lab_bundle.json from the live pipeline
PYTHONPATH=src python -m notebook_lab.build_notebook  # rebuild notebooks/geomind_virtual_lab.ipynb
```

`tests/test_notebook_mirror.py` fails loudly if the notebook engine ever diverges from the desktop
`app.engine`, so a stale or inconsistent mirror cannot ship silently.

---

## Roadmap (milestones)

| # | Milestone | Outcome |
|---|-----------|---------|
| **M1** | Deep analysis of the GEOMIND paper | A reproduction spec: architecture, features, targets, training protocol, metrics, and every result to reproduce |
| **M2** | Data cleaning, linkage & provenance | De-duplicated, encoding-fixed, schema-harmonised dataset + data dictionary + quality report |
| **M3a** | **Faithful replication** | GEOMIND reproduced on the paper's own 10 + 45 samples — proves the implementation is correct |
| **M3b** | **Cross-system transfer** *(re-scoped)* | The GEOMIND architecture applied to a **different material system** (fly-ash/slag concrete). Explicitly **not** a validation of GEOMIND — see below |
| **M4** | Fourth design dimension | Add **adsorption capacity** (Qmax) as a generative target |
| **M5** | Radionuclide application | Formulation design for Cs-137 / Sr-90 immobilisation |
| **M6** | Corpus expansion *(continuous)* | Literature/data mining to grow the 28-row adsorption set |

Each milestone is cut as a **release** and deposited to Zenodo as a **restricted-access record**,
yielding a timestamped DOI that establishes priority while keeping contents confidential.

## Engineering workflow

- `main` — protected, release-only. `dev` — integration. `feature/*` — one per unit of work.
- Work is tracked as GitHub **Issues** grouped under **Epics** and **Milestones**.
- Nothing merges to `main` except via `dev` at a milestone boundary.

## Environment

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

---

## Authors & contact

**Mulham Fetna** — lead author and investigator
Department of Mechatronics Engineering, Faculty of Electrical and Electronic Engineering,
University of Aleppo, Aleppo, Syria
ORCID [0009-0006-4432-798X](https://orcid.org/0009-0006-4432-798X)
✉ [mulham.fetna@alepuniv.edu.sy](mailto:mulham.fetna@alepuniv.edu.sy) ·
[contact@mulhamfetna.com](mailto:contact@mulhamfetna.com) ·
[Molhamfetneh@gmail.com](mailto:Molhamfetneh@gmail.com)

**Dr. Abdulrazzaq Hammal** — supervisor
Department of Basic Science – Chemistry, Faculty of Electrical Engineering,
University of Aleppo, Aleppo, Syria
ORCID [0000-0003-1828-1376](https://orcid.org/0000-0003-1828-1376)
✉ [ab.hammal@alepuniv.edu.sy](mailto:ab.hammal@alepuniv.edu.sy) ·
[hammal1986@gmail.com](mailto:hammal1986@gmail.com)

Correspondence about this repository, the dataset, or reuse requests is welcome at any of the
addresses above.

---

## Citation & DOI

If you use this software or dataset in your research, please cite it. Machine-readable metadata is
in [`CITATION.cff`](CITATION.cff) — GitHub renders a **"Cite this repository"** button from it.

- **Concept DOI — cite this one** (always resolves to the latest version):
  [`10.5281/zenodo.21510123`](https://doi.org/10.5281/zenodo.21510123)
- **This version (1.1.0):** [`10.5281/zenodo.21511375`](https://doi.org/10.5281/zenodo.21511375)

**BibTeX**

```bibtex
@software{fetna_hammal_geomind_r_2026,
  author  = {Fetna, Mulham and Hammal, Abdulrazzaq},
  title   = {{GEOMIND-R: An Audited Database, Structural Descriptor and
             Forward Model for Radionuclide Uptake in Geopolymers}},
  year    = {2026},
  version = {1.1.0},
  doi     = {10.5281/zenodo.21510123},
  url     = {https://doi.org/10.5281/zenodo.21510123}
}
```

## License

Two licenses, split by content type — **both require attribution**:

| Content | License |
|---|---|
| Software (`src/`, `app/`, `tests/`, `notebook_lab/*.py`, notebooks) | **AGPL-3.0-or-later** — [`LICENSE`](LICENSE) |
| Data, figures & documentation (`data/`, `knowledge_base/`, `reports/`, `docs/`, `manuscript/figures/`) | **CC BY 4.0** — [`LICENSE-DATA`](LICENSE-DATA) |

If you use the database, the figures or any derived number, **you must cite us** (see above). The
source publications analysed here remain the copyright of their publishers and are **not**
redistributed; see [`NOTICE.md`](NOTICE.md) for third-party materials and attribution.

---

© 2026 Mulham Fetna and Abdulrazzaq Hammal. Licensed under AGPL-3.0-or-later. See
[`NOTICE.md`](NOTICE.md).
