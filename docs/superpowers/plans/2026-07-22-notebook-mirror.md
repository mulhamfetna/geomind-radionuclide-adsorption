# Virtual Lab Notebook Mirror — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement
> this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship a single self-contained Colab notebook mirroring the desktop Virtual Lab, generated
from a tested engine so it cannot drift from `app/engine.py`.

**Architecture:** A `notebook_lab/` package: `bundle.py` exports the compiled data to
`lab_bundle.json`; `engine_lite.py` re-expresses the wired engine reading only that bundle;
`ui_lite.py` builds the 8-tab Gradio app; `build_notebook.py` emits `notebooks/geomind_virtual_lab.ipynb`
with the bundle + both modules embedded. A mirror test proves `engine_lite` reproduces `app.engine`.

**Tech Stack:** Python, pandas/numpy, gradio ≥ 4.44, matplotlib, base64/json (stdlib).

## Global Constraints

- **No drift:** `engine_lite` is unit-tested to match `app.engine`; the notebook is *generated*
  from the module sources (never hand-edited).
- **Colab-internal only:** `ui_lite.main()` uses `demo.launch()` — never `share=True`.
- **Only owned data ships:** compiled pools / registry / audit summary / rendered figures. No raw
  third-party files, no 31 MB DB.
- Dual-context imports: modules must import both as `notebook_lab.*` (repo tests) and as top-level
  (`import engine_lite`) in Colab — use try/except.
- Bundle path resolution: check `$LAB_BUNDLE`, then `cwd/lab_bundle.json`, then the module dir.
- Commit trailer on every commit:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- Verify pytest's **actual exit status** (redirect + `$?`) before every commit.

---

### Task 1: `bundle.py` exporter + generate `lab_bundle.json`

**Files:**
- Create: `notebook_lab/__init__.py`, `notebook_lab/bundle.py`
- Generate (committed): `notebook_lab/lab_bundle.json`
- Test: `tests/test_notebook_bundle.py`

**Interfaces:**
- Produces: `bundle.build_bundle() -> dict`; `bundle.write_bundle(path=None) -> str`.
- Bundle keys: `forward` (slope, intercept, x_min, x_max, r2_loo, rmse_loo, training[7]),
  `cs_pool` (records), `struct` {framework[], ca[]}, `pool_a` (141), `pool_b` (54),
  `audit` (91), `findings` (37), `decisions` (17), `figures` {fig1,fig2,fig4,fig6: b64 png}.

- [ ] **Step 1: Write the failing test** (`tests/test_notebook_bundle.py`)

```python
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from notebook_lab import bundle as B  # noqa: E402


def test_bundle_has_all_sections_with_expected_sizes():
    b = B.build_bundle()
    assert len(b["pool_a"]) == 141
    assert len(b["pool_b"]) == 54
    assert len(b["audit"]) == 91
    assert len(b["findings"]) == 37
    assert len(b["decisions"]) == 17
    assert len(b["forward"]["training"]) == 7
    assert {"fig1", "fig2", "fig4", "fig6"} <= set(b["figures"])
    for v in b["figures"].values():
        assert isinstance(v, str) and len(v) > 100   # base64 PNG
    assert len(b["cs_pool"]) >= 20
    assert b["struct"]["framework"] and b["struct"]["ca"]
```

- [ ] **Step 2: Run to verify it fails**

Run: `MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python -m pytest tests/test_notebook_bundle.py -q`
Expected: FAIL (ModuleNotFoundError: notebook_lab).

- [ ] **Step 3: Create `notebook_lab/__init__.py`**

```python
"""Self-contained notebook mirror of the desktop Virtual Lab."""
```

- [ ] **Step 4: Create `notebook_lab/bundle.py`**

