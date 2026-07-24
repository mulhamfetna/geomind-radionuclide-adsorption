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


# ---------------------------------------------------------------------------
# Re-triage of the existing corpus against the broader profile (2026-07-24)
# ---------------------------------------------------------------------------
def test_every_rejected_candidate_carries_a_principled_reason():
    """The re-triage found NO new qualifying study. Each rejection must be on a
    stated principle, not on the direction of its result - otherwise the
    inclusion criteria are just cherry-picking."""
    rej = M.REJECTED_CANDIDATES
    assert len(rej) >= 5
    for c in rej:
        assert c["reason"], f"{c['label']} has no stated reason"
        assert c["criterion"] in M.INCLUSION_CRITERIA, f"{c['label']}: unknown criterion"


def test_rejections_are_not_direction_dependent():
    """Both a SUPPORTING and an OPPOSING candidate must appear among the rejects.
    If we only ever rejected inconvenient results, the meta-analysis would be
    worthless."""
    dirs = {c["would_have"] for c in M.REJECTED_CANDIDATES}
    assert "supports" in dirs and "opposes" in dirs


def test_si_al_is_not_accepted_as_a_cross_class_proxy():
    """The re-triage established that Si/Al inverts between structural classes
    (F36), so it is admissible only inside one designed single-class series."""
    assert M.si_al_admissible(structural_class="zeolite", designed_series=False) is False
    assert M.si_al_admissible(structural_class="mixed", designed_series=True) is False
    assert M.si_al_admissible(structural_class="ca_si_al_slag", designed_series=True) is True
