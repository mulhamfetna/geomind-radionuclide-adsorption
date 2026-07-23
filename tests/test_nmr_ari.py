"""Tests for the Table 2 transcription and the Al-richness index.

The transcription is the weak point: these values were read off a rendered page,
not parsed. The sum-to-100 check is the real guard -- a mistyped digit almost
always breaks it.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from geomind.data import nmr_ari as N  # noqa: E402


def test_transcription_validates_clean():
    assert N.validate() == []


def test_twelve_samples_as_published():
    assert len(N.TABLE2) == 12


@pytest.mark.parametrize("sample", [s for s in N.TABLE2 if s not in N.KNOWN_INCOMPLETE])
def test_populations_sum_to_100(sample):
    """11 of 12 rows must sum to exactly 100 % -- the transcription's own check."""
    assert sum(N.TABLE2[sample].values()) == pytest.approx(100.0, abs=0.05)


def test_the_one_incomplete_row_is_declared_not_hidden():
    """Si10Al1Na1Ca11 sums to 99.0 in the source. Reproduced, not normalised."""
    assert sum(N.TABLE2["Si10Al1Na1Ca11"].values()) == pytest.approx(99.0, abs=0.05)


def test_ari_reproduces_hand_computed_values():
    """Spot-checks computed by hand from Table 2 before the module existed."""
    assert N.ari("Si2Al1Na1") == pytest.approx(2.336, abs=1e-3)   # 4*45.1 + 2*26.6
    assert N.ari("Si4Al1Na1") == pytest.approx(1.446, abs=1e-3)   # 4*24.9 + 1*45.0
    assert N.ari("Si10Al1Na1") == pytest.approx(0.500, abs=1e-3)  # 1*50.0
    assert N.ari("Si20Al1Na1") == pytest.approx(0.541, abs=1e-3)  # 1*54.1


def test_ari_is_zero_only_when_no_al_bearing_environment():
    """Every sample has some Al-bearing Si, so no ARI may be zero."""
    assert all(N.ari(s) > 0 for s in N.TABLE2)


def test_ca_bearing_samples_are_q4_poor():
    """Ca is a network modifier -- the framework descriptor should collapse (F19)."""
    ca_bearing = [s for s in N.TABLE2 if "Ca" in s]
    assert len(ca_bearing) == 8
    assert all(N.q4_fraction(s) < 30.0 for s in ca_bearing)


def test_ca_free_samples_are_q4_rich():
    ca_free = [s for s in N.TABLE2 if "Ca" not in s]
    assert len(ca_free) == 4
    assert all(N.q4_fraction(s) > 40.0 for s in ca_free)


def test_every_sample_maps_onto_a_pool_sorbent_name():
    from geomind.data.merge_adsorption import build

    pool_names = set(build()["sorbent_name"])
    missing = [n for n in N.POOL_NAME.values() if n not in pool_names]
    assert missing == [], f"unmatched sorbent names: {missing}"


def test_attach_adds_ari_without_dropping_or_duplicating_rows():
    from geomind.data.merge_adsorption import build

    pool = build()
    joined = N.attach(pool)
    assert len(joined) == len(pool)
    assert joined["ari"].notna().sum() == 39


def test_validator_catches_a_corrupted_population():
    original = N.TABLE2["Si2Al1Na1"]["Q4_4Al"]
    N.TABLE2["Si2Al1Na1"]["Q4_4Al"] = 55.1  # typo: sums to 110
    try:
        problems = N.validate()
        assert any("Si2Al1Na1" in p and "sum" in p for p in problems)
    finally:
        N.TABLE2["Si2Al1Na1"]["Q4_4Al"] = original


def test_validator_catches_an_unknown_environment_column():
    N.TABLE2["Si2Al1Na1"]["Q7_9Al"] = 0.0
    try:
        assert any("unknown environment" in p for p in N.validate())
    finally:
        del N.TABLE2["Si2Al1Na1"]["Q7_9Al"]


