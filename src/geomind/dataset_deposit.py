"""Assemble the standalone DATASET deposit — the database with its own citable identity.

    python -m geomind.dataset_deposit      # -> dist/GEOMIND-R-dataset/ and a .zip

The software (code + everything) is archived on Zenodo as one `software` record. Journals'
data-availability statements and data-citation indexes, however, expect a record typed
`dataset`, cited as "the data underlying this article". This module builds exactly that: a
self-describing bundle of the audited database, deposited on Zenodo as a separate `dataset`
record cross-linked to the software one, so the data can be cited on its own.

Rights are unaffected by the deposit: the data are CC BY 4.0, so attribution is legally
required wherever they are hosted. The dataset DOI adds *identification*, not rights.

Contents of the bundle:
  GEOMIND-R-complete-database.xlsx   the categorised database (20 sheets: pools, excluded
                                     rows, audit trail, registers, figure source data, meta)
  GEOMIND-R-source-data.xlsx         the exact values behind every figure panel
  pool_a_adsorption.csv              Pool A as a flat CSV, for machine reuse
  pool_b_immobilisation.csv          Pool B as a flat CSV
  DATA-DICTIONARY.md                 every column, its meaning and unit
  README.md                          what the dataset is, how it was audited, how to cite
  LICENSE                            CC BY 4.0
  CITATION.cff                       machine-readable citation
"""
from __future__ import annotations

import shutil
import sys
import zipfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))

OUT_DIR = _ROOT / "dist" / "GEOMIND-R-dataset"
CONCEPT_DOI = "10.5281/zenodo.21510123"        # the software record this dataset accompanies
DATASET_CONCEPT_DOI = "10.5281/zenodo.21540569"   # this dataset's own concept DOI (all versions)

#: Human-readable meaning + unit for every column that appears in the pools. Kept here (not
#: scraped from docstrings) so the dictionary is stable and reviewer-ready.
COLDESC: dict[str, tuple[str, str]] = {
    # identity
    "sample_id": ("Unique row id (source_label + sorbent + adsorbate)", "—"),
    "sorbent_name": ("Material name as given in the source", "—"),
    "matrix_name": ("Wasteform/matrix name as given in the source", "—"),
    "sorbent_class": ("Structural class of the sorbent", "categorical"),
    "matrix_class": ("Binder family of the wasteform", "categorical"),
    "framework_code": ("Zeolite framework type code where applicable", "—"),
    # species
    "adsorbate": ("Cation removed from solution (Cs, Sr, NH4+, …)", "—"),
    "adsorbate_class": ("radionuclide / analogue / dye — never pooled", "categorical"),
    "nuclide": ("Immobilised radionuclide (Cs or Sr)", "—"),
    "loading_wt_pct": ("Waste loading — a CONTROL variable set by the experimenter, never a target",
                       "wt%"),
    # adsorption target
    "capacity_mg_g": ("Adsorption capacity (higher is better)", "mg g-1"),
    "capacity_type": ("How the capacity was obtained (langmuir_qmax, iec, …)", "categorical"),
    "capacity_std": ("Reported standard deviation of the capacity", "mg g-1"),
    "kd_mL_g": ("Distribution coefficient — a DIFFERENT quantity from capacity", "mL g-1"),
    "selectivity_factor": ("Reported selectivity factor", "—"),
    # immobilisation target
    "retention_value": ("Retention target — see retention_type for direction of merit", "varies"),
    "retention_type": ("leachability_index / de_cm2_s / clf / leached_pct — not interconvertible",
                       "categorical"),
    "retention_std": ("Reported standard deviation of the retention value", "varies"),
    "censored": ("Left-censored flag: true value is below the detection bound", "categorical"),
    "censoring_bound": ("Detection bound for a left-censored row", "varies"),
    # conditions
    "initial_conc_mg_L": ("Initial adsorbate concentration C0", "mg L-1"),
    "dose_g_L": ("Solid/liquid dose", "g L-1"),
    "temperature_K": ("Temperature", "K"),
    "ph": ("Solution pH", "—"),
    "contact_time_h": ("Contact time", "h"),
    "competing_ion": ("Competing background ion, if any", "—"),
    "competing_ion_mg_L": ("Competing-ion concentration", "mg L-1"),
    "leachant": ("Leaching medium", "—"),
    "duration_days": ("Leach-test duration", "days"),
    "ph_leachant": ("Leachant pH", "—"),
    "interval_label": ("Leach interval label, where reported", "—"),
    # composition
    "si_al": ("Si/Al molar ratio (bulk)", "mol/mol"),
    "si_al_nmr": ("Si/Al from 29Si NMR deconvolution", "mol/mol"),
    "ca_si_al": ("Ca/(Si+Al) molar ratio — the Ca-content descriptor for Ca-bearing systems",
                 "mol/mol"),
    "na_al": ("Na/Al molar ratio", "mol/mol"),
    "k_al": ("K/Al molar ratio", "mol/mol"),
    "ca_al": ("Ca/Al molar ratio", "mol/mol"),
    "precursor": ("Aluminosilicate precursor", "—"),
    "activator": ("Alkali activator", "—"),
    "activator_molarity": ("Activator molarity", "mol L-1"),
    # structure — the descriptor
    "bet_m2_g": ("BET specific surface area", "m2 g-1"),
    "pore_volume_cm3_g": ("Pore volume", "cm3 g-1"),
    "cec_meq_100g": ("Cation exchange capacity", "meq/100g"),
    "al_content_mol_kg": ("Total Al content", "mol kg-1"),
    "al_iv_pct": ("Fraction of Al in tetrahedral (IV) coordination", "%"),
    "al_iv_mmol_g": ("Framework Al-IV concentration — THE descriptor of this study", "mmol g-1"),
    "ari": ("Al-richness index = sum(m x I_m)/100 from the Q4(mAl) deconvolution", "Al per Si"),
    "q4_4al_pct": ("Q4(4Al) 29Si population", "%"),
    "q4_3al_pct": ("Q4(3Al) 29Si population", "%"),
    "q4_2al_pct": ("Q4(2Al) 29Si population", "%"),
    "q4_1al_pct": ("Q4(1Al) 29Si population", "%"),
    "q4_0al_pct": ("Q4(0Al) 29Si population", "%"),
    "cn_sr_exafs": ("Sr coordination number from EXAFS", "—"),
    "chemical_shift_ppm": ("Reported NMR chemical shift", "ppm"),
    "porosity_pct": ("Porosity", "%"),
    "capillary_pore_volume_mL_g": ("Capillary pore volume", "mL g-1"),
    "critical_pore_diameter_nm": ("Critical pore diameter", "nm"),
    # isotherm
    "langmuir_b_L_mg": ("Langmuir affinity constant b (drives the saturation screen)", "L mg-1"),
    "freundlich_kf": ("Freundlich Kf", "—"),
    "freundlich_n": ("Freundlich n", "—"),
    "dr_e_kj_mol": ("Dubinin-Radushkevich mean free energy", "kJ mol-1"),
    "r2": ("Reported isotherm goodness of fit", "—"),
    # provenance
    "provenance_doi": ("DOI of the source publication", "—"),
    "source_label": ("Short source key (links to the manifest and finding register)", "—"),
    "leach_state": ("Preparation state (pre/post-leach/n/a)", "—"),
    "replicated": ("Row confirmed against a second reading of the source", "boolean"),
    "from_figure": ("Value read from a figure rather than a table", "boolean"),
    "value_repeated": ("A deliberate replicate composition", "boolean"),
}


