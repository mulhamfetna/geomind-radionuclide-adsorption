"""Merge every adsorption source into the pooled meta-analysis database.

Add a new `_from_*` adapter per source as M6 mining brings sources in; the schema
and validation stay fixed, so new sources cannot quietly break the target definition.

Usage:  python -m src.geomind.data.merge_adsorption
Output: data/processed/adsorption_pooled.csv  +  reports/adsorption-pool-summary.md
"""
from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

from .adsorption_schema import (
    AdsorbateClass,
    CapacityType,
    SorbentClass,
    conform,
    mmol_g_to_mg_g,
    pooling_warning,
    validate,
)

warnings.filterwarnings("ignore")

OUT = Path("data/processed/adsorption_pooled.csv")
REPORT = Path("reports/adsorption-pool-summary.md")


def _from_literature_compilation() -> pd.DataFrame:
    """Our hand-compiled literature table (Functional_Data).

    Reports Langmuir Qmax in mg/g for Cs and Sr, one column each. Long-format
    it so each row is a single (sorbent, adsorbate) measurement.
    """
    src = Path("data/processed/adsorption.csv")
    if not src.exists():
        return pd.DataFrame()
    raw = pd.read_csv(src)

    # --- F7 audit corrections (each verified inline against the source PDF) ---
    # Rows that do NOT appear in their stated source, or are internal duplicates.
    QUARANTINE = {
        # El-Naggar 2018 reports ONLY MKBFS systems. "Na-MK" carries the values of
        # U-P MK100 from the magnetic-ternary paper (misattribution); "K-MK" is a
        # verbatim duplicate of K-MKBFS (fabricated distinct sorbent).
        ("Na-MK", "Cs"), ("K-MK", "Cs"),
        # Niu 2022 tabulates no capacities at all - only ion-exchange log K.
        ("MS-GP", "Cs"), ("SC-GP", "Cs"), ("MS-GP", "Sr"), ("SC-GP", "Sr"),
    }
    # Species mislabels: values are real but belong to a different element.
    RELABEL_SPECIES = {("MU-PMK80", "Sr"): "Eu"}   # actually Eu-152+154
    # Capacity-model mislabels.
    FREUNDLICH = {("M/SZMs", "Cs")}   # Lei 2021: Cs fitted by Freundlich, Sr by Langmuir

    # F15: isotherm C0max recovered from each source's methods, so the saturation
    # screen (theta = K*C0/(1+K*C0)) can actually run. Absent entries stay unscreenable.
    C0_MAX = {
        # El-Naggar 2018: "10 mL of the desired dilutions of radioactive stock
        # solution (10^2-10^3 mg/L)", 0.1 g sorbent -> dose 10 g/L
        "El-Naggar_2018": (1000.0, 10.0),
        # Lei 2021 methods: "Initial concentration ... of 10-170 mg/L"
        "Lei_2021": (170.0, None),
        # Zheng 2023: 0.2 g in 50 mL CsCl, C0 = 50-800 mg/L -> dose 4 g/L
        "Zheng_2023": (800.0, 4.0),
        # Magnetic ternary (Hamed 2025): C0 200-1000 mg/L
        "Hamed_2025": (1000.0, None),
    }

    rows = []
    for _, r in raw.iterrows():
        for col, species in (("Qmax_Cs_mg_g", "Cs"), ("Qmax_Sr_mg_g", "Sr")):
            val = pd.to_numeric(r.get(col), errors="coerce")
            if pd.isna(val):
                continue
            sorbent = str(r.get("Sorbent_Type"))
            key = (sorbent, species)
            if key in QUARANTINE:
                continue                      # F7: not present in the stated source
            actual = RELABEL_SPECIES.get(key, species)
            klass = (AdsorbateClass.RADIONUCLIDE.value if actual in ("Cs", "Sr")
                     else AdsorbateClass.OTHER.value)
            ctype = (CapacityType.FREUNDLICH_QMAX.value if key in FREUNDLICH
                     else CapacityType.LANGMUIR_QMAX.value)
            flag_col = "cs_value_repeated" if species == "Cs" else "sr_value_repeated"
            rows.append(
                {
                    "sample_id": f"{sorbent}_{actual}_{r.get('Temp_K')}",
                    "sorbent_name": r.get("Sorbent_Type"),
                    "adsorbate": actual,
                    "adsorbate_class": klass,
                    "capacity_mg_g": float(val),
                    "capacity_type": ctype,
                    "temperature_K": pd.to_numeric(r.get("Temp_K"), errors="coerce"),
                    "si_al": pd.to_numeric(r.get("Si_Al"), errors="coerce"),
                    "activator_molarity": pd.to_numeric(r.get("NaOH_M"), errors="coerce"),
                    "langmuir_b_L_mg": pd.to_numeric(r.get("b_L_mg"), errors="coerce"),
                    "dr_e_kj_mol": pd.to_numeric(r.get("E_kJ_mol"), errors="coerce"),
                    "r2": pd.to_numeric(r.get("R2_Langmuir"), errors="coerce"),
                    "initial_conc_mg_L": C0_MAX.get(str(r.get("provenance")), (None, None))[0],
                    "dose_g_L": C0_MAX.get(str(r.get("provenance")), (None, None))[1],
                    "provenance_doi": r.get("provenance"),
                    "source_label": "literature_compilation",
                    "value_repeated": bool(r.get(flag_col, False)),
                    "from_figure": pd.NA,
                    "replicated": pd.NA,
                }
            )
    return pd.DataFrame(rows)


