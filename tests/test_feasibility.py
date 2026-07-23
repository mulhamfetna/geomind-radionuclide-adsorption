"""Tests for the Feasibility Controller.

The viscosity boundaries are verified against the paper's explicit statements.
The chemical envelope is provisional (gap G3); these tests pin down its *behaviour*
and, critically, record the evidence that the shipped `Feasibility_Ranges` sheet
must not be used.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.geomind.chemistry import PRECURSOR_ORDER, compute_molar_features
from src.geomind.feasibility import (
    INFEASIBLE,
    ViscosityClass,
    apply_sentinel,
    check_feasibility,
    classify_viscosity,
)

RAW = Path("data/raw/GEOMIND_RADIOACTIVE_MASTER.xlsx")
PROPS = [
    "mixture_density(g/cm³)",
    "viscosity(Pa.s)",
    "material_density(g/cm³)",
    "compressive_strength(MPa)",
]


def _published() -> pd.DataFrame:
    if not RAW.exists():
        pytest.skip(f"{RAW} not available")
    df = pd.read_excel(RAW, sheet_name="GEOMIND_Samples")
    df.columns = [str(c).strip() for c in df.columns]
    return df


def _mass_fractions(row: pd.Series) -> dict[str, float]:
    out = {}
    for n in PRECURSOR_ORDER:
        v = pd.to_numeric(row.get(f"{n}(%)"), errors="coerce")
        out[n] = 0.0 if pd.isna(v) else float(v)
    return out


# --- viscosity: verified against the paper --------------------------------


@pytest.mark.parametrize(
    "value,expected",
    [
        (0.2, ViscosityClass.LOW),
        (1.99, ViscosityClass.LOW),
        (2.0, ViscosityClass.MEDIUM),   # "low is BELOW 2 Pa s"
        (50.0, ViscosityClass.MEDIUM),
        (100.0, ViscosityClass.MEDIUM),  # "high is ABOVE 100 Pa s"
        (100.1, ViscosityClass.HIGH),
        (1314.0, ViscosityClass.HIGH),
    ],
)
def test_viscosity_classes(value: float, expected: ViscosityClass) -> None:
    assert classify_viscosity(value) is expected


# --- provisional envelope behaviour ---------------------------------------


def test_published_feasible_samples_pass_the_provisional_envelope() -> None:
    """The envelope is fitted to these, so this is a consistency check, not proof."""
    df = _published()
    infeasible = (df[PROPS].apply(pd.to_numeric, errors="coerce") == INFEASIBLE).any(axis=1)
    failures = []
    for i, row in df.iterrows():
        if infeasible.iloc[i]:
            continue
        v = check_feasibility(_mass_fractions(row))
        if not v.feasible:
            failures.append(f"row {i}: {v.violations}")
    assert not failures, "feasible samples rejected:\n" + "\n".join(failures)


def test_verdict_is_flagged_provisional_until_g3_closes() -> None:
    """Callers must be able to see that this is not the paper's real domain."""
    v = check_feasibility({"M1": 0.5, "S1": 0.3, "KOH": 0.2})
    assert v.provisional is True
    # supplying a real envelope clears the flag
    v2 = check_feasibility({"M1": 0.5, "S1": 0.3, "KOH": 0.2}, envelope={"si_al": (0, 99)})
    assert v2.provisional is False


def test_mixture_with_no_activator_is_infeasible() -> None:
    """Pure metakaolin cannot geopolymerise: solid/liquid is undefined."""
    v = check_feasibility({"M1": 1.0})
    assert not v.feasible
    assert any("undefined" in s for s in v.violations)


def test_sentinel_overwrites_all_properties() -> None:
    props = {"viscosity": 5.0, "mixture_density": 1.8, "strength": 40.0}
    bad = check_feasibility({"M1": 1.0})
    assert apply_sentinel(props, bad) == {k: INFEASIBLE for k in props}
    good = check_feasibility({"M1": 0.5, "S1": 0.3, "KOH": 0.2}, envelope={"si_al": (0, 99)})
    assert apply_sentinel(props, good) == props


# --- the shipped Feasibility_Ranges sheet is NOT usable (evidence) --------


def test_shipped_feasibility_ranges_sheet_is_anticorrelated_with_truth() -> None:
    """Regression guard for finding F6.

    If anyone later wires `Feasibility_Ranges` into the controller, this test
    documents why that is wrong: the sheet's chemical ranges reject most genuinely
    feasible samples and accept the infeasible one.
    """
    df = _published()
    fr = pd.read_excel(RAW, sheet_name="Feasibility_Ranges")
    rng = {r.Parameter: (r.Min_Value, r.Max_Value) for r in fr.itertuples()}
    infeasible = (df[PROPS].apply(pd.to_numeric, errors="coerce") == INFEASIBLE).any(axis=1)

    wrongly_rejected = wrongly_accepted = 0
    for i, row in df.iterrows():
        f = compute_molar_features(_mass_fractions(row))
        ok = (
            rng["Si/Al_Ratio"][0] <= f.si_al <= rng["Si/Al_Ratio"][1]
            and rng["Si/M_Ratio"][0] <= f.si_m_sol <= rng["Si/M_Ratio"][1]
            and rng["Solid/Liquid"][0] <= f.solid_liquid <= rng["Solid/Liquid"][1]
        )
        if infeasible.iloc[i] and ok:
            wrongly_accepted += 1
        elif not infeasible.iloc[i] and not ok:
            wrongly_rejected += 1

    assert wrongly_rejected >= 6, "sheet unexpectedly accurate — re-open F6"
    assert wrongly_accepted >= 1, "sheet unexpectedly accurate — re-open F6"
