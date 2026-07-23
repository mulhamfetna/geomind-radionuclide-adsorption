"""Tests for Pool B — the immobilisation schema and its adapters (D13)."""

import math
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from geomind.data import immobilisation_schema as S  # noqa: E402
from geomind.data import merge_immobilisation as M  # noqa: E402


# --------------------------------------------------------------------------
# The LI <-> De relation, verified against two independent published tables
# --------------------------------------------------------------------------

KIM_TABLE2_CELLS = [
    (8.88e-16, 15.5), (3.80e-14, 13.4), (2.10e-16, 15.7), (6.36e-16, 15.2),
    (1.17e-15, 14.9), (1.14e-16, 15.9), (1.91e-16, 15.7), (2.00e-16, 15.7),
    (5.80e-18, 17.2), (7.66e-17, 16.1), (5.70e-17, 16.2), (2.33e-17, 16.6),
    (3.03e-17, 16.5),
]
#: the single cell that does NOT satisfy LI = -log10(De) — a typo in the source
KIM_ERRATUM_CELL = (8.88e-16, 15.5)


@pytest.mark.parametrize("de,li", [c for c in KIM_TABLE2_CELLS if c != KIM_ERRATUM_CELL])
def test_li_from_de_matches_kim_table2(de, li):
    assert S.li_from_de(de) == pytest.approx(li, abs=0.06)


def test_the_kim_erratum_cell_really_does_disagree():
    """Guards the erratum: if a future edit 'fixes' this, the test fails loudly."""
    de, printed = KIM_ERRATUM_CELL
    assert S.li_from_de(de) == pytest.approx(15.05, abs=0.01)
    assert abs(S.li_from_de(de) - printed) > 0.4


def test_kim_column_average_proves_the_erratum():
    """Kim's own Average LI for NaSr1 is 15.5, reachable only from 15.05, not 15.5."""
    lis = [S.li_from_de(8.88e-16), S.li_from_de(1.14e-16)]
    assert sum(lis) / 2 == pytest.approx(15.5, abs=0.02)
    assert (15.5 + 15.94) / 2 == pytest.approx(15.72, abs=0.02)  # what a real 15.5 gives


@pytest.mark.parametrize("de,li", [(2.2e-19, 18.7), (7.8e-20, 19.1),
                                   (5.4e-14, 13.3), (6.0e-14, 13.2)])
def test_li_from_de_matches_nevin_table2(de, li):
    """Independent confirmation from a different paper and instrument."""
    assert S.li_from_de(de) == pytest.approx(li, abs=0.06)


def test_de_from_li_round_trips():
    assert S.de_from_li(S.li_from_de(3.03e-17)) == pytest.approx(3.03e-17, rel=1e-9)


def test_li_of_nonpositive_de_raises_rather_than_returning_nan():
    with pytest.raises(ValueError):
        S.li_from_de(0.0)


# --------------------------------------------------------------------------
# Direction of merit — trap 1
# --------------------------------------------------------------------------

def test_li_and_de_have_opposite_directions_of_merit():
    assert S.HIGHER_IS_BETTER[S.RetentionType.LEACHABILITY_INDEX] is True
    assert S.HIGHER_IS_BETTER[S.RetentionType.EFFECTIVE_DIFFUSIVITY] is False


def test_every_retention_type_declares_a_direction():
    for t in S.RetentionType:
        assert t in S.HIGHER_IS_BETTER


def test_pooling_warns_when_directions_conflict():
    df = M.build()
    df.loc[0, "retention_type"] = S.RetentionType.EFFECTIVE_DIFFUSIVITY.value
    warns = S.pooling_warning(df)
    assert any("OPPOSING directions" in w for w in warns)


# --------------------------------------------------------------------------
# Censoring — trap 3
# --------------------------------------------------------------------------

def test_kim_below_detection_samples_are_left_censored_not_null():
    df = M.build()
    for sample in ("KSr1", "KSr2"):
        row = df[df["matrix_name"] == sample].iloc[0]
        assert row["censored"] == S.Censoring.LEFT.value
        assert row["censoring_bound"] == M.KIM_ICP_OES_LIMIT_PPM


def test_censored_rows_are_surfaced_in_pooling_warnings():
    assert any("CENSORED" in w for w in S.pooling_warning(M.build()))


def test_validator_rejects_a_censored_row_with_no_bound():
    df = M.build()
    df.loc[df["censored"] == S.Censoring.LEFT.value, "censoring_bound"] = None
    rep = S.validate(df)
    assert "censored_without_bound" in set(rep["issue"])


