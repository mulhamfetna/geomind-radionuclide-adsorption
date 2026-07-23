# NOTICE — Copyright, licensing and third-party materials

© 2026 **Mulham Fetna** ([ORCID 0009-0006-4432-798X](https://orcid.org/0009-0006-4432-798X))
and **Dr. Abdulrazzaq Hammal** ([ORCID 0000-0003-1828-1376](https://orcid.org/0000-0003-1828-1376)),
University of Aleppo, Aleppo, Syria.

**Contact** — Mulham Fetna: mulham.fetna@alepuniv.edu.sy · contact@mulhamfetna.com ·
Molhamfetneh@gmail.com | Abdulrazzaq Hammal: ab.hammal@alepuniv.edu.sy · hammal1986@gmail.com

## License — two licenses, split by content type

| Content | License | Paths |
|---|---|---|
| **Software** | **AGPL-3.0-or-later** ([`LICENSE`](LICENSE)) | `src/`, `app/`, `tests/`, `notebook_lab/*.py`, `manuscript/figures.py`, `notebooks/*.ipynb` |
| **Data, figures & documentation** | **CC BY 4.0** ([`LICENSE-DATA`](LICENSE-DATA)) | `data/`, `knowledge_base/`, `notebook_lab/lab_bundle.json`, `manuscript/figures/`, `docs/`, `reports/`, `papers/MANIFEST.md`, and the Markdown documentation |

**Both licenses require attribution.** If you use the database, the figures or any derived numbers,
**you must credit us** — cite the DOI in [`CITATION.cff`](CITATION.cff). If you modify the software
and run it as a network service, the AGPL additionally requires you to offer users the
corresponding source.

*Why the split:* AGPL is a software license and maps poorly onto a CSV — "corresponding source" has
no clear meaning for data. **CC BY 4.0** is the standard for research data: it keeps attribution
legally binding while remaining compatible with journal data-availability policies and with reuse
by other laboratories. Nothing is given away — credit is still a condition of use.

If you use this work in research, please cite it — see [`CITATION.cff`](CITATION.cff) and the
*Citation & DOI* section of the [README](README.md).

## What is *not* covered

- **The source publications.** The papers analysed in this project are the copyrighted works of
  their respective publishers and authors. They are **not redistributed here** — they are excluded
  from version control and catalogued in [`papers/MANIFEST.md`](papers/MANIFEST.md) with source
  identifiers so any reader can obtain each one legitimately from its publisher.
- **The primary reference work.** *GEOMIND* (RSC Digital Discovery, DOI
  [10.1039/d5dd00383k](https://doi.org/10.1039/d5dd00383k)) is licensed **CC-BY-NC 4.0** by its
  authors. Our use is non-commercial research with attribution, consistent with those terms.
- **Third-party datasets.** The Oulu alkali-activated-materials dataset (DOI
  [10.1016/j.matdes.2026.115471](https://doi.org/10.1016/j.matdes.2026.115471)) is **CC BY** and is
  used with attribution. Every ingested source is recorded with its provenance in
  `knowledge_base/registry.yaml` and in the audit trail.

**Facts and measurements extracted from published literature are not themselves copyrightable.**
What we publish here is our own compiled, audited and re-expressed database together with its
provenance record — not copies of the source articles.

## Manuscript

The manuscript reporting these results is **withheld pending journal submission and peer review**
and is deliberately not part of this repository. The data, code and analyses needed to reproduce
every number are here; the paper will be added in a later release once published.

## Prior, unrelated release

An earlier and **unrelated** tool was published from a previous repository under Apache-2.0 and
remains archived at Zenodo DOI
[10.5281/zenodo.21236404](https://doi.org/10.5281/zenodo.21236404). That release keeps its original
license; **it does not extend to, and is not continuous with, the work in this repository.**
