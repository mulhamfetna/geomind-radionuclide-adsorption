import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from notebook_lab import bundle as B  # noqa: E402


def test_bundle_has_all_sections_with_expected_sizes():
    b = B.build_bundle()
    assert len(b["pool_a"]) == 141
    assert len(b["pool_b"]) == 73
    assert len(b["audit"]) == 91
    assert len(b["findings"]) == 42
    assert len(b["decisions"]) == 17
    assert len(b["forward"]["training"]) == 7
    assert {"fig1", "fig2", "fig4", "fig6"} <= set(b["figures"])
    for v in b["figures"].values():
        assert isinstance(v, str) and len(v) > 100   # base64 PNG
    assert len(b["cs_pool"]) >= 20
    assert b["struct"]["framework"] and b["struct"]["ca"]