# --------------------------------------------------------------------------
# Structure-only rows must be counted, not faulted — and loading is not a target
# --------------------------------------------------------------------------

def test_structure_only_rows_are_informational_not_errors():
    rep = S.validate(M.build())
    assert "missing_retention_value" not in set(rep["issue"])
    assert "structure_only_rows" in set(rep["issue"])


def test_validator_faults_a_declared_type_with_no_value():
    df = M.build()
    df.loc[0, "retention_value"] = None
    assert "missing_retention_value" in set(S.validate(df)["issue"])


def test_loading_is_a_control_variable_with_only_designed_levels():
    df = M.build()
    levels = sorted(df["loading_wt_pct"].dropna().unique())
    assert levels == [0.0, 1.0, 2.0, 3.0, 5.0], "loadings are set by the experimenter"


# --------------------------------------------------------------------------
# Adapter content, checked against the source
# --------------------------------------------------------------------------

def test_pool_shape():
    df = M.build()
    assert len(df) == 54
    assert set(df["source_label"]) == {"kim2026", "nevin2026", "kurumisawa2021", "jang2016", "stanojevic2025", "komljenovic2020", "arbelhaddad2022", "frederickx2025"}
    # 8 Kim/Nevin + 10 Kurumisawa + 14 Jang + 2 Stanojevic + 2 Komljenovic + 6 Arbel + 4 Frederickx = 46
    assert df["retention_value"].notna().sum() == 46


def test_nevin_cs_rows_are_present():
    """The master sheet dropped both Cs rows (F22); the adapter must not."""
    df = M.build()
    cs = df[(df["source_label"] == "nevin2026") & (df["retention_value"].notna())
            & (df["nuclide"] == "Cs")]
    assert len(cs) == 2
    assert sorted(cs["retention_value"]) == [13.2, 13.3]


def test_sr_is_retained_far_better_than_cs_in_the_same_matrix():
    """Nevin's headline: same K-A-S-H gel, ~6 orders of magnitude difference."""
    sr = M.NEVIN_TABLE2["Sr_3"][0]
    cs = M.NEVIN_TABLE2["Cs_3"][0]
    assert math.log10(cs / sr) > 5


def test_all_li_values_clear_the_regulatory_floor():
    df = M.build()
    li = df[df["retention_type"] == S.RetentionType.LEACHABILITY_INDEX.value]
    measured = li["retention_value"].dropna()  # censored rows have no value to compare
    assert len(measured) == 30  # 8 Kim/Nevin + 14 Jang + 2 Stanojevic + 2 Komljenovic + 4 Frederickx
    assert (measured >= S.ANS_16_1_MIN_LI).all()
    assert "li_below_ans_16_1" not in set(S.validate(df)["issue"])


def test_ari_matches_the_pool_a_definition():
    """Same descriptor definition in both pools, even though the pools never merge."""
    from geomind.data import nmr_ari

    q = (18.2, 44.3, 31.8, 5.7)  # Nevin Sr_1_Pre
    assert M._ari_from_q4(*q) == pytest.approx(
        (4 * q[0] + 3 * q[1] + 2 * q[2] + 1 * q[3]) / 100.0
    )
    assert nmr_ari.M_WEIGHT["Q4_4Al"] == 4  # the weights agree


def test_kim_exafs_coordination_numbers_are_kims_not_yildirims():
    """F21: 7.87 / 7.95 are Kim's NaSr3 pre/post values, credited to Geddes 2025."""
    assert M.KIM_CN_SR[("NaSr3", "pre")][0] == 7.87
    assert M.KIM_CN_SR[("NaSr3", "post")][0] == 7.95
    assert M.KIM_CN_SR[("KSr3", "pre")][0] == 7.55


def test_pools_a_and_b_share_no_columns_that_could_be_confused():
    """D13: the two pools must never be concatenated by accident."""
    from geomind.data import adsorption_schema

    assert "capacity_mg_g" not in S.COLUMNS
    assert "retention_value" not in adsorption_schema.COLUMNS


# --------------------------------------------------------------------------
# Kurumisawa — the recovered bridge source, and the diffusivity category error
# --------------------------------------------------------------------------

def test_ingress_and_effective_diffusivity_are_distinct_members():
    assert S.RetentionType.INGRESS_DIFFUSIVITY != S.RetentionType.EFFECTIVE_DIFFUSIVITY
    assert len(S.INCOMPATIBLE_DIFFUSIVITIES) == 2


