import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from geomind import robustness as R  # noqa: E402


def test_varon_table2_derivation_is_internally_consistent():
    """[Al^IV] = total Al x tetrahedral fraction, to Varon's reported precision."""
    import numpy as np
    derived = R.VARON_AL_TOTAL * R.VARON_ALIV_FRACTION
    # atol 0.05 absorbs Varon's own 2-dp rounding of the fraction and total
    assert np.allclose(derived, R.VARON_ALIV, atol=0.05)   # matches Table 2's [Al^IV]exp


def test_analytical_robustness_holds():
    a = R.analytical_robustness()
    # the core correlation is not driven by one point
    assert a["jackknife_r_min"] > 0.80
    # rank correlation agrees with Pearson (not an outlier artefact)
    assert a["spearman_rho"] > 0.85
    # the fitted slope is stable under jackknife
    assert 2400 < a["jackknife_slope_min"] and a["jackknife_slope_max"] < 3200
    # the saturation-artefact count is stable across thresholds (not cherry-picked)
    assert set(a["saturation_artefacts_by_threshold"].values()) <= {3, 4}
    # the meta-analysis mean is positive under every weighting
    assert all(v > 0.5 for v in a["meta_r_bar_by_weighting"].values())


def test_s3_at_reported_precision_leaves_the_result_essentially_unchanged():
    """The reported +/-1 pp on the tetrahedral fraction does not overturn the relationship."""
    s = R.aliv_uncertainty_sensitivity(include_xrf=False, draws=4000)
    assert s["mean_relative_sigma_pct"] < 2.0            # ~1.1% relative on [Al^IV]
    assert s["r_mean"] > 0.90                            # correlation essentially unchanged
    assert s["prob_r_above_0p8"] > 0.99                 # r>0.8 in ~all draws
    assert 2600 < s["slope_mean"] < 2900                # negligible regression dilution


def test_s3_is_deterministic_across_runs():
    """Seeded RNG — the sensitivity numbers must reproduce exactly."""
    a = R.aliv_uncertainty_sensitivity(include_xrf=False, draws=2000)
    b = R.aliv_uncertainty_sensitivity(include_xrf=False, draws=2000)
    assert a["r_mean"] == b["r_mean"] and a["slope_mean"] == b["slope_mean"]
