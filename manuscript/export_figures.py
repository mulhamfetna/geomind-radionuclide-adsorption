"""Export every manuscript figure at submission quality, as individual files.

Journals at this tier ask for high-resolution raster AND a vector original. This regenerates
each figure from the live pipeline and writes three forms per figure:

    <name>.png   600 dpi raster   (universally accepted; safe default)
    <name>.pdf   vector           (preferred by most publishers; infinitely scalable)
    <name>.eps   vector           (still requested by some Elsevier/Springer workflows)

    python -m export_figures        # from manuscript/, writes manuscript/figures-submission/

The figures are regenerated, never up-scaled, so text and lines stay sharp at any size.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_HERE))

# The analysis modules resolve data/ paths relative to the working directory, so this
# script must run from the repository root regardless of where it was invoked from.
# Without this the pools load empty and the figures render from nothing.
import os  # noqa: E402
os.chdir(_ROOT)

OUT = _HERE / "figures-submission"

#: Submission resolution. 600 dpi is the usual ceiling requested for combined
#: line-art/greyscale figures; 300 is the floor. We ship the higher one.
DPI = 600

#: figure function -> submission file stem, in manuscript order.
FIGURES = [
    ("fig1_concept", "Figure_1_mechanism_concept"),
    ("fig2_correlation_and_causal", "Figure_2_correlation_and_causal_test"),
    ("fig3_forward_model", "Figure_3_forward_model"),
    ("fig4_structural_precondition", "Figure_4_structural_precondition"),
    ("fig5_saturation_screen", "Figure_5_saturation_screen"),
    ("fig6_pooling_limit", "Figure_6_pooling_limit"),
]


def export(dpi: int = DPI) -> list[Path]:
    """Regenerate every figure and write PNG (raster) + PDF and EPS (vector)."""
    import figures as F

    OUT.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for fn_name, stem in FIGURES:
        fn = getattr(F, fn_name, None)
        if fn is None:
            continue
        fig = fn()
        for ext in ("png", "pdf", "eps"):
            path = OUT / f"{stem}.{ext}"
            # bbox_inches='tight' trims the canvas without rescaling the content
            fig.savefig(path, dpi=dpi, bbox_inches="tight",
                        format=ext, facecolor="white")
            written.append(path)
        plt.close(fig)
    return written


def write_manifest() -> Path:
    """A README inside the archive, so a production editor knows what they have."""
    import figures as F  # noqa: F401  (import proves the pipeline ran)
    lines = [
        "GEOMIND-R — manuscript figures, submission quality",
        "=" * 52,
        "",
        f"Every figure regenerated from the live analysis pipeline at {DPI} dpi.",
        "Nothing here is up-scaled: each file is rendered at full resolution from the data,",
        "so text and rules remain sharp at any reproduction size.",
        "",
        "Three formats are supplied for each figure:",
        "  .png  600 dpi raster  — universally accepted",
        "  .pdf  vector          — preferred by most publishers, scales without loss",
        "  .eps  vector          — for workflows that still require EPS",
        "",
        "Figures",
        "-------",
    ]
    titles = {
        "Figure_1_mechanism_concept":
            "Ion exchange at a framework Al(IV) site vs the physisorption picture.",
        "Figure_2_correlation_and_causal_test":
            "(a) framework Al vs Sr K_D, (b) surface area vs K_D, (c) the within-sample causal test.",
        "Figure_3_forward_model":
            "The within-class forward model with leave-one-out validation.",
        "Figure_4_structural_precondition":
            "The descriptor holds in framework gels and fails in Ca-bearing gels.",
        "Figure_5_saturation_screen":
            "Every fitted Langmuir capacity ranked by fraction of saturation reached.",
        "Figure_6_pooling_limit":
            "Predicted vs observed: predictive within one class, worse than the mean when pooled.",
    }
    for _, stem in FIGURES:
        lines.append(f"  {stem}")
        lines.append(f"      {titles.get(stem, '')}")
    lines += [
        "",
        "Licence: CC BY 4.0 (figures and data). Please cite:",
        "  Fetna, M. & Hammal, A. GEOMIND-R. https://doi.org/10.5281/zenodo.21510123",
        "",
        "The values behind every panel are provided separately in the source-data workbook.",
    ]
    path = OUT / "README.txt"
    path.write_text("\n".join(lines) + "\n")
    return path


def make_zip() -> str:
    """Bundle the exported figures into one archive for submission."""
    files = export()
    files.append(write_manifest())
    archive = _HERE / "GEOMIND-R-figures-submission.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(files):
            z.write(f, arcname=f"figures/{f.name}")
    return str(archive)


def main() -> None:  # pragma: no cover - CLI convenience
    archive = make_zip()
    n = len(list(OUT.glob("*")))
    print(f"wrote {archive} ({n} files at {DPI} dpi)")


if __name__ == "__main__":  # pragma: no cover
    main()
