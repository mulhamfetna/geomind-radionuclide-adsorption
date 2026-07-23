# Virtual Lab Phase 3 — Reproducibility Console Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement
> this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a Reproducibility Console to the Gradio app — browse the audited pools, the finding
register and the veracity audit trail, and re-run the headline numbers live from the pipeline.

**Architecture:** Read-only data loaders in `app/engine.py` over the existing pools, the registry
YAML, and the prebuilt warehouse SQLite DB, plus a `rerun_headline_numbers()` that recomputes the
paper's key figures from the tested engine. `app/lab.py` gains a Console tab group that renders
them. No rebuilds, no writes, no network.

**Tech Stack:** Python, pandas, pyyaml, sqlite3 (stdlib, read-only), gradio ≥ 4.44.

## Global Constraints

- **Read-only.** The warehouse DB is opened `mode=ro`; the registry and pools are read, never
  written. Never call `warehouse.build()` from the app (it re-ingests 22k rows).
- Paths resolve from the repo root: `_ROOT = Path(__file__).resolve().parents[1]`.
- Graceful degradation: if the warehouse DB is absent, the audit loader returns an **empty frame**
  with the right columns, never raises.
- Reuse existing engine functions for every recomputed number — do not re-implement a fit.
- Commit trailer on every commit:
  `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>`
- Verify pytest's **actual exit status** (redirect + `$?`, not a pipe tail) before every commit.

---

### Task 1: Data loaders — pools + finding register

**Files:**
- Modify: `app/engine.py` (append; add `_ROOT` near the imports)
- Test: `tests/test_lab_engine.py` (append)

**Interfaces:**
- Produces: `load_pool(name: str = "A") -> pandas.DataFrame`;
  `load_findings() -> list[dict]`; `load_decisions() -> list[dict]`.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_lab_engine.py`)

```python
def test_load_pool_a_and_b_row_counts():
    assert len(E.load_pool("A")) == 141
    assert len(E.load_pool("B")) == 54


def test_load_findings_and_decisions_counts():
    f = E.load_findings()
    d = E.load_decisions()
    assert len(f) == 37 and all("id" in x and "title" in x for x in f)
    assert len(d) == 17
```

- [ ] **Step 2: Run to verify they fail**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL (no attribute `load_pool`).

- [ ] **Step 3: Add `_ROOT`** to `app/engine.py`, immediately after the `sys.path.insert(...)` line
near the top:

```python
_ROOT = Path(__file__).resolve().parents[1]
```

- [ ] **Step 4: Append the loaders** to `app/engine.py`

```python
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
```

- [ ] **Step 5: Run to verify they pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q` — Expected: PASS.
Confirm `EXIT=0`.

- [ ] **Step 6: Commit**

```bash
git add app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): read-only loaders for pools + finding/decision registers"
```

---

### Task 2: Audit-trail loader (warehouse, read-only)

**Files:**
- Modify: `app/engine.py` (append)
- Test: `tests/test_lab_engine.py` (append)

**Interfaces:**
- Produces: `load_audit_summary(db_path=None) -> pandas.DataFrame`
  (columns: source_file, source_table, n_rows, veracity, utility, reason). Empty frame if the DB
  is absent.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_lab_engine.py`)

```python
def test_load_audit_summary_has_veracity_labels():
    df = E.load_audit_summary()
    assert {"veracity", "reason", "n_rows"} <= set(df.columns)
    assert len(df) >= 1
    assert "VERIFIED_TRUE" in set(df["veracity"])


def test_load_audit_summary_missing_db_is_empty_not_error(tmp_path):
    df = E.load_audit_summary(db_path=tmp_path / "nope.db")
    assert len(df) == 0
    assert {"veracity", "reason", "n_rows"} <= set(df.columns)
```

- [ ] **Step 2: Run to verify they fail**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL (no attribute `load_audit_summary`).

- [ ] **Step 3: Append the loader** to `app/engine.py`

```python
_AUDIT_COLS = ["source_file", "source_table", "n_rows", "veracity", "utility", "reason"]


def load_audit_summary(db_path=None):
    """The per-file veracity audit from the prebuilt warehouse (tables_seen), read-only.
    Every ingested table carries an explicit verdict and a reason. Returns an empty frame
    (with the right columns) if the DB is not present — never raises."""
    import sqlite3
    import pandas as pd
    db = Path(db_path) if db_path is not None else _ROOT / "data" / "warehouse" / "geomind.db"
    if not db.exists():
        return pd.DataFrame(columns=_AUDIT_COLS)
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        return pd.read_sql_query(
            "SELECT source_file, source_table, n_rows, veracity, utility, reason "
            "FROM tables_seen ORDER BY veracity, n_rows DESC", con)
    finally:
        con.close()
