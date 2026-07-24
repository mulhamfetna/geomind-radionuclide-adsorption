"""Canonical schema for Pool B — the immobilisation / wasteform meta-analysis.

Pool A (`adsorption_schema`) models **removal from solution**: a sorbent takes Cs or
Sr out of water, and the target is a capacity. Pool B models **immobilisation**: the
radionuclide is mixed in during synthesis and the target is how well the matrix
*retains* it under leaching.

Decision **D13** keeps the two pools parallel and **never merged**. They answer
different questions, and their targets run in opposite directions.

## The four traps this schema exists to prevent

1. **The target is inverted.** A high capacity is good; a high leach rate is *bad*.
   The leachability index is the well-behaved target because higher LI = better
   retention, matching the sign convention of Pool A — but `De` and `CLF` run the
   other way. Mixing them without noting the sign teaches a model backwards.
   :data:`HIGHER_IS_BETTER` states the direction for every target type.

2. **Loading is a control variable, not a measurement.** In Pool A the capacity is
   measured; here `loading_wt_pct` is *set by the experimenter* (typically 1 or 3 wt%).
   It must never be used as a target, and :func:`validate` refuses rows that try.

3. **Below-detection is information, not missing data.** Kim's KSr1 and KSr2 leached
   *below the ICP-OES limit* — they are the best-performing samples in the study, yet
   a naive reader records them as null and drops them. That inverts the result:
   the top performers vanish and the pool is left with only the leakier matrices.
   `censored` marks these rows as **left-censored** (true value below the bound).

4. **LI is logarithmic, and averaging is not commutative.** LI = -log10(De), so the
   mean of several LI values is a *geometric* mean of De, not an arithmetic one.
   Papers report the mean LI over leaching intervals; that number cannot be converted
   back to a single De. `LI` and `De` are therefore separate columns and neither is
   derived from the other at ingest.

Units fixed at the boundary: De in **cm2/s**, LI **dimensionless**, CLF a **fraction**,
loading in **wt%**, duration in **days**.
"""

from __future__ import annotations

import math
from enum import Enum

import pandas as pd


class RetentionType(str, Enum):
    """What the retention number actually is. Not interconvertible in general.

    ``EFFECTIVE_DIFFUSIVITY`` and ``INGRESS_DIFFUSIVITY`` are the dangerous pair.
    Both are reported in the literature as "the diffusion coefficient of Cs", but
    they come from opposite experiments:

    * **effective** (ANSI/ANS 16.1) — the nuclide is *doped into* the matrix at
      synthesis and diffuses **OUT** during a semi-dynamic leach test.
      Kim ~1e-16 cm2/s, Nevin ~1e-19 cm2/s.
    * **ingress** — a cured specimen is *immersed in* a Cs solution and the nuclide
      diffuses **IN**. Kurumisawa ~4e-12 m2/s = 4e-8 cm2/s.

    That is a **twelve order of magnitude** gap between quantities sharing a name.
    Pooling them is not a bias, it is a category error, so they are separate members
    and :func:`pooling_warning` refuses to let them merge silently.
    """

    LEACHABILITY_INDEX = "leachability_index"   # -log10(De); ANSI/ANS 16.1
    EFFECTIVE_DIFFUSIVITY = "de_cm2_s"          # cm2/s, nuclide leaching OUT
    INGRESS_DIFFUSIVITY = "d_ingress_cm2_s"     # cm2/s, nuclide diffusing IN
    CUMULATIVE_LEACHED_FRACTION = "clf"         # dimensionless fraction of inventory
    LEACHED_PERCENT = "leached_pct"             # % of inventory released


#: Members that are all "a diffusion coefficient" but measure different experiments.
#: Any two of these appearing together is a category error, not a pooling nuisance.
INCOMPATIBLE_DIFFUSIVITIES = {
    RetentionType.EFFECTIVE_DIFFUSIVITY,
    RetentionType.INGRESS_DIFFUSIVITY,
}

#: 1 m2/s = 1e4 cm2/s. Kurumisawa reports m2/s; Kim and Nevin report cm2/s.
M2_S_TO_CM2_S = 1.0e4


#: Direction of merit. True == a larger number means better immobilisation.
HIGHER_IS_BETTER: dict[RetentionType, bool] = {
    RetentionType.LEACHABILITY_INDEX: True,
    RetentionType.EFFECTIVE_DIFFUSIVITY: False,
    RetentionType.INGRESS_DIFFUSIVITY: False,
    RetentionType.CUMULATIVE_LEACHED_FRACTION: False,
    RetentionType.LEACHED_PERCENT: False,
}

#: ANSI/ANS 16.1 acceptance threshold for radioactive cations (Kim p10, Nevin p4).
ANS_16_1_MIN_LI = 6.0


class Censoring(str, Enum):
    """Detection-limit status. NONE is an ordinary measurement."""

    NONE = "none"
    LEFT = "left"    # true value is BELOW the reported bound (better than measured)
    RIGHT = "right"  # true value is ABOVE the reported bound