def _from_oulu() -> pd.DataFrame:
    """Oulu designed composition study (doi:10.1016/j.matdes.2026.115471).

    The workbook reports concentration *removed* (mg/L). The paper states the
    adsorbent dose was **1 g/L**, so q[mg/g] = dC[mg/L] / dose[g/L] -- numerically
    identical here, but the conversion is written out so the basis is auditable.

    These are **single-point** uptakes at C0 = 100 mg/L, not Langmuir Qmax.
    """
    src = Path("data/raw/external/oulu2026_adsorption.csv")
    if not src.exists():
        return pd.DataFrame()
    raw = pd.read_csv(src)

    DOSE_G_L = 1.0  # paper, methods: "The adsorbent dose was 1 g/L."
    C0 = {"NH4+": 100.0, "methylene_blue": 100.0, "rhodamine_6G": 150.0}
    KLASS = {
        "NH4+": AdsorbateClass.ANALOGUE.value,   # monovalent-cation proxy for Cs+
        "methylene_blue": AdsorbateClass.DYE.value,
        "rhodamine_6G": AdsorbateClass.DYE.value,
    }

    out = pd.DataFrame(
        {
            "sample_id": raw["sample_id"] + "_" + raw["adsorbate"],
            "sorbent_name": raw["sample_id"],
            "adsorbate": raw["adsorbate"],
            "adsorbate_class": raw["adsorbate"].map(KLASS),
            "capacity_mg_g": pd.to_numeric(raw["adsorbed_mg_L"], errors="coerce") / DOSE_G_L,
            "capacity_std": pd.to_numeric(raw["std_mg_L"], errors="coerce") / DOSE_G_L,
            "capacity_type": CapacityType.SINGLE_POINT.value,
            "initial_conc_mg_L": raw["adsorbate"].map(C0),
            "dose_g_L": DOSE_G_L,
            "ph": 7.0,  # phosphate-buffered to pH 7
            "si_al": pd.to_numeric(raw["si_al"], errors="coerce"),
            "na_al": pd.to_numeric(raw["na"], errors="coerce")
            / pd.to_numeric(raw["al"], errors="coerce"),
            "ca_al": pd.to_numeric(raw["ca"], errors="coerce")
            / pd.to_numeric(raw["al"], errors="coerce"),
            "bet_m2_g": pd.to_numeric(raw.get("bet_m2_g"), errors="coerce"),
            "precursor": "synthetic_colloidal_silica_Al_nitrate",
            "provenance_doi": raw["provenance"],
            "source_label": "oulu2026",
            "replicated": True,  # triplicate
            "from_figure": False,
            "value_repeated": False,
        }
    )
    return out


def _from_katada2024() -> pd.DataFrame:
    """Katada et al., Langmuir 40(37):19324-19331 (2024), doi:10.1021/acs.langmuir.4c00801.

    Open on PMC11411716 (CC BY-NC-ND 4.0 — factual table values only are used here;
    no part of the article text is reproduced).

    Table 1: six Na-form zeolites. `c_IEZ` is the Cs ion-exchange capacity in mol/kg;
    Cs+ is monovalent, so mol/kg == eq/kg == meq/g, and mg/g = value * M(Cs).

    Two caveats carried into the rows:
    * These are **zeolites**, not geopolymers -> `sorbent_class=zeolite`.
    * Measured against a **1000 mg/L Na background**, so this is a *selectivity-limited*
      capacity, not a clean single-ion Qmax. `competing_ion` records that.
    """
    from .adsorption_schema import SorbentClass, meq_g_to_mg_g

    # sample, framework, Si/Al, c_Al(mol/kg), c_IEZ(mol/kg), K
    TABLE1 = [
        ("FAU 6.1", "FAU", 1.37, 6.08, 0.55, 3.41),
        ("LTA 6.7", "LTA", 1.12, 6.69, 0.18, 20.4),
        ("MFI 1.2", "MFI", 12.3, 1.22, 1.00, 50.9),
        ("YFI 1.3", "YFI", 11.1, 1.33, 0.83, 73.1),
        ("MOR 1.5", "MOR", 9.88, 1.48, 1.44, 177.0),
        ("MOR 1.7", "MOR", 8.37, 1.71, 1.59, 187.0),
    ]

    rows = []
    for name, framework, si_al, c_al, c_iez, k_eq in TABLE1:
        rows.append(
            {
                "sample_id": f"katada2024_{name.replace(' ', '_')}",
                "sorbent_name": name,
                "sorbent_class": SorbentClass.ZEOLITE.value,
                "framework_code": framework,
                "adsorbate": "Cs",
                "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
                "capacity_mg_g": meq_g_to_mg_g(c_iez, "Cs"),
                "capacity_type": CapacityType.ION_EXCHANGE_CAPACITY.value,
                "initial_conc_mg_L": 210.0,  # midpoint of the stated 60-360 g/m3 range
                "dose_g_L": 1.0,             # 0.1 g in 100 cm3
                "temperature_K": 298.0,
                "contact_time_h": 5 / 60,    # 5 min
                "competing_ion": "Na",
                "competing_ion_mg_L": 1000.0,
                "si_al": si_al,
                "al_content_mol_kg": c_al,
                "provenance_doi": "10.1021/acs.langmuir.4c00801",
                "source_label": "katada2024",
                "replicated": pd.NA,
                "from_figure": False,
                "value_repeated": False,
                # K is a thermodynamic selectivity constant, not an isotherm fit;
                # parked in freundlich_kf would be wrong, so it rides in r2's sibling slot
                "langmuir_b_L_mg": pd.NA,
                "freundlich_kf": pd.NA,
                "r2": pd.NA,
                "_k_eq": k_eq,  # dropped by conform(); retained here for traceability
            }
        )
    return pd.DataFrame(rows)


#: register new adapters here as M6 mining lands sources
ADAPTERS = {
    "literature_compilation": _from_literature_compilation,
    "oulu2026": _from_oulu,
    "katada2024": _from_katada2024,
}


