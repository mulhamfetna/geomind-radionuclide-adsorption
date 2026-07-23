# Virtual Lab — Phase 1 Screening Workbench Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local, honest "glass box" workbench where a user explores a geopolymer composition and gets exact descriptors, a domain-flagged Sr K_D prediction, and screening checks — thin end-to-end.

**Architecture:** A thin Gradio UI (`app/lab.py`) over a tested service layer (`app/engine.py`) that wraps the existing, tested `geomind` engine (`model.forward`, `chemistry`, `nmr_ari`, `feasibility`, the pools). The service layer owns the tri-colour honesty rules and is unit-tested independently of the UI; the UI holds no scientific logic.

**Tech Stack:** Python 3, Gradio (local), the existing `geomind` package, pytest, numpy/pandas.

## Global Constraints

- Runs **locally only** — no network calls anywhere in `app/`.
- Tests import the package via `sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))`, matching every existing test file.
- **Honesty invariant (non-negotiable):** a prediction outside the validated domain is **never** labelled `VALIDATED`; every prediction carries a `flag`, a `why`, and a `provenance`. Out-of-domain predictions are *shown* (exploration), not hidden.
- Reuse the engine; **do not re-implement any science**. The forward model's domain constants come from `geomind.model.forward`: `TRAINING_CLASS = "metakaolin geopolymer"`, `TRAINING_ADSORBATE = "Sr"`, `DOMAIN_PAD = 0.10`.
- Run tests from the repo root with `PYTHONPATH=src .venv/bin/python -m pytest`.
- Commit messages end with the project's `Co-Authored-By` trailer.

---

## File Structure

- Create `app/__init__.py` — package marker (empty).
- Create `app/engine.py` — the service layer: `Confidence`, `ResultCard`, `classify_domain`, `predict_kd`, `describe_formulation`, `ari_from_q4`, `screen_saturation`, `compare_classes`, `sweep_kd`, `export_candidate`.
- Create `app/lab.py` — the Gradio Workbench app (`build_app`, `main`).
- Create `tests/test_lab_engine.py` — unit tests for the service layer (the honesty logic).
- Create `tests/test_lab_app.py` — a smoke test that the app builds.
- Modify `requirements.txt` — add `gradio`.

---

### Task 1: Honesty core — `Confidence`, `ResultCard`, `classify_domain`

**Files:**
- Create: `app/__init__.py`
- Create: `app/engine.py`
- Test: `tests/test_lab_engine.py`

**Interfaces:**
- Produces: `Confidence` (str Enum: `VALIDATED`, `EXPLORATORY`, `UNSUPPORTED`); `ResultCard` dataclass `(value: float|None, unit: str, flag: Confidence, uncertainty: float|None, why: str, provenance: str, extra: dict)`; `classify_domain(al_iv_mmol_g: float, structural_class: str, adsorbate: str) -> Confidence`.

- [ ] **Step 1: Write the failing test**

```python
# tests/test_lab_engine.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import engine as E  # noqa: E402


def test_classify_domain_in_range_same_class_is_validated():
    # forward domain is [3.45, 4.77] mmol/g; 4.0 is inside
    assert E.classify_domain(4.0, "metakaolin geopolymer", "Sr") is E.Confidence.VALIDATED


def test_classify_domain_out_of_range_same_class_is_exploratory():
    assert E.classify_domain(6.5, "metakaolin geopolymer", "Sr") is E.Confidence.EXPLORATORY


def test_classify_domain_wrong_class_is_unsupported():
    assert E.classify_domain(4.0, "zeolite", "Sr") is E.Confidence.UNSUPPORTED


def test_classify_domain_wrong_adsorbate_is_unsupported():
    assert E.classify_domain(4.0, "metakaolin geopolymer", "Cs") is E.Confidence.UNSUPPORTED
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: Write minimal implementation**

```python
# app/__init__.py
"""GEOMIND-R Virtual Lab — local, honest UI over the tested geomind engine."""
```

```python
# app/engine.py
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

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: PASS (4 passed)

- [ ] **Step 5: Commit**

