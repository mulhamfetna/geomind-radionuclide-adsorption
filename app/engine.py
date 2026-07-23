"""Service layer for the Virtual Lab.

Wraps the tested `geomind` engine and owns the tri-colour honesty rules. The UI
consumes only this module; it never touches the science directly. Every prediction
returns a ResultCard carrying its confidence flag, its reason, and its provenance.
"""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

_ROOT = Path(__file__).resolve().parents[1]

from geomind.model import forward as FW  # noqa: E402


class Confidence(str, Enum):
    VALIDATED = "validated"        # in the trained domain and class -> trustworthy
    EXPLORATORY = "exploratory"    # right class, extrapolating -> shown, unvalidated
    UNSUPPORTED = "unsupported"    # wrong class/adsorbate -> not a prediction we stand behind


@dataclass
class ResultCard:
    value: float | None
    unit: str
    flag: Confidence
    uncertainty: float | None
    why: str
    provenance: str
    extra: dict = field(default_factory=dict)


def classify_domain(al_iv_mmol_g: float, structural_class: str, adsorbate: str) -> Confidence:
    """Where does this input sit relative to the forward model's validated domain?"""
    if structural_class != FW.TRAINING_CLASS or adsorbate != FW.TRAINING_ADSORBATE:
        return Confidence.UNSUPPORTED
    model = _model()
    span = model.x_max - model.x_min
    lo, hi = model.x_min - FW.DOMAIN_PAD * span, model.x_max + FW.DOMAIN_PAD * span
    return Confidence.VALIDATED if lo <= al_iv_mmol_g <= hi else Confidence.EXPLORATORY


_CACHED = {}


def _model():
    """The fitted forward model, cached (fitting reads the pool once)."""
    if "m" not in _CACHED:
        _CACHED["m"] = FW.fit()
    return _CACHED["m"]


_PROVENANCE = ("Forward model (Varon metakaolin geopolymers, Sr; n=7; "
               "LOO-CV R^2=0.81). See reports/forward-model-report.md, finding F37.")


def predict_kd(al_iv_mmol_g: float,
               structural_class: str = "metakaolin geopolymer",
               adsorbate: str = "Sr") -> ResultCard:
    """Predict Sr K_D from framework Al^IV, with a tri-colour confidence flag."""
    model = _model()
    flag = classify_domain(al_iv_mmol_g, structural_class, adsorbate)
    value = model.predict(al_iv_mmol_g, strict=False)  # never raises; flag carries the caveat

    if flag is Confidence.VALIDATED:
        why = ("Cation uptake is ion exchange at framework Al^IV sites; within the "
               "trained metakaolin-geopolymer domain this relationship predicts held-out "
               "samples (LOO-CV R^2=0.81).")
        uncertainty = model.rmse_loo
    elif flag is Confidence.EXPLORATORY:
        why = (f"[Al^IV]={al_iv_mmol_g:.2f} is outside the validated range "
               f"[{model.x_min:.2f}, {model.x_max:.2f}] mmol/g — extrapolation, "
               "unvalidated, for exploration only.")
        uncertainty = None
    else:
        why = (f"The descriptor is not validated for '{structural_class}'/'{adsorbate}' "
               "(F19: the relationship does not carry across structural classes). "
               "This is not a prediction we can stand behind.")
        uncertainty = None

    return ResultCard(value=float(value), unit="mL/g", flag=flag,
                      uncertainty=uncertainty, why=why, provenance=_PROVENANCE,
                      extra={"al_iv_mmol_g": al_iv_mmol_g, "class": structural_class,
                             "adsorbate": adsorbate})


import json as _json  # noqa: E402

from geomind.chemistry import compute_molar_features  # noqa: E402
from geomind.data.nmr_ari import M_WEIGHT  # noqa: E402


def describe_formulation(mass_fractions: dict[str, float]) -> dict:
    """Exact molar descriptors from a precursor/activator mass-fraction mixture."""
    f = compute_molar_features(mass_fractions)
    return {"si_al": f.si_al, "si_m_sol": f.si_m_sol, "solid_liquid": f.solid_liquid}


def ari_from_q4(q4: dict[str, float]) -> float:
    """Al-richness index from a Q4(mAl) deconvolution (percent populations)."""
    unknown = set(q4) - set(M_WEIGHT)
    if unknown:
        raise KeyError(f"unknown Q4 site(s): {sorted(unknown)}")
    return sum(M_WEIGHT[k] * v for k, v in q4.items()) / 100.0


_SAT_PROVENANCE = ("Saturation screen theta = b*C0/(1+b*C0) = 1 - R_L; the "
                   "Langmuir separation factor (F14-F17). See "
                   "reports/forward-model-report.md.")


