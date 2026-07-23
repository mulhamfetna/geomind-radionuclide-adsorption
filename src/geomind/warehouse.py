"""Unified warehouse — every record from every source, mined and labelled.

Principle: **after this runs, no analysis touches an original file again.**
Everything lives in one queryable SQLite database with a per-record verdict.

Nothing is left unmined. A sheet that turns out to be worthless is still
ingested and labelled `FALSE` or `IRRELEVANT` — because "we looked and it was
worthless" is knowledge, while "we never looked" is a hole.

Usage:
    python -m src.geomind.warehouse          # build
    python -m src.geomind.warehouse --report # coverage + label summary
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import warnings
from enum import Enum
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

DB = Path("data/warehouse/geomind.db")
RAW = Path("data/raw")
EXTERNAL = Path("data/external/aam-oulu-2026")


# =====================================================================
# STRICT LABEL VOCABULARY
# =====================================================================
class Veracity(str, Enum):
    """Is the record TRUE? Independent of whether it is useful."""

    VERIFIED_TRUE = "VERIFIED_TRUE"    # checked in context against the primary source
    PROBABLE = "PROBABLE"              # source-consistent, not individually re-checked
    UNVERIFIED = "UNVERIFIED"          # ingested, never checked against a source
    REDUNDANT = "REDUNDANT"            # true but a duplicate of another record
    FALSE = "FALSE"                    # proven wrong: transplanted, misattributed, fabricated


class Utility(str, Enum):
    """Is the record USEFUL for our question? Independent of whether it is true."""

    CORE = "CORE"              # directly trains/validates the target model
    SUPPORTING = "SUPPORTING"  # features, structure, conditions attached to CORE records
    CONTEXT = "CONTEXT"        # real and relevant but not modellable (mechanisms, leaching)
    DISCARD = "DISCARD"        # no value: duplicate, wrong, or outside the question


class Granularity(str, Enum):
    """WHAT KIND of thing the record is - orthogonal to true/useful.

    Without this, a raw XRD intensity point and a fitted Langmuir capacity look
    identical to a query, and a naive `SELECT ... WHERE modellable=1` would sweep
    ~18k spectrum points into a training set.
    """

    OBSERVATION = "OBSERVATION"  # one sample x one measurement -> can be a training row
    RAW_SIGNAL = "RAW_SIGNAL"    # spectrum/isotherm point; must be REDUCED to a feature first
    REFERENCE = "REFERENCE"      # dictionary, parameter list, metadata


#: A record may enter a model only if it is true, useful AND an observation.
def modellable(v: Veracity, u: Utility, g: Granularity = Granularity.OBSERVATION) -> bool:
    return (v in (Veracity.VERIFIED_TRUE, Veracity.PROBABLE)
            and u in (Utility.CORE, Utility.SUPPORTING)
            and g is Granularity.OBSERVATION)


#: tables whose rows are spectral/instrument traces, not observations
RAW_SIGNAL_HINTS = ("xrd", "ftir", "si nmr", "psd", "bet", "all data", "zeta")


SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    record_id      TEXT PRIMARY KEY,
    source_file    TEXT NOT NULL,
    source_table   TEXT NOT NULL,
    row_index      INTEGER NOT NULL,
    domain         TEXT NOT NULL,
    veracity       TEXT NOT NULL,
    utility        TEXT NOT NULL,
    label_reason   TEXT NOT NULL,
    modellable     INTEGER NOT NULL,
    granularity    TEXT NOT NULL,
    payload        TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS tables_seen (
    source_file  TEXT NOT NULL,
    source_table TEXT NOT NULL,
    n_rows       INTEGER,
    n_cols       INTEGER,
    domain       TEXT,
    granularity  TEXT,
    veracity     TEXT,
    utility      TEXT,
    reason       TEXT,
    PRIMARY KEY (source_file, source_table)
);
CREATE TABLE IF NOT EXISTS assets_non_tabular (
    path TEXT PRIMARY KEY, kind TEXT, bytes INTEGER, note TEXT
);
CREATE INDEX IF NOT EXISTS idx_dom ON records(domain);
CREATE INDEX IF NOT EXISTS idx_lab ON records(veracity, utility);
"""