class MatrixClass(str, Enum):
    """Binder family. Activator cation matters enough to separate Na- from K-."""

    NA_GEOPOLYMER = "na_geopolymer"
    K_GEOPOLYMER = "k_geopolymer"
    FLY_ASH_GEOPOLYMER = "fly_ash_geopolymer"
    SLAG_BLEND = "slag_blend"
    PORTLAND_CEMENT = "portland_cement"
    OTHER = "other"


def li_from_de(de_cm2_s: float) -> float:
    """Leachability index from an effective diffusivity: LI = -log10(De).

    Verified against Kim 2026 Table 2: 12 of 13 published (De, LI) pairs agree to
    within 0.06. The 13th is a typo in the paper — see :data:`KNOWN_SOURCE_ERRATA`.
    """
    if de_cm2_s <= 0:
        raise ValueError("De must be positive to take a logarithm")
    return -math.log10(de_cm2_s)


def de_from_li(li: float) -> float:
    """Inverse of :func:`li_from_de`.

    WARNING: valid only for a single-interval LI. A *mean* LI reported over several
    leaching intervals is a geometric mean of De and does not invert to a meaningful
    single diffusivity (trap 4 in the module docstring).
    """
    return 10.0 ** (-li)


#: Errors found in published sources, with the evidence that establishes them.
KNOWN_SOURCE_ERRATA: dict[str, str] = {
    "kim2026_table2_NaSr1_2h": (
        "Published as '8.88 E-16 (15.5)'. But -log10(8.88e-16) = 15.05, and every "
        "other one of the 12 cells in the table agrees with -log10(De) to within 0.06. "
        "The paper's own Average LI for NaSr1 is 15.5, which is mean(15.05, 15.94) = "
        "15.50 exactly; had the cell truly been 15.5 the average would read 15.7. "
        "The tabulated (15.5) is therefore a typo for (15.1). The column average is "
        "correct, so the reported Average LI is used unchanged."
    ),
}


COLUMNS: list[str] = [
    # identity
    "sample_id", "matrix_name", "matrix_class",
    # the immobilised species
    "nuclide", "loading_wt_pct",          # CONTROL variable, never a target
    # the target
    "retention_value", "retention_type", "retention_std", "censored", "censoring_bound",
    # leaching conditions
    "leachant", "duration_days", "interval_label", "ph_leachant", "temperature_K",
    "surface_area_volume_ratio",
    # pore structure — the transport pathway; Jang 2016 links these directly to De
    "porosity_pct", "capillary_pore_volume_mL_g", "critical_pore_diameter_nm",
    # BET specific surface area. Present so the surface-area hypothesis can be tested in
    # the immobilisation regime too, as it was in Pool A (where it is NEGATIVELY related
    # to uptake). Beware confounding: in Jain 2022 both BET and LX rise with Cs dosage.
    "bet_m2_g",
    # matrix composition
    "si_al", "na_al", "k_al", "ca_al", "precursor", "activator", "activator_molarity",
    # Ca/(Si+Al) — the ratio Ca-bearing slag studies actually report. Kept SEPARATE from
    # ca_al: they are different quantities and mapping one onto the other would be the
    # kind of definition error this schema exists to prevent. Carries the F19/D12
    # structural precondition into the pool, so Ca-bearing rows stay auditable.
    "ca_si_al",
    # structure — the reason Pool B exists at all
    "q4_4al_pct", "q4_3al_pct", "q4_2al_pct", "q4_1al_pct", "q4_0al_pct",
    "si_al_nmr", "ari", "al_iv_pct", "cn_sr_exafs", "chemical_shift_ppm",
    # provenance & quality
    "provenance_doi", "source_label", "leach_state", "from_figure", "value_repeated",
]

NUMERIC: list[str] = [
    "loading_wt_pct", "retention_value", "retention_std", "censoring_bound",
    "duration_days", "ph_leachant", "temperature_K", "surface_area_volume_ratio",
    "porosity_pct", "capillary_pore_volume_mL_g", "critical_pore_diameter_nm", "bet_m2_g",
    "si_al", "na_al", "k_al", "ca_al", "ca_si_al", "activator_molarity",
    "q4_4al_pct", "q4_3al_pct", "q4_2al_pct", "q4_1al_pct", "q4_0al_pct",
    "si_al_nmr", "ari", "al_iv_pct", "cn_sr_exafs", "chemical_shift_ppm",
]

#: plausibility bounds — violations are flagged, never silently clipped
BOUNDS: dict[str, tuple[float, float]] = {
    "loading_wt_pct": (0.0, 50.0),
    "si_al": (0.3, 30.0),
    "ph_leachant": (0.0, 14.0),
    "temperature_K": (273.0, 373.0),
    "duration_days": (0.0, 3650.0),
    "cn_sr_exafs": (4.0, 12.0),   # Sr-O coordination; brewsterite-Sr is ~9
    "porosity_pct": (0.0, 80.0),
}


def empty_frame() -> pd.DataFrame:
    df = pd.DataFrame({c: pd.Series(dtype="object") for c in COLUMNS})
    for c in NUMERIC:
        df[c] = pd.Series(dtype="float64")
    return df


