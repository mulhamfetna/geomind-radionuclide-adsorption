# Virtual Lab Phase 2 — Teaching Lab Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement
> this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an interactive Teaching Lab to the Gradio app that makes the paper's argument
explorable — grounded strictly in real data and the existing correct figures.

**Architecture:** Two new *honest, data-backed* engine functions (`pooled_loo_r2`,
`structural_precondition`) reusing the tested `geomind` layer, plus a Teaching tab group in
`app/lab.py` that wires them, reuses `screen_saturation`, and embeds the live manuscript figures
with narration and concept cards. No UI holds science; the engine owns every number.

**Tech Stack:** Python, pandas/numpy, gradio ≥ 4.44, matplotlib (via `manuscript/figures.py`).

## Global Constraints

- **No fabrication.** The spec's "Ca-content slider" and "physisorption↔exchange toggle" are
  **dropped as literally specified** — they would invent a continuous parameter absent from the
  data. The same teaching payload is delivered from the two *real* data groups
  (framework vs Ca-bearing) and the existing figures. Record this in code comments.
- Every predicted number renders through a `ResultCard` with a confidence flag; the flag is shown
  as **text**, never colour-alone.
- **Local only** — no network calls anywhere.
- Reuse `geomind.model.forward._loo`, `geomind.data.merge_adsorption.build`,
  `geomind.data.nmr_ari.attach`, `manuscript/figures.py`. Do not re-implement any fit.
- Commit trailer required on every commit:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- Verify pytest's **actual exit status** (not a pipe's tail) before every commit.

---

### Task 1: `pooled_loo_r2` — the pooling-fails sandbox brain

**Files:**
- Modify: `app/engine.py` (append)
- Test: `tests/test_lab_engine.py` (append)

**Interfaces:**
- Consumes: `geomind.model.forward._loo` (as `FW._loo`), `geomind.data.merge_adsorption.build`,
  `numpy`.
- Produces: `pooling_sources() -> list[str]`; `pooled_loo_r2(source_labels) -> ResultCard`
  (value = LOO-CV R², `extra["verdict"]` in {"predictive","worse-than-mean","undefined"},
  `extra["n"]`, `extra["sources"]`).

- [ ] **Step 1: Write the failing tests** (append to `tests/test_lab_engine.py`)

```python
def test_pooling_sources_lists_the_cs_langmuir_labs():
    srcs = E.pooling_sources()
    assert len(srcs) >= 3
    assert all(isinstance(s, str) for s in srcs)


def test_pooled_loo_r2_all_sources_is_worse_than_mean():
    r = E.pooled_loo_r2(E.pooling_sources())
    assert r.value < 0                       # the F36 result: pooled R^2 < 0
    assert r.extra["verdict"] == "worse-than-mean"
    assert r.flag is E.Confidence.UNSUPPORTED


def test_pooled_loo_r2_too_few_points_is_undefined():
    r = E.pooled_loo_r2([])
    assert r.value is None
    assert r.extra["verdict"] == "undefined"
```

- [ ] **Step 2: Run to verify they fail**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL (AttributeError: module 'app.engine' has no attribute 'pooling_sources').

- [ ] **Step 3: Add `import numpy as np`** near the top imports of `app/engine.py` (after
`from pathlib import Path`), if not already present.

- [ ] **Step 4: Append the implementation** to `app/engine.py`

```python
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
```

- [ ] **Step 5: Run to verify they pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: PASS (all green). Confirm `echo "EXIT=$?"` prints `EXIT=0`.

- [ ] **Step 6: Commit**

```bash
git add app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): pooled_loo_r2 + pooling_sources (F36 sandbox brain)"
```

---

### Task 2: `structural_precondition` — framework vs Ca-bearing (real groups)

**Files:**
- Modify: `app/engine.py` (append)
- Test: `tests/test_lab_engine.py` (append)

**Interfaces:**
- Consumes: `geomind.data.merge_adsorption.build`, `geomind.data.nmr_ari.attach`, `numpy`.
- Produces: `structural_precondition(include_ca: bool = False) -> ResultCard`
  (value = Pearson r of ARI→uptake for the selected group; `extra["n"]`,
  `extra["framework_r"]`, `extra["include_ca"]`).

- [ ] **Step 1: Write the failing tests** (append to `tests/test_lab_engine.py`)

```python
def test_structural_precondition_framework_only_is_strong():
    r = E.structural_precondition(include_ca=False)
    assert r.value > 0.85                     # framework (Ca-free) gels: r ~ +0.93


def test_structural_precondition_pooling_ca_degrades_it():
    fw = E.structural_precondition(include_ca=False).value
    mixed = E.structural_precondition(include_ca=True).value
    assert mixed < fw                         # adding real Ca-bearing gels weakens r
```

- [ ] **Step 2: Run to verify they fail**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL (no attribute `structural_precondition`).