# =====================================================================
# LABEL RULES — every table gets an explicit verdict, with a reason.
# Keyed by (file stem, table name). Findings referenced are in the registry.
# =====================================================================
V, U = Veracity, Utility
RULES: dict[tuple[str, str], tuple[str, V, U, str]] = {
    # ---- master workbook, sheet by sheet ----
    ("GEOMIND_RADIOACTIVE_MASTER", "GEOMIND_Samples"):
        ("physical", V.VERIFIED_TRUE, U.CORE, "Paper's 10 published samples; schema matches authors' CSV"),
    ("GEOMIND_RADIOACTIVE_MASTER", "Validation_Samples"):
        ("physical", V.VERIFIED_TRUE, U.CORE, "Paper Table S5, 15 samples x 3 property types"),
    ("GEOMIND_RADIOACTIVE_MASTER", "GEOMIND_Parameters"):
        ("metadata", V.PROBABLE, U.SUPPORTING, "Model/GEOMIND parameter list; descriptive"),
    ("GEOMIND_RADIOACTIVE_MASTER", "Feasibility_Ranges"):
        ("structural", V.FALSE, U.DISCARD,
         "F6: constants verbatim from retired tool v1.0.0; rejects 7/9 feasible samples"),
    ("GEOMIND_RADIOACTIVE_MASTER", "Adsorption_Isotherms"):
        ("adsorption", V.REDUNDANT, U.DISCARD,
         "F8: duplicates Functional_Data incl. fabricated Na-MK/K-MK; 3 extra values are Co-60"),
    ("GEOMIND_RADIOACTIVE_MASTER", "Cs_Isotherms"):
        ("adsorption", V.REDUNDANT, U.DISCARD, "F8: strict subset of Adsorption_Isotherms"),
    ("GEOMIND_RADIOACTIVE_MASTER", "NMR_Sr_Cs_Data"):
        ("structural", V.VERIFIED_TRUE, U.SUPPORTING,
         "Q4(mAl) for Nevin 2026; NOT transplanted (0 matches to Varon); single formulation Si/Al=3"),
    ("GEOMIND_RADIOACTIVE_MASTER", "Surface_Complexation"):
        ("mechanistic", V.UNVERIFIED, U.CONTEXT,
         "AUDIT: Source column cites 'Eq. (10)-(12)' - EQUATION references, not data sources. "
         "These are model outputs, not measurements. Cannot be source-verified."),
    ("GEOMIND_RADIOACTIVE_MASTER", "Surface_Complexation_Sr"):
        ("mechanistic", V.UNVERIFIED, U.CONTEXT, "AUDIT: cites Yildirim_2024, a paper we do NOT hold. Unverifiable until acquired."),
    ("GEOMIND_RADIOACTIVE_MASTER", "Thermodynamics"):
        ("thermodynamic", V.UNVERIFIED, U.CONTEXT, "dG/dH/dS; explains temperature trends, not capacity"),
    ("GEOMIND_RADIOACTIVE_MASTER", "Thermodynamics_Expanded"):
        ("thermodynamic", V.REDUNDANT, U.DISCARD, "Same shape/columns as Thermodynamics"),
    ("GEOMIND_RADIOACTIVE_MASTER", "Magnetic_Properties"):
        ("structural", V.UNVERIFIED, U.CONTEXT, "Magnetisation of magnetic composites; niche"),
    ("GEOMIND_RADIOACTIVE_MASTER", "Sr_Leaching_Data"):
        ("leaching", V.UNVERIFIED, U.CONTEXT, "AUDIT: cites Kim_2026/Nevin_2026/Yildirim_2024; only Nevin held. 54.8% duplication."),
    ("GEOMIND_RADIOACTIVE_MASTER", "MD_Simulation_Sr_Cs"):
        ("simulation", V.UNVERIFIED, U.CONTEXT, "AUDIT: cites Duque_Redondo_2023 (not held). Simulation output, not measurement."),
    ("GEOMIND_RADIOACTIVE_MASTER", "Sr_Immobilization_Mechanisms"):
        ("mechanistic", V.FALSE, U.DISCARD,
         "AUDIT F11: NO source column at all + 66.7% internal duplication. Same signature as the "
         "fabricated Na-MK/K-MK rows (F7). Untraceable and largely repeated - do not use."),
    ("GEOMIND_RADIOACTIVE_MASTER", "Zeolite_Comparison_Sr_Cs"):
        ("adsorption", V.UNVERIFIED, U.CONTEXT, "AUDIT: cites Duque_Redondo_2023 (not held). 21.9% duplication."),
    ("GEOMIND_RADIOACTIVE_MASTER", "Leaching_Model_Comparison"):
        ("leaching", V.UNVERIFIED, U.CONTEXT, "Leaching model fits"),
    ("GEOMIND_RADIOACTIVE_MASTER", "EXAFS_Sr_Structural_Parameters"):
        ("structural", V.UNVERIFIED, U.SUPPORTING, "AUDIT: 31.2% duplication; cites Kim_2026 (not held). Verify before feature use."),
    ("GEOMIND_RADIOACTIVE_MASTER", "FTIR_Sr_Characterization"):
        ("structural", V.UNVERIFIED, U.SUPPORTING, "AUDIT: 88.9% internal duplication - near-zero information content."),
    ("GEOMIND_RADIOACTIVE_MASTER", "XRD_Sr_Phases"):
        ("structural", V.UNVERIFIED, U.SUPPORTING, "AUDIT: 72.7% internal duplication. Cites Kim_2026 (not held)."),
    ("GEOMIND_RADIOACTIVE_MASTER", "Mass_Transport_Models_Sr"):
        ("leaching", V.UNVERIFIED, U.CONTEXT, "Diffusivity/transport models"),
    ("GEOMIND_RADIOACTIVE_MASTER", "Summary_Statistics_GEOMIND_R"):
        ("metadata", V.REDUNDANT, U.DISCARD, "Derived summary of other sheets"),

    # ---- standalone provided files ----
    ("Functional_Data", "_"):
        ("adsorption", V.PROBABLE, U.CORE, "Hand-compiled Cs/Sr capacities; 10/31 expanded rows failed audit (F7)"),
    ("Physical_Data", "_"):
        ("physical", V.PROBABLE, U.SUPPORTING, "Concrete strength; Si_Al/Density/Metakaolin dropped (F1,F2)"),
    ("Data", "_"):
        ("physical", V.VERIFIED_TRUE, U.SUPPORTING, "Upstream source of Physical_Data strengths"),
    ("N data", "_"):
        ("physical", V.VERIFIED_TRUE, U.SUPPORTING, "Second upstream strength source"),
    ("GEOMIND_R_MASTER_DATABASE_v2", "_"):
        ("physical", V.UNVERIFIED, U.DISCARD, "F4: disagrees with Physical_Data in 22 cells, no changelog"),
    ("Metadata", "_"):
        ("metadata", V.VERIFIED_TRUE, U.SUPPORTING, "Column dictionary; cp1256 encoded"),
    ("baek2018_zeolites", "_"):
        ("adsorption", V.VERIFIED_TRUE, U.CORE,
         "Baek 2018 Cs Langmuir + CEC + Si/Al; chabazite Qmax flagged (F14)"),
    ("oulu2026_adsorption", "_"):
        ("adsorption", V.VERIFIED_TRUE, U.CORE, "Oulu tidy extract; NH4+/dyes with BET"),
}

