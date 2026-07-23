"""Canonical schema for the pooled adsorption meta-analysis database.

Every source we mine — full datasets, review tables, single papers — is normalised
into ONE row format so the pipeline can train on the merged corpus.

## The two traps this schema exists to prevent

1. **Capacity is not one quantity.** A Langmuir *Q*max (saturation capacity fitted
   over a full isotherm) and a single-point uptake at one initial concentration are
   different numbers with different meanings. Pooling them silently would inflate or
   deflate the target. `capacity_type` keeps them separable, and any model must
   either filter on it or include it as a covariate.

2. **Adsorbate is not one species.** Cs+ measurements, Sr2+ measurements, analogue
   cations (NH4+, K+, Rb+) and organic dyes cannot be pooled into a single target
   without saying so. `adsorbate` and `adsorbate_class` make that explicit.

Units are fixed at the schema boundary: capacity in **mg/g**, concentration in
**mg/L**, dose in **g/L**, temperature in **K**.
"""
from __future__ import annotations

from enum import Enum

import pandas as pd


class CapacityType(str, Enum):
    """What the capacity number actually is.

    The M6 literature sweep confirmed the field reports at least five different
    quantities. They are NOT interconvertible without extra information, so the
    type travels with every row.
    """

    LANGMUIR_QMAX = "langmuir_qmax"        # fitted saturation capacity, mg/g
    FREUNDLICH_QMAX = "freundlich_qmax"    # Freundlich-fitted maximum, mg/g
    SINGLE_POINT = "single_point_q"        # uptake at one stated C0, mg/g
    EXPERIMENTAL_MAX = "experimental_max"  # highest measured uptake, not fitted
    ION_EXCHANGE_CAPACITY = "iec_meq_g"    # meq/g — needs valence+molar mass to reach mg/g
    KD = "kd_mL_g"                         # distribution coefficient, mL/g — NOT a capacity


#: types whose value is in mg/g and may be compared directly
MG_PER_G_TYPES = {
    CapacityType.LANGMUIR_QMAX,
    CapacityType.FREUNDLICH_QMAX,
    CapacityType.SINGLE_POINT,
    CapacityType.EXPERIMENTAL_MAX,
}

#: molar mass (g/mol) and charge, for meq/g -> mg/g conversion
ION_PROPERTIES: dict[str, tuple[float, int]] = {
    "Cs": (132.905, 1),
    "Sr": (87.62, 2),
    "NH4+": (18.039, 1),
    "K": (39.098, 1),
    "Rb": (85.468, 1),
}


def meq_g_to_mg_g(value: float, ion: str) -> float:
    """Convert ion-exchange capacity (meq/g) to mg/g for a given ion.

    mg/g = meq/g * (molar_mass / charge) ... since 1 eq = molar_mass/charge grams.

    Raises:
        KeyError: if the ion's properties are unknown — better than a silent guess.
    """
    molar_mass, charge = ION_PROPERTIES[ion]
    return value * molar_mass / charge


def mmol_g_to_mg_g(value: float, ion: str) -> float:
    """Convert a MOLAR capacity (mmol/g) to mg/g.

    Distinct from `meq_g_to_mg_g`: mmol is an amount of substance, meq is an amount
    of CHARGE. For monovalent Cs+ they coincide; for divalent Sr2+ they differ by a
    factor of 2. Confusing them silently doubles or halves every Sr capacity, so the
    two conversions are kept as separate named functions.
    """
    molar_mass, _charge = ION_PROPERTIES[ion]
    return value * molar_mass


def langmuir_K_per_mmol_to_b_per_mg(k: float, ion: str) -> float:
    """Langmuir affinity K [L/mmol] -> b [L/mg]."""
    molar_mass, _ = ION_PROPERTIES[ion]
    return k / molar_mass


class AdsorbateClass(str, Enum):
    """How the adsorbate relates to our Cs-137 / Sr-90 target."""

    RADIONUCLIDE = "radionuclide"  # Cs, Sr (incl. non-active isotopes as simulants)
    ANALOGUE = "analogue"          # NH4+, K+, Rb+ — monovalent-cation proxies for Cs+
    DYE = "dye"                    # methylene blue, rhodamine 6G — NOT a proxy
    OTHER = "other"


class SorbentClass(str, Enum):
    """Material family. Geopolymers and zeolites are related aluminosilicates but
    are NOT the same material; pooling them needs an explicit justification."""

    GEOPOLYMER = "geopolymer"
    AAM = "alkali_activated_material"
    ZEOLITE = "zeolite"
    ZEOLITE_FROM_GEOPOLYMER = "zeolite_from_geopolymer"
    CLAY = "clay"
    OTHER = "other"


