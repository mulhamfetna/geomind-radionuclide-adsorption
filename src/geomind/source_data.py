"""Source data — the numbers behind every figure and table, in one workbook.

Top journals increasingly require a "source data" file: the exact values plotted in each
figure, so a reader can re-draw or re-check any panel without re-running the pipeline. This
module regenerates that file from the LIVE pipeline, so it can never drift from the figures.

    python -m geomind.source_data          # writes data/source-data/GEOMIND-R-source-data.xlsx

Every sheet is derived with the same logic as `manuscript/figures.py`.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))

from geomind.data import nmr_ari as N  # noqa: E402
from geomind.data.merge_adsorption import build as build_A  # noqa: E402
from geomind.data.merge_immobilisation import build as build_B  # noqa: E402
from geomind.model import forward as FM  # noqa: E402

#: Figure-derived theta values (isotherm-validation report, F17/F24) that cannot be computed
#: from b*C0 in the pool (negative-intercept fits / figure reads). Mirrors figures.py.
_REPORT_THETA = {
    "Zhang slag geomaterial": 0.074,
    "Zhang fly-ash geomaterial": 0.365,
    "Kurumisawa N11": 0.499,
}


def _strip(s: str) -> str:
    """Normalise a Varon sorbent name for fresh<->leached matching (as in figures.py)."""
    return re.sub(r"\s*\((inferred|leached 96h)\)", "", s).strip()


def _loo_pred(x: np.ndarray, y: np.ndarray):
    """Leave-one-out predictions and R^2 for a straight-line fit."""
    p = np.empty(len(x))
    for i in range(len(x)):
        m = np.ones(len(x), bool)
        m[i] = False
        b1, b0 = np.polyfit(x[m], y[m], 1)
        p[i] = b1 * x[i] + b0
    r2 = 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    return p, float(r2)


def build_source_data() -> dict[str, pd.DataFrame]:
    """Every figure's underlying values, one DataFrame per panel, plus the audited pools."""
    A = N.attach(build_A())
    out: dict[str, pd.DataFrame] = {}

    # ---- Fig 2 (a) framework Al -> K_D, (b) surface area -> K_D -----------------------
    v = A[A.source_label == "varon2025"].dropna(subset=["al_iv_mmol_g", "bet_m2_g", "kd_mL_g"])
    out["Fig2a_framework_Al"] = v[["sorbent_name", "al_iv_mmol_g", "kd_mL_g"]].reset_index(drop=True)
    out["Fig2b_surface_area"] = v[["sorbent_name", "bet_m2_g", "kd_mL_g"]].reset_index(drop=True)

    # ---- Fig 2 (c) the within-sample causal test (F27) --------------------------------
    f = A[A.source_label == "varon2025"].dropna(subset=["al_iv_mmol_g", "kd_mL_g"]).copy()
    lz = A[A.source_label == "varon_leached2026"].dropna(subset=["al_iv_mmol_g", "kd_mL_g"]).copy()
    f["k"] = f["sorbent_name"].map(_strip)
    lz["k"] = lz["sorbent_name"].map(_strip)
    f = f.set_index("k")
    lz = lz.set_index("k")
    common = [i for i in f.index if i in lz.index]
    out["Fig2c_causal_test"] = pd.DataFrame({
        "sample": common,
        "al_iv_fresh_mmol_g": [f.loc[i, "al_iv_mmol_g"] for i in common],
        "al_iv_leached_mmol_g": [lz.loc[i, "al_iv_mmol_g"] for i in common],
        "delta_al_iv_mmol_g": [f.loc[i, "al_iv_mmol_g"] - lz.loc[i, "al_iv_mmol_g"] for i in common],
        "kd_fresh_mL_g": [f.loc[i, "kd_mL_g"] for i in common],
        "kd_leached_mL_g": [lz.loc[i, "kd_mL_g"] for i in common],
        "delta_kd_mL_g": [f.loc[i, "kd_mL_g"] - lz.loc[i, "kd_mL_g"] for i in common],
    })

    # ---- Fig 3 the forward model, with leave-one-out predictions ---------------------
    tdf = FM.training_data(build_A())
    x = tdf[FM.DESCRIPTOR].to_numpy(float)
    y = tdf[FM.TARGET].to_numpy(float)
    m = FM.fit()
    pred_loo, _ = _loo_pred(x, y)
    out["Fig3_forward_model"] = pd.DataFrame({
        "sorbent_name": tdf["sorbent_name"],
        "al_iv_mmol_g": x,
        "kd_observed_mL_g": y,
        "kd_fitted_mL_g": m.slope * x + m.intercept,
        "kd_predicted_leave_one_out_mL_g": pred_loo,
    })

    # ---- Fig 4 the structural precondition (F19) -------------------------------------
    o = A[(A.source_label == "oulu2026") & (A.adsorbate == "NH4+")].copy()
    o["ca_free"] = o["ca_al"].fillna(0) == 0
    s4 = o.dropna(subset=["ari", "capacity_mg_g"])[
        ["sorbent_name", "ari", "capacity_mg_g", "ca_al", "ca_free"]].copy()
    s4["group"] = np.where(s4["ca_free"], "framework (Ca-free) gel", "Ca-bearing gel")
    out["Fig4_structural"] = s4.drop(columns=["ca_free"]).reset_index(drop=True)

    # ---- Fig 5 the saturation screen (theta = 1 - R_L) -------------------------------
    lang = build_A()
    lang = lang[lang.capacity_type == "langmuir_qmax"].dropna(
        subset=["langmuir_b_L_mg", "initial_conc_mg_L"]).copy()
    bc = lang["langmuir_b_L_mg"] * lang["initial_conc_mg_L"]
    s5 = pd.DataFrame({
        "sorbent_name": lang["sorbent_name"],
        "source_label": lang["source_label"],
        "langmuir_b_L_mg": lang["langmuir_b_L_mg"],
        "initial_conc_mg_L": lang["initial_conc_mg_L"],
        "theta": (bc / (1 + bc)).to_numpy(),
        "theta_origin": "computed from b*C0",
    })
    s5 = pd.concat([s5, pd.DataFrame({
        "sorbent_name": list(_REPORT_THETA),
        "source_label": "isotherm-validation-report",
        "langmuir_b_L_mg": np.nan, "initial_conc_mg_L": np.nan,
        "theta": list(_REPORT_THETA.values()),
        "theta_origin": "figure-derived (F17/F24)",
    })], ignore_index=True)
    s5["verdict"] = np.where(s5.theta < 0.5, "artefact",
                             np.where(s5.theta < 0.8, "weakly-constrained", "sound"))
    out["Fig5_saturation"] = s5.sort_values("theta").reset_index(drop=True)

    # ---- Fig 6 the pooling limit (F36) ----------------------------------------------
    cq = build_A()
    cq = cq[(cq.adsorbate == "Cs") & (cq.capacity_type == "langmuir_qmax")].dropna(
        subset=["si_al", "capacity_mg_g"])
    xp = cq["si_al"].to_numpy(float)
    yp = cq["capacity_mg_g"].to_numpy(float)
    pp, _ = _loo_pred(xp, yp)
    out["Fig6_pooling_limit"] = pd.DataFrame({
        "sorbent_name": cq["sorbent_name"].to_numpy(),
        "source_label": cq["source_label"].to_numpy(),
        "si_al": xp,
        "capacity_observed_mg_g": yp,
        "capacity_predicted_leave_one_out_mg_g": pp,
    })

    # ---- the audited pools ----------------------------------------------------------
    out["PoolA_adsorption"] = build_A()
    out["PoolB_immobilisation"] = build_B()
    return out


