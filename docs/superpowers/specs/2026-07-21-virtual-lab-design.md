# Design — GEOMIND-R Virtual Chemistry Lab & Simulator

**Date:** 2026-07-21 · **Status:** design for review · **Confidential (pre-publication)**

A local, interactive laboratory in which a user explores geopolymer compositions and receives
**descriptor calculations, a domain-flagged Sr K_D prediction, and screening checks** — grounded
strictly in what the project established (the forward model, the chemistry layer, the audit, the
mechanism). It is a **glass box, not an oracle**: every prediction carries its *why*, its
uncertainty, and a confidence flag, and predictions outside the validated envelope are shown for
exploration but marked unvalidated rather than hidden or dressed up.

---

## 1. Purpose and honest scope

The forward model predicts held-out compositions it never trained on (leave-one-out R² = 0.81),
which is what makes an interactive lab meaningful. But F36/D17 bound *where* predictions are
trustworthy: within one structural class and protocol, not across the pooled literature. The lab's
first duty is to make that boundary visible, not to hide it.

**In scope (what our outcomes support):**
- Exact descriptor computation for any composition (Si/Al, molar ratios, ARI, Al^IV) — verified to
  1–3% (M3a chemistry layer).
- Sr K_D prediction for metakaolin geopolymers, with an uncertainty band and a confidence flag
  (the `forward` model).
- Screening checks: isotherm saturation (θ = 1 − R_L), feasibility (viscosity class), the Cs<Sr
  retention ranking and binder-class leachability stratification.
- Teaching the mechanism and the methods, interactively.
- Reproducing every number and figure from the live pipeline.

**Explicit non-goals (what we will NOT claim):**
- A validated predictor for arbitrary material classes (zeolites, Ca-rich gels) or protocols —
  F36 showed the relationship does not pool and Si/Al's sign flips across classes.
- A generative inverse-design engine — that is M5, gated on single-protocol data, not this tool.
- Any online / hosted deployment — the lab runs **locally** to preserve confidentiality.

### 1.1 The tri-colour confidence system (governs every prediction)

Every predicted value renders with one of three states, chosen by the input's position relative to
the model's trained domain and structural class:

| Flag | Condition | Behaviour |
|---|---|---|
| 🟢 **validated** | metakaolin geopolymer, Sr, [Al^IV] inside the trained range (3.45–4.77 mmol g⁻¹, ±10% pad) | prediction + LOO uncertainty band, shown normally |
| 🟡 **exploratory** | right class, but [Al^IV] outside the padded range (near-to-moderate extrapolation) | prediction shown, banner: "extrapolation beyond the validated range — unvalidated, for exploration only"; uncertainty widened/omitted |
| 🔴 **unsupported** | wrong structural class (zeolite, Ca-rich gel) or a different adsorbate | the *extrapolated* number is shown only behind an explicit "show anyway" reveal, with "the descriptor is not valid here (F19) — this is not a prediction we can stand behind" |

This is the "wider domain, eyes open" refinement: the user may probe anywhere, but the flag always
tells them how far they have stepped off validated ground. A prediction is never presented as
trustworthy where our own findings say it is not. The `forward.predict(..., strict=False)` path
already supports deliberate extrapolation; the UI wraps it in this flagging.

---

## 2. Architecture

A single **local Gradio application** over the existing `geomind` Python package. Chosen because the
entire prediction engine is already Python and tested, so the UI is a thin, honest wrapper with no
model re-implementation, and because local execution keeps confidential contents off any server.
(A self-contained HTML artifact cannot run the Python model client-side; a FastAPI+JS stack adds a
build for no benefit. Gradio is the fit.)

```
                    ┌──────────────── shared engine (existing, tested) ─────────────────┐
                    │ model.forward     — domain-guarded Sr K_D prediction + LOO metrics │
                    │ chemistry         — Si/Al, Si/Msol, Solid/Liquid molar ratios      │
                    │ data.nmr_ari      — ARI / Al^IV from Q4(mAl) deconvolution         │
                    │ feasibility       — viscosity class, provisional envelope          │
                    │ adsorption/immob. — the two audited pools + pooling_warning        │
                    │ saturation screen — θ = 1 − R_L                                     │
                    └───────────────────────────────────────────────────────────────────┘
                              ▲                    ▲                     ▲
        ┌─────────────────────┴──────┐  ┌──────────┴─────────┐  ┌───────┴────────────────┐
        │ Tab 1: Screening Workbench │  │ Tab 2: Teaching Lab│  │ Tab 3: Reproducibility │
        │ (Phase 1 — ship first)     │  │ (Phase 2)          │  │ Console (Phase 3)      │
        └────────────────────────────┘  └────────────────────┘  └────────────────────────┘
```

**New code, kept small and bounded:**
- `app/lab.py` — Gradio app assembly (tabs, layout).
- `app/engine.py` — a thin **service layer**: `describe(formulation)`, `predict_kd(descriptor)`,
  `screen_saturation(b, C0)`, `feasibility(...)`, `compare(candidates)` — each returns a plain
  result object `{value, flag, uncertainty, why, provenance}`. This is the single interface the UI
  and tests use; the tabs never touch the model directly. Enables independent testing of the
  honesty logic apart from the UI.
- `app/widgets/` — the interactive teaching widgets (Phase 2) and the pool/finding browsers
  (Phase 3).

