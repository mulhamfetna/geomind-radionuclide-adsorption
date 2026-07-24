import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import engine as E  # noqa: E402


def test_classify_domain_in_range_same_class_is_validated():
    # forward domain is [3.45, 4.77] mmol/g; 4.0 is inside
    assert E.classify_domain(4.0, "metakaolin geopolymer", "Sr") is E.Confidence.VALIDATED


def test_classify_domain_out_of_range_same_class_is_exploratory():
    assert E.classify_domain(6.5, "metakaolin geopolymer", "Sr") is E.Confidence.EXPLORATORY


def test_classify_domain_wrong_class_is_unsupported():
    assert E.classify_domain(4.0, "zeolite", "Sr") is E.Confidence.UNSUPPORTED


def test_classify_domain_wrong_adsorbate_is_unsupported():
    assert E.classify_domain(4.0, "metakaolin geopolymer", "Cs") is E.Confidence.UNSUPPORTED


def test_predict_kd_in_domain_has_value_band_and_validated_flag():
    r = E.predict_kd(4.0)
    assert r.flag is E.Confidence.VALIDATED
    assert r.value > 0
    assert r.uncertainty is not None and r.uncertainty > 0
    assert r.unit == "mL/g"


def test_predict_kd_wrong_class_is_unsupported_and_bandless():
    r = E.predict_kd(4.0, structural_class="zeolite")
    assert r.flag is E.Confidence.UNSUPPORTED
    assert r.uncertainty is None          # never imply precision off-domain
    assert "not" in r.why.lower()         # states it is not validated here


def test_predict_kd_never_labels_out_of_domain_as_validated():
    for r in (E.predict_kd(9.0), E.predict_kd(4.0, adsorbate="Cs"),
              E.predict_kd(4.0, structural_class="zeolite")):
        assert r.flag is not E.Confidence.VALIDATED


def test_describe_formulation_matches_chemistry_layer():
    from geomind.chemistry import molar_ratios, PRECURSORS
    name = next(n for n, p in PRECURSORS.items() if p.kind == "metakaolin")
    sil = next(n for n, p in PRECURSORS.items() if p.kind == "silicate")
    mix = {name: 0.7, sil: 0.3}
    d = E.describe_formulation(mix)
    exp_si_al, exp_si_m, exp_sl = molar_ratios(mix)
    assert d["si_al"] == exp_si_al


def test_ari_from_q4_weights_by_aluminium_count():
    # ARI weights each site by its Al count. The deconvolution schema merges Q3/Q4
    # for the 2Al and 1Al sites, so the labels are Q3Q4_2Al / Q3Q4_1Al (see nmr_ari.M_WEIGHT).
    q4 = {"Q4_4Al": 40, "Q4_3Al": 30, "Q3Q4_2Al": 20, "Q3Q4_1Al": 10, "Q4_0Al": 0}
    assert E.ari_from_q4(q4) == (4*40 + 3*30 + 2*20 + 1*10) / 100  # = 3.0


def test_ari_from_q4_rejects_unknown_site_labels():
    with pytest.raises(KeyError):
        E.ari_from_q4({"Q4_9Al": 100})


def test_screen_saturation_high_theta_is_sound():
    r = E.screen_saturation(0.05, 1000.0)   # theta = 0.05*1000/(1+50) ~ 0.98
    assert r.value > 0.8
    assert r.extra["verdict"] == "sound"


def test_screen_saturation_low_theta_is_artefact():
    r = E.screen_saturation(7.94e-5, 2658.0)  # the chabazite case, theta ~ 0.17
    assert r.value < 0.5
    assert r.extra["verdict"] == "artefact"


def test_compare_classes_mixed_warns():
    msg = E.compare_classes(["metakaolin geopolymer", "zeolite"])
    assert msg is not None
    assert "class" in msg.lower()


def test_compare_classes_same_class_is_clean():
    assert E.compare_classes(["metakaolin geopolymer", "metakaolin geopolymer"]) is None