def conform(df: pd.DataFrame) -> pd.DataFrame:
    out = empty_frame()
    for c in COLUMNS:
        out[c] = df[c] if c in df.columns else pd.NA
    for c in NUMERIC:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out.reset_index(drop=True)


def validate(df: pd.DataFrame) -> pd.DataFrame:
    """Schema and plausibility report. Nothing is mutated."""
    issues: list[tuple[str, int, str]] = []

    valid_types = {t.value for t in RetentionType}
    bad = (~df["retention_type"].isin(valid_types)) & df["retention_type"].notna()
    if bad.any():
        issues.append(("bad_retention_type", int(bad.sum()), "not in RetentionType"))

    valid_cens = {c.value for c in Censoring}
    bad = (~df["censored"].isin(valid_cens)) & df["censored"].notna()
    if bad.any():
        issues.append(("bad_censored", int(bad.sum()), "not in Censoring"))

    # trap 3: a censored row must state the bound it is censored at
    cens = df["censored"].isin([Censoring.LEFT.value, Censoring.RIGHT.value])
    missing_bound = cens & df["censoring_bound"].isna()
    if missing_bound.any():
        issues.append(("censored_without_bound", int(missing_bound.sum()),
                       "censored rows must record the detection bound"))

    # A row that DECLARES a retention_type must carry a value (unless censored).
    # A row with no retention_type at all is a legitimate STRUCTURE-ONLY row — it
    # contributes a descriptor (Q4 speciation, EXAFS) without a leaching target, e.g.
    # Nevin's post-leach and control samples. Those are counted, not faulted.
    declared = df["retention_type"].notna()
    no_value = declared & ~cens & df["retention_value"].isna()
    if no_value.any():
        issues.append(("missing_retention_value", int(no_value.sum()),
                       "rows declaring a retention_type but carrying no value"))

    structure_only = int((~declared & ~cens).sum())
    if structure_only:
        issues.append(("structure_only_rows", structure_only,
                       "INFO: descriptor without a retention target - usable for "
                       "structural comparison, not for training a retention model"))

    for col in ("nuclide", "provenance_doi", "source_label"):
        n = int(df[col].isna().sum())
        if n:
            issues.append((f"missing_{col}", n, f"rows lacking {col}"))

    # trap 1: LI below the regulatory floor is a red flag worth surfacing
    li = df["retention_type"] == RetentionType.LEACHABILITY_INDEX.value
    below = li & (pd.to_numeric(df["retention_value"], errors="coerce") < ANS_16_1_MIN_LI)
    if below.any():
        issues.append(("li_below_ans_16_1", int(below.sum()),
                       f"LI < {ANS_16_1_MIN_LI}, the ANSI/ANS 16.1 acceptance floor"))

    for col, (lo, hi) in BOUNDS.items():
        s = pd.to_numeric(df[col], errors="coerce")
        out = ((s < lo) | (s > hi)) & s.notna()
        if out.any():
            issues.append((f"out_of_range_{col}", int(out.sum()), f"outside [{lo}, {hi}]"))

    return pd.DataFrame(issues, columns=["issue", "count", "detail"])


def pooling_warning(df: pd.DataFrame) -> list[str]:
    """Flag combinations that must not be pooled into one training target."""
    warns: list[str] = []

    types = df["retention_type"].dropna().unique()

    # The category error, checked before the milder direction-of-merit warning.
    present = {RetentionType(t) for t in types} & INCOMPATIBLE_DIFFUSIVITIES
    if len(present) > 1:
        warns.append(
            "CATEGORY ERROR: both effective (leaching-OUT) and ingress (diffusing-IN) "
            "diffusivities are present. These share the name 'diffusion coefficient of "
            "Cs' but differ by ~12 orders of magnitude because they measure opposite "
            "experiments. They must NEVER be pooled or compared as one variable."
        )

    if len(types) > 1:
        directions = {t: HIGHER_IS_BETTER[RetentionType(t)] for t in types}
        if len(set(directions.values())) > 1:
            warns.append(
                f"MIXED retention_type with OPPOSING directions of merit {directions} — "
                "a higher LI is better but a higher De is worse; pooling these teaches "
                "the model backwards. Stratify or transform before training."
            )
        else:
            warns.append(f"MIXED retention_type {sorted(types)} — not interconvertible.")

    if df["nuclide"].dropna().nunique() > 1:
        warns.append(
            f"MULTIPLE nuclides {sorted(df['nuclide'].dropna().unique())} — Cs+ and Sr2+ "
            "differ in charge and ionic radius; retention is species-specific."
        )

    n_cens = int(df["censored"].isin([Censoring.LEFT.value, Censoring.RIGHT.value]).sum())
    if n_cens:
        warns.append(
            f"{n_cens} CENSORED row(s) — these are detection-limit results, not missing "
            "data. Left-censored rows are the BEST performers; dropping them biases the "
            "pool toward leakier matrices."
        )

    if df["matrix_class"].dropna().nunique() > 1:
        warns.append(
            f"MULTIPLE matrix classes {sorted(df['matrix_class'].dropna().unique())} — "
            "activator cation changes leaching behaviour (Kim: K-GP resists better than Na-GP)."
        )
    return warns