def build() -> pd.DataFrame:
    frames = []
    for name, fn in ADAPTERS.items():
        df = fn()
        if df.empty:
            print(f"  {name:24s} -- no data (skipped)")
            continue
        print(f"  {name:24s} {len(df):4d} rows")
        frames.append(conform(df))
    if not frames:
        raise SystemExit("no sources available")
    return pd.concat(frames, ignore_index=True)


def main() -> None:
    print("Building pooled adsorption database\n")
    pool = build()

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pool.to_csv(OUT, index=False)
    print(f"\nwrote {OUT}  {pool.shape}")

    issues = validate(pool)
    warns = pooling_warning(pool)

    lines = ["# Pooled adsorption database — summary", ""]
    lines.append(f"**Rows:** {len(pool)}  ·  **Sources:** {pool.source_label.nunique()}")
    lines.append("")
    lines.append("## Composition of the pool")
    lines.append("")
    lines.append("| adsorbate | class | capacity_type | n |")
    lines.append("|---|---|---|---|")
    grp = pool.groupby(
        ["adsorbate", "adsorbate_class", "capacity_type"], dropna=False
    ).size()
    for (a, c, t), n in grp.items():
        lines.append(f"| {a} | {c} | {t} | {n} |")

    lines += ["", "## ⚠️ Pooling warnings", ""]
    lines += [f"- {w}" for w in warns] or ["- none"]

    lines += ["", "## Validation issues", ""]
    if issues.empty:
        lines.append("- none")
    else:
        lines.append("| issue | count | detail |")
        lines.append("|---|---|---|")
        for _, r in issues.iterrows():
            lines.append(f"| {r['issue']} | {r['count']} | {r['detail']} |")

    # what is actually usable for the Cs/Sr target
    rad = pool[pool.adsorbate_class == AdsorbateClass.RADIONUCLIDE.value]
    ana = pool[pool.adsorbate_class == AdsorbateClass.ANALOGUE.value]
    lines += [
        "",
        "## Usable for the radionuclide target",
        "",
        f"- **True radionuclide rows (Cs/Sr):** {len(rad)}",
        f"- **Analogue rows (NH4+ etc.):** {len(ana)} — usable only as a clearly-labelled proxy",
        f"- **Dye rows:** {len(pool) - len(rad) - len(ana)} — structural signal only, not a Cs/Sr target",
    ]

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text("\n".join(lines) + "\n")
    print(f"wrote {REPORT}")
    for w in warns:
        print(f"  ⚠️  {w}")




def _from_tarnovsky2024() -> pd.DataFrame:
    """Tarnovsky, Fedoryshyn, Vyshnevskyi, Romanova (2024),
    Chem. Phys. Technol. Surf. 15(1):102-109, doi:10.15407/hftp15.01.102 (CC BY).

    Metakaolin-based geopolymers with Langmuir Cs+ AND Sr2+ isotherms plus full
    BET/porosity — exactly the composition->structure->capacity chain we need.

    Capacities are reported in **mmol/g** (molar), not meq/g, so they convert with
    `mmol_g_to_mg_g`. For divalent Sr the distinction matters by a factor of 2.

    Si/Al computed from the paper's oxide table (wt %):
        Si/Al = (SiO2 / M_SiO2) / (2 * Al2O3 / M_Al2O3)
    """
    from .adsorption_schema import (
        SorbentClass,
        langmuir_K_per_mmol_to_b_per_mg,
        mmol_g_to_mg_g,
    )

    # Methods: isotherms run over 0.1-10 mmol/L. Molar, so mg/L differs by ion.
    C0_MMOL_MAX = 10.0
    M_ION = {"Cs": 132.905, "Sr": 87.62}
    M_SIO2, M_AL2O3 = 60.084, 101.961
    # sample: (SiO2 wt%, Al2O3 wt%, BET m2/g, pore vol cm3/g, avg radius nm, class)
    SAMPLES = {
        "Kaolin": (29.9, 24.7, 9.0, 0.12, 28.0, SorbentClass.CLAY.value),
        "GP 1": (58.7, 25.5, 26.0, 0.25, 19.2, SorbentClass.GEOPOLYMER.value),
        "GP 2": (53.1, 28.3, 88.0, 0.29, 6.6, SorbentClass.GEOPOLYMER.value),
    }
    # Table 4: sample -> ion -> (Q mmol/g, K L/mmol)
    ISOTHERMS = {
        "Kaolin": {"Cs": (0.10, 13.5), "Sr": (0.17, 2.39)},
        "GP 1": {"Cs": (1.75, 6.64), "Sr": (0.55, 4.7)},
        "GP 2": {"Cs": (0.93, 19.2), "Sr": (0.65, 4.02)},
    }

    rows = []
    for name, (sio2, al2o3, bet, pv, _r, klass) in SAMPLES.items():
        si_al = (sio2 / M_SIO2) / (2 * al2o3 / M_AL2O3)
        for ion, (q_mmol, k_l_mmol) in ISOTHERMS[name].items():
            rows.append(
                {
                    "sample_id": f"tarnovsky2024_{name.replace(' ', '')}_{ion}",
                    "initial_conc_mg_L": C0_MMOL_MAX * M_ION[ion],
                    "sorbent_name": name,
                    "sorbent_class": klass,
                    "adsorbate": ion,
                    "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
                    "capacity_mg_g": mmol_g_to_mg_g(q_mmol, ion),
                    "capacity_type": CapacityType.LANGMUIR_QMAX.value,
                    "langmuir_b_L_mg": langmuir_K_per_mmol_to_b_per_mg(k_l_mmol, ion),
                    "si_al": si_al,
                    "bet_m2_g": bet,
                    "pore_volume_cm3_g": pv,
                    "precursor": "metakaolin",
                    "provenance_doi": "10.15407/hftp15.01.102",
                    "source_label": "tarnovsky2024",
                    "from_figure": False,
                    "value_repeated": False,
                    "replicated": pd.NA,
                }
            )
    return pd.DataFrame(rows)


