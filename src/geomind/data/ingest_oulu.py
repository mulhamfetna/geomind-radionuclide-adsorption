"""Ingest the Oulu AAM dataset into a tidy composition-adsorption table.

Source dataset: "Dataset for the synthesis of alkali-activated materials"
Companion paper: Hossain, M. F.; Hossain, M. A.; Bhuyan, M.; Vepsalainen, J.;
Luukkonen, T. "Composition-properties-performance relationships of alkali-activated
materials and geopolymers over extended silicon-aluminum-sodium-calcium ratios in
adsorption applications." Materials & Design 262 (2026) 115471.
DOI: 10.1016/j.matdes.2026.115471

Why this matters here: it is a *designed* composition study - Si/Al/Na/Ca varied
systematically, adsorption measured in triplicate, with full structural
characterisation. That is a different quality class from our literature compilation.

Caveat carried into every output row: the adsorbates are NH4+, methylene blue and
rhodamine 6G - **not** Cs-137/Sr-90. NH4+ is a recognised monovalent-cation analogue
for Cs+, so it informs cation-exchange behaviour, but it is an analogue, not a
substitute. The `adsorbate` and `is_radionuclide_analogue` columns keep this explicit.

Usage:  python -m src.geomind.data.ingest_oulu
"""
from __future__ import annotations

import re
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path("data/external/aam-oulu-2026")
OUT = Path("data/raw/external/oulu2026_adsorption.csv")
SOURCE_DOI = "10.1016/j.matdes.2026.115471"

#: sheet name -> (adsorbate label, analogue status)
ADSORBATES = {
    "Ammonium ion.xlsx": ("NH4+", True),   # monovalent cation; Cs+ analogue
    "MB.xlsx": ("methylene_blue", False),  # organic dye
    "R6G.xlsx": ("rhodamine_6G", False),   # organic dye
}

_ID = re.compile(
    r"Si\s*([\d.]+)\s*Al\s*([\d.]+)\s*Na\s*([\d.]+)(?:\s*Ca\s*([\d.]+))?", re.I
)


def parse_sample_id(sample_id: str) -> dict[str, float | None]:
    """'Si20 Al1 Na1' -> {'si': 20, 'al': 1, 'na': 1, 'ca': None}."""
    m = _ID.search(str(sample_id).replace(" ", " "))
    if not m:
        return {"si": None, "al": None, "na": None, "ca": None}
    si, al, na, ca = m.groups()
    return {
        "si": float(si),
        "al": float(al),
        "na": float(na),
        "ca": float(ca) if ca else 0.0,
    }


def _find_data_block(raw: pd.DataFrame) -> pd.DataFrame:
    """Locate the 'Serial No.' header row and return the block beneath it."""
    header_row = None
    for i in range(len(raw)):
        if raw.iloc[i].astype(str).str.contains("Serial No", case=False, na=False).any():
            header_row = i
            break
    if header_row is None:
        raise ValueError("no 'Serial No.' header row found")
    block = raw.iloc[header_row + 1 :].dropna(how="all").dropna(axis=1, how="all")
    return block.reset_index(drop=True)


def ingest_sheet(path: Path, adsorbate: str, analogue: bool) -> pd.DataFrame:
    """Parse one adsorption workbook into tidy rows."""
    xl = pd.ExcelFile(path)
    sheet = next((s for s in xl.sheet_names if "adsorption" in s.lower()), xl.sheet_names[-1])
    block = _find_data_block(xl.parse(sheet, header=None))

    rows = []
    for _, r in block.iterrows():
        vals = r.tolist()
        sample_id = str(vals[1]).strip() if len(vals) > 1 else ""
        comp = parse_sample_id(sample_id)
        if comp["si"] is None:
            continue  # not a data row
        nums = [v for v in vals[2:] if isinstance(v, (int, float)) and pd.notna(v)]
        # layout: ..., adsorption[mg/L], STD[mg/L], adsorption[mmol/L], STD[mmol/L]
        adsorbed = std = None
        if len(nums) >= 4:
            adsorbed, std = float(nums[-4]), float(nums[-3])
        rows.append(
            {
                "sample_id": sample_id,
                **comp,
                "si_al": comp["si"] / comp["al"] if comp["al"] else None,
                "adsorbate": adsorbate,
                "adsorbed_mg_L": adsorbed,
                "std_mg_L": std,
                "is_radionuclide_analogue": analogue,
                "provenance": f"doi:{SOURCE_DOI}",
            }
        )
    return pd.DataFrame(rows)


