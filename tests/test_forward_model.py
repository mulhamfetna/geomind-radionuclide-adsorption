"""Tests for the within-class forward model (M4 demonstration, F36/D17)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from geomind.model import forward as F  # noqa: E402


@pytest.fixture(scope="module")
def model():
    return F.fit()


def test_trained_on_the_clean_single_class_series(model):
    from geomind.data.merge_adsorption import build

    df = F.training_data(build())
    assert model.n == len(df) == 7          # Varon metakaolin geopolymers, Sr
    assert (df[F.DESCRIPTOR] > 0).all() and (df[F.TARGET] > 0).all()


def test_the_relationship_is_positive_and_physical(model):
    """More framework Al -> more exchange sites -> higher K_D (the whole point)."""
    assert model.slope > 0


def test_it_predicts_out_of_sample_not_just_in_sample(model):
    """The honest claim: leave-one-out CV, not the flattering in-sample fit."""
    assert model.r2_loo > 0.8               # genuinely predictive within the class
    assert model.r2_loo < model.r2_in_sample  # LOO is (correctly) the harder number


def test_predict_matches_the_fitted_line(model):
    mid = 0.5 * (model.x_min + model.x_max)
    assert model.predict(mid) == pytest.approx(model.slope * mid + model.intercept)


def test_predict_refuses_out_of_domain_by_default(model):
    # far below and far above the trained [Al^IV] range
    with pytest.raises(F.OutOfDomainError):
        model.predict(model.x_min - 1.0)
    with pytest.raises(F.OutOfDomainError):
        model.predict(model.x_max + 1.0)


def test_extrapolation_is_possible_only_when_explicitly_asked(model):
    # strict=False lets a caller extrapolate deliberately, no exception
    val = model.predict(model.x_max + 1.0, strict=False)
    assert isinstance(val, float)


def test_a_small_pad_inside_the_domain_is_allowed(model):
    span = model.x_max - model.x_min
    assert isinstance(model.predict(model.x_max + 0.05 * span), float)


def test_pooled_cross_lab_data_is_deliberately_NOT_used():
    """Guard the core F36 decision: this model must not be trained on the pooled set.

    If someone ever 'improves' it by pooling all sources, the LOO R^2 collapses below
    zero (the whole reason the model is within-class). This test documents that.
    """
    import numpy as np

    from geomind.data.merge_adsorption import build

    A = build()
    cq = A[(A["adsorbate"] == "Cs") & (A["capacity_type"] == "langmuir_qmax")].dropna(
        subset=["si_al", "capacity_mg_g"]
    )
    x = cq["si_al"].to_numpy(float)
    y = cq["capacity_mg_g"].to_numpy(float)
    r2_loo, _ = F._loo(x, y)
    assert r2_loo < 0, "pooled cross-lab model should be worse than the mean (F36)"
