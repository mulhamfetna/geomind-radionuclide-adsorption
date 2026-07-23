import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from notebook_lab import ui_lite as U  # noqa: E402


def test_app_builds():
    demo = U.build_app()
    assert demo is not None and hasattr(demo, "launch")


def test_predict_handler_flag_and_unit():
    label, detail = U._predict_handler(4.0, "metakaolin geopolymer", "Sr")
    assert "validated" in label.lower() and "mL/g" in detail