ADAPTERS["tarnovsky2024"] = _from_tarnovsky2024




def _from_varon2025() -> pd.DataFrame:
    """Varon, Gossard, Coppel, Barre, Poulesquen (CEA) (2025),
    Cleaner Materials 17:100331, doi:10.1016/j.clema.2025.100331 (CC BY-NC).

    Designed K-geopolymer series varying SiO2/K2O and H2O/M2O, with BET, 27Al NMR
    (Al-IV) and 29Si Q4(mAl) speciation on the SAME samples as the Sr sorption tests.

    Reports **K_D (mL/g)**, a distribution coefficient — NOT a capacity. These rows
    therefore carry `kd_mL_g` and leave `capacity_mg_g` NULL, so they can never be
    pooled into an mg/g regression by accident.

    Sample-name mapping for rows 5-7 is INFERRED from context (BET 15 matches the
    K-1.2-8 sample described as type-II with no hysteresis; FKD 16.2 matches the
    abstract's "H2O/K2O = 12 exhibiting the highest" selectivity). Names are marked
    accordingly; the numeric values themselves come straight from Tables 1-3.
    """
    from .adsorption_schema import SorbentClass

    # (label, nominal Si/Al, measured Si/Al, BET, AlIV %, AlIV mmol/g, KD_Sr, KD_Ca, FKD)
    ROWS = [
        ("K-0.5-16", 1.27, 1.14, 72.0, 96.0, 4.77, 4100.0, 630.0, 6.7),
        ("K-1-16", 1.52, 1.55, 163.0, 93.8, 4.14, 2500.0, 280.0, 10.0),
        ("K-1.2-16", 1.63, 1.67, 188.0, 94.0, 3.94, 1800.0, 220.0, 8.2),
        ("K-1.5-16", 1.77, 1.79, 212.0, 91.4, 3.71, 1100.0, 190.0, 6.5),
        ("K-1.2-8 (inferred)", 1.63, 1.83, 15.0, 88.0, 3.61, 70.0, 20.0, 2.4),
        ("K-1.2-12 (inferred)", 1.63, 1.63, 182.0, 92.4, 3.83, 1900.0, 120.0, 16.2),
        ("Na-1.2-16 (inferred)", 1.63, 1.67, 38.0, 84.7, 3.45, 900.0, 180.0, 5.1),
    ]

    out = []
    for label, si_al_nom, si_al, bet, al_iv_pct, al_iv, kd_sr, _kd_ca, fkd in ROWS:
        out.append(
            {
                "sample_id": f"varon2025_{label.split(' ')[0]}",
                "sorbent_name": label,
                "sorbent_class": SorbentClass.GEOPOLYMER.value,
                "adsorbate": "Sr",
                "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
                "capacity_mg_g": pd.NA,          # deliberately absent: KD is not a capacity
                "capacity_type": CapacityType.KD.value,
                "kd_mL_g": kd_sr,
                "kd_competing_ion": "Ca",        # selectivity measured against Ca2+
                "selectivity_factor": fkd,
                "si_al": si_al,
                "bet_m2_g": bet,
                "al_iv_pct": al_iv_pct,
                "al_iv_mmol_g": al_iv,
                "precursor": "metakaolin",
                "provenance_doi": "10.1016/j.clema.2025.100331",
                "source_label": "varon2025",
                "from_figure": False,
                "value_repeated": False,
                "replicated": pd.NA,
            }
        )
    return pd.DataFrame(out)


ADAPTERS["varon2025"] = _from_varon2025




def _from_lin2026() -> pd.DataFrame:
    """Lin, Liu & Jhou (2026), Ceramics 9(2):21, doi:10.3390/ceramics9020021 (CC BY).

    Granulated adsorbents. Only values the paper explicitly labels **Langmuir q_m**
    are ingested; the powder "screening capacities" (ZA 8.15, Ba-ZA 2.38, ...) are
    stated without an isotherm model and are deliberately EXCLUDED.

    Non-aluminosilicate benchmarks (Na-titanate SrTreat, hexacyanoferrate CsTreat)
    are also excluded: they carry no composition and would pad a composition->capacity
    database, per the same reasoning that rejected the Tian supplement.

    All tests ran in high-salinity matrices (up to 35,000 mg/L NaCl), so these are
    SELECTIVITY-limited capacities, recorded via competing_ion.
    """
    from .adsorption_schema import SorbentClass, meq_g_to_mg_g

    # name, class, ion, q_m meq/g, BET, pore_vol, NaCl mg/L
    ROWS = [
        ("ACSr", SorbentClass.GEOPOLYMER, "Sr", 5.07, None, None, 35000.0),
        ("NCGO", SorbentClass.GEOPOLYMER, "Cs", 0.41, 39.2, 0.25, 35000.0),
        ("NiGO", SorbentClass.GEOPOLYMER, "Cs", 0.35, 38.8, 0.15, 35000.0),
        ("CoGO", SorbentClass.GEOPOLYMER, "Cs", 0.34, 29.3, 0.13, 35000.0),
        ("Ba-4A", SorbentClass.ZEOLITE, "Sr", 3.81, None, None, 35000.0),
        ("CuFC/4A", SorbentClass.ZEOLITE, "Cs", 0.65, 5.25, 1.52, 35000.0),
    ]
    return pd.DataFrame([
        {
            "sample_id": f"lin2026_{n}", "sorbent_name": n, "sorbent_class": k.value,
            "adsorbate": ion, "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
            "capacity_mg_g": meq_g_to_mg_g(q, ion),
            "capacity_type": CapacityType.ION_EXCHANGE_CAPACITY.value,
            "temperature_K": 298.0, "initial_conc_mg_L": 10.0 if ion == "Cs" else pd.NA,
            "competing_ion": "Na", "competing_ion_mg_L": nacl,
            "bet_m2_g": bet, "pore_volume_cm3_g": pv,
            "provenance_doi": "10.3390/ceramics9020021", "source_label": "lin2026",
            "from_figure": False, "value_repeated": False, "replicated": pd.NA,
        }
        for n, k, ion, q, bet, pv, nacl in ROWS
    ])


