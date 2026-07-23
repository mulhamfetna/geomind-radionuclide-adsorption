"""Assemble the shareable, self-contained Colab notebook from the tested modules + bundle.

The notebook's code cells are the *verbatim* sources of engine_lite.py / ui_lite.py, and the
data is the base64 of lab_bundle.json — so the shipped notebook cannot drift from what the
mirror test verifies. Colab-internal launch only (no share=True).
"""
from __future__ import annotations

import base64
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_HERE = _ROOT / "notebook_lab"


def _code_cell(source: str) -> dict:
    return {"cell_type": "code", "metadata": {}, "execution_count": None,
            "outputs": [], "source": source.splitlines(keepends=True)}


def _md_cell(source: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


_INTRO = """\
# GEOMIND-R Virtual Chemistry Lab

**Confidential — pre-publication.** An interactive lab to explore geopolymer compositions and get
domain-flagged Sr K_D predictions, screening checks, and the paper's argument, live.

### How to run
1. **Runtime → Run all** (or run each cell top to bottom).
2. The last cell prints a link and shows the app **inside this notebook** — nothing is sent to any
   public server.
3. Pick an [Al^IV] value and click **Predict K_D**; explore the Teaching and Console tabs.

_It is a glass box, not an oracle: every prediction carries its confidence flag, its reason, and its
source. Predictions outside the validated envelope are shown for exploration but marked, never
dressed up._
"""


def build(out=None) -> str:
    out = Path(out) if out is not None else _ROOT / "notebooks" / "geomind_virtual_lab.ipynb"
    out.parent.mkdir(parents=True, exist_ok=True)

    bundle_b64 = base64.b64encode((_HERE / "lab_bundle.json").read_bytes()).decode("ascii")
    engine_src = (_HERE / "engine_lite.py").read_text()
    ui_src = (_HERE / "ui_lite.py").read_text()

    install_cell = "# One dependency; everything else ships in this notebook.\n!pip -q install gradio\n"

    bundle_cell = (
        "# Write the embedded data bundle (the project's compiled data) to disk.\n"
        "import base64, pathlib\n"
        f'_BUNDLE_B64 = "{bundle_b64}"\n'
        'pathlib.Path("lab_bundle.json").write_bytes(base64.b64decode(_BUNDLE_B64))\n'
        'print("bundle ready:", pathlib.Path("lab_bundle.json").stat().st_size, "bytes")\n'
    )

    engine_cell = "%%writefile engine_lite.py\n" + engine_src
    ui_cell = "%%writefile ui_lite.py\n" + ui_src

    launch_cell = (
        "# Launch the lab inside this notebook (Colab-internal; no public tunnel).\n"
        "from ui_lite import build_app\n"
        "build_app().launch()\n"
    )

    nb = {
        "cells": [
            _md_cell(_INTRO),
            _code_cell(install_cell),
            _code_cell(bundle_cell),
            _code_cell(engine_cell),
            _code_cell(ui_cell),
            _code_cell(launch_cell),
        ],
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
            "colab": {"provenance": []},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }
    out.write_text(json.dumps(nb, indent=1))
    return str(out)


if __name__ == "__main__":
    print("wrote", build())