- [ ] **Step 3: Append the implementation** to `app/engine.py`

```python
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
```

- [ ] **Step 4: Run to verify they pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: PASS. Confirm `EXIT=0`.

- [ ] **Step 5: Commit**

```bash
git add app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): structural_precondition (framework vs real Ca-bearing gels, F19)"
```

---

### Task 3: Teaching-tab handlers + wiring

**Files:**
- Modify: `app/lab.py` (add handlers + Teaching tabs inside `build_app`)
- Test: `tests/test_lab_app.py` (append)

**Interfaces:**
- Consumes: `E.pooled_loo_r2`, `E.pooling_sources`, `E.structural_precondition`,
  `E.screen_saturation` (existing), `_screen_handler` (existing).
- Produces: `_pooling_handler(sources: list[str]) -> str`;
  `_structural_handler(include_ca: bool) -> str`. Both return Markdown.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_lab_app.py`)

```python
def test_pooling_handler_reports_collapse_for_all_sources():
    md = L._pooling_handler(L.E.pooling_sources())
    assert "worse-than-mean" in md
    assert "R^2" in md or "R²" in md


def test_structural_handler_reports_both_groups():
    md_fw = L._structural_handler(False)
    md_mix = L._structural_handler(True)
    assert "framework" in md_fw.lower()
    assert "r =" in md_mix.lower() or "r=" in md_mix.lower()
```

- [ ] **Step 2: Run to verify they fail**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_app.py -q`
Expected: FAIL (no attribute `_pooling_handler`).

- [ ] **Step 3: Add the handlers** to `app/lab.py` (after `_screen_handler`)

```python
def _pooling_handler(sources) -> str:
    """UI adapter for the pooling-fails sandbox. Returns Markdown."""
    card = E.pooled_loo_r2(sources)
    if card.value is None:
        return f"**{card.extra['verdict']}** — {card.why}\n\n_{card.provenance}_"
    verdict = card.extra["verdict"]
    mark = "✓ predictive" if verdict == "predictive" else "✗ worse-than-mean"
    return (f"**LOO-CV R^2 = {card.value:+.2f}**  ({mark}, n = {card.extra['n']})\n\n"
            f"{card.why}\n\n_{card.provenance}_")


def _structural_handler(include_ca: bool) -> str:
    """UI adapter for the structural-precondition demo. Returns Markdown."""
    card = E.structural_precondition(include_ca=bool(include_ca))
    return (f"**r = {card.value:+.2f}**  (n = {card.extra['n']}; "
            f"framework-only r = {card.extra['framework_r']:+.2f})\n\n"
            f"{card.why}\n\n_{card.provenance}_")
```

- [ ] **Step 4: Wire the Teaching tabs** inside `build_app`, immediately before `return demo`

```python
        with gr.Tab("Teaching · Pooling fails (F36)"):
            gr.Markdown("Within one laboratory the descriptor predicts held-out samples. "
                        "Pool across laboratories and it falls apart. Pick sources and watch "
                        "the leave-one-out R² drop below zero.")
            pool_pick = gr.CheckboxGroup(E.pooling_sources(),
                                         value=E.pooling_sources(),
                                         label="Laboratories pooled (Cs Langmuir q_max)")
            pool_out = gr.Markdown()
            pool_pick.change(_pooling_handler, pool_pick, pool_out)

        with gr.Tab("Teaching · Structural precondition (F19)"):
            gr.Markdown("The Al-richness descriptor tracks uptake **within a structural class**. "
                        "Toggle in the real Ca-bearing gels and watch the correlation weaken.")
            ca_toggle = gr.Checkbox(value=False, label="Include the real Ca-bearing gels")
            struct_out = gr.Markdown()
            ca_toggle.change(_structural_handler, ca_toggle, struct_out)
```

- [ ] **Step 5: Run to verify they pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_app.py -q`
Expected: PASS. Confirm `EXIT=0`.

- [ ] **Step 6: Commit**

```bash
git add app/lab.py tests/test_lab_app.py
git commit -m "feat(lab): Teaching tabs — pooling-fails + structural-precondition (interactive)"
```

---

### Task 4: Figures panel + concept cards + saturation-reveal tab

**Files:**
- Modify: `app/lab.py` (figures/concepts tabs in `build_app`)
- Test: `tests/test_lab_app.py` (append)

**Interfaces:**
- Consumes: `manuscript/figures.py` figure functions; existing `_screen_handler`.
- Produces: `_concept_cards() -> str` (Markdown).

- [ ] **Step 1: Write the failing test** (append to `tests/test_lab_app.py`)

```python
def test_concept_cards_cover_the_core_ideas():
    md = L._concept_cards()
    for token in ("Al", "ARI", "θ", "pool"):
        assert token in md