DEFAULT_RULE = ("unclassified", V.UNVERIFIED, U.CONTEXT, "Ingested by sweep; not yet triaged")

#: Pattern rules, matched against the full path (lowercased) when no exact rule
#: exists. Order matters - first match wins. These cover the Oulu instrument
#: dumps, which are raw spectra rather than curated tables.
PATTERN_RULES: list[tuple[str, tuple[str, V, U, str]]] = [
    ("si nmr", ("structural", V.VERIFIED_TRUE, U.SUPPORTING,
                "Raw 29Si MAS-NMR spectra; needs deconvolution to yield Q4(mAl) (see NMR plan)")),
    ("xrd", ("structural", V.VERIFIED_TRUE, U.SUPPORTING,
             "Raw XRD diffractograms; phase ID - supports crystallinity descriptors")),
    ("ftir", ("structural", V.VERIFIED_TRUE, U.SUPPORTING,
              "Raw FTIR spectra; Si-O-T band positions track network polymerisation")),
    ("psd", ("structural", V.VERIFIED_TRUE, U.SUPPORTING,
             "Particle size distributions")),
    ("xrf", ("composition", V.VERIFIED_TRUE, U.CORE,
             "XRF elemental composition - the measured basis for Si/Al")),
    ("zeta", ("structural", V.VERIFIED_TRUE, U.SUPPORTING,
              "Zeta potential; surface charge, mechanistically relevant to cation uptake")),
    ("bet", ("structural", V.VERIFIED_TRUE, U.SUPPORTING,
             "BET/BJH isotherms; surface area and porosity")),
    ("synthesis data", ("composition", V.VERIFIED_TRUE, U.CORE,
                        "Designed Si:Al:Na:Ca ratios and reagent masses - the composition axis")),
    ("adsorption data", ("adsorption", V.VERIFIED_TRUE, U.CORE,
                         "Oulu batch adsorption workbooks (NH4+, MB, R6G)")),
]


