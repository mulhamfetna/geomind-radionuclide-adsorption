import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import lab as L  # noqa: E402


def test_app_builds():
    demo = L.build_app()
    # gradio Blocks expose a .blocks registry once assembled
    assert demo is not None
    assert hasattr(demo, "launch")


def test_predict_handler_validated_carries_flag_and_unit():
    label, detail = L._predict_handler(4.0, "metakaolin geopolymer", "Sr")
    assert "validated" in label.lower()
    assert "mL/g" in detail


def test_predict_handler_unsupported_never_says_validated():
    label, detail = L._predict_handler(4.0, "zeolite", "Sr")
    assert "validated" not in label.lower()
    assert "unsupported" in label.lower()


def test_pooling_handler_reports_collapse_for_all_sources():
    md = L._pooling_handler(L.E.pooling_sources())
    assert "worse-than-mean" in md
    assert "R^2" in md or "R²" in md


def test_structural_handler_reports_both_groups():
    md_fw = L._structural_handler(False)
    md_mix = L._structural_handler(True)
    assert "framework" in md_fw.lower()
    assert "r =" in md_mix.lower() or "r=" in md_mix.lower()


def test_concept_cards_cover_the_core_ideas():
    md = L._concept_cards()
    for token in ("Al", "ARI", "θ", "pool"):
        assert token in md


def test_pool_handler_returns_the_full_pool():
    assert len(L._pool_handler("A")) == 141


def test_findings_table_filters_by_query():
    all_rows = L._findings_table("")
    f36 = L._findings_table("F36")
    assert len(all_rows) == 44
    assert 1 <= len(f36) < len(all_rows)


def test_rerun_handler_reports_the_headline_numbers():
    md = L._rerun_handler()
    assert "0.81" in md            # forward R^2_LOO
    assert "F36" in md or "pool" in md.lower()


def test_audit_summary_md_mentions_verified():
    md = L._audit_summary_md()
    assert "VERIFIED_TRUE" in md or "verified" in md.lower()