#: canonical column order
COLUMNS: list[str] = [
    # identity
    "sample_id", "sorbent_name", "sorbent_class", "framework_code",
    # adsorbate
    "adsorbate", "adsorbate_class",
    # the target
    "capacity_mg_g", "capacity_type", "capacity_std",
    # experimental conditions (needed to compare capacities fairly)
    "initial_conc_mg_L", "dose_g_L", "temperature_K", "ph", "contact_time_h",
    # competing ions — a capacity measured against a high Na background is a
    # SELECTIVITY-limited capacity, not a clean single-ion Qmax
    "competing_ion", "competing_ion_mg_L",
    # sorbent composition
    "si_al", "na_al", "k_al", "ca_al", "precursor", "activator_molarity",
    # structure
    "bet_m2_g", "pore_volume_cm3_g", "cec_meq_100g", "al_content_mol_kg",
    "al_iv_pct", "al_iv_mmol_g",
    # distribution coefficient — a DIFFERENT quantity from capacity; kept in its
    # own column so it can never be read as mg/g
    "kd_mL_g", "kd_competing_ion", "selectivity_factor",
    # isotherm parameters
    "langmuir_b_L_mg", "freundlich_kf", "freundlich_n", "dr_e_kj_mol", "r2",
    # provenance & quality
    "provenance_doi", "source_label", "replicated", "from_figure", "value_repeated",
]

NUMERIC: list[str] = [
    "capacity_mg_g", "capacity_std", "initial_conc_mg_L", "dose_g_L", "temperature_K",
    "ph", "contact_time_h", "competing_ion_mg_L", "si_al", "na_al", "k_al", "ca_al",
    "activator_molarity", "bet_m2_g", "pore_volume_cm3_g", "cec_meq_100g",
    "al_content_mol_kg", "al_iv_pct", "al_iv_mmol_g", "kd_mL_g", "selectivity_factor",
    "langmuir_b_L_mg",
    "freundlich_kf", "freundlich_n", "dr_e_kj_mol", "r2",
]

#: plausibility bounds — violations are flagged, never silently clipped
BOUNDS: dict[str, tuple[float, float]] = {
    "capacity_mg_g": (0.0, 1000.0),
    "si_al": (0.3, 30.0),
    "temperature_K": (273.0, 373.0),
    "ph": (0.0, 14.0),
    "r2": (0.0, 1.0),
    "bet_m2_g": (0.0, 1500.0),
    "dose_g_L": (0.001, 100.0),
}


def empty_frame() -> pd.DataFrame:
    """An empty frame with the canonical columns, correctly typed."""
    df = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUMNS})
    for c in NUMERIC:
        df[c] = pd.Series(dtype="float64")
    return df


def conform(df: pd.DataFrame) -> pd.DataFrame:
    """Coerce an arbitrary frame to the canonical schema (missing cols -> NA)."""
    out = empty_frame()
    for c in COLUMNS:
        out[c] = df[c] if c in df.columns else pd.NA
    for c in NUMERIC:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out.reset_index(drop=True)


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Return a report of schema and plausibility problems. Nothing is mutated."""
    issues = []

    no_target = (df["capacity_mg_g"].isna() & df["kd_mL_g"].isna()).sum()
    if no_target:
        issues.append(("missing_target", int(no_target), "rows with neither capacity_mg_g nor kd_mL_g"))

    for col in ("adsorbate", "adsorbate_class", "capacity_type", "provenance_doi"):
        n = df[col].isna().sum()
        if n:
            issues.append((f"missing_{col}", int(n), f"rows lacking {col}"))

    valid_classes = {c.value for c in AdsorbateClass}
    bad = (~df["adsorbate_class"].isin(valid_classes)) & df["adsorbate_class"].notna()
    if bad.any():
        issues.append(("bad_adsorbate_class", int(bad.sum()), "not in AdsorbateClass"))

    valid_types = {c.value for c in CapacityType}
    bad = (~df["capacity_type"].isin(valid_types)) & df["capacity_type"].notna()
    if bad.any():
        issues.append(("bad_capacity_type", int(bad.sum()), "not in CapacityType"))

    for col, (lo, hi) in BOUNDS.items():
        s = pd.to_numeric(df[col], errors="coerce")
        out = ((s < lo) | (s > hi)) & s.notna()
        if out.any():
            issues.append((f"out_of_range_{col}", int(out.sum()), f"outside [{lo}, {hi}]"))

    return pd.DataFrame(issues, columns=["issue", "count", "detail"])


def pooling_warning(df: pd.DataFrame) -> list[str]:
    """Flag combinations that must not be pooled into one training target.

    Returns human-readable warnings; callers decide how to stratify. This is the
    guard against the meta-analysis's two headline failure modes.
    """
    warns = []
    types = df["capacity_type"].dropna().unique()
    if len(types) > 1:
        counts = df["capacity_type"].value_counts().to_dict()
        warns.append(
            f"MIXED capacity_type {counts} — Langmuir Qmax and single-point uptake are "
            "different quantities; filter or stratify before training."
        )
    classes = df["adsorbate_class"].dropna().unique()
    if len(classes) > 1:
        counts = df["adsorbate_class"].value_counts().to_dict()
        warns.append(
            f"MIXED adsorbate_class {counts} — radionuclides, analogues and dyes are not "
            "one target; pool only with an explicit, stated justification."
        )
    if df["adsorbate"].dropna().nunique() > 1:
        warns.append(
            f"MULTIPLE adsorbates {sorted(df['adsorbate'].dropna().unique())} — "
            "capacity is species-specific."
        )
    return warns
