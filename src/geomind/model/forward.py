"""Within-class forward model — the M4 quantitative demonstration.

Given the framework-aluminium content of a metakaolin geopolymer, predict its Sr
distribution coefficient K_D. This is the concrete, on-data output justified by the
data-sufficiency analysis (finding F36, decision D17): a pooled cross-laboratory model
is not supported by the literature (leave-one-out R^2 < 0), but a model fit **within a
single structural class and protocol** is genuinely predictive out of sample.

## Scope and honesty (read before using a prediction)

This is a **proof-of-concept**, not a production predictor:

* It is trained on ONE clean series — Varon *et al.*'s seven metakaolin geopolymers
  (`varon2025`), Sr sorption, one laboratory, one protocol. n = 7.
* It is valid ONLY for **metakaolin geopolymers**, for **Sr**, and ONLY for framework
  aluminium in the covered range. Outside that domain :meth:`ForwardModel.predict`
  refuses, because F19/D12 established that the descriptor's sign is not portable across
  structural classes (in zeolites Si/Al correlates the OTHER way) and F36 showed pooling
  destroys predictability.
* The point is not the exact numbers; it is that the mechanism (F27, F34) yields a
  relationship that predicts held-out samples (LOO-CV R^2 = 0.81) when — and only when —
  the class and protocol are held fixed.

The right form is a simple straight line: with n = 7 and a mechanistically monotonic
relationship, anything more flexible would overfit. The model reports its own
leave-one-out cross-validation so its predictive claim is never taken on faith.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

#: The descriptor and target this model relates.
DESCRIPTOR = "al_iv_mmol_g"   # framework Al^IV concentration, mmol/g
TARGET = "kd_mL_g"            # Sr distribution coefficient, mL/g

#: The single clean series this proof-of-concept is trained on.
TRAINING_SOURCE = "varon2025"
TRAINING_CLASS = "metakaolin geopolymer"
TRAINING_ADSORBATE = "Sr"

#: Predictions are refused more than this fraction beyond the trained descriptor range,
#: since the relationship is only established inside the covered domain.
DOMAIN_PAD = 0.10


class OutOfDomainError(ValueError):
    """Raised when a prediction is requested outside the model's domain of validity."""


@dataclass(frozen=True)
class ForwardModel:
    """A fitted within-class Al^IV -> Sr K_D line, with its own CV metrics and domain."""

    slope: float           # mL/g per (mmol/g)
    intercept: float       # mL/g
    x_min: float           # descriptor domain (mmol/g)
    x_max: float
    n: int
    r2_in_sample: float
    r2_loo: float          # leave-one-out cross-validated R^2 -- the honest number
    rmse_loo: float        # mL/g
    y_mean: float

    # -- use -----------------------------------------------------------------
    def predict(self, al_iv_mmol_g: float, *, strict: bool = True) -> float:
        """Predict Sr K_D (mL/g) from framework Al^IV (mmol/g).

        Args:
            al_iv_mmol_g: framework-aluminium concentration of a *metakaolin geopolymer*.
            strict: if True (default), refuse inputs outside the trained domain
                (padded by :data:`DOMAIN_PAD`). Set False only for deliberate,
                clearly-labelled extrapolation.

        Raises:
            OutOfDomainError: input outside the domain of validity while ``strict``.
        """
        span = self.x_max - self.x_min
        lo, hi = self.x_min - DOMAIN_PAD * span, self.x_max + DOMAIN_PAD * span
        if strict and not (lo <= al_iv_mmol_g <= hi):
            raise OutOfDomainError(
                f"[Al^IV] = {al_iv_mmol_g:.2f} mmol/g is outside the model's domain "
                f"[{self.x_min:.2f}, {self.x_max:.2f}] (metakaolin geopolymers, Sr). "
                "The descriptor's relationship is class-specific (F19/D12) and was not "
                "established here; pass strict=False only to extrapolate deliberately."
            )
        return self.slope * al_iv_mmol_g + self.intercept

    def summary(self) -> str:
        return (
            f"K_D = {self.slope:.0f}*[Al^IV] {self.intercept:+.0f}  (mL/g; "
            f"{TRAINING_CLASS}, Sr, n={self.n})\n"
            f"  in-sample R^2 = {self.r2_in_sample:.3f}\n"
            f"  leave-one-out R^2 = {self.r2_loo:.3f}, RMSE = {self.rmse_loo:.0f} mL/g "
            f"(mean K_D = {self.y_mean:.0f})\n"
            f"  domain: [Al^IV] in [{self.x_min:.2f}, {self.x_max:.2f}] mmol/g"
        )


def _loo(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    """Leave-one-out CV of a straight-line fit -> (R^2, RMSE)."""
    pred = np.empty(len(x))
    for i in range(len(x)):
        m = np.ones(len(x), bool)
        m[i] = False
        b1, b0 = np.polyfit(x[m], y[m], 1)
        pred[i] = b1 * x[i] + b0
    ss_res = float(((y - pred) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    r2 = 1.0 - ss_res / ss_tot
    rmse = float(np.sqrt(((y - pred) ** 2).mean()))
    return r2, rmse


def training_data(pool: pd.DataFrame) -> pd.DataFrame:
    """The clean single-class series this model is fit on, pulled from Pool A."""
    df = pool[pool["source_label"] == TRAINING_SOURCE].dropna(
        subset=[DESCRIPTOR, TARGET]
    )
    return df[[DESCRIPTOR, TARGET, "sorbent_name"]].sort_values(DESCRIPTOR).reset_index(drop=True)


def fit(pool: pd.DataFrame | None = None) -> ForwardModel:
    """Fit the within-class forward model from Pool A (or a provided pool)."""
    if pool is None:
        from geomind.data.merge_adsorption import build

        pool = build()
    df = training_data(pool)
    x = df[DESCRIPTOR].to_numpy(float)
    y = df[TARGET].to_numpy(float)
    if len(x) < 3:
        raise ValueError(f"need >=3 training points, got {len(x)}")
    b1, b0 = np.polyfit(x, y, 1)
    pred = b1 * x + b0
    r2_in = 1.0 - ((y - pred) ** 2).sum() / ((y - y.mean()) ** 2).sum()
    r2_loo, rmse_loo = _loo(x, y)
    return ForwardModel(
        slope=float(b1), intercept=float(b0),
        x_min=float(x.min()), x_max=float(x.max()), n=len(x),
        r2_in_sample=float(r2_in), r2_loo=r2_loo, rmse_loo=rmse_loo,
        y_mean=float(y.mean()),
    )


def main() -> None:  # pragma: no cover - CLI convenience
    m = fit()
    print(m.summary())


if __name__ == "__main__":  # pragma: no cover
    main()