```python
"""Export the compiled data the notebook mirror needs into lab_bundle.json.

Runs against the LIVE pipeline via app.engine so the bundle is always consistent with the
desktop app at export time. Only project-owned compiled data is written — no raw third-party
files, no warehouse DB.
"""
from __future__ import annotations

import base64
import io
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))

import matplotlib  # noqa: E402
matplotlib.use("Agg")

from app import engine as E  # noqa: E402


def _records(df):
    """DataFrame -> JSON-safe list of dicts (NaN -> null, numpy -> native)."""
    return json.loads(df.to_json(orient="records"))


def _figures() -> dict:
    sys.path.insert(0, str(_ROOT / "manuscript"))
    import figures as F
    out = {}
    for key, fn in (("fig1", "fig1_concept"), ("fig2", "fig2_correlation_and_causal"),
                    ("fig4", "fig4_structural_precondition"), ("fig6", "fig6_pooling_limit")):
        fig = getattr(F, fn)()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
        out[key] = base64.b64encode(buf.getvalue()).decode("ascii")
    return out


def build_bundle() -> dict:
    m = E._model()
    fwd_df = None
    from geomind.model import forward as FW
    from geomind.data.merge_adsorption import build as build_A
    tdf = FW.training_data(build_A())
    training = [{"al_iv": float(r[FW.DESCRIPTOR]), "kd": float(r[FW.TARGET])}
                for _, r in tdf.iterrows()]

    cs = E._cs_langmuir_pool()[["source_label", "si_al", "capacity_mg_g"]]

    # structural-precondition points (same query as app.engine.structural_precondition)
    from geomind.data import nmr_ari as N
    A = N.attach(build_A())
    o = A[(A["source_label"] == "oulu2026") & (A["adsorbate"] == "NH4+")].copy()
    o["ca_free"] = o["ca_al"].fillna(0) == 0
    cf = o[o["ca_free"]].dropna(subset=["ari", "capacity_mg_g"])
    cb = o[~o["ca_free"]].dropna(subset=["ari", "capacity_mg_g"])
    struct = {
        "framework": [{"ari": float(a), "cap": float(c)} for a, c in
                      zip(cf["ari"], cf["capacity_mg_g"])],
        "ca": [{"ari": float(a), "cap": float(c)} for a, c in
               zip(cb["ari"], cb["capacity_mg_g"])],
    }

    return {
        "forward": {"slope": float(m.slope), "intercept": float(m.intercept),
                    "x_min": float(m.x_min), "x_max": float(m.x_max),
                    "r2_loo": float(m.r2_loo), "rmse_loo": float(m.rmse_loo),
                    "training": training},
        "cs_pool": _records(cs),
        "struct": struct,
        "pool_a": _records(E.load_pool("A")),
        "pool_b": _records(E.load_pool("B")),
        "audit": _records(E.load_audit_summary()),
        "findings": E.load_findings(),
        "decisions": E.load_decisions(),
        "figures": _figures(),
    }


def write_bundle(path=None) -> str:
    path = Path(path) if path else _ROOT / "notebook_lab" / "lab_bundle.json"
    path.write_text(json.dumps(build_bundle()))
    return str(path)


if __name__ == "__main__":
    print("wrote", write_bundle())
```

- [ ] **Step 5: Run to verify the test passes**

Run: `MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python -m pytest tests/test_notebook_bundle.py -q`
Expected: PASS. Confirm `EXIT=0`.

- [ ] **Step 6: Generate the committed bundle**

Run: `MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python -m notebook_lab.bundle`
Expected: `wrote .../notebook_lab/lab_bundle.json`. Check size is roughly < 3 MB:
`ls -lh notebook_lab/lab_bundle.json`.

- [ ] **Step 7: Commit**

```bash
git add notebook_lab/__init__.py notebook_lab/bundle.py notebook_lab/lab_bundle.json tests/test_notebook_bundle.py
git commit -m "feat(notebook): data-bundle exporter + generated lab_bundle.json"
```

---

### Task 2: `engine_lite.py` — the mirror engine

**Files:**
- Create: `notebook_lab/engine_lite.py`
- Test: `tests/test_notebook_mirror.py`

**Interfaces:**
- Produces (mirroring `app.engine`): `Confidence`, `ResultCard`, `classify_domain`, `predict_kd`,
  `screen_saturation`, `sweep_kd`, `pooling_sources`, `pooled_loo_r2`, `structural_precondition`,
  `load_pool`, `load_findings`, `load_decisions`, `load_audit_summary`, `rerun_headline_numbers`.

- [ ] **Step 1: Write the failing mirror test** (`tests/test_notebook_mirror.py`)