BET_DIR = ROOT / ("2. Characterization data/2. Characterization data of AAMs "
                  "and geopolymers/BET-BJH AAMs & geopolymers")


def extract_bet() -> dict[int, float]:
    """Pull BET surface area (m2/g) from the ASAP-2020 BIFF2 .xls reports.

    These are Excel-2/BIFF2 binaries that pandas cannot open. The report text is
    embedded but interleaved with control bytes, so `BET Surface Area:` is not a
    contiguous substring after a naive decode -- a tolerant regex is required.

    A strict pattern is essential: the file also contains
    "single point surface area at p/p = 0.30", and a loose fallback silently
    captures that PRESSURE (0.3) as if it were an area.
    """
    out: dict[int, float] = {}
    for f in BET_DIR.glob("S-*.xls"):
        n = int(re.search(r"S-(\d+)", f.name).group(1))
        text = f.read_bytes().replace(b"\x00", b"").decode("latin-1", errors="ignore")
        # allow stray control bytes between the label and the number
        m = re.search(r"BET\W{0,3}Surface\W{0,3}Area\W{0,6}?([0-9]+\.[0-9]+)", text)
        if m:
            val = float(m.group(1))
            if val > 0.5:          # guard against the p/p0 = 0.3 trap
                out[n] = val
    return out


def sample_order() -> dict[int, str]:
    """Serial number -> sample ID, read from the NH4 workbook."""
    f = next(ROOT.rglob("Ammonium ion.xlsx"))
    d = pd.read_excel(f, sheet_name="NH4 adsorption experiment", header=None)
    out = {}
    for _, r in d.iterrows():
        v = r.tolist()
        m = re.match(r"Sample\s+(\d+)", str(v[0]).strip())
        if m and isinstance(v[1], str):
            out[int(m.group(1))] = v[1].strip()
    return out


def main() -> None:
    if not ROOT.exists():
        raise SystemExit(f"{ROOT} not found - extract the dataset first")

    frames = []
    for filename, (adsorbate, analogue) in ADSORBATES.items():
        matches = list(ROOT.rglob(filename))
        if not matches:
            print(f"  ! {filename} not found - skipped")
            continue
        df = ingest_sheet(matches[0], adsorbate, analogue)
        print(f"  {adsorbate:16s} {len(df):3d} rows  "
              f"Si/Al {df.si_al.min():.2f}-{df.si_al.max():.2f}")
        frames.append(df)

    tidy = pd.concat(frames, ignore_index=True)

    # attach BET surface area by sample number
    bet = extract_bet()
    order = sample_order()
    id_to_bet = {sid: bet[n] for n, sid in order.items() if n in bet}
    tidy["bet_m2_g"] = tidy["sample_id"].map(id_to_bet)
    print(f"  BET attached to {int(tidy.bet_m2_g.notna().sum())}/{len(tidy)} rows "
          f"({tidy.bet_m2_g.min():.1f}-{tidy.bet_m2_g.max():.1f} m2/g)")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    tidy.to_csv(OUT, index=False)
    print(f"\nwrote {OUT}  {tidy.shape}")
    print(f"  adsorbates: {tidy.adsorbate.value_counts().to_dict()}")
    print(f"  Cs-analogue rows (NH4+): {int(tidy.is_radionuclide_analogue.sum())}")
    print(f"  distinct compositions: {tidy.sample_id.nunique()}")


if __name__ == "__main__":
    main()
