import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from geomind import manifest as M  # noqa: E402

_HAS_CORPUS = M.REFS.exists() and any(M.REFS.iterdir())


@pytest.mark.skipif(not _HAS_CORPUS, reason="reference corpus not present on this machine")
def test_manifest_has_one_row_per_catalogued_file():
    rows = M.build_rows()
    # saved publisher web pages are deliberately excluded (see manifest._build)
    on_disk = [f for f in M.REFS.iterdir()
               if f.is_file() and f.suffix.lower() not in {".html", ".htm"}]
    assert len(rows) == len(on_disk)
    assert not any(r["file"].lower().endswith((".html", ".htm")) for r in rows)
    for r in rows:
        assert len(r["sha16"]) == 16 and all(c in "0123456789abcdef" for c in r["sha16"])
        assert r["type"] in {"MAIN", "REF"}


@pytest.mark.skipif(not _HAS_CORPUS, reason="reference corpus not present on this machine")
def test_manifest_links_known_dois_to_registry_source_labels():
    rows = {r["file"]: r for r in M.build_rows()}
    # the 137Cs geopolymer-foams paper is xiang2021 in the registry, matched via its DOI
    foam = next((r for f, r in rows.items() if "foams" in f.lower() and "137" in f), None)
    assert foam is not None
    assert foam["doi"].startswith("10.")
    assert foam["source"] == "xiang2021"


def test_render_is_stable_markdown():
    sample = [{"type": "REF", "file": "x.pdf", "mb": 1.2, "sha16": "0123456789abcdef",
               "doi": "10.1/abc", "source": "src1"}]
    md = M.render(sample)
    assert "| 1 | REF | `x.pdf` | 1.2 | `0123456789abcdef` | 10.1/abc | src1 |" in md
    assert "1 documents on disk" in md