```python
import sys
from pathlib import Path
import pytest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import engine as REAL          # noqa: E402
from notebook_lab import engine_lite as LITE  # noqa: E402

APPROX = dict(rel=1e-6, abs=1e-6)


def test_predict_matches():
    for x in (4.0, 3.6, 9.0):
        r, l = REAL.predict_kd(x), LITE.predict_kd(x)
        assert l.flag.value == r.flag.value
        assert l.value == pytest.approx(r.value, **APPROX)
    assert LITE.predict_kd(4.0, structural_class="zeolite").flag.value == "unsupported"


def test_screen_matches():
    for b, c0 in ((0.05, 1000.0), (7.94e-5, 2658.0)):
        r, l = REAL.screen_saturation(b, c0), LITE.screen_saturation(b, c0)
        assert l.value == pytest.approx(r.value, **APPROX)
        assert l.extra["verdict"] == r.extra["verdict"]


def test_pooling_and_structural_match():
    assert sorted(LITE.pooling_sources()) == sorted(REAL.pooling_sources())
    r = REAL.pooled_loo_r2(REAL.pooling_sources()).value
    l = LITE.pooled_loo_r2(LITE.pooling_sources()).value
    assert l == pytest.approx(r, rel=1e-6, abs=1e-6)
    for inc in (False, True):
        assert LITE.structural_precondition(inc).value == pytest.approx(
            REAL.structural_precondition(inc).value, rel=1e-6, abs=1e-6)


def test_headline_and_counts_match():
    hr, hl = REAL.rerun_headline_numbers(), LITE.rerun_headline_numbers()
    assert set(hl) == set(hr)
    for k in hr:
        assert hl[k] == pytest.approx(hr[k], rel=1e-6, abs=1e-6)
    assert len(LITE.load_pool("A")) == 141 and len(LITE.load_pool("B")) == 54
    assert len(LITE.load_findings()) == 37 and len(LITE.load_decisions()) == 17
    assert len(LITE.load_audit_summary()) == 91
```

- [ ] **Step 2: Run to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_notebook_mirror.py -q`
Expected: FAIL (no module `engine_lite`).

- [ ] **Step 3: Create `notebook_lab/engine_lite.py`** — the full mirror (numeric logic + prose
copied from `app/engine.py`; data from the bundle). Constants match `forward.py`
(`DOMAIN_PAD=0.10`, class "metakaolin geopolymer", adsorbate "Sr"). *(Full code written during
execution; it re-expresses `_loo`, `classify_domain`, `predict_kd`, `screen_saturation`,
`sweep_kd`, `pooling_sources`, `pooled_loo_r2`, `structural_precondition`, `load_*`,
`rerun_headline_numbers`, reading `lab_bundle.json` via a `$LAB_BUNDLE` / cwd / module-dir lookup.)*

- [ ] **Step 4: Run to verify the mirror test passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_notebook_mirror.py -q`
Expected: PASS (mirror reproduces the desktop engine). Confirm `EXIT=0`.

- [ ] **Step 5: Commit**

```bash
git add notebook_lab/engine_lite.py tests/test_notebook_mirror.py
git commit -m "feat(notebook): engine_lite mirror, proven to match app.engine"
```

---

### Task 3: `ui_lite.py` — the notebook Gradio app

**Files:**
- Create: `notebook_lab/ui_lite.py`
- Test: `tests/test_notebook_ui.py`

**Interfaces:**
- Consumes: `engine_lite` (dual-context import).
- Produces: `build_app() -> gr.Blocks`; `main()` (calls `demo.launch()`).

- [ ] **Step 1: Write the failing test** (`tests/test_notebook_ui.py`)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from notebook_lab import ui_lite as U  # noqa: E402


def test_app_builds():
    demo = U.build_app()
    assert demo is not None and hasattr(demo, "launch")


def test_predict_handler_flag_and_unit():
    label, detail = U._predict_handler(4.0, "metakaolin geopolymer", "Sr")
    assert "validated" in label.lower() and "mL/g" in detail
```

- [ ] **Step 2: Run to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_notebook_ui.py -q`
Expected: FAIL (no module `ui_lite`).

- [ ] **Step 3: Create `notebook_lab/ui_lite.py`** — mirrors `app/lab.py`'s eight tabs against
`engine_lite`, with a dual-context import of the engine, the Figures tab rendering the four bundled
base64 PNGs (decoded to temp files), and `main()` calling `demo.launch()`. *(Full code written
during execution.)*

