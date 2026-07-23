# Within-class forward model — M4 demonstration

**Built:** 2026-07-21 · **Module:** `src/geomind/model/forward.py` · **Finding:** F37 ·
**Follows:** F36/D17 (data-sufficiency analysis) · **Tests:** 8, all passing

The data-sufficiency analysis (F36) showed that a pooled cross-laboratory model is not
supported by the literature (leave-one-out R² < 0), but a model fit **within one structural
class and protocol** is genuinely predictive. This is that model — the concrete quantitative
output of the M4 adsorption dimension.

---

## The model

Trained on Varon *et al.*'s seven metakaolin geopolymers (`varon2025`, Sr sorption, one
laboratory, one protocol):

```
K_D = 2812 · [Al^IV]  −  9258         (mL/g;  [Al^IV] in mmol/g)
```

| metric | value |
|---|---|
| in-sample R² | 0.895 |
| **leave-one-out CV R²** | **0.811** |
| LOO RMSE | 522 mL/g (mean K_D = 1767) |
| domain | [Al^IV] ∈ [3.45, 4.77] mmol/g |
| n | 7 |

The leave-one-out figure is the one that matters: **the model predicts samples it never saw**,
so the relationship is real, not a retrospective fit.

---

## Why it is built this way

- **A straight line, deliberately.** With n = 7 and a mechanistically monotonic relationship
  (more framework Al → more charge-balancing exchange sites → more Sr uptake, proven atomically
  by Geddes/F34), any more flexible model would overfit. The honesty is in the form.
- **Framework Al^IV concentration as the input**, not Si/Al. F36 showed Si/Al is a within-class
  proxy whose sign flips across material families; [Al^IV] is the mechanistic descriptor and it
  is what predicts (+0.95).
- **A hard domain guard.** `predict()` refuses inputs outside the trained range (padded 10%),
  because the relationship is class-specific and was only established for metakaolin geopolymers
  and Sr. Deliberate extrapolation requires `strict=False`.

---

## What it is — and is not

- ✅ A **proof of concept** that the descriptor→property relationship is *predictive*, not merely
  correlational, when the class and protocol are held fixed. This is the quantitative backbone of
  the descriptor-and-methodology paper.
- ❌ **Not** a general, cross-material predictor. A test in the suite
  (`test_pooled_cross_lab_data_is_deliberately_NOT_used`) asserts that pooling the cross-lab data
  drives the LOO R² below zero — it will fail loudly if anyone ever tries to "improve" the model
  by pooling, guarding decision D17 in code.

## How it extends

The same recipe — one class, one protocol, the proper descriptor, LOO-validated — applies to any
future single-lab series (e.g. the confidential GEOMIND set or a short own-lab Si/Al campaign).
Those are what a *general* model would need; this module is the template they would slot into.