def _from_tian2019_espr() -> pd.DataFrame:
    """Tian & Sasaki (2019), Environ Sci Pollut Res, doi:10.1007/s11356-019-05612-1.

    NOTE: distinct from the Water Sci. Technol. Tian 2019 already in the pool.
    The sorbent here is **zeolite A synthesised from fly ash** — the geopolymer in
    this paper is an encapsulation matrix evaluated by TCLP leaching, NOT a sorbent,
    so no geopolymer capacity row exists.

    Capacities are mmol/g (molar) -> mmol_g_to_mg_g. Si/Al computed from the fly-ash
    oxide analysis (SiO2 44.60 / Al2O3 46.10 wt%).
    """
    from .adsorption_schema import SorbentClass, mmol_g_to_mg_g

    si_al = (44.60 / 60.084) / (2 * 46.10 / 101.961)
    ROWS = [("Cs", 2.12, 3.21, 0.9788), ("Sr", 1.93, 16.96, 0.9989)]
    return pd.DataFrame([
        {
            "sample_id": f"tian2019espr_zeoliteA_{ion}",
            "sorbent_name": "Zeolite A (from fly ash)",
            "sorbent_class": SorbentClass.ZEOLITE.value,
            "adsorbate": ion, "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
            "capacity_mg_g": mmol_g_to_mg_g(q, ion),
            "capacity_type": CapacityType.LANGMUIR_QMAX.value,
            "r2": r2, "si_al": si_al, "bet_m2_g": 121.0, "pore_volume_cm3_g": 0.23,
            "dose_g_L": 1.0, "ph": 7.0, "temperature_K": 298.0, "contact_time_h": 3.0,
            "precursor": "coal_fly_ash", "provenance_doi": "10.1007/s11356-019-05612-1",
            "source_label": "tian2019_espr", "from_figure": False,
            "value_repeated": False, "replicated": pd.NA,
        }
        for ion, q, _b, r2 in ROWS
    ])


def _from_xiang2021_foams() -> pd.DataFrame:
    """Xiang et al. (2021), J Environ Chem Eng 9:105733, doi:10.1016/j.jece.2021.105733.

    Four metakaolin geopolymer FOAMS of increasing density (GF300-GF600), Cs only.

    Striking result: across the series BET falls 53.8 -> 37.8 m2/g and porosity falls
    83.8 -> 68.4 %, while Cs uptake RISES 161.8 -> 192.1 mg/g
    (corr(BET, uptake) = -0.92; corr(porosity, uptake) = -0.96).

    GF300-GF500 report single-point uptake at C0 = 500 mg/L; only GF600 has a fitted
    Langmuir Qmax (216.1 mg/g), recorded as a separate row with its own capacity_type.

    Si/Al from the metakaolin XRF (SiO2 52.92 / Al2O3 43.85 wt%). Solution volume is
    NOT reported in the paper, so dose_g_L is left null rather than guessed.
    """
    from .adsorption_schema import SorbentClass

    si_al = (52.92 / 60.084) / (2 * 43.85 / 101.961)
    base = {
        "sorbent_class": SorbentClass.GEOPOLYMER.value, "adsorbate": "Cs",
        "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
        "si_al": si_al, "na_al": 0.716, "precursor": "metakaolin_foam",
        "initial_conc_mg_L": 500.0, "ph": 7.0, "temperature_K": 298.0,
        "contact_time_h": 96.0, "provenance_doi": "10.1016/j.jece.2021.105733",
        "source_label": "xiang2021", "from_figure": False,
        "value_repeated": False, "replicated": True,
    }
    # name, q single-point, std, BET, porosity%
    FOAMS = [
        ("GF300", 161.75, 3.24, 53.78), ("GF400", 164.16, 3.28, 49.42),
        ("GF500", 185.82, 3.72, 45.83), ("GF600", 192.14, 3.84, 37.77),
    ]
    rows = [
        {**base, "sample_id": f"xiang2021_{n}", "sorbent_name": n,
         "capacity_mg_g": q, "capacity_std": sd,
         "capacity_type": CapacityType.SINGLE_POINT.value, "bet_m2_g": bet}
        for n, q, sd, bet in FOAMS
    ]
    # GF600 also has a fitted Langmuir maximum — a DIFFERENT quantity, own row
    rows.append({**base, "sample_id": "xiang2021_GF600_langmuir",
                 "sorbent_name": "GF600", "capacity_mg_g": 216.1,
                 "capacity_type": CapacityType.LANGMUIR_QMAX.value,
                 "langmuir_b_L_mg": 0.026, "r2": 0.9808, "bet_m2_g": 37.77})
    return pd.DataFrame(rows)


ADAPTERS.update({
    "lin2026": _from_lin2026,
    "tian2019_espr": _from_tian2019_espr,
    "xiang2021": _from_xiang2021_foams,
})