```

- [ ] **Step 4: Run to verify they pass**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q` — Expected: PASS.
Confirm `EXIT=0`.

- [ ] **Step 5: Commit**

```bash
git add app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): read-only warehouse audit-trail loader (tables_seen)"
```

---

### Task 3: `rerun_headline_numbers` — live recomputation

**Files:**
- Modify: `app/engine.py` (append)
- Test: `tests/test_lab_engine.py` (append)

**Interfaces:**
- Produces: `rerun_headline_numbers() -> dict` with keys `forward_r2_loo`, `forward_slope`,
  `forward_intercept`, `pooled_r2`, `framework_r`, `pooled_struct_r` (all floats).

- [ ] **Step 1: Write the failing test** (append to `tests/test_lab_engine.py`)

```python
def test_rerun_headline_numbers_match_the_paper():
    h = E.rerun_headline_numbers()
    assert h["forward_r2_loo"] > 0.7          # within-class LOO-CV ~ 0.81
    assert h["pooled_r2"] < 0                  # pooled across labs ~ -0.09
    assert h["framework_r"] > 0.85             # framework ARI r ~ +0.93
    assert h["pooled_struct_r"] < h["framework_r"]
```

- [ ] **Step 2: Run to verify it fails**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q`
Expected: FAIL (no attribute `rerun_headline_numbers`).

- [ ] **Step 3: Append the function** to `app/engine.py`

```python
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
```

- [ ] **Step 4: Run to verify it passes**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_engine.py -q` — Expected: PASS.
Confirm `EXIT=0`.

- [ ] **Step 5: Commit**

```bash
git add app/engine.py tests/test_lab_engine.py
git commit -m "feat(lab): rerun_headline_numbers (live reproducibility recomputation)"
```

---

### Task 4: Reproducibility Console tabs + wiring

**Files:**
- Modify: `app/lab.py` (handlers + Console tabs in `build_app`)
- Test: `tests/test_lab_app.py` (append)

**Interfaces:**
- Consumes: `E.load_pool`, `E.load_findings`, `E.load_decisions`, `E.load_audit_summary`,
  `E.rerun_headline_numbers`.
- Produces: `_pool_handler(name) -> pandas.DataFrame`; `_findings_table(query: str) -> pandas.DataFrame`;
  `_audit_summary_md() -> str`; `_rerun_handler() -> str`.

- [ ] **Step 1: Write the failing tests** (append to `tests/test_lab_app.py`)

```python
def test_pool_handler_returns_the_full_pool():
    assert len(L._pool_handler("A")) == 141


def test_findings_table_filters_by_query():
    all_rows = L._findings_table("")
    f36 = L._findings_table("F36")
    assert len(all_rows) == 37
    assert 1 <= len(f36) < len(all_rows)


def test_rerun_handler_reports_the_headline_numbers():
    md = L._rerun_handler()
    assert "0.81" in md            # forward R^2_LOO
    assert "F36" in md or "pool" in md.lower()


def test_audit_summary_md_mentions_verified():
    md = L._audit_summary_md()
    assert "VERIFIED_TRUE" in md or "verified" in md.lower()
```

- [ ] **Step 2: Run to verify they fail**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_app.py -q`
Expected: FAIL (no attribute `_pool_handler`).

- [ ] **Step 3: Add the handlers** to `app/lab.py` (after `_structural_handler`)

```python
import pandas as _pd  # noqa: E402


def _pool_handler(name):
    """Return the chosen audited pool as a DataFrame for display."""
    return E.load_pool(name)


def _findings_table(query: str):
    """Finding register as a compact DataFrame, filtered by a free-text query."""
    rows = E.load_findings()
    q = (query or "").strip().lower()
    if q:
        rows = [r for r in rows
                if q in " ".join(str(r.get(k, "")) for k in
                                  ("id", "severity", "title", "evidence", "action", "status")).lower()]
    return _pd.DataFrame([{"id": r.get("id"), "severity": r.get("severity"),
                           "title": r.get("title"), "status": r.get("status"),
                           "action": r.get("action")} for r in rows])


def _audit_summary_md() -> str:
    """Veracity breakdown of the warehouse audit trail, as Markdown."""
    df = E.load_audit_summary()
    if len(df) == 0:
        return "_Warehouse DB not present in this checkout — audit trail unavailable._"
    g = df.groupby("veracity").agg(files=("source_file", "count"),
                                   rows=("n_rows", "sum")).reset_index()
    lines = ["| veracity | files | rows |", "|---|---:|---:|"]
    for _, r in g.iterrows():
        lines.append(f"| {r['veracity']} | {int(r['files'])} | {int(r['rows'])} |")
    total = int(g["files"].sum())
    kept = int(g[g["veracity"].isin(["VERIFIED_TRUE", "PROBABLE"])]["files"].sum())
    lines.append("")
    lines.append(f"**{total} tables audited; {total - kept} set aside** "
                 "(UNVERIFIED / REDUNDANT / FALSE) — every one with a recorded reason.")
    return "\n".join(lines)


