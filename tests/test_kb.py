"""The knowledge registry must stay coherent, and the validator must actually work.

These tests exist because the project's recurring failure mode is *implicit*
knowledge drifting away from reality. A registry nobody validates is just a
second place for the truth to rot.
"""
from __future__ import annotations

import copy

import pytest

from src.geomind import kb


@pytest.fixture(scope="module")
def registry() -> dict:
    return kb.load()


def test_registry_is_valid(registry: dict) -> None:
    """The committed registry must have zero validation errors."""
    assert kb.validate(registry) == []


def test_every_asset_declares_status_and_usage(registry: dict) -> None:
    """`usage` is the field that stops data being misapplied — it is mandatory."""
    for a in registry["assets"]:
        assert a.get("status"), f"{a['id']} has no status"
        assert a.get("usage"), f"{a['id']} has no usage constraint"


def test_rejected_and_duplicate_assets_say_so_in_usage(registry: dict) -> None:
    """An asset we must not use has to make that explicit where a reader will look."""
    for a in registry["assets"]:
        if a["status"] in ("rejected", "duplicate", "suspect"):
            usage = a["usage"].lower()
            assert any(k in usage for k in ("not used", "never", "not be", "requires")), (
                f"{a['id']} is {a['status']} but its usage does not forbid use: {a['usage']!r}"
            )


def test_pool_row_count_matches_reality(registry: dict) -> None:
    """The registry's headline number must match the actual pooled file."""
    import pandas as pd
    from pathlib import Path

    p = Path("data/processed/adsorption_pooled.csv")
    if not p.exists():
        pytest.skip("pooled file not built")
    assert len(pd.read_csv(p)) == registry["meta"]["pool_rows"]


# --- the validator itself must catch drift -------------------------------

@pytest.mark.parametrize(
    "label,mutate",
    [
        ("bad status", lambda k: k["assets"][0].__setitem__("status", "probably_fine")),
        ("missing usage", lambda k: k["assets"][1].pop("usage")),
        ("dangling finding", lambda k: k["assets"][2].__setitem__("related_findings", ["F99"])),
        ("duplicate id", lambda k: k["assets"].append(dict(k["assets"][0]))),
        ("finding without action", lambda k: k["findings"][0].pop("action")),
        ("question blocks unknown", lambda k: k["open_questions"][0].__setitem__("blocks", ["nope"])),
    ],
)
def test_validator_catches(registry: dict, label: str, mutate) -> None:
    broken = copy.deepcopy(registry)
    mutate(broken)
    assert kb.validate(broken), f"validator missed: {label}"


def test_findings_reference_only_known_severities(registry: dict) -> None:
    for f in registry["findings"]:
        assert f["severity"] in kb.SEVERITY_ORDER