def _write_pools() -> None:
    from geomind.data.merge_adsorption import build as build_A
    from geomind.data.merge_immobilisation import build as build_B
    build_A().to_csv(OUT_DIR / "pool_a_adsorption.csv", index=False)
    build_B().to_csv(OUT_DIR / "pool_b_immobilisation.csv", index=False)


def _data_dictionary() -> str:
    from geomind.data.merge_adsorption import build as build_A
    from geomind.data.merge_immobilisation import build as build_B
    a, b = build_A(), build_B()
    L = ["# GEOMIND-R database — data dictionary", "",
         "Two pools, audited separately and **never merged** (they measure opposite-signed "
         "targets). Every column below carries its meaning and unit. Booleans and categoricals "
         "are marked as such.", ""]
    for name, df, note in (
        ("Pool A — adsorption (`pool_a_adsorption.csv`)", a,
         "Removal of a cation from solution. Target: `capacity_mg_g` or `kd_mL_g` — **higher is "
         "better**."),
        ("Pool B — immobilisation (`pool_b_immobilisation.csv`)", b,
         "Retention of a doped-in nuclide under leaching. Target direction depends on "
         "`retention_type` (a high leachability index is good; a high diffusivity or % leached is "
         "bad).")):
        L += [f"## {name}", "", note, "",
              f"*{len(df)} rows · {df['source_label'].nunique()} sources.*", "",
              "| Column | Meaning | Unit |", "|---|---|---|"]
        for c in df.columns:
            meaning, unit = COLDESC.get(c, ("", ""))
            L.append(f"| `{c}` | {meaning} | {unit} |")
        L.append("")
    L += ["## Provenance and audit", "",
          "Every row traces to a source publication by `provenance_doi` / `source_label`; the "
          "source publications are catalogued (with checksums) in the software record's manifest "
          "and are not redistributed. The complete workbook "
          "(`GEOMIND-R-complete-database.xlsx`) additionally contains the rows the audit "
          "**excluded** and why, the per-table veracity trail, and the finding register.", ""]
    return "\n".join(L)