# --------------------------------------------------------------------------
# Kurumisawa — recovered into Pool A (F24)
# --------------------------------------------------------------------------

def test_kurumisawa_capacities_enter_pool_a_in_mg_per_g():
    from geomind.data.merge_adsorption import KURUMISAWA_QMAX_MMOL_G, build

    pool = build()
    ku = pool[pool["source_label"] == "kurumisawa2021"]
    assert len(ku) == 5
    n11 = ku[ku["sorbent_name"] == "N11"].iloc[0]
    assert n11["capacity_mg_g"] == pytest.approx(0.727 * 132.905, rel=1e-6)
    assert KURUMISAWA_QMAX_MMOL_G["N11"] == 0.727


def test_kurumisawa_n11_fails_the_saturation_screen():
    """The HIGHEST reported capacity is the least saturated — F14/F16 in action."""
    from geomind.data.merge_adsorption import (
        KURUMISAWA_HIGHEST_POINT,
        KURUMISAWA_QMAX_MMOL_G,
    )

    theta = {s: KURUMISAWA_HIGHEST_POINT[s][1] / q
             for s, q in KURUMISAWA_QMAX_MMOL_G.items()}
    assert theta["N11"] < 0.5
    assert max(KURUMISAWA_QMAX_MMOL_G, key=KURUMISAWA_QMAX_MMOL_G.get) == "N11"
    assert theta["K11"] > 0.8 and theta["KN11"] > 0.8


# --------------------------------------------------------------------------
# Varon leaching companion — the within-sample causal test (F27, batch 4)
# --------------------------------------------------------------------------

def test_varon_leached_rows_present_and_distinct_from_fresh():
    from geomind.data.merge_adsorption import build

    pool = build()
    fresh = pool[pool["source_label"] == "varon2025"]
    leached = pool[pool["source_label"] == "varon_leached2026"]
    assert len(leached) == 7
    # leached rows must be a DISTINCT sorbent state, never sharing a name with fresh
    assert leached["sorbent_name"].str.contains("leached").all()
    assert not set(leached["sorbent_name"]) & set(fresh["sorbent_name"])


def test_varon_leaching_is_a_causal_test_of_framework_al():
    """corr(Δ[AlIV], ΔKD) is strongly positive: losing framework Al loses sorption."""
    import numpy as np

    # (label, [AlIV]mmol 0h, KD 0h, [AlIV]mmol 96h, KD 96h) from Tables 3-4
    d = [
        ("K-0.5-16", 4.77, 4100, 3.38, 1350), ("K-1-16", 4.14, 2500, 3.82, 1050),
        ("K-1.2-16", 3.94, 1800, 3.73, 820), ("K-1.5-16", 3.71, 1100, 3.67, 450),
        ("K-1.2-8", 3.61, 70, 3.61, 150), ("K-1.2-12", 3.83, 1900, 3.61, 1000),
        ("Na-1.2-16", 3.45, 900, 3.20, 130),
    ]
    d_aliv = np.array([r[1] - r[3] for r in d])
    d_kd = np.array([r[2] - r[4] for r in d])
    r = np.corrcoef(d_aliv, d_kd)[0, 1]
    assert r > 0.9, f"causal Δ correlation should be strong, got {r:.3f}"


def test_varon_aliv_concentration_beats_bet_for_kd():
    """[AlIV] mmol/g predicts KD; BET does not (the central project finding, 0h)."""
    import numpy as np

    aliv = np.array([4.77, 4.14, 3.94, 3.71, 3.61, 3.83, 3.45])
    bet = np.array([72, 163, 188, 212, 15, 182, 38.0])
    kd = np.array([4100, 2500, 1800, 1100, 70, 1900, 900.0])
    assert np.corrcoef(aliv, kd)[0, 1] > 0.9
    assert np.corrcoef(bet, kd)[0, 1] < 0.3