def test_sweep_kd_flags_each_point_by_domain():
    cards = E.sweep_kd([3.5, 4.0, 9.0])
    assert len(cards) == 3
    assert cards[0].flag is E.Confidence.VALIDATED
    assert cards[2].flag is E.Confidence.EXPLORATORY


def test_export_candidate_writes_json_locally(tmp_path):
    card = E.predict_kd(4.0)
    bundle = {"inputs": {"al_iv_mmol_g": 4.0},
              "prediction": {"value": card.value, "flag": card.flag.value,
                             "unit": card.unit}}
    out = tmp_path / "candidate.json"
    written = E.export_candidate(bundle, out)
    import json
    data = json.loads(Path(written).read_text())
    assert data["prediction"]["flag"] == "validated"
    assert data["prediction"]["unit"] == "mL/g"


def test_pooling_sources_lists_the_cs_langmuir_labs():
    srcs = E.pooling_sources()
    assert len(srcs) >= 3
    assert all(isinstance(s, str) for s in srcs)


def test_pooled_loo_r2_all_sources_is_worse_than_mean():
    r = E.pooled_loo_r2(E.pooling_sources())
    assert r.value < 0                       # the F36 result: pooled R^2 < 0
    assert r.extra["verdict"] == "worse-than-mean"
    assert r.flag is E.Confidence.UNSUPPORTED


def test_pooled_loo_r2_too_few_points_is_undefined():
    r = E.pooled_loo_r2([])
    assert r.value is None
    assert r.extra["verdict"] == "undefined"


def test_structural_precondition_framework_only_is_strong():
    r = E.structural_precondition(include_ca=False)
    assert r.value > 0.85                     # framework (Ca-free) gels: r ~ +0.93


def test_structural_precondition_pooling_ca_degrades_it():
    fw = E.structural_precondition(include_ca=False).value
    mixed = E.structural_precondition(include_ca=True).value
    assert mixed < fw                         # adding real Ca-bearing gels weakens r


def test_load_pool_a_and_b_row_counts():
    assert len(E.load_pool("A")) == 141
    assert len(E.load_pool("B")) == 73


def test_load_findings_and_decisions_counts():
    f = E.load_findings()
    d = E.load_decisions()
    assert len(f) == 43 and all("id" in x and "title" in x for x in f)
    assert len(d) == 17


def test_load_audit_summary_has_veracity_labels():
    df = E.load_audit_summary()
    assert {"veracity", "reason", "n_rows"} <= set(df.columns)
    assert len(df) >= 1
    assert "VERIFIED_TRUE" in set(df["veracity"])


def test_load_audit_summary_missing_db_is_empty_not_error(tmp_path):
    df = E.load_audit_summary(db_path=tmp_path / "nope.db")
    assert len(df) == 0
    assert {"veracity", "reason", "n_rows"} <= set(df.columns)


def test_rerun_headline_numbers_match_the_paper():
    h = E.rerun_headline_numbers()
    assert h["forward_r2_loo"] > 0.7          # within-class LOO-CV ~ 0.81
    assert h["pooled_r2"] < 0                  # pooled across labs ~ -0.09
    assert h["framework_r"] > 0.85             # framework ARI r ~ +0.93
    assert h["pooled_struct_r"] < h["framework_r"]


def test_load_audit_summary_falls_back_to_committed_csv(tmp_path, monkeypatch):
    """A fresh clone has no 31 MB warehouse DB — the committed summary CSV must carry it."""
    import shutil
    fake_root = tmp_path / "root"
    (fake_root / "data" / "warehouse").mkdir(parents=True)
    shutil.copy(E._ROOT / "data" / "warehouse" / "audit_summary.csv",
                fake_root / "data" / "warehouse" / "audit_summary.csv")
    monkeypatch.setattr(E, "_ROOT", fake_root)          # no geomind.db under this root
    df = E.load_audit_summary()
    assert len(df) == 91
    assert "VERIFIED_TRUE" in set(df["veracity"])