def _readme() -> str:
    from geomind.data.merge_adsorption import build as build_A
    from geomind.data.merge_immobilisation import build as build_B
    na, nb = len(build_A()), len(build_B())
    return f"""# GEOMIND-R — audited database of Cs/Sr uptake and immobilisation in geopolymers

An audited, provenance-tracked meta-analysis database of caesium and strontium uptake and
immobilisation in geopolymers and alkali-activated materials, compiled and source-audited from
the published literature.

This deposit is the **dataset of record**. The analysis code, the interactive Virtual Lab and
the full reasoning history are archived separately as the software record
(https://doi.org/{CONCEPT_DOI}); this dataset and that software cross-reference each other.

## What is here

| File | Contents |
|---|---|
| `GEOMIND-R-complete-database.xlsx` | The categorised database — 20 sheets: both pools, the audit-excluded rows with reasons, the 91-table veracity trail, the finding/decision/source registers, the exact values behind every figure, and the study-level meta-analysis. |
| `GEOMIND-R-source-data.xlsx` | One sheet per figure panel — the exact plotted values. |
| `pool_a_adsorption.csv` | Pool A ({na} rows): adsorption (removal from solution). |
| `pool_b_immobilisation.csv` | Pool B ({nb} rows): immobilisation (retention under leaching). |
| `DATA-DICTIONARY.md` | Every column, its meaning and unit. |
| `LICENSE` | CC BY 4.0. |
| `CITATION.cff` | Machine-readable citation. |

## Two pools, never merged

Pool A measures how much cation a material removes from solution (higher is better); Pool B
measures how well a material retains a nuclide under leaching (direction depends on the metric).
They answer different questions with opposite-signed targets and are kept strictly separate.

## Provenance and integrity

Every value was checked against its primary published source before inclusion; roughly a third of
candidate rows failed that audit and are recorded — with the reason — in the complete workbook
rather than silently dropped. Source publications are catalogued with checksums but not
redistributed (publisher copyright).

## Licence and citation

Licensed **CC BY 4.0** — reuse freely **with attribution**. If you use this database or any value
derived from it, please cite:

> Fetna, M. & Hammal, A. GEOMIND-R: audited database of caesium and strontium uptake and
> immobilisation in geopolymers. Zenodo. https://doi.org/{DATASET_CONCEPT_DOI}

The companion software record is at https://doi.org/{CONCEPT_DOI}.
"""


def _citation_cff() -> str:
    return f"""cff-version: 1.2.0
message: "If you use this dataset, please cite it as below."
title: "GEOMIND-R: audited database of caesium and strontium uptake and immobilisation in geopolymers"
abstract: >-
  An audited, provenance-tracked meta-analysis database of caesium and strontium uptake
  (adsorption) and immobilisation (leaching) in geopolymers and alkali-activated materials,
  compiled and source-audited from the published literature. Two pools, kept separate; every
  value traced to its primary source; excluded rows and the audit trail included.
type: dataset
authors:
  - family-names: Fetna
    given-names: Mulham
    orcid: "https://orcid.org/0009-0006-4432-798X"
    affiliation: "Department of Mechatronics Engineering, Faculty of Electrical and Electronic Engineering, University of Aleppo, Aleppo, Syria"
  - family-names: Hammal
    given-names: Abdulrazzaq
    orcid: "https://orcid.org/0000-0003-1828-1376"
    affiliation: "Department of Basic Science - Chemistry, Faculty of Electrical Engineering, University of Aleppo, Aleppo, Syria"
license: CC-BY-4.0
keywords:
  - geopolymer
  - caesium-137
  - strontium-90
  - adsorption
  - immobilisation
  - radionuclide
  - meta-analysis
  - nuclear waste
doi: "{DATASET_CONCEPT_DOI}"
related-identifiers:
  - type: doi
    value: "{CONCEPT_DOI}"
    relation: isSupplementTo
"""


def build() -> str:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True)

    # regenerate the two workbooks fresh, then copy them in
    from geomind import database_export, source_data
    database_export.write(OUT_DIR / "GEOMIND-R-complete-database.xlsx")
    source_data.write_xlsx(OUT_DIR / "GEOMIND-R-source-data.xlsx")
    _write_pools()

    (OUT_DIR / "DATA-DICTIONARY.md").write_text(_data_dictionary())
    (OUT_DIR / "README.md").write_text(_readme())
    (OUT_DIR / "CITATION.cff").write_text(_citation_cff())
    shutil.copy(_ROOT / "LICENSE-DATA", OUT_DIR / "LICENSE")

    archive = _ROOT / "dist" / "GEOMIND-R-dataset.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(OUT_DIR.iterdir()):
            z.write(f, arcname=f"GEOMIND-R-dataset/{f.name}")
    return str(archive)


def main() -> None:  # pragma: no cover
    a = build()
    n = len(list(OUT_DIR.iterdir()))
    print(f"wrote {a} ({n} files)")


if __name__ == "__main__":  # pragma: no cover
    main()