def _from_zhang2021() -> pd.DataFrame:
    """Zhang, Zhu, Du, Feng, Miyamoto & Kano (2021), Applied Sciences 11:8407,
    doi:10.3390/app11188407 (CC BY). Verified inline from the PDF, Table 4.

    Alkali-treated fly-ash and slag "geomaterials" (zeolite-bearing), Cs only.

    Table 4 verbatim:
        Flyash  qmax 89.32 mg/g, K_L 0.1665 L/mg, R2 0.9948 | K_F 10.75, 1/n 0.01620, R2 0.1309
        Slag    qmax 44.52 mg/g, K_L 0.02126,     R2 0.9954 | K_F 20.55, 1/n 0.04660, R2 0.3698

    The Freundlich R2 values are genuinely poor; the authors state Langmuir fits
    better, so only the Langmuir maxima are used as the target.
    """
    from .adsorption_schema import SorbentClass

    ROWS = [("Flyash-geomaterial", 89.32, 0.1665, 0.9948),
            ("Slag-geomaterial", 44.52, 0.02126, 0.9954)]
    return pd.DataFrame([
        {
            "sample_id": f"zhang2021_{n.split('-')[0]}", "sorbent_name": n,
            "sorbent_class": SorbentClass.AAM.value,
            "adsorbate": "Cs", "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
            "capacity_mg_g": q, "capacity_type": CapacityType.LANGMUIR_QMAX.value,
            "langmuir_b_L_mg": kl, "r2": r2,
            "provenance_doi": "10.3390/app11188407", "source_label": "zhang2021",
            "from_figure": False, "value_repeated": False, "replicated": pd.NA,
        }
        for n, q, kl, r2 in ROWS
    ])


ADAPTERS["zhang2021"] = _from_zhang2021




def _from_baek2018() -> pd.DataFrame:
    """Baek, Ha, Hong, Kim & Kim (2018), Micropor. Mesopor. Mater. 264:159-166,
    doi:10.1016/j.micromeso.2018.01.025. Extracted inline from the PDF.

    Three natural zeolites with Cs Langmuir fits, CEC and Si/Al.

    Table (verbatim):
        Q0L (mg/g)  chabazite 1249.5   stilbite 76.278  heulandite 59.488
        KL (L/mg)   7.9433e-05         0.0012934        0.0016726
        R2          0.99989            0.99994          0.99998
        Si/Al       1.50               3.88             3.48
        CEC         chabazite 238.1 meq/100 g (highest)

    ⚠️ CHABAZITE'S Q0L IS AN EXTRAPOLATION ARTIFACT, NOT A CAPACITY.
    Its K_L is 7.9e-05 L/mg -- two orders below the other two -- and the paper's own
    kinetic section reports equilibrium uptake of only **1.184 mg/g**. A Langmuir
    fit with such a small K over data collected far below saturation extrapolates the
    plateau ~1000x beyond anything measured. R2 = 0.99989 does not rescue this: a
    near-linear low-coverage isotherm fits the Langmuir form almost perfectly while
    leaving Q0 essentially unconstrained.

    It is ingested (never silently dropped) but exceeds the schema's plausibility
    bound of 1000 mg/g, so `validate()` flags it and it must be excluded from any
    fit unless the extrapolation is defended explicitly.
    """
    from .adsorption_schema import SorbentClass

    # Isotherm C0 range recovered from the paper's methods: 3.0e-6 to 2.0e-2 M,
    # i.e. 0.40 to 2658 mg/L for Cs. Recording C0max lets the F15 saturation screen
    # actually run on these rows.
    C0_MAX = 2658.1  # mg/L

    ROWS = [  # name, Si/Al, Q0L mg/g, KL L/mg, R2, CEC meq/100g
        ("chabazite", 1.50, 1249.5, 7.9433e-05, 0.99989, 238.1),
        ("stilbite", 3.88, 76.278, 0.0012934, 0.99994, None),
        ("heulandite", 3.48, 59.488, 0.0016726, 0.99998, None),
    ]
    return pd.DataFrame([
        {
            "sample_id": f"baek2018_{n}", "sorbent_name": n,
            "sorbent_class": SorbentClass.ZEOLITE.value,
            "adsorbate": "Cs", "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
            "capacity_mg_g": q, "capacity_type": CapacityType.LANGMUIR_QMAX.value,
            "langmuir_b_L_mg": kl, "r2": r2, "si_al": sial, "cec_meq_100g": cec,
            "initial_conc_mg_L": C0_MAX,
            "provenance_doi": "10.1016/j.micromeso.2018.01.025",
            "source_label": "baek2018", "from_figure": False,
            "value_repeated": False, "replicated": pd.NA,
        }
        for n, sial, q, kl, r2, cec in ROWS
    ])


ADAPTERS["baek2018"] = _from_baek2018


# ---------------------------------------------------------------------------
# Kurumisawa, Omatu & Yamashina, Materials and Structures 54(4):169 (2021)
# doi:10.1617/s11527-021-01758-y
#
# RECOVERED SOURCE. This paper was rejected from the corpus as "a diffusivity study
# (diffus 65)" during batch triage — correct on the keyword balance, wrong on the
# content. Figure 3b publishes the Langmuir MONOLAYER ADSORPTION CAPACITY of Cs for
# five metakaolin geopolymers made with five different alkali activators. That is a
# Pool A capacity with real compositional variation, which the pool is short of.
#
# The same five specimens also carry a Cs INGRESS diffusivity, ingested separately
# into Pool B (merge_immobilisation._from_kurumisawa2021). The two pools stay
# separate under D13; only the sorbent identity is shared.
# ---------------------------------------------------------------------------
KURUMISAWA_DOI = "10.1617/s11527-021-01758-y"

#: Figure 3b, p31 — monolayer adsorption capacity, mmol/g. Bar chart, linear axis,
#: read to roughly +/-0.01 mmol/g.
KURUMISAWA_QMAX_MMOL_G = {
    "K11": 0.315, "K9": 0.425, "0.66K": 0.530, "N11": 0.727, "KN11": 0.393,
}

#: Figure 3a, p31 — the isotherm itself. Highest equilibrium point actually measured,
#: needed for the F14/F16 saturation screen: a monolayer capacity is only a capacity
#: if the plateau was approached. (Ce mmol/L, q mmol/g).
KURUMISAWA_HIGHEST_POINT = {
    "K11": (5.0, 0.303), "K9": (5.2, 0.299), "0.66K": (4.0, 0.322),
    "N11": (1.9, 0.363), "KN11": (3.4, 0.333),
}

