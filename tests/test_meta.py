import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from geomind import meta as M  # noqa: E402


def test_every_study_reports_direction_n_and_effect():
    studies = M.collect_studies()
    assert len(studies) >= 4
    for s in studies:
        assert s.n >= 3, f"{s.label}: an effect size needs n>=3"
        assert -1.0 <= s.r <= 1.0
        assert s.descriptor and s.target and s.source_label


def test_all_studies_run_in_the_predicted_direction():
    """The claim under test: more framework Al -> better uptake/retention. Every
    study is sign-corrected so + always means 'supports', whatever its raw target."""
    res = M.meta_analyse(M.collect_studies())
    assert res["k"] >= 4
    assert res["n_supporting"] == res["k"], "a study opposing the direction must be reported, not hidden"
    assert res["r_bar"] > 0.5
    assert 0.0 < res["sign_test_p"] <= 0.0625


def test_negative_controls_do_not_show_the_pattern():
    """Mechanistic specificity: surface area should not predict, the descriptor
    should die in Ca-bearing gels, and it should not track a non-cation adsorbate."""
    ctrl = {c.label: c for c in M.collect_negative_controls()}
    assert abs(ctrl["BET surface area (Varon)"].r) < 0.5
    assert abs(ctrl["ARI in Ca-bearing gels (Oulu)"].r) < 0.3
    # a dye is not exchanged at Al sites - the descriptor must NOT track it positively
    assert ctrl["ARI vs dye uptake (Oulu)"].r < 0


def test_fisher_z_matches_a_hand_computation():
    import numpy as np
    r_bar = M._fisher_z_mean([0.5, 0.5], [10, 10])
    assert r_bar == pytest.approx(0.5, abs=1e-9)
    # weighting: a larger study pulls the mean toward its own value
    mixed = M._fisher_z_mean([0.9, 0.1], [50, 5])
    assert mixed > M._fisher_z_mean([0.9, 0.1], [5, 50])


def test_power_projection_is_honest_about_k():
    """Each ADDITIONAL STUDY, not each additional row, is what buys significance."""
    assert M.sign_test_p(4) == pytest.approx(0.0625)
    assert M.sign_test_p(5) == pytest.approx(0.03125)
    assert M.sign_test_p(6) == pytest.approx(0.015625)
    assert M.sign_test_p(8) < 0.005
