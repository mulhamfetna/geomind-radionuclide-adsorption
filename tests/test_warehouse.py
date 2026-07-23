"""The warehouse must mine everything and label everything — provably.

These tests encode the two promises the warehouse makes:
  1. Nothing is left unmined or untriaged.
  2. A naive query cannot pull unusable data into a model.
"""
from __future__ import annotations

import sqlite3

import pytest

from src.geomind.warehouse import DB, Granularity, Utility, Veracity, modellable


@pytest.fixture(scope="module")
def con():
    if not DB.exists():
        pytest.skip("warehouse not built - run python -m src.geomind.warehouse")
    c = sqlite3.connect(DB)
    yield c
    c.close()


def test_every_table_has_an_explicit_verdict(con) -> None:
    """The promise: no file is left unmined. A default-rule row is a hole."""
    n = con.execute(
        "SELECT COUNT(*) FROM tables_seen WHERE reason LIKE 'Ingested by sweep%'"
    ).fetchone()[0]
    assert n == 0, f"{n} table(s) still on the default rule"


def test_all_labels_are_in_the_closed_vocabulary(con) -> None:
    ver = {r[0] for r in con.execute("SELECT DISTINCT veracity FROM records")}
    uti = {r[0] for r in con.execute("SELECT DISTINCT utility FROM records")}
    gra = {r[0] for r in con.execute("SELECT DISTINCT granularity FROM records")}
    assert ver <= {v.value for v in Veracity}
    assert uti <= {u.value for u in Utility}
    assert gra <= {g.value for g in Granularity}


def test_every_record_carries_a_reason(con) -> None:
    n = con.execute(
        "SELECT COUNT(*) FROM records WHERE label_reason IS NULL OR TRIM(label_reason)=''"
    ).fetchone()[0]
    assert n == 0


def test_raw_signal_is_never_modellable(con) -> None:
    """A spectrum point is not a training row.

    Without this, `SELECT ... WHERE modellable=1` would sweep ~18k XRD/FTIR
    intensity points into a training set — which is exactly what the first
    build of this warehouse did.
    """
    n = con.execute(
        "SELECT COUNT(*) FROM records WHERE granularity='RAW_SIGNAL' AND modellable=1"
    ).fetchone()[0]
    assert n == 0


def test_false_and_redundant_are_never_modellable(con) -> None:
    n = con.execute(
        "SELECT COUNT(*) FROM records "
        "WHERE veracity IN ('FALSE','REDUNDANT') AND modellable=1"
    ).fetchone()[0]
    assert n == 0


def test_discard_is_never_modellable(con) -> None:
    n = con.execute(
        "SELECT COUNT(*) FROM records WHERE utility='DISCARD' AND modellable=1"
    ).fetchone()[0]
    assert n == 0


def test_known_bad_sources_are_labelled_false_or_redundant(con) -> None:
    """The audited failures must stay labelled — a regression guard on F6/F8."""
    for table, expect in [("Feasibility_Ranges", "FALSE"),
                          ("Adsorption_Isotherms", "REDUNDANT"),
                          ("Cs_Isotherms", "REDUNDANT")]:
        row = con.execute(
            "SELECT veracity FROM tables_seen WHERE source_table=?", (table,)
        ).fetchone()
        assert row and row[0] == expect, f"{table} should be {expect}, got {row}"


@pytest.mark.parametrize(
    "v,u,g,expected",
    [
        (Veracity.VERIFIED_TRUE, Utility.CORE, Granularity.OBSERVATION, True),
        (Veracity.VERIFIED_TRUE, Utility.CORE, Granularity.RAW_SIGNAL, False),
        (Veracity.FALSE, Utility.CORE, Granularity.OBSERVATION, False),
        (Veracity.VERIFIED_TRUE, Utility.DISCARD, Granularity.OBSERVATION, False),
        (Veracity.REDUNDANT, Utility.SUPPORTING, Granularity.OBSERVATION, False),
        (Veracity.PROBABLE, Utility.SUPPORTING, Granularity.OBSERVATION, True),
    ],
)
def test_modellable_logic(v, u, g, expected) -> None:
    assert modellable(v, u, g) is expected


def test_non_tabular_assets_are_catalogued(con) -> None:
    """Binaries we cannot table must still be recorded, not silently skipped."""
    n = con.execute("SELECT COUNT(*) FROM assets_non_tabular").fetchone()[0]
    assert n > 0