#: Table 2, p27 — activator. Si/Al of the hardened gel is not stated and is NOT
#: inferred here; the activator's SiO2/Al2O3 is recorded instead.
KURUMISAWA_ACTIVATOR_SIO2_AL2O3 = {
    "K11": 1.0, "K9": 1.0, "0.66K": 1.5, "N11": 1.0, "KN11": 1.0,
}


def _from_kurumisawa2021() -> pd.DataFrame:
    rows = []
    for sample, q_mmol in KURUMISAWA_QMAX_MMOL_G.items():
        ce_max, q_at_max = KURUMISAWA_HIGHEST_POINT[sample]
        rows.append(
            {
                "sample_id": f"kurumisawa2021_{sample}",
                "sorbent_name": sample,
                "sorbent_class": SorbentClass.GEOPOLYMER.value,
                "adsorbate": "Cs",
                "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
                # mmol/g -> mg/g. Cs+ is monovalent so mmol and meq coincide here,
                # but the MOLAR conversion is used deliberately (see schema docstring).
                "capacity_mg_g": mmol_g_to_mg_g(q_mmol, "Cs"),
                "capacity_type": CapacityType.LANGMUIR_QMAX.value,
                "initial_conc_mg_L": mmol_g_to_mg_g(ce_max, "Cs"),  # highest Ce reached
                "precursor": "metakaolin",
                "activator_molarity": None,
                "provenance_doi": KURUMISAWA_DOI,
                "source_label": "kurumisawa2021",
                "replicated": False,
                "from_figure": True,
                "value_repeated": False,
            }
        )
    return pd.DataFrame(rows)


ADAPTERS["kurumisawa2021"] = _from_kurumisawa2021


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Varon et al., Open Ceramics 25 (2026) 100895, doi:10.1016/j.oceram.2025.100895
# "Microstructural and sorption properties evolution on leached geopolymers for
#  strontium decontamination." (CEA Montpellier; same group/samples as varon2025.)
#
# This is the LEACHING COMPANION to varon2025 (Cleaner Materials). The 0 h data are
# identical to varon2025 (verified: K-0.5-16 BET 72, AlIV 96.0, KD 4100) and are NOT
# re-ingested. The NEW contribution is the 96 h WATER-LEACHED state (Table 3 + 4):
# post-leach Sr KD, AlIV and Q4(mAl) on the same samples.
#
# Scientific payload (finding F27): across the 7 samples, [AlIV] concentration
# governs Sr KD (corr +0.946, +0.986 excl. the barely-reacted K-1.2-8), and the
# leaching acts as a WITHIN-SAMPLE causal test - corr(Δ[AlIV], ΔKD) = +0.938: the
# samples that lose the most framework Al on leaching lose the most sorption.
# ---------------------------------------------------------------------------
def _from_varon_leached2026() -> pd.DataFrame:
    # 96 h leached state, Tables 3 & 4 (read from the PDF).
    # (label, Si/Al, BET_96h, AlIV%_96h, [AlIV]mmol_96h, KD_Sr_96h, Qmax_96h mmol/g)
    ROWS = [
        ("K-0.5-16",  1.27, 109.0, 82.4, 3.38, 1350.0, 0.59),
        ("K-1-16",    1.52, 181.0, 92.1, 3.82, 1050.0, 0.40),
        ("K-1.2-16",  1.63, 199.0, 91.9, 3.73, 820.0,  0.41),
        ("K-1.5-16",  1.77, 221.0, 93.6, 3.67, 450.0,  0.24),
        ("K-1.2-8",   1.63, 28.0,  88.8, 3.61, 150.0,  0.51),
        ("K-1.2-12",  1.63, 220.0, 90.4, 3.61, 1000.0, 0.55),
        ("Na-1.2-16", 1.63, 44.0,  85.8, 3.20, 130.0,  0.28),
    ]
    out = []
    for label, si_al, bet, al_iv_pct, al_iv, kd_sr, qmax_mmol in ROWS:
        out.append(
            {
                "sample_id": f"varon_leached2026_{label}",
                # distinct sorbent STATE - a water-leached geopolymer, not the fresh
                # material; named so it can never be pooled with the 0 h varon2025 rows.
                "sorbent_name": f"{label} (leached 96h)",
                "sorbent_class": SorbentClass.GEOPOLYMER.value,
                "adsorbate": "Sr",
                "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
                # KD is the reported target; Qmax_exp is a molar capacity in mmol/g,
                # converted to mg/g via the MOLAR conversion (Sr).
                "capacity_mg_g": mmol_g_to_mg_g(qmax_mmol, "Sr"),
                "capacity_type": CapacityType.EXPERIMENTAL_MAX.value,
                "kd_mL_g": kd_sr,
                "si_al": si_al,
                "bet_m2_g": bet,
                "al_iv_pct": al_iv_pct,
                "al_iv_mmol_g": al_iv,
                "precursor": "metakaolin_water_leached_96h",
                "provenance_doi": "10.1016/j.oceram.2025.100895",
                "source_label": "varon_leached2026",
                "from_figure": False,
                "value_repeated": False,
                "replicated": pd.NA,
            }
        )
    return pd.DataFrame(out)


ADAPTERS["varon_leached2026"] = _from_varon_leached2026


