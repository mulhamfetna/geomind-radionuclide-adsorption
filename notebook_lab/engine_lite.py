"""Self-contained mirror of the desktop Virtual Lab engine (app/engine.py).

Reads only lab_bundle.json — no geomind package, no data files. Its numeric logic and prose
mirror the desktop engine; tests/test_notebook_mirror.py proves the two agree. This module is
embedded verbatim into the shareable Colab notebook.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

# --- bundle loading (env override -> cwd -> module dir) --------------------------------------
_CACHE: dict = {}


def _bundle() -> dict:
    if "b" not in _CACHE:
        candidates = []
        if os.environ.get("LAB_BUNDLE"):
            candidates.append(Path(os.environ["LAB_BUNDLE"]))
        candidates.append(Path.cwd() / "lab_bundle.json")
        candidates.append(Path(__file__).resolve().parent / "lab_bundle.json")
        for p in candidates:
            if p.exists():
                _CACHE["b"] = json.loads(p.read_text())
                break
        else:
            raise FileNotFoundError("lab_bundle.json not found (set $LAB_BUNDLE)")
    return _CACHE["b"]


# --- constants (mirror geomind.model.forward) -----------------------------------------------
TRAINING_CLASS = "metakaolin geopolymer"
TRAINING_ADSORBATE = "Sr"
DOMAIN_PAD = 0.10


# --- types (mirror app.engine) --------------------------------------------------------------
class Confidence(str, Enum):
    VALIDATED = "validated"
    EXPLORATORY = "exploratory"
    UNSUPPORTED = "unsupported"


@dataclass
class ResultCard:
    value: float | None
    unit: str
    flag: Confidence
    uncertainty: float | None
    why: str
    provenance: str
    extra: dict = field(default_factory=dict)


# --- numeric helpers ------------------------------------------------------------------------
def _fit(x, y):
    n = len(x)
    sx = sum(x); sy = sum(y); sxx = sum(v * v for v in x); sxy = sum(a * b for a, b in zip(x, y))
    denom = n * sxx - sx * sx
    slope = (n * sxy - sx * sy) / denom
    intercept = (sy - slope * sx) / n
    return slope, intercept


def _loo(x, y):
    """Leave-one-out CV of a straight-line fit -> (R^2, RMSE). Mirrors forward._loo."""
    n = len(x)
    pred = []
    for i in range(n):
        xx = [x[j] for j in range(n) if j != i]
        yy = [y[j] for j in range(n) if j != i]
        b1, b0 = _fit(xx, yy)
        pred.append(b1 * x[i] + b0)
    ybar = sum(y) / n
    ss_res = sum((y[i] - pred[i]) ** 2 for i in range(n))
    ss_tot = sum((v - ybar) ** 2 for v in y)
    r2 = 1.0 - ss_res / ss_tot
    rmse = (ss_res / n) ** 0.5
    return r2, rmse


def _corr(x, y):
    n = len(x)
    mx = sum(x) / n; my = sum(y) / n
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    sx = sum((v - mx) ** 2 for v in x) ** 0.5
    sy = sum((v - my) ** 2 for v in y) ** 0.5
    return cov / (sx * sy)


# --- prediction -----------------------------------------------------------------------------
def _fwd():
    return _bundle()["forward"]


def classify_domain(al_iv_mmol_g: float, structural_class: str, adsorbate: str) -> Confidence:
    if structural_class != TRAINING_CLASS or adsorbate != TRAINING_ADSORBATE:
        return Confidence.UNSUPPORTED
    f = _fwd()
    span = f["x_max"] - f["x_min"]
    lo, hi = f["x_min"] - DOMAIN_PAD * span, f["x_max"] + DOMAIN_PAD * span
    return Confidence.VALIDATED if lo <= al_iv_mmol_g <= hi else Confidence.EXPLORATORY


_PROVENANCE = ("Forward model (Varon metakaolin geopolymers, Sr; n=7; "
               "LOO-CV R^2=0.81). See reports/forward-model-report.md, finding F37.")


def predict_kd(al_iv_mmol_g: float,
               structural_class: str = "metakaolin geopolymer",
               adsorbate: str = "Sr") -> ResultCard:
    """Predict Sr K_D from framework Al^IV, with a tri-colour confidence flag."""
    f = _fwd()
    flag = classify_domain(al_iv_mmol_g, structural_class, adsorbate)
    value = f["slope"] * al_iv_mmol_g + f["intercept"]

    if flag is Confidence.VALIDATED:
        why = ("Cation uptake is ion exchange at framework Al^IV sites; within the "
               "trained metakaolin-geopolymer domain this relationship predicts held-out "
               "samples (LOO-CV R^2=0.81).")
        uncertainty = f["rmse_loo"]
    elif flag is Confidence.EXPLORATORY:
        why = (f"[Al^IV]={al_iv_mmol_g:.2f} is outside the validated range "
               f"[{f['x_min']:.2f}, {f['x_max']:.2f}] mmol/g — extrapolation, "
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


def sweep_kd(al_iv_values, structural_class="metakaolin geopolymer", adsorbate="Sr"):
    return [predict_kd(x, structural_class=structural_class, adsorbate=adsorbate)
            for x in al_iv_values]


# --- saturation screen ----------------------------------------------------------------------
_SAT_PROVENANCE = ("Saturation screen theta = b*C0/(1+b*C0) = 1 - R_L; the "
                   "Langmuir separation factor (F14-F17). See "
                   "reports/forward-model-report.md.")


def screen_saturation(b_L_mg: float, c0_mg_L: float) -> ResultCard:
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


# --- pooling sandbox ------------------------------------------------------------------------
_CS_POOL_PROV = ("Pooled Cs Langmuir q_max across laboratories (Pool A): LOO-CV of "
                 "Si/Al -> capacity. The F36/D17 pooling limit; cf. manuscript Fig 6b.")


def pooling_sources() -> list[str]:
    return sorted({r["source_label"] for r in _bundle()["cs_pool"]})


def pooled_loo_r2(source_labels) -> ResultCard:
    want = set(source_labels)
    rows = [r for r in _bundle()["cs_pool"] if r["source_label"] in want]
    x = [r["si_al"] for r in rows]
    y = [r["capacity_mg_g"] for r in rows]
    n = len(x)
    if n < 3 or (max(x) - min(x)) == 0.0:
        return ResultCard(
            value=None, unit="R^2 (LOO-CV)", flag=Confidence.UNSUPPORTED, uncertainty=None,
            why=(f"Only {n} pooled point(s) with spread — leave-one-out is undefined here. "
                 "Select more sources."),
            provenance=_CS_POOL_PROV,
            extra={"n": n, "verdict": "undefined", "sources": sorted(want)})
    r2, rmse = _loo(x, y)
    predictive = r2 > 0
    verdict = "predictive" if predictive else "worse-than-mean"
    flag = Confidence.VALIDATED if predictive else Confidence.UNSUPPORTED
    tail = ("still predictive." if predictive else
            "worse than guessing the mean — the descriptor does not survive "
            "cross-laboratory pooling (F36).")
    used = sorted({r["source_label"] for r in rows})
    why = f"Pooling {used} (n={n}): LOO-CV R^2 = {r2:+.2f} — {tail}"
    return ResultCard(value=float(r2), unit="R^2 (LOO-CV)", flag=flag, uncertainty=float(rmse),
                      why=why, provenance=_CS_POOL_PROV,
                      extra={"n": n, "verdict": verdict, "sources": used})


# --- structural precondition ----------------------------------------------------------------
_STRUCT_PROV = ("oulu2026 NH4+ series (Pool A + nmr_ari): framework (Ca-free) gels vs the "
                "real Ca-bearing gels — the F19/D12 structural precondition; cf. Fig 4. "
                "No fabricated Ca sweep: these are the two actual data groups.")


def structural_precondition(include_ca: bool = False) -> ResultCard:
    s = _bundle()["struct"]
    fw = s["framework"]
    fw_r = _corr([p["ari"] for p in fw], [p["cap"] for p in fw])
    grp = fw + s["ca"] if include_ca else fw
    x = [p["ari"] for p in grp]
    y = [p["cap"] for p in grp]
    r = _corr(x, y)
    which = "framework + Ca-bearing gels pooled" if include_ca else "framework (Ca-free) gels only"
    why = (f"ARI -> uptake over {which} (n={len(x)}): r = {r:+.2f}. "
           + ("Pooling the Ca-bearing gels in weakens the relationship — the descriptor is "
              "defined only within a structural class (F19/D12)." if include_ca
              else "Within the framework class the descriptor tracks uptake strongly."))
    return ResultCard(value=float(r), unit="Pearson r", flag=Confidence.VALIDATED, uncertainty=None,
                      why=why, provenance=_STRUCT_PROV,
                      extra={"n": len(x), "framework_r": float(fw_r), "include_ca": include_ca})


# --- reproducibility console data -----------------------------------------------------------
def load_pool(name: str = "A"):
    import pandas as pd
    key = str(name).strip().upper()
    if key == "A":
        return pd.DataFrame(_bundle()["pool_a"])
    if key == "B":
        return pd.DataFrame(_bundle()["pool_b"])
    raise ValueError(f"unknown pool {name!r}; expected 'A' or 'B'")


def load_findings() -> list[dict]:
    return list(_bundle()["findings"])


def load_decisions() -> list[dict]:
    return list(_bundle()["decisions"])


def load_audit_summary(db_path=None):
    import pandas as pd
    cols = ["source_file", "source_table", "n_rows", "veracity", "utility", "reason"]
    return pd.DataFrame(_bundle()["audit"], columns=cols)


def rerun_headline_numbers() -> dict:
    f = _fwd()
    pooled = pooled_loo_r2(pooling_sources())
    return {
        "forward_r2_loo": float(f["r2_loo"]),
        "forward_slope": float(f["slope"]),
        "forward_intercept": float(f["intercept"]),
        "pooled_r2": float(pooled.value),
        "framework_r": float(structural_precondition(False).value),
        "pooled_struct_r": float(structural_precondition(True).value),
    }