def test_pooling_raises_a_category_error_when_both_diffusivities_appear():
    df = M.build()
    df.loc[0, "retention_type"] = S.RetentionType.EFFECTIVE_DIFFUSIVITY.value
    assert any("CATEGORY ERROR" in w for w in S.pooling_warning(df))


def test_kurumisawa_ingress_d_is_twelve_orders_above_nevin_leaching_de():
    """The exact trap: same name, opposite experiment, ~12 orders apart."""
    df = M.build()
    ingress = df[df["retention_type"] == S.RetentionType.INGRESS_DIFFUSIVITY.value]
    assert len(ingress) == 10
    fastest = ingress["retention_value"].max()          # cm2/s
    nevin_de = M.NEVIN_TABLE2["Sr_3"][0]                # cm2/s
    assert math.log10(fastest / nevin_de) > 10


def test_kurumisawa_m2_s_conversion_is_applied():
    df = M.build()
    k11 = df[df["sample_id"] == "kurumisawa2021_K11_4w"].iloc[0]
    # 40e-13 m2/s * 1e4 = 4e-8 cm2/s
    assert k11["retention_value"] == pytest.approx(4.0e-8, rel=1e-9)


def test_kurumisawa_rows_are_flagged_as_figure_derived():
    df = M.build()
    ku = df[df["source_label"] == "kurumisawa2021"]
    assert ku["from_figure"].all()


def test_kurumisawa_has_no_loading_because_cs_was_not_doped_in():
    df = M.build()
    ku = df[df["source_label"] == "kurumisawa2021"]
    assert ku["loading_wt_pct"].isna().all()


def test_kurumisawa_ingress_rows_present():
    df = M.build()
    assert len(df[df["source_label"] == "kurumisawa2021"]) == 10


# --------------------------------------------------------------------------
# Jang 2016 — recovered from disk via F25 (Q11)
# --------------------------------------------------------------------------

def test_jang_adds_fourteen_li_rows_both_nuclides():
    df = M.build()
    j = df[df["source_label"] == "jang2016"]
    assert len(j) == 14
    assert set(j["nuclide"]) == {"Cs", "Sr"}
    assert (j["retention_type"] == S.RetentionType.LEACHABILITY_INDEX.value).all()


def test_jang_li_is_the_ans_aggregate_not_log_of_mean_de():
    """Trap 4: LI = mean(-log10 De_n). F1 Cs interval De's must aggregate to 10.0."""
    cs_F1 = [9.4e-10, 1.1e-9, 4.8e-10, 3.9e-10, 1.9e-10,
             1.6e-10, 1.6e-10, 1.2e-11, 3.6e-12, 1.5e-12]
    aggregate = sum(S.li_from_de(x) for x in cs_F1) / len(cs_F1)
    assert aggregate == pytest.approx(10.0, abs=0.05)
    # the wrong route (-log10 of the arithmetic mean) must NOT match
    wrong = S.li_from_de(sum(cs_F1) / len(cs_F1))
    assert abs(wrong - 10.0) > 0.4
    assert M.JANG_LI["F1"][0] == 10.0


def test_jang_sr_is_retained_better_than_cs_in_every_specimen():
    """The universal Cs<Sr retention result, now across 7 more matrices."""
    for spec, (cs_li, sr_li) in M.JANG_LI.items():
        assert sr_li > cs_li, spec


def test_jang_stores_no_si_al_because_it_would_be_misleading():
    """Precursor-bulk Si/Al omits the activator silicate; storing it would lie."""
    df = M.build()
    j = df[df["source_label"] == "jang2016"]
    assert j["si_al"].isna().all()


def test_jang_pore_structure_is_captured():
    df = M.build()
    f1 = df[df["sample_id"] == "jang2016_F1_Cs"].iloc[0]
    assert f1["porosity_pct"] == 29.9
    assert f1["critical_pore_diameter_nm"] == 62


def test_jang_portland_cement_baseline_is_flagged_separable():
    df = M.build()
    pc = df[(df["source_label"] == "jang2016")
            & (df["matrix_class"] == S.MatrixClass.PORTLAND_CEMENT.value)]
    assert len(pc) == 2  # Cs + Sr, the paper's negative control


def test_pool_b_shape_after_jang():
    df = M.build()
    assert len(df) == 54
    assert set(df["source_label"]) == {"kim2026", "nevin2026", "kurumisawa2021", "jang2016", "stanojevic2025", "komljenovic2020", "arbelhaddad2022", "frederickx2025"}