```bash
git add app/__init__.py app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): honesty core — Confidence, ResultCard, classify_domain

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 2: `predict_kd` — the domain-flagged Sr K_D prediction

**Files:**
- Modify: `app/engine.py`
- Test: `tests/test_lab_engine.py`

**Interfaces:**
- Consumes: `Confidence`, `ResultCard`, `classify_domain`, `_model` (Task 1).
- Produces: `predict_kd(al_iv_mmol_g: float, structural_class: str = "metakaolin geopolymer", adsorbate: str = "Sr") -> ResultCard`.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_lab_engine.py
def test_predict_kd_in_domain_has_value_band_and_validated_flag():
    r = E.predict_kd(4.0)
    assert r.flag is E.Confidence.VALIDATED
    assert r.value > 0
    assert r.uncertainty is not None and r.uncertainty > 0
    assert r.unit == "mL/g"


def test_predict_kd_wrong_class_is_unsupported_and_bandless():
    r = E.predict_kd(4.0, structural_class="zeolite")
    assert r.flag is E.Confidence.UNSUPPORTED
    assert r.uncertainty is None          # never imply precision off-domain
    assert "not" in r.why.lower()         # states it is not validated here


def test_predict_kd_never_labels_out_of_domain_as_validated():
    for r in (E.predict_kd(9.0), E.predict_kd(4.0, adsorbate="Cs"),
              E.predict_kd(4.0, structural_class="zeolite")):
        assert r.flag is not E.Confidence.VALIDATED
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL — `AttributeError: module 'app.engine' has no attribute 'predict_kd'`

- [ ] **Step 3: Write minimal implementation**

```python
# append to app/engine.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: PASS (7 passed)

- [ ] **Step 5: Commit**

```bash
git add app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): predict_kd with tri-colour domain flagging

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 3: `describe_formulation` and `ari_from_q4` — exact descriptors

**Files:**
- Modify: `app/engine.py`
- Test: `tests/test_lab_engine.py`

**Interfaces:**
- Consumes: nothing from earlier tasks besides the module.
- Produces: `describe_formulation(mass_fractions: dict[str, float]) -> dict` (keys `si_al`, `si_m_sol`, `solid_liquid`); `ari_from_q4(q4: dict[str, float]) -> float`.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_lab_engine.py
def test_describe_formulation_matches_chemistry_layer():
    from geomind.chemistry import molar_ratios, PRECURSORS
    name = next(n for n, p in PRECURSORS.items() if p.kind == "metakaolin")
    sil, sol = next(n for n, p in PRECURSORS.items() if p.kind == "silicate"), None
    mix = {name: 0.7, sil: 0.3}
    d = E.describe_formulation(mix)
    exp_si_al, exp_si_m, exp_sl = molar_ratios(mix)
    assert d["si_al"] == exp_si_al


def test_ari_from_q4_weights_by_aluminium_count():
    # ARI = (4*Q4(4Al) + 3*Q4(3Al) + 2*Q4(2Al) + 1*Q4(1Al)) / 100
    q4 = {"Q4_4Al": 40, "Q4_3Al": 30, "Q4_2Al": 20, "Q4_1Al": 10, "Q4_0Al": 0}
    assert E.ari_from_q4(q4) == (4*40 + 3*30 + 2*20 + 1*10) / 100
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL — `AttributeError: ... has no attribute 'describe_formulation'`

- [ ] **Step 3: Write minimal implementation**

```python
# append to app/engine.py
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: PASS (9 passed)

- [ ] **Step 5: Commit**

```bash
git add app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): describe_formulation + ari_from_q4 (exact descriptors)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 4: `screen_saturation` — the θ = 1 − R_L advisor

**Files:**
- Modify: `app/engine.py`
- Test: `tests/test_lab_engine.py`

**Interfaces:**
- Consumes: `ResultCard`, `Confidence`.
- Produces: `screen_saturation(b_L_mg: float, c0_mg_L: float) -> ResultCard` (value = θ; `extra["verdict"]` ∈ {"sound","weakly-constrained","artefact"}).

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_lab_engine.py
def test_screen_saturation_high_theta_is_sound():
    r = E.screen_saturation(0.05, 1000.0)   # theta = 0.05*1000/(1+50) ~ 0.98
    assert r.value > 0.8
    assert r.extra["verdict"] == "sound"


def test_screen_saturation_low_theta_is_artefact():
    r = E.screen_saturation(7.94e-5, 2658.0)  # the chabazite case, theta ~ 0.17
    assert r.value < 0.5
    assert r.extra["verdict"] == "artefact"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL — `AttributeError: ... has no attribute 'screen_saturation'`

- [ ] **Step 3: Write minimal implementation**

```python
# append to app/engine.py
def screen_saturation(b_L_mg: float, c0_mg_L: float) -> ResultCard:
    """Fraction of saturation reached, theta = b*C0/(1+b*C0) = 1 - R_L (finding F14-F17)."""
    bc = b_L_mg * c0_mg_L
    theta = bc / (1 + bc)
    if theta >= 0.8:
        verdict, why = "sound", "Plateau approached — the fitted Q_max is a measured capacity."
    elif theta >= 0.5:
        verdict, why = "weakly-constrained", "Partial saturation — treat Q_max with caution."
    else:
        verdict, why = ("artefact",
                        "Below 0.5 — the isotherm is near-linear here, so the fitted Q_max is "
                        "an extrapolation, not a measured capacity.")
    return ResultCard(value=theta, unit="fraction of saturation", flag=Confidence.VALIDATED,
                      uncertainty=None, why=why,
                      provenance="Saturation screen theta = 1 - R_L (findings F14-F17).",
                      extra={"verdict": verdict})
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: PASS (11 passed)