```

- [ ] **Step 2: Run to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_app.py -q`
Expected: FAIL (no attribute `_concept_cards`).

- [ ] **Step 3: Add `_concept_cards`** to `app/lab.py`

```python
def _concept_cards() -> str:
    """Static concept glossary for the Teaching Lab."""
    return (
        "### Concept cards\n"
        "- **Framework Al^IV** — tetrahedral aluminium in the aluminosilicate network. Each "
        "Al^IV carries a negative charge balanced by an exchangeable cation — the actual uptake "
        "site. Not the same as surface area.\n"
        "- **ARI (Al-richness index)** — framework Al per Si from the Q⁴(mAl) NMR deconvolution; "
        "the composition-side proxy for exchange-site density.\n"
        "- **Qⁿ(mAl)** — ²⁹Si NMR speciation: a Si tetrahedron with *n* bridging oxygens, *m* of "
        "them to Al. The deconvolution that yields ARI.\n"
        "- **θ = 1 − R_L** — fraction of Langmuir saturation reached at the highest C₀ tested. "
        "θ ≥ 0.8 sound; θ < 0.5 the fitted capacity is an extrapolation artefact.\n"
        "- **Two pools** — Pool A (adsorption K_D / q_max) and Pool B (immobilisation / "
        "leachability) are audited separately and never merged.\n"
    )
```

- [ ] **Step 4: Wire the figures + concepts + reveal tabs** inside `build_app`, before `return demo`

```python
        with gr.Tab("Teaching · Saturation reveal"):
            gr.Markdown("A Langmuir fit can report R² = 0.9999 and still be an artefact. Enter "
                        "its *b* and highest C₀ and reveal how little of the isotherm it saw.")
            with gr.Row():
                rb = gr.Number(value=7.94e-5, label="Langmuir b (L mg⁻¹)")
                rc0 = gr.Number(value=2658.0, label="C₀ (mg L⁻¹)")
            reveal_btn = gr.Button("Reveal θ")
            reveal_out = gr.Markdown()
            reveal_btn.click(_screen_handler, [rb, rc0], reveal_out)

        with gr.Tab("Teaching · Figures & concepts"):
            gr.Markdown("The paper's argument, rendered live from the pipeline.")
            gr.Markdown(_concept_cards())
            try:
                import sys as _sys
                _sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "manuscript"))
                import figures as _figs  # noqa: F401
                for _name, _fn in (("Concept (Fig 1)", "fig1_concept"),
                                   ("Three levels (Fig 2)", "fig2_correlation_and_causal"),
                                   ("Structural precondition (Fig 4)", "fig4_structural_precondition"),
                                   ("Pooling limit (Fig 6)", "fig6_pooling_limit")):
                    if hasattr(_figs, _fn):
                        gr.Markdown(f"**{_name}**")
                        gr.Plot(getattr(_figs, _fn)())
            except Exception as _e:  # pragma: no cover - figures are optional in the UI
                gr.Markdown(f"_Figures unavailable in this environment: {_e}_")
```

- [ ] **Step 5: Run the app-build test and the FULL suite**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_app.py -q` (Expected: PASS)
Run: `PYTHONPATH=src .venv/bin/python -m pytest -q` (Expected: PASS, all green)
Confirm `EXIT=0` on the full run (redirect to a file and check `$?`, do not trust a pipe tail).

- [ ] **Step 6: Smoke-launch** (build ≠ launch)

```bash
PYTHONPATH=src .venv/bin/python -c "
from app import lab as L
d = L.build_app(); app,url,share = d.launch(prevent_thread_lock=True, server_port=7862, quiet=True)
print('LAUNCHED', url); d.close(); print('CLOSED-OK')"
```
Expected: `LAUNCHED ... / CLOSED-OK`.

- [ ] **Step 7: Commit**

```bash
git add app/lab.py tests/test_lab_app.py
git commit -m "feat(lab): Teaching tabs — saturation reveal, live figures, concept cards"
```

---

## Self-Review

- **Spec coverage:** pooling sandbox (§4 "pooling fails"), saturation reveal (§4), structural
  precondition (§4, honestly via real groups), mechanism/three-level (§4, via embedded Figs 1/2),
  concept cards (§4). The physisorption↔exchange toggle and Ca *slider* are consciously dropped
  (fabrication) and replaced by Fig 1/Fig 4 + the real-group toggle — recorded in Global Constraints.
- **Placeholder scan:** none — every step carries full code.
- **Type consistency:** handlers return `str`; engine returns `ResultCard`; `pooling_sources()`
  returns `list[str]` used verbatim in Task 3 wiring.
- **Numbers are real:** all-pooled LOO R² = −0.09 (Task 1 assert `< 0`); framework r = +0.93
  (Task 2 assert `> 0.85`); pooled r = +0.55 `< 0.93` (Task 2). Verified against the live pipeline
  before writing this plan.
