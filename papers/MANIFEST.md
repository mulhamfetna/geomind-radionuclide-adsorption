# Literature Corpus — Manifest

> **Files are NOT committed.** These are copyrighted publications held as personal
> research copies (see `.gitignore`). This manifest makes the corpus *reproducible and
> auditable* — retrieve each item from its source, then verify the SHA-256 prefix.

_Manifest header last updated: 2026-07-23. Rows 1–19 authored 2026-07-19; rows 20–24 are batch-6 (2026-07-23). NOTE: the reference corpus on disk now holds more files than are tabulated here — full reconciliation is tracked as a separate task._

| # | Type | File | MB | SHA-256 (16) | Source DOI / URL |
|---|------|------|----|--------------|------------------|
| 1 | MAIN | `d5dd00383k (1).pdf` | 1.96 | `4b2bfc684215b68c` | 10.1039/d5dd00383k |
| 2 | MAIN | `d5dd00383k1_suppl.pdf` | 0.54 | `5f53769f5bcb2e45` | 10.1039/d5dd00383k |
| 3 | REF | `1091789.pdf` | 13.82 | `7fef2bf5e4e21075` | _TBD_ |
| 4 | REF | `Adsorption and enrichment of simulated 137Cs in geopolymer foams.pdf` | 14.14 | `fa2034ac0076685d` | _TBD_ |
| 5 | REF | `Adsorption behaviour of simulant radionuclide cations and anions in.pdf` | 2.33 | `b2ac1df2e6ca8555` | _TBD_ |
| 6 | REF | `AdsorptionDesorption Performances of Simulated Radioactive Nuclide Cs⁺ on the Zeolite-Rich Geopolymer from the Hydrothermal Synthesis of Fly Ash.pdf` | 7.76 | `02db0fc7e88cbb54` | _TBD_ |
| 7 | REF | `Application of fly ash-based geopolymer for removal of cesium strontium and arsenate from.pdf` | 0.49 | `cd2bf11328dc10ab` | _TBD_ |
| 8 | REF | `Application of fly ash-based materials for stabilization solidification of cesium and strontium.pdf` | 1.93 | `b0332b2b68a1f4d0` | _TBD_ |
| 9 | REF | `Facile fabrication of metakaolin slag-based zeolite microspheres MSZMs geopolymer for the efficient remediation of Cs+ and Sr2+.pdf` | 15.96 | `cb23e1df428d52b6` | _TBD_ |
| 10 | REF | `High-Performance Geopolymer-Based Granulated Adsorbents for Selective Sorption of Radioactive Cesium and Strontium..pdf` | 2.1 | `370f91b853c5b0e1` | _TBD_ |
| 11 | REF | `High-Performance Geopolymer-Based Granulated Adsorbents.pdf` | 2.1 | `370f91b853c5b0e1` | _TBD_ |
| 12 | REF | `Hossain-2026-composition-properties-adsorption-AAM.pdf` | 8.89 | `7a4dd1d51cd21b20` | 10.1016/j.matdes.2026.115471 |
| 13 | REF | `Magnetic ternary nanocomposite from ultra‑purified metakaolin.pdf` | 2.75 | `1525ab6dc612c3f2` | _TBD_ |
| 14 | REF | `Physical barrier effect of geopolymeric waste form on diffusivity of cesium and strontium.pdf` | 0.59 | `4c7b5a3b23578524` | _TBD_ |
| 15 | REF | `el-naggar2018.pdf` | 3.75 | `2b258326bbc339f9` | _TBD_ |
| 16 | REF | `gcdzxb-33-2-700.pdf` | 2.75 | `f2867c4e5f80735d` | _TBD_ |
| 17 | REF | `wst2019209supp.docx` | 1.73 | `e470c47515b87639` | _TBD_ |
| 18 | REF | `ذري 1.pdf` | 6.14 | `0bc7f2e9bb1072ef` | _TBD_ |
| 19 | REF | `ذري 2.pdf` | 1.56 | `c28638407576f278` | _TBD_ |
| 20 | REF | `walkley2020.pdf` | 3.93 | `67b3bdcbc529eabe` | 10.1016/j.jhazmat.2019.121015 |
| 21 | REF | `blackford2007.pdf` | 0.94 | `a7e5f82e6bb8e940` | 10.1111/j.1551-2916.2007.01532.x |
| 22 | REF | `perera2004.pdf` | 0.28 | `82508fa15e3f19e0` | MRS Symp. Proc. 824, CC8.35 (2004) |
| 23 | REF | `822897.pdf` | 32.0 | `76a51564aefc1729` | ISBN 978-3-95806-559-8 (RWTH/FZJ, 2020) |
| 24 | REF | `Muracchioli_Mattia_1128630.pdf` | 3.74 | `ede9edd06f7f82a5` | MSc thesis, Univ. Padua (2019) |

## Associated datasets

| Dataset | Location | Size | Companion paper |
|---|---|---|---|
| Oulu AAM synthesis / characterisation / adsorption (820 files) | `data/external/aam-oulu-2026/` *(not committed)* | 115 MB | 10.1016/j.matdes.2026.115471 |

## Notes

- **MAIN** — the paper being replicated: *GEOMIND*, RSC **Digital Discovery** (2026),
  DOI [10.1039/d5dd00383k](https://doi.org/10.1039/d5dd00383k), CC-BY-NC 4.0.
- `Hossain-2026-...` (originally supplied as `اثبات ان الامتزاز مرتبط بالتركيب.pdf`,
  "proof that adsorption is related to composition") is the **companion paper** to the
  Oulu dataset and is the strongest direct evidence for this project's core hypothesis.
- `_TBD_` DOIs are filled in during M6. Every compiled data row must trace to an entry here.
- **Batch-6 (2026-07-23), rows 20–24:** five papers triaged and read inline. `walkley2020` and `822897` (Weigelt dissertation) are structural (NMR/XRD) — mechanism evidence, no data rows (see findings F38, F40). `blackford2007` and `perera2004` (ANSTO) report no primary quantitative uptake/leach data of their own. `Muracchioli_Mattia_1128630` is out of scope (heavy-metal adsorption, not Cs/Sr). None add pool rows; see F40.