def resolve_rule(path: Path, stem: str, table: str) -> tuple[str, V, U, str]:
    """Exact rule -> file-level rule -> path pattern -> default."""
    if (stem, table) in RULES:
        return RULES[(stem, table)]
    if (stem, "_") in RULES:
        return RULES[(stem, "_")]
    hay = str(path).lower()
    for needle, rule in PATTERN_RULES:
        if needle in hay:
            return rule
    return DEFAULT_RULE


def _read_any(path: Path) -> dict[str, pd.DataFrame]:
    """Read any tabular file into {table_name: df}. Never raises."""
    out: dict[str, pd.DataFrame] = {}
    try:
        if path.suffix.lower() == ".csv":
            for enc in ("utf-8", "cp1256", "latin-1"):
                try:
                    out["_"] = pd.read_csv(path, encoding=enc)
                    break
                except UnicodeDecodeError:
                    continue
        elif path.suffix.lower() in (".xlsx", ".xls"):
            xl = pd.ExcelFile(path)
            for s in xl.sheet_names:
                out[s.strip()] = xl.parse(s)
    except Exception as e:  # noqa: BLE001 - a broken file is a fact to record, not a crash
        out["_ERROR_"] = pd.DataFrame([{"read_error": str(e)[:200]}])
    return out


def build() -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)

    # ---- 1. every tabular file we hold ----
    files = sorted(RAW.rglob("*.csv")) + sorted(RAW.rglob("*.xlsx")) + sorted(RAW.rglob("*.xls"))
    if EXTERNAL.exists():
        files += sorted(EXTERNAL.rglob("*.xlsx")) + sorted(EXTERNAL.rglob("*.xls"))

    n_rec = 0
    for path in files:
        stem = path.stem
        for table, df in _read_any(path).items():
            domain, ver, util, reason = resolve_rule(path, stem, table)
            hay = f"{path} {table}".lower()
            if any(h in hay for h in RAW_SIGNAL_HINTS) and len(df) > 100:
                gran = Granularity.RAW_SIGNAL
            elif domain == "metadata":
                gran = Granularity.REFERENCE
            else:
                gran = Granularity.OBSERVATION
            con.execute(
                "INSERT OR REPLACE INTO tables_seen VALUES (?,?,?,?,?,?,?,?,?)",
                (str(path), table, len(df), df.shape[1], domain, gran.value, ver.value, util.value, reason),
            )
            can_model = int(modellable(ver, util, gran))
            for i, row in df.iterrows():
                payload = json.dumps(
                    {str(k): (None if pd.isna(v) else str(v)) for k, v in row.items()},
                    ensure_ascii=False,
                )
                rid = hashlib.sha256(f"{path}|{table}|{i}".encode()).hexdigest()[:20]
                con.execute(
                    "INSERT OR REPLACE INTO records VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (rid, str(path), table, int(i), domain, ver.value, util.value,
                     reason, can_model, gran.value, payload),
                )
                n_rec += 1

    # ---- 2. non-tabular assets catalogued, never silently ignored ----
    n_bin = 0
    for base, kind in [(EXTERNAL, "instrument/binary"), (Path("papers"), "publication")]:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.suffix.lower() not in (".csv", ".xlsx", ".xls"):
                con.execute(
                    "INSERT OR REPLACE INTO assets_non_tabular VALUES (?,?,?,?)",
                    (str(p), kind, p.stat().st_size,
                     "catalogued; not tabular - mined via targeted extraction where relevant"),
                )
                n_bin += 1

    con.commit()
    print(f"warehouse built: {DB}")
    print(f"  tabular records : {n_rec}")
    print(f"  tables          : {con.execute('SELECT COUNT(*) FROM tables_seen').fetchone()[0]}")
    print(f"  non-tabular     : {n_bin}")
    con.close()


