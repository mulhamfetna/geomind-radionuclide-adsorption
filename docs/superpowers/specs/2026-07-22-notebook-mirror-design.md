# Design — GEOMIND-R Virtual Lab, Notebook Mirror

**Date:** 2026-07-22 · **Status:** design for review · **Confidential (pre-publication)**

A single self-contained Colab notebook that mirrors the desktop Virtual Lab, so the supervising
professor can try it by uploading **one file** and choosing *Run all* — no repo access, no
confidential raw files, no 31 MB warehouse DB, and **no public tunnel** (the app renders inside the
professor's own Colab session).

---

## 1. Goals and constraints

- **One file to share.** Everything the notebook needs — engine code and a compact data bundle —
  travels inside the `.ipynb`. The professor uploads it to Colab and runs all cells.
- **Colab-internal only.** `demo.launch()` (no `share=True`); Gradio renders in Colab's own output
  iframe. Nothing routes through a third-party `*.gradio.live` tunnel.
- **Faithful, not drifting.** The notebook must produce the *same numbers* as the desktop app. This
  is guaranteed by construction: the notebook's engine is a real, unit-tested module proven to
  reproduce `app/engine.py`'s outputs, and the notebook is generated from that module's source —
  never hand-edited.
- **Only data we own leaves.** The bundle carries the project's *compiled* pools, registry, audit
  summary and rendered figures — the factual data the project holds DOI rights to, shared with a
  repo co-owner. No third-party raw files, no 31 MB DB.

## 2. Why this shape (vs the alternatives)

A repo-cloning notebook stays in sync automatically but needs the professor to hold repo access and
paste a GitHub token into Colab — friction, and it exposes the whole confidential repo. A local
Jupyter notebook needs the repo cloned on the professor's machine. The self-contained notebook is
the only option that is genuinely *upload-one-file-and-run* for someone outside the project, and it
narrows what is shared to exactly the compiled data.

The cost is drift risk — a copied engine could disagree with the real one. We remove that cost with
a mirror **test** (§5), so the self-contained approach keeps its UX win without the correctness loss.

## 3. Architecture

```
  desktop app (source of truth)          notebook mirror (generated)
  ┌───────────────────────────┐          ┌──────────────────────────────┐
  │ app/engine.py  (tested)   │  ==test==│ notebook_lab/engine_lite.py  │
  │ app/lab.py                │          │ notebook_lab/ui_lite.py      │
  │ geomind + data + figures  │──export─▶│ notebook_lab/lab_bundle.json │
  └───────────────────────────┘          └──────────────┬───────────────┘
                                                         │ build
                                                         ▼
                                          notebooks/geomind_virtual_lab.ipynb
                                          (bundle + both modules embedded)
```

**New package `notebook_lab/` (4 pieces):**

- `bundle.py` — **exporter.** Pulls everything the mirror needs from the *live* pipeline via the
  real `app.engine`, and writes `lab_bundle.json`:
  - `forward`: slope, intercept, x_min, x_max, r2_loo, rmse_loo, and the 7 Varon training points.
  - `cs_pool`: the cross-lab Cs Langmuir rows `{source_label, si_al, capacity_mg_g}` (pooling sandbox).
  - `struct`: framework vs Ca-bearing ARI→uptake points (structural-precondition demo).
  - `pool_a` (141), `pool_b` (54): the browsable audited pools.
  - `audit`: the 91-row warehouse veracity summary `{source_file, source_table, n_rows, veracity, utility, reason}`.
  - `findings` (37), `decisions` (17).
  - `figures`: fig1/fig2/fig4/fig6 as base64 PNGs, rendered once from `manuscript/figures.py`
    (exact fidelity, no matplotlib re-porting).

- `engine_lite.py` — **self-contained engine.** Re-expresses the desktop engine's numeric logic
  (straight-line fit + predict, leave-one-out R², Pearson r, θ = 1 − R_L, tri-colour domain flag)
  reading only `lab_bundle.json`. Mirrors the *wired* engine surface: `classify_domain`,
  `predict_kd`, `screen_saturation`, `sweep_kd`, `pooling_sources`, `pooled_loo_r2`,
  `structural_precondition`, `load_pool`, `load_findings`, `load_decisions`, `load_audit_summary`,
  `rerun_headline_numbers`, plus the `Confidence`/`ResultCard` types. (Formulation-mode helpers
  `describe_formulation`/`ari_from_q4` are **not** mirrored — the desktop UI never wired them.)

- `ui_lite.py` — **the Gradio app**, mirroring `app/lab.py`'s eight tabs against `engine_lite`.
  Figures tab shows the four bundled PNGs. `main()` calls `demo.launch()` (Colab-internal).

- `build_notebook.py` — **assembler.** Emits `notebooks/geomind_virtual_lab.ipynb` whose cells are:
  (1) a Markdown intro with Run-all instructions; (2) `pip -q install gradio`; (3) a cell that
  writes `lab_bundle.json` from an embedded base64 blob; (4)+(5) `%%writefile` cells containing the
  **verbatim source** of `engine_lite.py` and `ui_lite.py`; (6) `from ui_lite import build_app;
  build_app().launch()`. Because the code cells are the exact module sources, the shipped notebook
  is byte-identical to the tested modules.

**Reused unchanged:** `app.engine` (as the export source and the test oracle), `manuscript/figures.py`.

## 4. Data flow

Build time (developer): `bundle.py` → `lab_bundle.json` (+ figures) → `build_notebook.py` →
`geomind_virtual_lab.ipynb`. Run time (professor): upload `.ipynb` → Run all → cells write the
bundle + modules to the Colab filesystem → Gradio launches inline. No network beyond the one
`pip install`.

## 5. Testing (this is what prevents drift)

- **Mirror-fidelity test** (`tests/test_notebook_mirror.py`): load `lab_bundle.json` through
  `engine_lite`, and assert its outputs equal the real `app.engine` on a battery of inputs —
  `predict_kd(4.0)` value+flag, an out-of-domain flag, two `screen_saturation` cases,
  `pooled_loo_r2(all)` ≈ −0.09, `structural_precondition(False/True)`, every key in
  `rerun_headline_numbers`, and pool/finding/audit row counts. If the mirror ever diverges, this
  fails.
- **Bundle-completeness test**: the exported JSON has every required key and the expected lengths
  (pool_a 141, pool_b 54, audit 91, findings 37, decisions 17, four figures).
- **UI-build test**: `ui_lite.build_app()` assembles without launching.
- **Notebook-validity test**: the emitted `.ipynb` is valid JSON with the expected cell count and a
  launch cell.

## 6. Non-goals

No public/hosted deployment; no `share=True`; no repo clone; no live re-fit from raw data in the
notebook (it reads the frozen bundle — refreshed by re-running the exporter). The notebook mirrors
what the desktop app *shows*; it is not a second implementation to maintain by hand.
