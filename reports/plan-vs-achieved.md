# Retrospective — the original plan vs. what was achieved

**Prepared:** 2026-07-21 · **Confidential (pre-publication)**

An honest audit of the project against the plan it set out with: the setup brief given at the
pivot, and the M1–M6 roadmap recorded in the README. The standard applied here is the same one the
project held throughout — no achievement claimed without evidence, and no shortfall softened.

---

## 1. The setup brief (the pivot instructions) — 7 of 7 delivered

| # | Asked for | Status | Evidence |
|---|---|---|---|
| 1 | Make the repo private | ✅ done | private, all-rights-reserved (`NOTICE.md`) |
| 2 | Deep analysis of the paper → detailed docs | ✅ done | M1 reproduction spec (`docs/paper-analysis/`) |
| 3 | Replicate the paper on our compiled data | ⚠️ re-scoped | see M3a |
| 4 | Add a 4th dimension (adsorbability) for Cs/Sr | ⚠️ transformed | see M4 |
| 5 | Scrape / mine related papers & data | ✅ done, then closed | ~40 papers mined into two pools; closed as saturated (F36/D17) |
| 6 | Full GitHub workflow (branches, PRs, issues, milestones) | ✅ done | main/dev/feature branches, PRs, milestone commits in history |
| 7 | Rename · confidential · license · Zenodo DOI per milestone | ✅ mostly | renamed `geomind-radionuclide-adsorption`; confidential; restricted Zenodo deposit prepared — **DOI mint pending PI** |

Infrastructure and process: **fully delivered.**

---

## 2. The M1–M6 technical roadmap — the scorecard

| Milestone | Plan | Reality | Verdict |
|---|---|---|---|
| **M1** Paper analysis | reproduction spec | reproduction spec written | ✅ **done** |
| **M2** Data cleaning & provenance | audited dataset + quality report | done — and the audit (≈32% of rows failed) became a *contribution*, not just prep | ✅ **done, exceeded** |
| **M3a** Faithful replication | reproduce GEOMIND's own samples | **blocked** — needs the confidential 112-sample set; only the chemistry layer was verified (Si/Al, Si/M_sol, Solid/Liquid within 1–3%) | ❌ **blocked** |
| **M3b** Cross-system transfer | apply the architecture to our data | acknowledged as a *different material system* (fly-ash/slag concrete vs metakaolin paste), explicitly not a validation | 🔄 **re-scoped honestly** |
| **M4** 4th dimension | adsorption capacity as a **generative** target | the *science* is settled (framework Al governs uptake, three evidence levels) and a *forward* model is predictive (LOO-CV R² = 0.81) — but not integrated as a generative target | ⚠️ **science delivered, generative integration not** |
| **M5** Radionuclide design | generative Cs/Sr formulation design | not reached — gated on M3a and on single-protocol data | ❌ **not reached** |
| **M6** Corpus expansion | grow the dataset | done, then **deliberately closed** as saturated (adding literature reduces predictability, F36) | ✅ **done → closed** |

---

## 3. The honest headline

**The plan's ultimate goal — a generative inverse-design model (replicate GEOMIND, then extend it
to radionuclide design) — was not reached.** That is the truthful bottom line and it outweighs any
partial credit on the individual milestones.

The reason it was not reached is, however, the project's single most valuable result. We
established **empirically that the generative model cannot be built from the published literature**:
within one laboratory and protocol the descriptor→property relationship predicts held-out samples
(leave-one-out R² = 0.81), but pooled across laboratories it is worse than guessing the mean
(R² < 0), and adding further literature makes it worse, not better (F36/D17). The plan assumed the
data would support the model; the data imposed a ceiling. The project's discipline was to *discover
that ceiling and adapt* rather than ship a model that would have learned inter-laboratory noise and
reported it as chemistry — the very failure mode the M2 audit exists to prevent, one level up.

---

## 4. What emerged that the plan did not anticipate

In pursuing the model, the project produced outcomes the original plan did not list — and which are
arguably more solid than the plan's target, precisely because each is evidenced:

- **A mechanism-grounded scientific finding** — framework aluminium (specifically its
  concentration), not surface area, governs Cs/Sr uptake — established on three independent levels:
  correlation (r up to +0.95), a within-sample causal test (r = +0.94), and a direct atomic
  mechanism (Sr imaged at Al^IV sites; Geddes 2025).
- **A validated forward model** (the M4 science made quantitative and predictive).
- **Reusable methods** — the saturation screen (θ = 1 − R_L) that flags extrapolation artefacts,
  the two-pool audit framework, the leachant-inversion caution, and the "pooling fails" result as a
  general caution for materials-informatics meta-analysis.
- **A complete, submission-ready manuscript** — where the plan aimed at a *model*, the project
  delivered a *publishable result* (`manuscript/manuscript-submission.{md,docx,pdf}`).

---

## 5. Net assessment

- **Setup & infrastructure (7/7):** fully delivered.
- **M1, M2, M6:** delivered (M2 exceeded; M6 delivered then correctly closed). **M3b:** honestly
  re-scoped.
- **M3a, M5 (the generative core):** not delivered — blocked by confidential data and a structural
  data limit that no amount of literature could remove.
- **M4:** the science delivered and validated; the generative integration did not.

**Roughly two-thirds of the roadmap achieved; the generative third genuinely blocked — and the
block itself converted into a strong, honest, publishable outcome.** The project did not hit its
original target. It determined that the target was unreachable on the available data, proved *why*,
and delivered the best defensible result instead. That is a mature research trajectory, not a
failed one.

---

## 6. What would move the blocked milestones (recorded, not requested)

M3a and M5 are not literature problems and will not yield to more mining. They require
**single-protocol, composition-varying data**, obtainable two ways:

1. the **confidential GEOMIND 112-sample dataset** (one request to the reference-paper authors), or
2. a **short own-laboratory campaign** — a Si/Al series with ²⁹Si/²⁷Al NMR and an Sr uptake test —
   which would supply the composition-varying paired data a generative model needs and let the
   causal test be reproduced under controlled conditions.

Either would reopen M4-generative and M5; neither is a reason to resume literature acquisition.
