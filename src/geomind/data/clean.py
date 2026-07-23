"""Build model-ready tables from data/raw, applying the M2 quality decisions.

Every transformation here is a recorded decision from
`reports/m2-data-quality-report.md`. Nothing is dropped silently.

Usage:  python -m src.geomind.data.clean
Outputs: data/processed/{physical,adsorption,geomind_reference}.csv + cleaning_log.md
"""
from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

RAW = Path("data/raw")
OUT = Path("data/processed")

# --- M2 decisions ---------------------------------------------------------
# F1: joined in from the GEOMIND paper's 10 published samples; NOT measurements
#     of these mixes. Confirmed by 9/11 exact Si/Al matches and 91/92 mixes
#     carrying a single broadcast value. Using them would learn a join artefact.
DROP_TRANSPLANTED = ["Si_Al", "Density"]
# F2: constant zero across all 867 rows — carries no information.
DROP_DEAD = ["Metakaolin"]

_log: list[str] = []


def log(msg: str) -> None:
    _log.append(msg)
    print(msg)


def build_physical() -> pd.DataFrame:
    """Fly-ash/slag concrete strength data (867 rows -> cleaned)."""
    log("\n## physical")
    df = pd.read_csv(RAW / "Physical_Data.csv")  # F4: CSV is authoritative
    log(f"- loaded `Physical_Data.csv` (authoritative over the byte-identical .xlsx): {df.shape}")

    before = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    log(f"- F4 removed {before - len(df)} exact duplicate rows -> {len(df)}")

    dropped = [c for c in DROP_TRANSPLANTED + DROP_DEAD if c in df.columns]
    df = df.drop(columns=dropped)
    log(f"- **F1 dropped {DROP_TRANSPLANTED}** — transplanted from the paper, not measured here")
    log(f"- F2 dropped {DROP_DEAD} — constant zero, no information")

    df["provenance"] = trace_provenance(df)
    counts = df["provenance"].value_counts().to_dict()
    log(f"- provenance attached by compressive-strength match: {counts}")

    df["material_system"] = "fly_ash_slag_concrete"
    log("- tagged `material_system=fly_ash_slag_concrete` (NOT the paper's metakaolin pastes)")
    return df


def trace_provenance(df: pd.DataFrame) -> pd.Series:
    """Best-effort row->source attribution via compressive strength values."""
    d = pd.read_excel(RAW / "Data.xlsx")
    n = pd.read_excel(RAW / "N data.xls")
    ds = set(d["Compressive Strength (Mpa)"].round(2))
    ns = set(n["compressive strength"].round(2))

    def tag(v: float) -> str:
        v = round(v, 2)
        in_d, in_n = v in ds, v in ns
        if in_d and in_n:
            return "ambiguous:Data.xlsx|N_data.xls"
        if in_d:
            return "Data.xlsx"
        if in_n:
            return "N_data.xls"
        return "UNTRACED"

    return df["Comp_Strength"].map(tag)


def build_adsorption() -> pd.DataFrame:
    """Cs/Sr adsorption data — the M4/M5 target. Small and partly duplicated."""
    log("\n## adsorption")
    df = pd.read_csv(RAW / "Functional_Data.csv")
    log(f"- loaded `Functional_Data.csv`: {df.shape}")

    df = df.rename(columns={"Source": "provenance"})
    df["provenance"] = df["provenance"].str.strip()
    log(f"- provenance already present: {sorted(df['provenance'].dropna().unique())}")

    # F3: flag (do not delete) values repeated verbatim elsewhere in the table
    for col, label in [("Qmax_Cs_mg_g", "cs"), ("Qmax_Sr_mg_g", "sr")]:
        dup = df[col].dropna().duplicated(keep=False)
        flag = pd.Series(False, index=df.index)
        flag.loc[dup[dup].index] = True
        df[f"{label}_value_repeated"] = flag
        n_rows, n_uniq = df[col].notna().sum(), df[col].dropna().nunique()
        log(f"- F3 {col}: {n_rows} rows but only {n_uniq} distinct values "
            f"-> {int(flag.sum())} flagged as repeated")

    log("- ⚠️ retained all rows; repetition is FLAGGED, not removed — dropping would "
        "silently discard genuine replicates. Model code must respect these flags.")
    return df


def build_geomind_reference() -> pd.DataFrame:
    """The paper's own 10 published samples — verified, used for M3a."""
    log("\n## geomind_reference")
    df = pd.read_excel(RAW / "GEOMIND_RADIOACTIVE_MASTER.xlsx", sheet_name="GEOMIND_Samples")
    log(f"- loaded `GEOMIND_Samples`: {df.shape} (verified == the paper's published subset)")
    df["provenance"] = "doi:10.1039/d5dd00383k"
    n_sentinel = int((df.select_dtypes("number") == -1).any(axis=1).sum())
    log(f"- {n_sentinel} row(s) carry the -1 infeasibility sentinel (NOT missing data)")
    return df


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    log("# M2 cleaning log\n")
    log("Decisions implement `reports/m2-data-quality-report.md`.")

    for name, frame in [
        ("physical", build_physical()),
        ("adsorption", build_adsorption()),
        ("geomind_reference", build_geomind_reference()),
    ]:
        path = OUT / f"{name}.csv"
        frame.to_csv(path, index=False)
        log(f"\n-> wrote `{path}` {frame.shape}")

    log("\n## Not carried forward")
    log("- `GEOMIND_R_MASTER_DATABASE_v2.xlsx` — disagrees with Physical_Data in 22 cells "
        "with no changelog; its 19 radionuclide columns are largely null. Unresolved (F4).")
    log("- `Data.xlsx`, `N data.xls` — retained as provenance sources only.")
    log("- `Metadata.csv` — cp1256; superseded by `docs/data-dictionary.md`.")

    (OUT / "cleaning_log.md").write_text("\n".join(_log) + "\n")
    print(f"\nwrote {OUT/'cleaning_log.md'}")


if __name__ == "__main__":
    main()