def screen_saturation(b_L_mg: float, c0_mg_L: float) -> ResultCard:
    """Fractional site saturation theta at C0 from a reported Langmuir b.

    A high-R^2 Langmuir fit is only trustworthy where the experiment actually
    approached saturation. theta = b*C0/(1+b*C0) tells us where on the isotherm
    C0 sat: near 1 the plateau is real (sound), near 0 the fit is a low-coverage
    extrapolation dressed up as an isotherm (artefact).
    """
    bc = b_L_mg * c0_mg_L
    theta = bc / (1.0 + bc)
    if theta >= 0.8:
        verdict = "sound"
        why = (f"theta={theta:.2f}: the experiment reached the plateau, so the "
               "Langmuir capacity is constrained by data, not extrapolation.")
    elif theta >= 0.5:
        verdict = "weakly-constrained"
        why = (f"theta={theta:.2f}: only partway up the isotherm — the plateau "
               "is partly extrapolated; treat the capacity as provisional.")
    else:
        verdict = "artefact"
        why = (f"theta={theta:.2f}: far below saturation — a high R^2 here fits "
               "the initial slope, not a real plateau (F14-F17).")
    return ResultCard(value=float(theta), unit="fraction", flag=Confidence.VALIDATED,
                      uncertainty=None, why=why, provenance=_SAT_PROVENANCE,
                      extra={"verdict": verdict, "b_L_mg": b_L_mg, "c0_mg_L": c0_mg_L,
                             "R_L": float(1.0 - theta)})


def compare_classes(structural_classes: list[str]) -> str | None:
    """Pooling caution for a comparison tray. Returns None if every candidate is
    the same structural class, otherwise a warning: the descriptor does not carry
    across classes (F19/D12), so a side-by-side comparison mixes incomparable
    regressions and must not be read as one relationship."""
    distinct = sorted(set(structural_classes))
    if len(distinct) <= 1:
        return None
    return ("Comparing across structural classes: " + ", ".join(distinct) + ". "
            "The Al^IV descriptor does not pool across classes (F19/D12) — each "
            "class is a separate regression, so read these side by side, not as "
            "one trend.")


def sweep_kd(al_iv_values,
             structural_class: str = "metakaolin geopolymer",
             adsorbate: str = "Sr") -> list[ResultCard]:
    """Predict Sr K_D across a range of [Al^IV], one domain-flagged card per point.
    Drives the what-if sweep view: the green (validated) envelope vs the amber
    (exploratory) extrapolation region are read straight off each card's flag."""
    return [predict_kd(x, structural_class=structural_class, adsorbate=adsorbate)
            for x in al_iv_values]


def export_candidate(bundle: dict, path) -> str:
    """Write a candidate report bundle to a LOCAL JSON file (no network). Returns
    the path written. The bundle is caller-assembled (inputs, descriptors,
    prediction, flags, caveats); this only serialises it."""
    path = Path(path)
    path.write_text(_json.dumps(bundle, indent=2, default=str))
    return str(path)


_CS_POOL_PROV = ("Pooled Cs Langmuir q_max across laboratories (Pool A): LOO-CV of "
                 "Si/Al -> capacity. The F36/D17 pooling limit; cf. manuscript Fig 6b.")


def _cs_langmuir_pool():
    """The cross-laboratory Cs Langmuir q_max rows the sandbox pools over."""
    from geomind.data.merge_adsorption import build
    A = build()
    return A[(A["adsorbate"] == "Cs") & (A["capacity_type"] == "langmuir_qmax")].dropna(
        subset=["si_al", "capacity_mg_g"])


def pooling_sources() -> list[str]:
    """Source labels that contribute Cs Langmuir q_max rows (the sandbox universe)."""
    return sorted(_cs_langmuir_pool()["source_label"].unique())


def pooled_loo_r2(source_labels) -> ResultCard:
    """LOO-CV R^2 of the Si/Al -> Cs-capacity line, pooled over the chosen sources.

    The F36 lesson, hands-on: one laboratory's series can be predictive, but pool across
    laboratories and the leave-one-out R^2 falls below zero — worse than guessing the mean.
    """
    pool = _cs_langmuir_pool()
    sub = pool[pool["source_label"].isin(list(source_labels))]
    x = sub["si_al"].to_numpy(float)
    y = sub["capacity_mg_g"].to_numpy(float)
    n = len(x)
    if n < 3 or float(np.ptp(x)) == 0.0:
        return ResultCard(
            value=None, unit="R^2 (LOO-CV)", flag=Confidence.UNSUPPORTED, uncertainty=None,
            why=(f"Only {n} pooled point(s) with spread — leave-one-out is undefined here. "
                 "Select more sources."),
            provenance=_CS_POOL_PROV,
            extra={"n": n, "verdict": "undefined", "sources": sorted(set(source_labels))})
    r2, rmse = FW._loo(x, y)
    predictive = r2 > 0
    verdict = "predictive" if predictive else "worse-than-mean"
    flag = Confidence.VALIDATED if predictive else Confidence.UNSUPPORTED
    tail = ("still predictive." if predictive else
            "worse than guessing the mean — the descriptor does not survive "
            "cross-laboratory pooling (F36).")
    used = sorted(sub["source_label"].unique())
    why = f"Pooling {used} (n={n}): LOO-CV R^2 = {r2:+.2f} — {tail}"
    return ResultCard(value=float(r2), unit="R^2 (LOO-CV)", flag=flag, uncertainty=float(rmse),
                      why=why, provenance=_CS_POOL_PROV,
                      extra={"n": n, "verdict": verdict, "sources": used})