# ---------------------------------------------------------------------------
# Qian, Sun & Tay, J. Nucl. Mater. 299 (2001) 199-204  (Q10 acquisition)
# doi:10.1016/S0022-3115(01)00700-0
# Batch-4. Scanned PDF (no text layer) - values read visually from page 4 text.
#
# Aluminium-rich alkali-activated slag (AAS) and M-AAS (AAS + metakaolin + zeolite
# + NaOH-treated attapulgite clay). A Ca-rich C-A-S-H system, NOT a framework
# geopolymer. Sr/Cs distribution ratio Rd measured by batch sorption (0.002 M
# CsCl/SrCl2, 7 days).
#
# SUPPORTS the framework-Al story from the Ca side: adding Al-rich metakaolin/clay
# to slag RAISES Rd (M-AAS > AAS for both ions) - more aluminosilicate exchange
# capacity = more uptake, even in a calcium-silicate binder.
#
# UNIT FLAG: the paper labels Rd "mol/g", but Rd = (mol/g adsorbed)/(equilibrium
# conc) is a distribution coefficient whose magnitude (3.9e3-1.2e4) is consistent
# with mL/g, not mol/g. Stored in kd_mL_g with this caveat; the LABEL in the source
# is anomalous and is recorded here rather than silently "corrected".
# ---------------------------------------------------------------------------
def _from_qian2001() -> pd.DataFrame:
    # (matrix, adsorbate, Rd)  -- page 4 text, verified visually
    ROWS = [
        ("AAS",   "Cs", 3.9e3),
        ("AAS",   "Sr", 6.4e3),
        ("M-AAS", "Cs", 6.4e3),
        ("M-AAS", "Sr", 1.2e4),
    ]
    out = []
    for matrix, ads, rd in ROWS:
        out.append(
            {
                "sample_id": f"qian2001_{matrix}_{ads}",
                "sorbent_name": matrix,
                # alkali-activated slag (C-A-S-H), not a framework geopolymer
                "sorbent_class": SorbentClass.AAM.value,
                "adsorbate": ads,
                "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
                "capacity_mg_g": pd.NA,        # a distribution ratio, not a capacity
                "capacity_type": CapacityType.KD.value,
                "kd_mL_g": rd,                 # see UNIT FLAG in the module comment
                "precursor": "blast_furnace_slag_metakaolin_clay",
                "provenance_doi": "10.1016/S0022-3115(01)00700-0",
                "source_label": "qian2001",
                "from_figure": False,          # read from body text, not a figure
                "value_repeated": False,
                "replicated": pd.NA,
            }
        )
    return pd.DataFrame(out)


ADAPTERS["qian2001"] = _from_qian2001


# ---------------------------------------------------------------------------
# Petlitckaia et al., J. Cleaner Production 269 (2020) 122400
# doi:10.1016/j.jclepro.2020.122400   (CEA / Poulesquen group)
# Batch-3 deferred item, now extracted (values read visually - mangled text layer).
#
# Two metakaolin-based K-geopolymer FOAMS: GF (bare) and FGF (functionalised with
# K2Cu(Fe(CN)6), a Prussian-blue analogue for Cs selectivity). Cs capacity is
# strongly matrix-dependent, so THREE different quantities are reported - kept apart:
#   * isotherm MAX, pure water (Fig 7a): GF 250, FGF 175 mg/g  <- ingested as the capacity
#     (saturation genuinely reached; capacity DECLINES past Cs_eq 3.92e-3 mol/L, so no
#      extrapolation-artefact concern - the F14/theta screen is satisfied by construction)
#   * single-point uptake at 100 ppm (Fig 6 kinetics): GF 80, FGF 65 mg/g - NOT ingested
#     (a kinetics endpoint at one C0, redundant with the isotherm max)
#   * fresh water, competitive K/Na/Mg/Ca: GF 150, FGF 100 mg/g <- ingested with a
#     competing_ion flag (a selectivity-limited capacity, a different quantity)
#
# NOTE the mechanism split: GF removes Cs by FRAMEWORK ion exchange (Na<->Cs); FGF adds
# ferrocyanide (K<->Cs). In pure water the bare FRAMEWORK out-capacities the functionalised
# foam (250 > 175); FGF wins only on SELECTIVITY (Kd ~3.5e5 mL/g, ~10x the GF).
# ---------------------------------------------------------------------------
def _from_petlitckaia2020() -> pd.DataFrame:
    # (sorbent, functionalised?, water, Cs Qmax mg/g, competing_ion, kd_mL_g)
    ROWS = [
        ("GF",  False, "pure",  250.0, None, 3.5e4),   # GF Kd ~10x below FGF (p7)
        ("FGF", True,  "pure",  175.0, None, 3.5e5),   # abstract: FGF Kd avg 3.5e5 mL/g
        ("GF",  False, "fresh", 150.0, "K,Na,Mg,Ca", None),
        ("FGF", True,  "fresh", 100.0, "K,Na,Mg,Ca", None),
    ]
    out = []
    for sorbent, func, water, qmax, comp, kd in ROWS:
        name = f"{sorbent} ({'functionalised ' if func else ''}geopolymer foam, {water} water)"
        out.append(
            {
                "sample_id": f"petlitckaia2020_{sorbent}_{water}",
                "sorbent_name": name,
                "sorbent_class": SorbentClass.GEOPOLYMER.value,
                "adsorbate": "Cs",
                "adsorbate_class": AdsorbateClass.RADIONUCLIDE.value,
                "capacity_mg_g": qmax,
                "capacity_type": CapacityType.EXPERIMENTAL_MAX.value,  # isotherm plateau
                "kd_mL_g": kd,
                "competing_ion": comp,
                "precursor": "metakaolin_geopolymer_foam"
                + ("_ferrocyanide" if func else ""),
                "provenance_doi": "10.1016/j.jclepro.2020.122400",
                "source_label": "petlitckaia2020",
                "from_figure": True,          # isotherm plateau read from Fig. 7
                "value_repeated": False,
                "replicated": pd.NA,
            }
        )
    return pd.DataFrame(out)


ADAPTERS["petlitckaia2020"] = _from_petlitckaia2020