def report() -> None:
    con = sqlite3.connect(DB)
    q = lambda s: con.execute(s).fetchall()  # noqa: E731

    print("=== LABEL MATRIX (records) ===")
    print(f"{'veracity':16s} {'utility':12s} {'n':>7s}  modellable")
    for v, u, n, m in q("SELECT veracity, utility, COUNT(*), MAX(modellable) "
                        "FROM records GROUP BY veracity, utility ORDER BY 1,2"):
        print(f"  {v:14s} {u:12s} {n:>7d}  {'YES' if m else 'no'}")

    print("\n=== BY DOMAIN ===")
    for d, n in q("SELECT domain, COUNT(*) FROM records GROUP BY domain ORDER BY 2 DESC"):
        print(f"  {d:16s} {n:>7d}")

    print("\n=== COVERAGE: any table left untriaged? ===")
    un = q("SELECT source_file, source_table, n_rows FROM tables_seen "
           "WHERE reason LIKE 'Ingested by sweep%' ORDER BY n_rows DESC")
    if not un:
        print("  none - every table has an explicit verdict ✓")
    else:
        print(f"  {len(un)} table(s) still on the default rule:")
        for f, t, n in un[:15]:
            print(f"    {Path(f).name:42s} :: {t:28s} {n:>6} rows")

    print("\n=== GRANULARITY (what kind of thing each record is) ===")
    for g, n, m in q("SELECT granularity, COUNT(*), SUM(modellable) FROM records "
                     "GROUP BY granularity ORDER BY 2 DESC"):
        print(f"  {g:14s} {n:>7d}  modellable: {m}")

    print("\n=== MODELLABLE POOL ===")
    n = q("SELECT COUNT(*) FROM records WHERE modellable=1")[0][0]
    print(f"  {n} records cleared for modelling "
          f"({q('SELECT COUNT(*) FROM records')[0][0]} total)")
    con.close()


if __name__ == "__main__":
    if "--report" in sys.argv:
        report()
    else:
        build()
        print()
        report()
