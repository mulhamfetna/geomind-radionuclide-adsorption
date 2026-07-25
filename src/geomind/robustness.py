"""Robustness and sensitivity analyses for the framework-aluminium result.

Two distinct families of check, both reported for a D1 submission:

1. **Analytical robustness** — do the conclusions survive reasonable changes to the *method*,
   holding the data fixed? Influential-point jackknife on the core correlation, a rank
   (Spearman) correlation, the forward-model slope under jackknife, the saturation-screen
   artefact count across thresholds, and the meta-analysis mean under different weightings.

2. **Input-uncertainty sensitivity (S3)** — the descriptor [Al^IV] is a *measured* quantity
   (total Al by XRF times the tetrahedral fraction from 27Al MAS NMR), so it carries error.
   Varon 2025 (Table 2) reports that error explicitly: **+/-1 percentage point** on the
   Al^IV fraction. We propagate it by Monte Carlo and watch the correlation and slope respond.
   This is an errors-in-variables / regression-dilution check, and it is *different* from the
   analytical robustness above.

All randomness is seeded (numpy Generator with a fixed seed) so every number is reproducible;
``numpy.random.default_rng`` is used deliberately rather than the global RNG.
"""
from __future__ import annotations

import numpy as np

# --- Varon 2025, Table 2 (verified inline against the PDF) --------------------------------
#: Total aluminium content per geopolymer, mmol/g (from XRF).
VARON_AL_TOTAL = np.array([4.97, 4.41, 4.20, 4.08, 4.11, 4.15, 4.11])
#: Tetrahedral (Al^IV) fraction per geopolymer, as a fraction (from 27Al MAS NMR).
VARON_ALIV_FRACTION = np.array([96.0, 93.8, 94.0, 91.4, 88.0, 92.4, 84.7]) / 100.0
#: The framework-Al descriptor [Al^IV]exp, mmol/g (= total x fraction; matches the pool).
VARON_ALIV = np.array([4.77, 4.14, 3.94, 3.71, 3.61, 3.83, 3.45])
#: REPORTED uncertainty on the Al^IV fraction: +/-1 percentage point (absolute).
ALIV_FRACTION_SIGMA = 0.01
#: A typical relative uncertainty on the XRF total-Al, used only in the conservative variant.
XRF_TOTAL_AL_REL_SIGMA = 0.015

_SEED = 20260725


def _varon_xy():
    """The n=7 Varon series (Al^IV, Sr K_D) from the live pool, in ascending Al^IV order."""
    from geomind.data.merge_adsorption import build as build_A
    v = build_A()
    v = v[v["source_label"] == "varon2025"].dropna(
        subset=["al_iv_mmol_g", "kd_mL_g"]).sort_values("al_iv_mmol_g")
    return v["al_iv_mmol_g"].to_numpy(float), v["kd_mL_g"].to_numpy(float)


def _r(a, b) -> float:
    return float(np.corrcoef(a, b)[0, 1])


# ---------------------------------------------------------------------------
# 1. Analytical robustness
# ---------------------------------------------------------------------------
def analytical_robustness() -> dict:
    """Do the conclusions survive reasonable analytical choices, data held fixed?"""
    from scipy import stats
    from geomind import meta as M
    from geomind.source_data import build_source_data

    x, y = _varon_xy()
    full = _r(x, y)
    jack_r = [_r(np.delete(x, i), np.delete(y, i)) for i in range(len(x))]
    jack_slope = [float(np.polyfit(np.delete(x, i), np.delete(y, i), 1)[0]) for i in range(len(x))]
    rho, p_rho = stats.spearmanr(x, y)

    theta = build_source_data()["Fig5_saturation"]["theta"].to_numpy(float)
    artefacts = {t: int((theta < t).sum()) for t in (0.4, 0.5, 0.6)}

    st = M.collect_studies()
    rs = [s.r for s in st]
    ns = [s.n for s in st]

    def _fz(weights):  # weighted mean correlation via Fisher's z (weights given directly)
        z = [np.arctanh(min(max(r, -0.999999), 0.999999)) for r in rs]
        return float(np.tanh(sum(w * zi for w, zi in zip(weights, z)) / sum(weights)))

    weightings = {
        "unweighted": _fz([1] * len(rs)),
        "n_minus_3": _fz([n - 3 for n in ns]),   # the estimator the paper uses
        "n": _fz(ns),
    }
    return {
        "pearson_full": full,
        "spearman_rho": float(rho),
        "spearman_p": float(p_rho),
        "jackknife_r_min": float(min(jack_r)),
        "jackknife_r_max": float(max(jack_r)),
        "jackknife_slope_min": float(min(jack_slope)),
        "jackknife_slope_max": float(max(jack_slope)),
        "saturation_artefacts_by_threshold": artefacts,
        "meta_r_bar_by_weighting": weightings,
        "meta_sign_p_k4": M.sign_test_p(4),
        "meta_sign_p_k3_conservative": M.sign_test_p(3),
    }