- [ ] **Step 4: Run to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_notebook_ui.py -q`
Expected: PASS. Confirm `EXIT=0`.

- [ ] **Step 5: Commit**

```bash
git add notebook_lab/ui_lite.py tests/test_notebook_ui.py
git commit -m "feat(notebook): ui_lite — 8-tab Gradio mirror, Colab-internal launch"
```

---

### Task 4: `build_notebook.py` + emit the shareable `.ipynb`

**Files:**
- Create: `notebook_lab/build_notebook.py`
- Generate (committed): `notebooks/geomind_virtual_lab.ipynb`
- Test: `tests/test_notebook_build.py`

**Interfaces:**
- Produces: `build_notebook.build(out=None) -> str` (writes the ipynb; returns path).

- [ ] **Step 1: Write the failing test** (`tests/test_notebook_build.py`)

```python
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from notebook_lab import build_notebook as BN  # noqa: E402


def test_notebook_is_valid_and_self_contained(tmp_path):
    out = BN.build(out=tmp_path / "nb.ipynb")
    nb = json.loads(Path(out).read_text())
    assert nb["nbformat"] == 4
    cells = nb["cells"]
    assert len(cells) >= 6
    src = "\n".join("".join(c["source"]) if isinstance(c["source"], list)
                    else c["source"] for c in cells)
    assert "pip" in src and "install" in src and "gradio" in src
    assert "%%writefile engine_lite.py" in src
    assert "%%writefile ui_lite.py" in src
    assert "build_app().launch()" in src
    assert "share=True" not in src            # Colab-internal only
    assert "lab_bundle.json" in src
```

- [ ] **Step 2: Run to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_notebook_build.py -q`
Expected: FAIL (no module `build_notebook`).

- [ ] **Step 3: Create `notebook_lab/build_notebook.py`** — assembles the nbformat-v4 JSON:
markdown intro; `!pip -q install gradio`; a cell that base64-decodes the embedded bundle to
`lab_bundle.json`; `%%writefile engine_lite.py` + `%%writefile ui_lite.py` with the verbatim module
sources; and `from ui_lite import build_app; build_app().launch()`. *(Full code written during
execution.)*

- [ ] **Step 4: Run to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_notebook_build.py -q`
Expected: PASS. Confirm `EXIT=0`.

- [ ] **Step 5: Generate the committed notebook**

Run: `MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python -m notebook_lab.build_notebook`
Expected: writes `notebooks/geomind_virtual_lab.ipynb`. Check `ls -lh` (~1–3 MB) and that it is
valid JSON.

- [ ] **Step 6: Full suite + notebook JSON validity**

Run (redirect + `$?`): `MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python -m pytest -q`
Expected: PASS, all green, `EXIT=0`.
Run: `.venv/bin/python -c "import json,sys; json.load(open('notebooks/geomind_virtual_lab.ipynb')); print('valid ipynb')"`

- [ ] **Step 7: Commit**

```bash
git add notebook_lab/build_notebook.py notebooks/geomind_virtual_lab.ipynb
git commit -m "feat(notebook): build_notebook + shareable geomind_virtual_lab.ipynb"
```

---

## Self-Review

- **Spec coverage:** self-contained single file (Task 4), Colab-internal launch (Task 3 `main`
  + Task 4 test asserts no `share=True`), no-drift via mirror test (Task 2), only-owned-data bundle
  (Task 1), all 8 tabs (Task 3). Figures via embedded PNGs (Task 1 `_figures`).
- **Placeholder scan:** Tasks 2–4 defer *full module bodies* to execution but pin every interface,
  import rule, and test — the executor writes the bodies to satisfy the mirror/UI/build tests.
- **Type consistency:** `engine_lite` mirrors `app.engine`'s public names (Task 2 test asserts
  equality); `ui_lite` handlers mirror `app/lab.py` (`_predict_handler` signature reused).
- **Numbers real:** the mirror asserts *equality with the live desktop engine*, so every number is
  exactly the desktop app's (0.81 / −0.09 / +0.93 / +0.55, 141/54/91/37/17).