def _readme_sheet() -> pd.DataFrame:
    m = FM.fit()
    return pd.DataFrame({
        "field": ["Title", "Authors", "DOI (concept)", "Licence", "Generated by",
                  "Forward model", "Forward LOO-CV R^2", "Note"],
        "value": [
            "GEOMIND-R source data — the values behind every figure",
            "Mulham Fetna; Abdulrazzaq Hammal",
            "10.5281/zenodo.21510123",
            "CC BY 4.0 — reuse freely with attribution; please cite the DOI",
            "python -m geomind.source_data (regenerated from the live pipeline)",
            f"K_D = {m.slope:.0f}*[Al_IV] {m.intercept:+.0f} mL/g (n={m.n})",
            f"{m.r2_loo:.3f}",
            "One sheet per figure panel; PoolA/PoolB are the full audited datasets.",
        ],
    })


def write_xlsx(path=None) -> str:
    """Write every sheet to a single .xlsx workbook (source-data file for submission)."""
    path = Path(path) if path is not None else (
        _ROOT / "data" / "source-data" / "GEOMIND-R-source-data.xlsx")
    path.parent.mkdir(parents=True, exist_ok=True)
    sheets = build_source_data()
    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        _readme_sheet().to_excel(xl, sheet_name="README", index=False)
        for name, df in sheets.items():
            df.to_excel(xl, sheet_name=name[:31], index=False)
    return str(path)


def main() -> None:  # pragma: no cover - CLI convenience
    print("wrote", write_xlsx())


if __name__ == "__main__":  # pragma: no cover
    main()