def _rerun_handler() -> str:
    """Recompute and report the paper's headline numbers live."""
    h = E.rerun_headline_numbers()
    return (
        "### Recomputed live from the pipeline\n"
        f"- **Forward model (within-class):** K_D = {h['forward_slope']:.0f}·[Al^IV] "
        f"− {abs(h['forward_intercept']):.0f} mL/g, **LOO-CV R² = {h['forward_r2_loo']:.2f}** "
        "— predicts held-out samples.\n"
        f"- **Pooled across laboratories (F36):** LOO-CV R² = **{h['pooled_r2']:+.2f}** "
        "— worse than the mean.\n"
        f"- **Structural precondition (F19):** framework ARI r = **{h['framework_r']:+.2f}**, "
        f"degrading to {h['pooled_struct_r']:+.2f} when Ca gels are pooled in.\n"
    )
```

- [ ] **Step 4: Wire the Console tabs** inside `build_app`, immediately before `return demo`

```python
        with gr.Tab("Console · Pool explorer"):
            gr.Markdown("The two audited pools, browsable. Pool A = adsorption (141 rows), "
                        "Pool B = immobilisation (54). They are never merged.")
            pool_pick2 = gr.Radio(["A", "B"], value="A", label="Pool")
            pool_df = gr.DataFrame(value=E.load_pool("A"), wrap=True)
            pool_pick2.change(_pool_handler, pool_pick2, pool_df)

        with gr.Tab("Console · Finding register"):
            gr.Markdown("37 findings, searchable. Each carries its evidence and the action taken.")
            find_q = gr.Textbox(label="Filter (id, word in title/evidence/action)", value="")
            find_df = gr.DataFrame(value=_findings_table(""), wrap=True)
            find_q.change(_findings_table, find_q, find_df)

        with gr.Tab("Console · Audit trail"):
            gr.Markdown("Every ingested table got an explicit verdict and a reason — the ~a-fifth "
                        "set aside is the point, not a footnote.")
            gr.Markdown(_audit_summary_md())
            gr.DataFrame(value=E.load_audit_summary(), wrap=True)

        with gr.Tab("Console · Re-run analyses"):
            gr.Markdown("Recompute the paper's headline numbers live from the current pipeline.")
            rerun_btn = gr.Button("Re-run", variant="primary")
            rerun_out = gr.Markdown()
            rerun_btn.click(_rerun_handler, None, rerun_out)
```

- [ ] **Step 5: Run the app tests, then the FULL suite**

Run: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_lab_app.py -q` (Expected: PASS)
Run (redirect + check `$?`): `MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python -m pytest -q`
Expected: PASS, all green, `EXIT=0`.

- [ ] **Step 6: Smoke-launch** (build ≠ launch)

```bash
MPLBACKEND=Agg PYTHONPATH=src .venv/bin/python -c "
from app import lab as L
d = L.build_app(); app,url,share = d.launch(prevent_thread_lock=True, server_port=7863, quiet=True)
print('LAUNCHED', url); d.close(); print('CLOSED-OK')"
```
Expected: `LAUNCHED ... / CLOSED-OK`.

- [ ] **Step 7: Commit**

```bash
git add app/lab.py tests/test_lab_app.py
git commit -m "feat(lab): Reproducibility Console — pools, findings, audit trail, re-run"
```

---

## Self-Review

- **Spec coverage (§5):** pool explorer (Task 4 tab), re-run analyses (Task 3 + tab),
  finding-register browser (Task 1 + tab), audit trail (Task 2 + tab). Manuscript-number→row
  *traceability* is served indirectly by the searchable finding register + pool explorer (a full
  cross-reference index is deferred, not fabricated) — noted here, not silently dropped.
- **Placeholder scan:** none — every step carries full code.
- **Type consistency:** `load_pool`→DataFrame (Task 1) consumed by `_pool_handler` (Task 4);
  `load_findings`→list[dict] consumed by `_findings_table`; `load_audit_summary`→DataFrame consumed
  by `_audit_summary_md`; `rerun_headline_numbers`→dict consumed by `_rerun_handler`.
- **Numbers are real (verified against the live pipeline before writing):** Pool A 141 / Pool B 54;
  37 findings / 17 decisions; 91 tables audited (67 VERIFIED_TRUE); forward R²_LOO 0.81; pooled
  R² −0.09; framework r +0.93; pooled r +0.55.
