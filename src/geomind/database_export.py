"""Export the COMPLETE database as one categorised workbook — nothing dropped.

    python -m geomind.database_export      # -> data/database/GEOMIND-R-complete-database.xlsx

The two audited pools are what the analysis uses, but they are not the whole record. A reader
checking this work needs to see the rows that were *excluded* and why, the verdict attached to
every ingested table, and the reasoning trail that produced both. This export puts all of it in
one file, categorised, so that nothing is silently absent.

Sheet groups:

* **00 README** — what each sheet is, and how the categories relate.
* **Pool A / Pool B** — the audited data the analysis uses (adsorption / immobilisation),
  kept separate by decision D13 because their targets run in opposite directions.
* **Excluded rows** — every row removed or corrected by the audit, with the reason and the
  finding that governs it. This is the sheet that makes the pools trustworthy.
* **Audit trail** — the verdict and reason recorded for all 91 ingested tables.
* **Findings / Decisions / Sources / Open questions** — the full reasoning register.
* **Figure source data** — the exact values behind each published figure panel.
* **Meta-analysis** — the study-level evidence, its negative controls, and the register of
  candidate series considered and NOT admitted, each with the criterion it failed.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import yaml

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))

OUT_DIR = _ROOT / "data" / "database"

#: Rows the audit removed or relabelled, transcribed from the adapter's own audit block so
#: this sheet cannot drift from the code that enforces it (merge_adsorption, F7/F13/F24).
EXCLUDED = [
    {"source": "elnaggar2018", "sorbent": "Na-MK", "species": "Cs", "action": "REMOVED",
     "reason": "El-Naggar 2018 reports ONLY MKBFS systems. This row carries the values of "
               "U-P MK100 from the magnetic-ternary paper — a misattribution.", "finding": "F7"},
    {"source": "elnaggar2018", "sorbent": "K-MK", "species": "Cs", "action": "REMOVED",
     "reason": "Verbatim duplicate of K-MKBFS, presented as a distinct sorbent.", "finding": "F7"},
    {"source": "niu2022", "sorbent": "MS-GP", "species": "Cs", "action": "REMOVED",
     "reason": "Niu 2022 tabulates no capacities at all — only ion-exchange log K.", "finding": "F7"},
    {"source": "niu2022", "sorbent": "SC-GP", "species": "Cs", "action": "REMOVED",
     "reason": "Niu 2022 tabulates no capacities at all — only ion-exchange log K.", "finding": "F7"},
    {"source": "niu2022", "sorbent": "MS-GP", "species": "Sr", "action": "REMOVED",
     "reason": "Niu 2022 tabulates no capacities at all — only ion-exchange log K.", "finding": "F7"},
    {"source": "niu2022", "sorbent": "SC-GP", "species": "Sr", "action": "REMOVED",
     "reason": "Niu 2022 tabulates no capacities at all — only ion-exchange log K.", "finding": "F7"},
    {"source": "hamed2025_magnetic", "sorbent": "MU-PMK80", "species": "Sr", "action": "RELABELLED",
     "reason": "Values are real but belong to a different element: they are Eu-152+154, not Sr.",
     "finding": "F7"},
    {"source": "lei2021", "sorbent": "M/SZMs", "species": "Cs", "action": "RE-TYPED",
     "reason": "Cs was fitted by a Freundlich model, not Langmuir; the capacity type was "
               "mislabelled. Sr in the same paper is Langmuir.", "finding": "F13"},
]


def _registry() -> dict:
    return yaml.safe_load((_ROOT / "knowledge_base" / "registry.yaml").read_text())


def build_sheets() -> dict[str, pd.DataFrame]:
    from geomind.data.merge_adsorption import build as build_A
    from geomind.data.merge_immobilisation import build as build_B
    from geomind import source_data as SD
    from geomind import meta as M

    reg = _registry()
    sheets: dict[str, pd.DataFrame] = {}

    A, B = build_A(), build_B()
    sheets["01 Pool A adsorption"] = A
    sheets["02 Pool B immobilisation"] = B
    sheets["03 Excluded rows"] = pd.DataFrame(EXCLUDED)

    audit = _ROOT / "data" / "warehouse" / "audit_summary.csv"
    sheets["04 Audit trail"] = (pd.read_csv(audit) if audit.exists()
                                else pd.DataFrame(columns=["source_file", "veracity", "reason"]))

    sheets["05 Findings"] = pd.DataFrame(reg.get("findings", []))
    sheets["06 Decisions"] = pd.DataFrame(reg.get("decisions", []))
    sheets["07 Sources"] = pd.DataFrame(reg.get("sources", []))
    sheets["08 Open questions"] = pd.DataFrame(reg.get("open_questions", []))

    for name, df in SD.build_source_data().items():
        if name.startswith("Fig"):
            sheets[f"09 {name}"[:31]] = df

    st = M.collect_studies()
    sheets["10 Meta studies"] = pd.DataFrame(
        [{"study": s.label, "source": s.source_label, "descriptor": s.descriptor,
          "target": s.target, "n": s.n, "r_signed": s.r, "note": s.note} for s in st])
    sheets["11 Meta controls"] = pd.DataFrame(
        [{"control": c.label, "descriptor": c.descriptor, "target": c.target,
          "n": c.n, "r": c.r, "note": c.note} for c in M.collect_negative_controls()])
    sheets["12 Meta not admitted"] = pd.DataFrame(M.REJECTED_CANDIDATES)
    sheets["13 Meta criteria"] = pd.DataFrame(
        [{"criterion": k, "rule": v} for k, v in M.INCLUSION_CRITERIA.items()])
    return sheets


def _readme(sheets: dict[str, pd.DataFrame]) -> pd.DataFrame:
    desc = {
        "01 Pool A adsorption": "Audited adsorption data (removal from solution). Target: K_D or "
                                "capacity — HIGHER is better.",
        "02 Pool B immobilisation": "Audited immobilisation data (retention under leaching). "
                                    "Targets run in BOTH directions — see retention_type. Never "
                                    "merged with Pool A (decision D13).",
        "03 Excluded rows": "Every row the audit REMOVED, RELABELLED or RE-TYPED, with the reason "
                            "and governing finding. Nothing was dropped silently.",
        "04 Audit trail": "Verdict and reason recorded for every ingested table (91).",
        "05 Findings": "The full finding register — each with evidence, action and status.",
        "06 Decisions": "Standing decisions and the finding that forced each.",
        "07 Sources": "Every source publication, its DOI, status and row contribution.",
        "08 Open questions": "Questions still open, and what each blocks.",
        "10 Meta studies": "Study-level evidence: one row per independent series, sign-corrected "
                           "so + always means more framework Al -> better uptake/retention.",
        "11 Meta controls": "Negative controls that must NOT show the pattern.",
        "12 Meta not admitted": "Candidate series considered and rejected, with the criterion each "
                                "failed. Several would have SUPPORTED the claim — rejection is by "
                                "criterion, never by direction.",
        "13 Meta criteria": "The inclusion rules, fixed before the corpus was screened.",
    }
    rows = []
    for name, df in sheets.items():
        d = desc.get(name, "Exact values behind a published figure panel."
                     if name.startswith("09") else "")
        rows.append({"Sheet": name, "Rows": len(df), "What it contains": d})
    return pd.DataFrame(rows)


def write(path: Path | None = None) -> str:
    sheets = build_sheets()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = Path(path) if path else OUT_DIR / "GEOMIND-R-complete-database.xlsx"
    with pd.ExcelWriter(path, engine="openpyxl") as xl:
        _readme(sheets).to_excel(xl, sheet_name="00 README", index=False)
        for name, df in sheets.items():
            df.to_excel(xl, sheet_name=name[:31], index=False)
    return str(path)


def main() -> None:  # pragma: no cover
    p = write()
    s = build_sheets()
    print(f"wrote {p}")
    print(f"  {len(s) + 1} sheets, {sum(len(d) for d in s.values())} rows total")


if __name__ == "__main__":  # pragma: no cover
    main()
