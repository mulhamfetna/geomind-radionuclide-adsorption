import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from notebook_lab import build_notebook as BN  # noqa: E402


def test_notebook_is_valid_and_self_contained(tmp_path):
    out = BN.build(out=tmp_path / "nb.ipynb")
    nb = json.loads(Path(out).read_text())
    assert nb["nbformat"] == 4
    cells = nb["cells"]
    assert len(cells) >= 6
    src = "\n".join("".join(c["source"]) if isinstance(c["source"], list)
                    else c["source"] for c in cells)
    assert "pip" in src and "install" in src and "gradio" in src
    assert "%%writefile engine_lite.py" in src
    assert "%%writefile ui_lite.py" in src
    assert "build_app().launch()" in src
    assert "share=True" not in src            # Colab-internal only
    assert "lab_bundle.json" in src
