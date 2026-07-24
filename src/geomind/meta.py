"""Study-level meta-analysis — the unit of analysis is the STUDY, not the sample.

## Why this module exists

The forward model is fit on n = 7, and finding F43 proved that ceiling is structural: no
additional row pairing framework Al^IV with Cs/Sr uptake exists anywhere in the published
literature, and every route to enlarging the training set fails. Finding F36 proved the
complementary point: pooling raw values across laboratories destroys predictability
(leave-one-out R^2 < 0), because each study is its own regime.

Those two findings look like a dead end. They are not — they are a signpost. If raw values
cannot be pooled but each laboratory's *internal* series is informative, then the right unit
of analysis is the **study**, not the sample. Instead of one regression over n rows, we ask
how many INDEPENDENT studies reproduce the same direction, and combine their effect sizes.

That is standard random-effects meta-analysis, and it is the correct tool for exactly the
situation F36 describes. Statistical power then comes from **k**, the number of independent
replications, and each newly acquired study raises k — which is achievable from literature,
whereas raising n is not.

## Sign convention

Targets run in opposite directions: a high K_D is good, a high percent-leached is bad. Every
study is sign-corrected at collection so that **positive always means "more framework
aluminium is associated with better uptake or retention"**. A study running the other way
must surface as negative, never be quietly flipped.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Study:
    """One independent internal series: a single laboratory, protocol and material class."""

    label: str
    source_label: str
    descriptor: str
    target: str
    n: int
    r: float          # sign-corrected: + supports the framework-Al claim
    note: str = ""


def _corr(x, y) -> float:
    return float(np.corrcoef(np.asarray(x, float), np.asarray(y, float))[0, 1])


def collect_studies() -> list[Study]:
    """Every independent series in the two pools that tests the framework-Al claim.

    A series qualifies only if it varies composition WITHIN one laboratory and protocol —
    the condition F36 shows is required for a descriptor-property relationship to hold.
    """
    from geomind.data.merge_adsorption import build as build_A
    from geomind.data.merge_immobilisation import build as build_B
    from geomind.data import nmr_ari as N

    A = N.attach(build_A())
    B = build_B()
    out: list[Study] = []

    # 1. Varon 2025 - the direct measurement: framework Al^IV vs Sr K_D. Higher K_D is better,
    #    so the raw correlation already carries the right sign.
    v = A[A.source_label == "varon2025"].dropna(subset=["al_iv_mmol_g", "kd_mL_g"])
    out.append(Study("Framework Al^IV vs Sr K_D (Varon)", "varon2025", "al_iv_mmol_g",
                     "Sr K_D", len(v), _corr(v["al_iv_mmol_g"], v["kd_mL_g"]),
                     "the model's own training series"))

    # 2. Oulu 2026, Ca-FREE subset only - ARI vs NH4+ uptake. NH4+ is a cation exchanged at the
    #    same sites; the Ca-bearing samples are excluded by the F19 structural precondition.
    o = A[(A.source_label == "oulu2026") & (A.adsorbate == "NH4+")].dropna(
        subset=["ari", "capacity_mg_g"]).copy()
    cf = o[o["ca_al"].fillna(0) == 0]
    out.append(Study("ARI vs NH4+ uptake, Ca-free (Oulu)", "oulu2026", "ari",
                     "NH4+ capacity", len(cf), _corr(cf["ari"], cf["capacity_mg_g"]),
                     "different adsorbate (cation), different laboratory"))

    # 3-4. Vandevenne 2018 - designed Ca-Si-Al slag series. The target is PERCENT RELEASED, so
    #      lower is better: a POSITIVE r(Si/Al, %released) means more Al retains better, which
    #      already supports the claim. Si/Al is an inverse proxy for framework Al content.
    vd = B[B.source_label == "vandevenne2018"]
    for nuc in ("Cs", "Sr"):
        s = vd[vd["nuclide"] == nuc]
        out.append(Study(f"Si/Al vs {nuc} retention (Vandevenne)", "vandevenne2018",
                         "si_al (inverse Al proxy)", f"{nuc} retention", len(s),
                         _corr(s["si_al"], s["retention_value"]),
                         "immobilisation regime, Ca-bearing class, independent laboratory"))
    return out


def collect_negative_controls() -> list[Study]:
    """Controls that must NOT show the pattern, or the claim is unfalsifiable.

    If framework Al drives cation exchange specifically, then (a) surface area should not
    predict uptake, (b) the descriptor should die where Ca occupies the sites (F19/F41), and
    (c) it should not track an adsorbate that is not exchanged at those sites at all.
    """
    from geomind.data.merge_adsorption import build as build_A
    from geomind.data import nmr_ari as N

    A = N.attach(build_A())
    out: list[Study] = []

    v = A[A.source_label == "varon2025"].dropna(subset=["bet_m2_g", "kd_mL_g"])
    out.append(Study("BET surface area (Varon)", "varon2025", "bet_m2_g", "Sr K_D",
                     len(v), _corr(v["bet_m2_g"], v["kd_mL_g"]),
                     "the hypothesis this project displaced"))

    o = A[(A.source_label == "oulu2026") & (A.adsorbate == "NH4+")].dropna(
        subset=["ari", "capacity_mg_g"]).copy()
    cb = o[o["ca_al"].fillna(0) != 0]
    out.append(Study("ARI in Ca-bearing gels (Oulu)", "oulu2026", "ari", "NH4+ capacity",
                     len(cb), _corr(cb["ari"], cb["capacity_mg_g"]),
                     "F19: outside the structural precondition the descriptor is dead"))

    d = A[(A.source_label == "oulu2026") & (A.adsorbate == "methylene_blue")].dropna(
        subset=["ari", "capacity_mg_g"]).copy()
    dcf = d[d["ca_al"].fillna(0) == 0]
    out.append(Study("ARI vs dye uptake (Oulu)", "oulu2026", "ari", "methylene blue capacity",
                     len(dcf), _corr(dcf["ari"], dcf["capacity_mg_g"]),
                     "a dye is not exchanged at Al^IV sites - specificity check"))
    return out


def _fisher_z_mean(rs, ns) -> float:
    """Inverse-variance (n-3) weighted mean correlation via Fisher's z transform.

    Correlations cannot be averaged directly - the sampling distribution is skewed. z =
    atanh(r) is approximately normal with variance 1/(n-3), so the weighted mean is taken
    in z and transformed back.
    """
    z = [math.atanh(max(min(r, 0.999999), -0.999999)) for r in rs]
    w = [max(n - 3, 1) for n in ns]
    zbar = sum(wi * zi for wi, zi in zip(w, z)) / sum(w)
    return math.tanh(zbar)


def sign_test_p(k: int, supporting: int | None = None) -> float:
    """One-sided exact sign test: P(all k studies agree by chance) = 0.5^k.

    This is the honest power statement. Each ADDITIONAL STUDY halves the p-value; additional
    rows within an existing study do not move it at all. That is why acquisition should target
    new independent series, not more rows (F43).
    """
    if supporting is None:
        supporting = k
    if supporting != k:                      # partial agreement: binomial tail
        from math import comb
        return sum(comb(k, i) for i in range(supporting, k + 1)) / 2 ** k
    return 0.5 ** k


def meta_analyse(studies: list[Study]) -> dict:
    """Combine independent studies into one honest summary."""
    rs = [s.r for s in studies]
    ns = [s.n for s in studies]
    k = len(studies)
    supporting = sum(1 for r in rs if r > 0)
    return {
        "k": k,
        "n_supporting": supporting,
        "n_opposing": k - supporting,
        "samples_represented": sum(ns),
        "r_bar": _fisher_z_mean(rs, ns),
        "r_min": min(rs),
        "r_max": max(rs),
        "sign_test_p": sign_test_p(k, supporting),
    }


def report() -> str:
    """Human-readable summary of the study-level evidence."""
    st = collect_studies()
    nc = collect_negative_controls()
    m = meta_analyse(st)
    L = ["STUDY-LEVEL META-ANALYSIS — unit of analysis is the study, not the sample",
         "sign convention: + means more framework Al -> better uptake/retention", ""]
    L.append(f"{'study':38s} {'n':>3s} {'r':>8s}  verdict")
    for s in st:
        L.append(f"{s.label:38s} {s.n:3d} {s.r:+8.3f}  {'supports' if s.r > 0 else 'OPPOSES'}")
    L += ["",
          f"  k = {m['k']} independent studies, {m['n_supporting']} supporting, {m['n_opposing']} opposing",
          f"  weighted mean correlation r_bar = {m['r_bar']:+.3f}  (range {m['r_min']:+.3f} to {m['r_max']:+.3f})",
          f"  samples represented             = {m['samples_represented']}",
          f"  exact sign test                 p = {m['sign_test_p']:.4f}",
          "", "NEGATIVE CONTROLS (must NOT show the pattern)"]
    for c in nc:
        L.append(f"{c.label:38s} {c.n:3d} {c.r:+8.3f}  {c.note}")
    return "\n".join(L)


def main() -> None:  # pragma: no cover - CLI convenience
    print(report())


if __name__ == "__main__":  # pragma: no cover
    main()