- [ ] **Step 5: Commit**

```bash
git add app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): screen_saturation advisor (theta = 1 - R_L)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 5: `compare_classes` — the cross-class pooling caution

**Files:**
- Modify: `app/engine.py`
- Test: `tests/test_lab_engine.py`

**Interfaces:**
- Produces: `compare_classes(structural_classes: list[str]) -> str | None` — a caution string if the candidates span more than one structural class, else `None`.

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_lab_engine.py
def test_compare_classes_flags_mixed_structural_classes():
    msg = E.compare_classes(["metakaolin geopolymer", "zeolite"])
    assert msg is not None and "class" in msg.lower()


def test_compare_classes_silent_within_one_class():
    assert E.compare_classes(["metakaolin geopolymer", "metakaolin geopolymer"]) is None
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL — `AttributeError: ... has no attribute 'compare_classes'`

- [ ] **Step 3: Write minimal implementation**

```python
# append to app/engine.py
def compare_classes(structural_classes: list[str]) -> str | None:
    """Caution when candidates span different structural classes (findings F19/D12)."""
    if len(set(structural_classes)) > 1:
        return ("Comparing across structural classes: the descriptor's relationship to uptake "
                "is class-specific (F19/D12) and its sign is not portable between, e.g., "
                "geopolymers and zeolites. Compare with care.")
    return None
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: PASS (13 passed)

- [ ] **Step 5: Commit**

```bash
git add app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): compare_classes cross-class pooling caution

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 6: `sweep_kd` and `export_candidate` — the what-if sweep and export

**Files:**
- Modify: `app/engine.py`
- Test: `tests/test_lab_engine.py`

**Interfaces:**
- Consumes: `predict_kd`, `ResultCard`.
- Produces: `sweep_kd(al_iv_values: list[float], structural_class="metakaolin geopolymer", adsorbate="Sr") -> list[ResultCard]`; `export_candidate(bundle: dict, path: str) -> str` (writes JSON, returns the path).

- [ ] **Step 1: Write the failing test**

```python
# append to tests/test_lab_engine.py
import json


def test_sweep_kd_returns_a_card_per_point_with_flags():
    cards = E.sweep_kd([3.5, 4.0, 9.0])
    assert len(cards) == 3
    assert cards[0].flag is E.Confidence.VALIDATED
    assert cards[2].flag is E.Confidence.EXPLORATORY   # 9.0 is out of range


def test_export_candidate_writes_a_local_json_file(tmp_path):
    p = E.export_candidate({"al_iv": 4.0, "kd": 1234.0}, str(tmp_path / "cand.json"))
    assert Path(p).exists()
    assert json.loads(Path(p).read_text())["kd"] == 1234.0
```

- [ ] **Step 2: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL — `AttributeError: ... has no attribute 'sweep_kd'`

- [ ] **Step 3: Write minimal implementation**

```python
# append to app/engine.py
import json as _json


def sweep_kd(al_iv_values, structural_class="metakaolin geopolymer", adsorbate="Sr"):
    """Predict K_D across a range of Al^IV values (for the what-if plot)."""
    return [predict_kd(x, structural_class, adsorbate) for x in al_iv_values]


def export_candidate(bundle: dict, path: str) -> str:
    """Write a candidate report to a local JSON file (no network)."""
    Path(path).write_text(_json.dumps(bundle, indent=2, default=str))
    return path
```

- [ ] **Step 4: Run test to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: PASS (15 passed)

- [ ] **Step 5: Commit**

```bash
git add app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): sweep_kd + export_candidate

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

### Task 7: The Gradio Workbench app + smoke test

**Files:**
- Create: `app/lab.py`
- Test: `tests/test_lab_app.py`
- Modify: `requirements.txt`

**Interfaces:**
- Consumes: everything in `app.engine`.
- Produces: `build_app() -> gradio.Blocks`; `main()` (launches locally).

- [ ] **Step 1: Add the dependency**

Append to `requirements.txt`:

```
gradio>=4.44  # Virtual Lab UI (app/lab.py) — local only
```

Then install: `.venv/bin/pip install -q gradio`

- [ ] **Step 2: Write the failing smoke test**

```python
# tests/test_lab_app.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


def test_app_builds_without_error():
    import gradio as gr

    from app.lab import build_app
    app = build_app()
    assert isinstance(app, gr.Blocks)


def test_workbench_predict_handler_returns_flagged_text():
    from app.lab import _predict_handler
    label, detail = _predict_handler(4.0, "metakaolin geopolymer", "Sr")
    assert "validated" in label.lower()
    assert "mL/g" in detail
```