# ---------------------------------------------------------------------------
# 2. Input-uncertainty sensitivity (S3)
# ---------------------------------------------------------------------------
def _aliv_sigma(include_xrf: bool) -> np.ndarray:
    """Per-sample absolute sigma on [Al^IV], from the reported measurement uncertainties.

    [Al^IV] = total_Al x fraction. The fraction carries +/-1 pp (reported). With
    ``include_xrf`` a typical XRF uncertainty on total Al is added in quadrature.
    """
    from_fraction = VARON_AL_TOTAL * ALIV_FRACTION_SIGMA
    if not include_xrf:
        return from_fraction
    from_xrf = VARON_ALIV_FRACTION * (XRF_TOTAL_AL_REL_SIGMA * VARON_AL_TOTAL)
    return np.sqrt(from_fraction ** 2 + from_xrf ** 2)


def aliv_uncertainty_sensitivity(include_xrf: bool = False, draws: int = 10000) -> dict:
    """S3: propagate the reported [Al^IV] measurement uncertainty into the correlation and slope.

    Returns the mean and 5-95% interval of r and slope, and the fraction of Monte-Carlo draws
    that keep r above 0.8. ``include_xrf=False`` uses only what Varon states (+/-1 pp on the
    tetrahedral fraction); True adds a typical XRF total-Al uncertainty as a conservative check.
    """
    x, y = _varon_xy()
    # align each pool x to its Table-2 sigma by matching [Al^IV]
    idx = [int(np.argmin(np.abs(VARON_ALIV - xi))) for xi in x]
    sigma = _aliv_sigma(include_xrf)[idx]

    rng = np.random.default_rng(_SEED)
    rs = np.empty(draws)
    slopes = np.empty(draws)
    for k in range(draws):
        xp = x + rng.normal(0.0, sigma)
        rs[k] = np.corrcoef(xp, y)[0, 1]
        slopes[k] = np.polyfit(xp, y, 1)[0]
    return {
        "scenario": "NMR fraction only (+/-1 pp)" if not include_xrf
                    else "NMR fraction + 1.5% XRF total-Al",
        "mean_relative_sigma_pct": float(np.mean(sigma / x) * 100),
        "r_mean": float(rs.mean()),
        "r_p05": float(np.percentile(rs, 5)),
        "r_p95": float(np.percentile(rs, 95)),
        "slope_mean": float(slopes.mean()),
        "slope_p05": float(np.percentile(slopes, 5)),
        "slope_p95": float(np.percentile(slopes, 95)),
        "prob_r_above_0p8": float((rs > 0.8).mean()),
        "observed_r": _r(x, y),
        "observed_slope": float(np.polyfit(x, y, 1)[0]),
    }


def report() -> str:
    a = analytical_robustness()
    s3a = aliv_uncertainty_sensitivity(include_xrf=False)
    s3b = aliv_uncertainty_sensitivity(include_xrf=True)
    L = ["ROBUSTNESS & SENSITIVITY", "=" * 24, "",
         "1. ANALYTICAL ROBUSTNESS (data fixed, method varied)",
         f"   core correlation r(Al^IV, K_D)     = {a['pearson_full']:+.3f}",
         f"   influential-point jackknife range  = [{a['jackknife_r_min']:+.3f}, "
         f"{a['jackknife_r_max']:+.3f}]  (drops the extreme point too)",
         f"   Spearman rank rho                  = {a['spearman_rho']:+.3f} "
         f"(p = {a['spearman_p']:.3f})",
         f"   forward slope jackknife            = [{a['jackknife_slope_min']:.0f}, "
         f"{a['jackknife_slope_max']:.0f}]  (fitted 2812)",
         f"   saturation artefacts by threshold  = {a['saturation_artefacts_by_threshold']}",
         f"   meta r_bar by weighting            = "
         + ", ".join(f"{k} {v:+.2f}" for k, v in a['meta_r_bar_by_weighting'].items()),
         f"   meta sign test p                   = {a['meta_sign_p_k4']:.4f} (k=4); "
         f"{a['meta_sign_p_k3_conservative']:.4f} (conservative k=3)", "",
         "2. S3 - SENSITIVITY TO [Al^IV] UNCERTAINTY (input error propagated)",
         "   Varon 2025 reports +/-1 percentage point on the 27Al tetrahedral fraction."]
    for s in (s3a, s3b):
        L += [f"   {s['scenario']}  (~{s['mean_relative_sigma_pct']:.1f}% relative on [Al^IV]):",
              f"      r     = {s['r_mean']:+.3f}  (5-95%: {s['r_p05']:+.3f} .. {s['r_p95']:+.3f})"
              f"   P(r>0.8) = {s['prob_r_above_0p8']*100:.0f}%",
              f"      slope = {s['slope_mean']:.0f}   (5-95%: {s['slope_p05']:.0f} .. "
              f"{s['slope_p95']:.0f})"]
    L += ["", f"   observed (no perturbation): r = {s3a['observed_r']:+.3f}, "
          f"slope = {s3a['observed_slope']:.0f}"]
    return "\n".join(L)


def main() -> None:  # pragma: no cover
    print(report())


if __name__ == "__main__":  # pragma: no cover
    main()
