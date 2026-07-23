# Pooled adsorption database — summary

**Rows:** 121  ·  **Sources:** 10

## Composition of the pool

| adsorbate | class | capacity_type | n |
|---|---|---|---|
| Cs | radionuclide | freundlich_qmax | 1 |
| Cs | radionuclide | iec_meq_g | 10 |
| Cs | radionuclide | langmuir_qmax | 25 |
| Cs | radionuclide | single_point_q | 4 |
| Eu | other | langmuir_qmax | 3 |
| NH4+ | analogue | single_point_q | 21 |
| Sr | radionuclide | iec_meq_g | 2 |
| Sr | radionuclide | kd_mL_g | 7 |
| Sr | radionuclide | langmuir_qmax | 6 |
| methylene_blue | dye | single_point_q | 21 |
| rhodamine_6G | dye | single_point_q | 21 |

## ⚠️ Pooling warnings

- MIXED capacity_type {'single_point_q': 67, 'langmuir_qmax': 34, 'iec_meq_g': 12, 'kd_mL_g': 7, 'freundlich_qmax': 1} — Langmuir Qmax and single-point uptake are different quantities; filter or stratify before training.
- MIXED adsorbate_class {'radionuclide': 55, 'dye': 42, 'analogue': 21, 'other': 3} — radionuclides, analogues and dyes are not one target; pool only with an explicit, stated justification.
- MULTIPLE adsorbates ['Cs', 'Eu', 'NH4+', 'Sr', 'methylene_blue', 'rhodamine_6G'] — capacity is species-specific.

## Validation issues

| issue | count | detail |
|---|---|---|
| out_of_range_capacity_mg_g | 1 | outside [0.0, 1000.0] |

## Usable for the radionuclide target

- **True radionuclide rows (Cs/Sr):** 55
- **Analogue rows (NH4+ etc.):** 21 — usable only as a clearly-labelled proxy
- **Dye rows:** 45 — structural signal only, not a Cs/Sr target
