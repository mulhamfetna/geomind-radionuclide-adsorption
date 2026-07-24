import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import engine as REAL          # noqa: E402
from notebook_lab import engine_lite as LITE  # noqa: E402

APPROX = dict(rel=1e-6, abs=1e-6)


def test_predict_matches():
    for x in (4.0, 3.6, 9.0):
        r, l = REAL.predict_kd(x), LITE.predict_kd(x)
        assert l.flag.value == r.flag.value
        assert l.value == pytest.approx(r.value, **APPROX)
    assert LITE.predict_kd(4.0, structural_class="zeolite").flag.value == "unsupported"


def test_screen_matches():
    for b, c0 in ((0.05, 1000.0), (7.94e-5, 2658.0)):
        r, l = REAL.screen_saturation(b, c0), LITE.screen_saturation(b, c0)
        assert l.value == pytest.approx(r.value, **APPROX)
        assert l.extra["verdict"] == r.extra["verdict"]


def test_pooling_and_structural_match():
    assert sorted(LITE.pooling_sources()) == sorted(REAL.pooling_sources())
    r = REAL.pooled_loo_r2(REAL.pooling_sources()).value
    l = LITE.pooled_loo_r2(LITE.pooling_sources()).value
    assert l == pytest.approx(r, rel=1e-6, abs=1e-6)
    for inc in (False, True):
        assert LITE.structural_precondition(inc).value == pytest.approx(
            REAL.structural_precondition(inc).value, rel=1e-6, abs=1e-6)


def test_headline_and_counts_match():
    hr, hl = REAL.rerun_headline_numbers(), LITE.rerun_headline_numbers()
    assert set(hl) == set(hr)
    for k in hr:
        assert hl[k] == pytest.approx(hr[k], rel=1e-6, abs=1e-6)
    assert len(LITE.load_pool("A")) == 141 and len(LITE.load_pool("B")) == 73
    assert len(LITE.load_findings()) == 44 and len(LITE.load_decisions()) == 17
    assert len(LITE.load_audit_summary()) == 91
