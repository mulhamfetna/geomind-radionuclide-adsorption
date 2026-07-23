"""Reproduce every figure quoted in reports/m2-data-quality-report.md.

Usage:  python -m src.geomind.data.profile      (from the repo root)
"""
from __future__ import annotations

import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")
RAW = Path("data/raw")


def load(name: str, **kw) -> pd.DataFrame:
    path = RAW / name
    return pd.read_csv(path, **kw) if name.endswith(".csv") else pd.read_excel(path, **kw)


def f4_redundancy() -> None:
    print("\n=== F4: CSV/XLSX pairs are byte-identical ===")
    for base in ("Functional_Data", "Physical_Data"):
        a, b = load(f"{base}.csv"), load(f"{base}.xlsx")
        same = a.shape == b.shape and a.fillna(-999).round(6).equals(b.fillna(-999).round(6))
        print(f"  {base}: csv{a.shape} xlsx{b.shape} identical={same}")

    p, v2 = load("Physical_Data.csv"), load("GEOMIND_R_MASTER_DATABASE_v2.xlsx")
    shared = [c for c in p.columns if c in v2.columns]
    diff = (p[shared].round(6).values != v2[shared].round(6).values).sum()
    print(f"  v2 vs Physical_Data: {len(shared)}/{len(p.columns)} shared cols, "
          f"{diff} disagreeing cells, v2 nulls={v2.isna().sum().sum()}")
    print(f"  exact duplicate rows in Physical_Data: {p.duplicated().sum()}")


def f2_cardinality() -> None:
    print("\n=== F2: degenerate feature space ===")
    p = load("Physical_Data.csv")
    for c in p.columns:
        n = p[c].nunique()
        flag = "  <-- DEAD (constant)" if n <= 1 else ("  <-- low cardinality" if n <= 6 else "")
        print(f"  {c:15s} unique={n:4d}{flag}")
    mix_cols = ["FlyAsh", "GGBFS", "NaOH_M", "Na2SiO3", "CopperSlag", "RecycledAgg"]
    grp = p.groupby(mix_cols)
    print(f"  distinct mix designs: {grp.ngroups} (from {len(p)} rows)")
    print(f"  mixes with a single Si_Al value : {(grp.Si_Al.nunique() == 1).sum()}/{grp.ngroups}")
    print(f"  mixes with a single Density value: {(grp.Density.nunique() == 1).sum()}/{grp.ngroups}")


def f1_transplant() -> None:
    """The critical finding: Si_Al / Density appear to come from the paper's 10 samples."""
    print("\n=== F1 (CRITICAL): Si_Al / Density vs the paper's published samples ===")
    p = load("Physical_Data.csv")
    g = load("GEOMIND_RADIOACTIVE_MASTER.xlsx", sheet_name="GEOMIND_Samples")

    ours = sorted(p.Si_Al.unique())
    paper = sorted(pd.to_numeric(g["Si/Al"], errors="coerce").dropna().unique())
    hits = [v for v in ours if any(abs(v - q) < 1e-6 for q in paper)]
    print(f"  our Si_Al uniques  : {ours}")
    print(f"  paper Si/Al values : {paper}")
    print(f"  >>> EXACT matches  : {len(hits)}/{len(ours)} -> {hits}")

    dens = sorted(p.Density.unique())
    pdens = sorted(
        pd.to_numeric(g["mixture_density(g/cm³)"], errors="coerce").dropna().tolist()
        + pd.to_numeric(g["material_density(g/cm³)"], errors="coerce").dropna().tolist()
    )
    dhits = [v for v in dens if any(abs(v - q) < 1e-6 for q in pdens)]
    print(f"  >>> Density exact matches: {len(dhits)}/{len(dens)} -> {dhits}")


def f3_adsorption() -> None:
    print("\n=== F3: adsorption dataset — the M4/M5 bottleneck ===")
    f = load("Functional_Data.csv")
    print(f"  rows={len(f)}  Qmax_Cs present={f.Qmax_Cs_mg_g.notna().sum()}  "
          f"Qmax_Sr present={f.Qmax_Sr_mg_g.notna().sum()}")
    print(f"  distinct Qmax_Cs values: {f.Qmax_Cs_mg_g.dropna().nunique()} "
          f"(from {f.Qmax_Cs_mg_g.notna().sum()} rows) -> repeated blocks")
    print(f"  sources: {sorted(f.Source.dropna().unique())}")


def f5_encoding() -> None:
    print("\n=== F5: encoding ===")
    try:
        load("Metadata.csv")
        print("  Metadata.csv: read as UTF-8 (unexpected)")
    except UnicodeDecodeError:
        m = load("Metadata.csv", encoding="cp1256")
        print(f"  Metadata.csv: NOT utf-8; reads as cp1256 -> shape {m.shape}")


def f4_traceability() -> None:
    print("\n=== F4: strength traceability to source files ===")
    p, d, n = load("Physical_Data.csv"), load("Data.xlsx"), load("N data.xls")
    ps = set(p.Comp_Strength.round(2))
    ds = set(d["Compressive Strength (Mpa)"].round(2))
    ns = set(n["compressive strength"].round(2))
    print(f"  distinct Comp_Strength: ours={len(ps)} Data.xlsx={len(ds)} N-data={len(ns)}")
    print(f"  in Data.xlsx={len(ps & ds)}  in N-data={len(ps & ns)}  in NEITHER={len(ps - ds - ns)}")
    print(f"  row arithmetic: {len(d)} + {len(n)} = {len(d) + len(n)} vs {len(p)} "
          f"(diff {len(p) - len(d) - len(n)}) -> not a plain concatenation")


def main() -> None:
    f4_redundancy()
    f2_cardinality()
    f1_transplant()
    f3_adsorption()
    f4_traceability()
    f5_encoding()
    print("\nSee reports/m2-data-quality-report.md for interpretation.")


if __name__ == "__main__":
    main()