_STRUCT_PROV = ("oulu2026 NH4+ series (Pool A + nmr_ari): framework (Ca-free) gels vs the "
                "real Ca-bearing gels — the F19/D12 structural precondition; cf. Fig 4. "
                "No fabricated Ca sweep: these are the two actual data groups.")


def structural_precondition(include_ca: bool = False) -> ResultCard:
    """Pearson r of ARI -> NH4+ uptake. Framework-only the relationship is strong; pool in
    the *real* Ca-bearing gels and it degrades (F19/D12) — the descriptor is class-specific."""
    from geomind.data.merge_adsorption import build
    from geomind.data import nmr_ari as N
    A = N.attach(build())
    o = A[(A["source_label"] == "oulu2026") & (A["adsorbate"] == "NH4+")].copy()
    o["ca_free"] = o["ca_al"].fillna(0) == 0
    cf = o[o["ca_free"]].dropna(subset=["ari", "capacity_mg_g"])
    fw_r = float(np.corrcoef(cf["ari"].to_numpy(float), cf["capacity_mg_g"].to_numpy(float))[0, 1])
    grp = o.dropna(subset=["ari", "capacity_mg_g"]) if include_ca else cf
    x = grp["ari"].to_numpy(float)
    y = grp["capacity_mg_g"].to_numpy(float)
    r = float(np.corrcoef(x, y)[0, 1])
    which = "framework + Ca-bearing gels pooled" if include_ca else "framework (Ca-free) gels only"
    why = (f"ARI -> uptake over {which} (n={len(x)}): r = {r:+.2f}. "
           + ("Pooling the Ca-bearing gels in weakens the relationship — the descriptor is "
              "defined only within a structural class (F19/D12)." if include_ca
              else "Within the framework class the descriptor tracks uptake strongly."))
    return ResultCard(value=r, unit="Pearson r", flag=Confidence.VALIDATED, uncertainty=None,
                      why=why, provenance=_STRUCT_PROV,
                      extra={"n": len(x), "framework_r": fw_r, "include_ca": include_ca})


def load_pool(name: str = "A"):
    """Return an audited pool as a DataFrame. 'A' = adsorption (141 rows),
    'B' = immobilisation (54 rows). Read-only; reuses the tested merge builders."""
    key = str(name).strip().upper()
    if key == "A":
        from geomind.data.merge_adsorption import build
        return build()
    if key == "B":
        from geomind.data.merge_immobilisation import build
        return build()
    raise ValueError(f"unknown pool {name!r}; expected 'A' or 'B'")


def _registry() -> dict:
    import yaml
    return yaml.safe_load((_ROOT / "knowledge_base" / "registry.yaml").read_text())


def load_findings() -> list[dict]:
    """The finding register (37 entries), each with id / severity / title / evidence / action."""
    return list(_registry().get("findings", []))


def load_decisions() -> list[dict]:
    """The decision register (17 entries), each with id / decision / reason."""
    return list(_registry().get("decisions", []))


_AUDIT_COLS = ["source_file", "source_table", "n_rows", "veracity", "utility", "reason"]


def load_audit_summary(db_path=None):
    """The per-file veracity audit from the prebuilt warehouse (tables_seen), read-only.
    Every ingested table carries an explicit verdict and a reason.

    The 31 MB warehouse DB is not committed, so when it is absent (a fresh clone) this
    falls back to the committed 91-row summary CSV. Returns an empty frame with the right
    columns if neither exists — never raises. An explicitly supplied `db_path` is taken
    literally: no CSV fallback, so callers can test the missing-DB case.
    """
    import sqlite3
    import pandas as pd
    explicit = db_path is not None
    db = Path(db_path) if explicit else _ROOT / "data" / "warehouse" / "geomind.db"
    if db.exists():
        con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
        try:
            return pd.read_sql_query(
                "SELECT source_file, source_table, n_rows, veracity, utility, reason "
                "FROM tables_seen ORDER BY veracity, n_rows DESC", con)
        finally:
            con.close()
    if not explicit:
        csv = _ROOT / "data" / "warehouse" / "audit_summary.csv"
        if csv.exists():
            return pd.read_csv(csv)[_AUDIT_COLS]
    return pd.DataFrame(columns=_AUDIT_COLS)


def rerun_headline_numbers() -> dict:
    """Recompute the paper's key figures live from the tested engine — the reproducibility
    check: within-class predicts (R^2_LOO ~ 0.81), pooled fails (R^2 < 0), the descriptor is
    strong within the framework class and degrades when Ca gels are pooled in."""
    m = _model()
    pooled = pooled_loo_r2(pooling_sources())
    return {
        "forward_r2_loo": float(m.r2_loo),
        "forward_slope": float(m.slope),
        "forward_intercept": float(m.intercept),
        "pooled_r2": float(pooled.value),
        "framework_r": float(structural_precondition(False).value),
        "pooled_struct_r": float(structural_precondition(True).value),
    }