**Reused unchanged:** `model.forward`, `chemistry`, `data.nmr_ari`, `feasibility`, the schemas and
pools, `pooling_warning`, and `manuscript/figures.py` (for live figure regeneration in Phase 3).

---

## 3. Phase 1 — The Screening Workbench (build first, thin end-to-end)

The minimum end-to-end loop, usable on its own: **input → descriptors → domain-flagged prediction →
screen → export.**

### 3.1 Composition input (two modes)
- **Formulation mode:** precursor identity + mass fractions (metakaolin / fly-ash / slag), activator
  (SiO₂/Na₂O modulus, water/solids), → the chemistry layer computes descriptors. Class inferred
  from precursor.
- **Descriptor mode:** enter [Al^IV] (mmol g⁻¹) or Si/Al and the structural class directly, for
  users who already have NMR.
- Optional: paste a Q⁴(mAl) deconvolution → ARI/Al^IV via `nmr_ari` (with the sum-to-100 and
  ambiguous-assignment guards, F23).

### 3.2 Descriptor panel
Live Si/Al, molar ratios (Si/M_sol, Solid/Liquid), ARI, Al^IV — each labelled exact vs inferred.

### 3.3 Sr K_D prediction (the centrepiece)
The `forward` model output, rendered through the tri-colour system: predicted K_D, the LOO
uncertainty band where 🟢, the model equation, and the confidence flag with its plain-language
reason. A one-line "why" links to the mechanism (Al^IV exchange sites).

### 3.4 What-if sweep
Vary one input (e.g. Si/Al or [Al^IV]) across a range; plot predicted K_D as a curve with the
**validated envelope shaded green** and the extrapolation region amber. This is the single most
useful screening view — it shows at a glance where a candidate sits relative to trustworthy ground.

### 3.5 Screening checks
- **Saturation advisor:** enter a reported Langmuir b and C₀ → θ = 1 − R_L, with the sound /
  weakly-constrained / artefact verdict (F14–F17).
- **Feasibility:** viscosity class from the composition, flagged provisional (F6).
- **Cs vs Sr guidance:** the retention ranking and binder-class leachability stratification (Table 3).

### 3.6 Comparison tray
Add several candidates; compare descriptors, predictions and flags side by side. If two candidates
are of different structural classes, `pooling_warning` surfaces a caution — you may compare, but the
tool says so.

### 3.7 Export
A candidate report (inputs, descriptors, prediction, flags, caveats) written to a **local file**
(Markdown/JSON). No network.

---

## 4. Phase 2 — The Teaching Lab

Interactive renderings of the paper's argument, for the seminar / students / reviewers:
- **Mechanism explorer** — toggle physisorption vs Al^IV ion-exchange (Fig 1 alive); watch why
  surface area fails.
- **Three-level walkthrough** — correlation → within-sample causal test → atomic mechanism (Fig 2),
  explorable point by point.
- **Structural-precondition demo** — a Ca-content slider that visibly collapses the Q⁴ population and
  kills the descriptor (Fig 4 live) — the F19 lesson.
- **"Pooling fails" sandbox** — let the user pool sources and watch the leave-one-out R² fall below
  zero (the F36 insight, hands-on).
- **Saturation-screen reveal** — an R² = 0.9999 fit unmasked as a ~1000× extrapolation.
- **Concept cards** — Al^IV, ARI, Q^n(mAl), θ = 1 − R_L, the two pools.

---

## 5. Phase 3 — The Reproducibility Console

- **Pool explorer** — browse Pool A (141 rows) and Pool B (54) with provenance and veracity labels;
  filter, sort, inspect any row.
- **Re-run analyses** — regenerate the correlations, the LOO-CV numbers and the figures on demand
  from the live pipeline.
- **Finding-register browser** — the 37 findings, searchable, each with evidence and action.
- **Traceability** — from a manuscript number to its source row / finding.
- **Audit trail** — the ~32% excluded rows and the reason each failed.

---

## 6. Data flow, errors, testing

**Data flow.** UI event → `app/engine.py` service call → existing engine module → a result object
`{value, flag, uncertainty, why, provenance}` → the tab renders it with the tri-colour treatment.
The UI holds no scientific logic; the service layer owns the honesty rules.

**Error handling.** Invalid/empty composition → inline validation, never a crash. Out-of-domain →
the tri-colour flag, never a silent number. Ambiguous NMR input → the F23 guard refuses to compute
ARI and says why. No network calls anywhere.

**Testing.** `app/engine.py` is unit-tested independently of Gradio: the tri-colour flag is asserted
across in-domain / near-edge / wrong-class inputs; the saturation verdict; the pooling caution; that
no 🔴 result is ever labelled validated. The UI itself is smoke-tested (the app builds, tabs mount).
The engine's science is already covered by the existing 133-test suite.

---

## 7. Build sequence

1. **Phase 1 thin slice** — `engine.py` service layer + the Workbench tab (input → descriptors →
   prediction → sweep → export). Usable and shippable on its own.
2. **Phase 2** — the teaching widgets against the same engine.
3. **Phase 3** — the pool / finding / traceability browsers.

Each phase stands alone; the shared engine is built once.

---

## 8. Non-goals (restated, to prevent scope creep)

No hosted/online deployment; no cross-class *validated* prediction; no generative inverse design; no
new science — the lab exposes what is already established and tested, and is honest about its edges.