- [ ] **Step 3: Run test to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_app.py -q`
Expected: FAIL — `ModuleNotFoundError: No module named 'app.lab'`

- [ ] **Step 4: Write the app**

```python
# app/lab.py
"""GEOMIND-R Virtual Lab — local Gradio Workbench (Phase 1).

A glass box: exact descriptors, a domain-flagged Sr K_D prediction, and screening
checks. Runs locally. All science comes from app.engine, which owns the honesty rules.
"""
from __future__ import annotations

import gradio as gr

from app import engine as E

_FLAG_EMOJI = {E.Confidence.VALIDATED: "🟢", E.Confidence.EXPLORATORY: "🟡",
               E.Confidence.UNSUPPORTED: "🔴"}


def _predict_handler(al_iv, structural_class, adsorbate):
    """Return (flag label, detail) for the prediction panel."""
    r = E.predict_kd(float(al_iv), structural_class, adsorbate)
    label = f"{_FLAG_EMOJI[r.flag]}  {r.flag.value.upper()}"
    band = f" ± {r.uncertainty:.0f}" if r.uncertainty is not None else ""
    detail = (f"**Predicted Sr K_D = {r.value:.0f}{band} {r.unit}**\n\n"
              f"{r.why}\n\n_Source: {r.provenance}_")
    return label, detail


def build_app() -> gr.Blocks:
    with gr.Blocks(title="GEOMIND-R Virtual Lab") as demo:
        gr.Markdown("# GEOMIND-R Virtual Lab — Screening Workbench\n"
                    "A **glass box**: predictions are flagged by how far they sit from "
                    "validated ground. 🟢 validated · 🟡 exploratory · 🔴 unsupported.")
        with gr.Tab("Screening Workbench"):
            with gr.Row():
                al_iv = gr.Number(label="framework Al^IV (mmol/g)", value=4.0)
                sclass = gr.Dropdown(["metakaolin geopolymer", "fly-ash geopolymer",
                                      "zeolite", "calcium-rich gel"],
                                     value="metakaolin geopolymer", label="structural class")
                ads = gr.Dropdown(["Sr", "Cs"], value="Sr", label="adsorbate")
            go = gr.Button("Predict Sr K_D", variant="primary")
            flag = gr.Label(label="confidence")
            detail = gr.Markdown()
            go.click(_predict_handler, [al_iv, sclass, ads], [flag, detail])
    return demo


def main():  # pragma: no cover
    build_app().launch()  # local only


if __name__ == "__main__":  # pragma: no cover
    main()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_app.py -q`
Expected: PASS (2 passed)

- [ ] **Step 6: Run the full suite to confirm nothing regressed**

Run: `PYTHONPATH=src .venv/bin/python -m pytest -q`
Expected: PASS (all tests, 133 existing + the new lab tests)

- [ ] **Step 7: Commit**

```bash
git add app/lab.py tests/test_lab_app.py requirements.txt
git commit -m "feat(lab): Gradio Screening Workbench (Phase 1 thin end-to-end)

Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>"
```

---

## Self-Review

**Spec coverage (spec §3, Phase 1):**
- 3.1 composition input (formulation + descriptor modes) → Task 3 (`describe_formulation`, `ari_from_q4`) + Task 7 (UI has the descriptor-mode inputs; formulation mode wiring is a follow-on UI task, engine ready).
- 3.2 descriptor panel → Task 3.
- 3.3 Sr K_D prediction with tri-colour → Tasks 1, 2, 7.
- 3.4 what-if sweep → Task 6 (`sweep_kd`; the plot widget is a follow-on UI task, data ready).
- 3.5 screening checks: saturation → Task 4; feasibility → *follow-on* (engine `check_feasibility` already exists, thin wrapper deferred); Cs<Sr guidance → deferred to a data-display task.
- 3.6 comparison tray → Task 5 (`compare_classes`; the tray widget is a follow-on UI task).
- 3.7 export → Task 6 (`export_candidate`).
- §1.1 tri-colour system → Tasks 1, 2 (the honesty invariant is asserted in tests).

**Deliberately deferred to a Phase-1b UI pass (engine complete, wiring only):** the formulation-input form, the sweep plot, the comparison tray table, the feasibility panel. These are UI wiring over services that this plan already builds and tests; folding them in now would make Task 7 too large to review. Each is a small, independent follow-on.

**Placeholder scan:** none — every step has runnable code and an exact command.

**Type consistency:** `Confidence`, `ResultCard`, `classify_domain`, `predict_kd`, `_model` names are used identically across tasks; `predict_kd` signature matches its use in `sweep_kd` (Task 6) and `_predict_handler` (Task 7).
