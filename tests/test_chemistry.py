"""Validate the chemistry layer against the paper's 10 published samples.

The published subset (paper Table / `GEOMIND_Samples`) reports the derived molar
ratios alongside the precursor mass fractions. Recomputing those ratios from the
mass fractions alone is therefore a genuine oracle test of our independent
implementation — no reference code required.
"""
from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pytest

from src.geomind.chemistry import PRECURSOR_ORDER, compute_molar_features, molar_ratios

RAW = Path("data/raw/GEOMIND_RADIOACTIVE_MASTER.xlsx")

# published column -> our attribute
COLUMN_MAP = {"Si/Al": "si_al", "Si/M_Sol": "si_m_sol", "Solid/Liquid": "solid_liquid"}


def _load_published() -> pd.DataFrame:
    df = pd.read_excel(RAW, sheet_name="GEOMIND_Samples")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _mass_fractions(row: pd.Series) -> dict[str, float]:
    """Pull the 11 precursor mass fractions out of a published row."""
    out = {}
    for name in PRECURSOR_ORDER:
        col = f"{name}(%)"
        val = pd.to_numeric(row.get(col), errors="coerce")
        out[name] = 0.0 if pd.isna(val) else float(val)
    return out


@pytest.fixture(scope="module")
def published() -> pd.DataFrame:
    if not RAW.exists():
        pytest.skip(f"{RAW} not available")
    return _load_published()


def test_precursor_fractions_sum_to_one(published: pd.DataFrame) -> None:
    """Paper: 'precursor data format is a vector whose sum is equal to 1'.

    The published fractions are rounded to 2 dp, so summing 11 of them drifts:
    observed sums run 1.000-1.020. That drift is a property of the *source data*,
    not of our code, and it is the reason the ratio tolerances below are ~3 %.
    """
    for i, row in published.iterrows():
        total = sum(_mass_fractions(row).values())
        assert total == pytest.approx(1.0, abs=0.03), f"row {i}: precursors sum to {total}"


# Tolerance justification: inputs are rounded to 2 dp, so a fraction printed as
# "0.38" is really 0.375-0.385 (~1.3 % uncertainty). Propagated through a ratio of
# sums this yields a few percent. Measured agreement is Si/Al <=1.1 %,
# Solid/Liquid <=1.9 %, Si/M_Sol <=2.7 % across all ten samples, with errors
# scattered either side of zero -- the signature of rounding noise, not bias.
RATIO_REL_TOL = 0.03


@pytest.mark.parametrize("column", list(COLUMN_MAP))
def test_derived_ratios_match_published(published: pd.DataFrame, column: str) -> None:
    """Our recomputed ratios must match the paper's published values."""
    attr = COLUMN_MAP[column]
    errors = []
    for i, row in published.iterrows():
        expected = pd.to_numeric(row.get(column), errors="coerce")
        if pd.isna(expected):
            continue
        got = getattr(compute_molar_features(_mass_fractions(row)), attr)
        if not math.isclose(got, float(expected), rel_tol=RATIO_REL_TOL, abs_tol=0.01):
            errors.append(f"  row {i}: {column} expected {expected:.3f}, got {got:.3f}")
    assert not errors, f"{column} mismatches:\n" + "\n".join(errors)


@pytest.mark.parametrize("column", list(COLUMN_MAP))
def test_ratios_show_no_systematic_bias(published: pd.DataFrame, column: str) -> None:
    """Guards against a wrong formula hiding inside a loose per-row tolerance.

    Rounding noise averages out; a wrong formula would not. So require the *mean
    signed* relative error to be near zero, which per-row tolerances cannot catch.
    """
    attr = COLUMN_MAP[column]
    signed = []
    for _, row in published.iterrows():
        expected = pd.to_numeric(row.get(column), errors="coerce")
        if pd.isna(expected) or not float(expected):
            continue
        got = getattr(compute_molar_features(_mass_fractions(row)), attr)
        signed.append((got - float(expected)) / float(expected))
    mean_bias = sum(signed) / len(signed)
    assert abs(mean_bias) < 0.01, f"{column}: mean signed error {mean_bias:+.4f} suggests bias"


def test_infeasibility_sentinel_is_preserved(published: pd.DataFrame) -> None:
    """-1 marks a chemically infeasible mixture; it is never a measurement."""
    props = [
        "mixture_density(g/cm³)",
        "viscosity(Pa.s)",
        "material_density(g/cm³)",
        "compressive_strength(MPa)",
    ]
    present = [c for c in props if c in published.columns]
    sentinel_rows = (published[present].apply(pd.to_numeric, errors="coerce") == -1).any(axis=1)
    assert sentinel_rows.sum() >= 1, "expected at least one infeasible sample in the subset"


def test_unknown_precursor_rejected() -> None:
    with pytest.raises(KeyError):
        compute_molar_features({"NotAPrecursor": 1.0})


def test_ratios_are_scale_invariant() -> None:
    """Ratios must not depend on the mass basis chosen."""
    mix = {"M1": 0.56, "S1": 0.28, "SNa": 0.05, "KOH": 0.12}
    a = molar_ratios(mix)
    b = molar_ratios({k: v * 7.3 for k, v in mix.items()})
    assert a == pytest.approx(b, rel=1e-12)


def test_pure_metakaolin_has_no_liquid() -> None:
    """No activator -> undefined solid/liquid, and no solution-derived Si."""
    f = compute_molar_features({"M1": 1.0})
    assert math.isnan(f.solid_liquid)
    assert f.n_si_sol == 0.0
    assert f.n_si_met > 0 and f.n_al > 0
