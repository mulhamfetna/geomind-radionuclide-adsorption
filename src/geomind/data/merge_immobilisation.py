"""Pool B — immobilisation / leach-resistance pool (decision D13).

One ``_from_*`` adapter per source. Every value here was read **in context** in the
source PDF, per the project's standing rule; the page is cited on each block.

Pool B exists because of finding **F20**: solid-state NMR and adsorption capacity are
near-disjoint in this literature, and the NMR — the only descriptor that predicts
cation uptake — lives almost entirely in the immobilisation studies.
"""

from __future__ import annotations

import pandas as pd

from .immobilisation_schema import (
    Censoring,
    MatrixClass,
    RetentionType,
    conform,
)

# ---------------------------------------------------------------------------
# Kim et al., Cement and Concrete Research 205 (2026) 108214
# doi:10.1016/j.cemconres.2026.108214   (author-accepted version, CC-BY 4.0)
# ---------------------------------------------------------------------------
KIM_DOI = "10.1016/j.cemconres.2026.108214"

#: Table 2, p10: average leachability index over the leaching intervals.
#: Verified cell by cell against LI = -log10(De) — see immobilisation_schema.
KIM_TABLE2_AVG_LI = {"NaSr1": 15.5, "NaSr2": 14.8, "NaSr3": 16.0, "KSr3": 16.0}

#: Kim p10 + Table 2 caption: "Sr leachate concentrations in KSr1, KSr2 ... were below
#: the ICP-OES detection limit (0.001 ppm), yielding non-detectable values for De and LI."
#: These are LEFT-CENSORED, and they are the BEST performers, not missing data.
KIM_CENSORED = {"KSr1", "KSr2"}

#: Detection limit stated by Kim, in ppm of Sr in the leachate.
KIM_ICP_OES_LIMIT_PPM = 0.001

#: Sr K-edge EXAFS coordination numbers, Kim p26 verbatim. Pre- and post-leach.
#: NOTE: Kim credits the NaSr3 pre-leach figure to reference [7] = Geddes et al.,
#: J. Hazard. Mater. 488 (2025) 137426 — NOT to Yildirim 2024, which the master
#: workbook claimed. That misattribution is finding F21.
KIM_CN_SR = {
    ("NaSr3", "pre"): (7.87, 0.69),
    ("NaSr3", "post"): (7.95, 0.43),
    ("KSr3", "pre"): (7.55, 0.14),
    ("KSr3", "post"): (7.94, 0.45),
}

#: Kim methods: Si/Al = 2.7 throughout; Sr added as Sr(OH)2.8H2O at 1/2/3 wt%.
KIM_SI_AL = 2.7
KIM_LOADING = {"NaSr1": 1.0, "NaSr2": 2.0, "NaSr3": 3.0,
               "KSr1": 1.0, "KSr2": 2.0, "KSr3": 3.0}


def _from_kim2026() -> pd.DataFrame:
    rows = []
    for sample, loading in KIM_LOADING.items():
        na = sample.startswith("Na")
        censored = sample in KIM_CENSORED
        rows.append(
            {
                "sample_id": f"kim2026_{sample}",
                "matrix_name": sample,
                "matrix_class": (MatrixClass.NA_GEOPOLYMER if na
                                 else MatrixClass.K_GEOPOLYMER).value,
                "nuclide": "Sr",
                "loading_wt_pct": loading,
                "retention_value": None if censored else KIM_TABLE2_AVG_LI[sample],
                "retention_type": RetentionType.LEACHABILITY_INDEX.value,
                "censored": (Censoring.LEFT if censored else Censoring.NONE).value,
                # left-censored: true LI is ABOVE this, because De is below detection
                "censoring_bound": KIM_ICP_OES_LIMIT_PPM if censored else None,
                "leachant": "deionised_water",
                "duration_days": 28.0,
                "si_al": KIM_SI_AL,
                "activator": "sodium_silicate" if na else "potassium_silicate",
                "precursor": "metakaolin",
                "cn_sr_exafs": KIM_CN_SR.get((sample, "pre"), (None, None))[0],
                "leach_state": "pre",
                "provenance_doi": KIM_DOI,
                "source_label": "kim2026",
                "from_figure": False,
                "value_repeated": False,
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Nevin et al., J. Mater. Chem. A 14 (2026) 10000-10023  (open access, CC-BY 3.0)
# ---------------------------------------------------------------------------
NEVIN_DOI = "10.1039/d5ta90211h"  # placeholder-safe: see MANIFEST for the resolved DOI

#: Nevin **Table 2**, p6: "Calculated diffusion coefficients and associated
#: leachability indices for Sr and Cs". All four samples, De and LI with errors.
#: Independently confirms LI = -log10(De): 18.66/19.11/13.27/13.22 against the
#: published 18.7/19.1/13.3/13.2.
#:
#: NOTE the master sheet Sr_Leaching_Data carried only the two Sr rows and dropped
#: both Cs rows — a silent 50% loss of this table (finding F22).
NEVIN_TABLE2 = {
    #  sample: (De cm2/s, De_err, LI, LI_err)
    "Sr_1": (2.2e-19, 3.4e-23, 18.7, 0.00007),
    "Sr_3": (7.8e-20, 1.9e-24, 19.1, 0.00001),
    "Cs_1": (5.4e-14, 1.6e-18, 13.3, 0.00001),
    "Cs_3": (6.0e-14, 3.1e-18, 13.2, 0.00002),
}
NEVIN_LI = {k: v[2] for k, v in NEVIN_TABLE2.items()}

#: Q4(mAl) speciation, master sheet NMR_Sr_Cs_Data, sourced to Nevin 2026 and
#: audited as traceable (registry asset master.nmr_sr_cs, status verified).
#: All rows are ONE formulation at Si/Al = 3, pre- and post-leach.
NEVIN_NMR = {
    ("C_0", "pre"):  (23.9, 38.6, 32.1, 5.4, 1.42, -88.5, None),
    ("Sr_1", "pre"): (18.2, 44.3, 31.8, 5.7, 1.45, -89.0, "Sr"),
    ("Sr_3", "pre"): (17.3, 47.4, 33.1, 2.3, 1.43, -89.0, "Sr"),
    ("Cs_1", "pre"): (21.3, 36.1, 37.7, 4.9, 1.46, -88.5, "Cs"),
    ("Cs_3", "pre"): (26.5, 38.1, 29.9, 5.4, 1.40, -88.5, "Cs"),
    ("C_0", "post"):  (21.7, 41.7, 32.5, 4.2, 1.42, -88.5, None),
    ("Sr_1", "post"): (32.1, 32.1, 32.1, 3.8, 1.37, -89.0, "Sr"),
    ("Sr_3", "post"): (24.6, 37.3, 32.8, 5.3, 1.42, -89.0, "Sr"),
    ("Cs_1", "post"): (19.2, 46.0, 30.5, 4.2, 1.43, -88.5, "Cs"),
    ("Cs_3", "post"): (21.9, 38.8, 32.5, 6.8, 1.45, -88.5, "Cs"),
}

NEVIN_LOADING = {"C_0": 0.0, "Sr_1": 1.0, "Sr_3": 3.0, "Cs_1": 1.0, "Cs_3": 3.0}


def _ari_from_q4(q4_4al, q4_3al, q4_2al, q4_1al) -> float:
    """Al-richness index restricted to Q4 environments: mean Al neighbours per Si.

    Same definition as :mod:`geomind.data.nmr_ari`, so Pool A and Pool B descriptors
    are directly comparable even though the pools themselves are never merged (D13).
    """
    return (4 * q4_4al + 3 * q4_3al + 2 * q4_2al + 1 * q4_1al) / 100.0


def _from_nevin2026() -> pd.DataFrame:
    rows = []
    for (sample, state), vals in NEVIN_NMR.items():
        q4_4, q4_3, q4_2, q4_1, si_al_nmr, shift, nuclide = vals
        # The leach test is what produces the LI, so it attaches to the pre-leach
        # formulation: that is the material whose structure was characterised before
        # being subjected to leaching. Post-leach rows carry structure only.
        entry = NEVIN_TABLE2.get(sample) if state == "pre" else None
        li = entry[2] if entry else None
        rows.append(
            {
                "sample_id": f"nevin2026_{sample}_{state}",
                "matrix_name": sample,
                "matrix_class": MatrixClass.K_GEOPOLYMER.value,  # K-A-S-H gel
                "nuclide": nuclide or "none",
                "loading_wt_pct": NEVIN_LOADING[sample],
                "retention_value": li,
                "retention_type": (RetentionType.LEACHABILITY_INDEX.value
                                   if li is not None else None),
                "retention_std": entry[3] if entry else None,
                "censored": Censoring.NONE.value,
                "leachant": "deionised_water",
                "duration_days": 35.0,
                "si_al": 3.0,
                "precursor": "metakaolin",
                "activator": "potassium_silicate",
                "q4_4al_pct": q4_4, "q4_3al_pct": q4_3,
                "q4_2al_pct": q4_2, "q4_1al_pct": q4_1,
                "si_al_nmr": si_al_nmr,
                "ari": _ari_from_q4(q4_4, q4_3, q4_2, q4_1),
                "chemical_shift_ppm": shift,
                "leach_state": state,
                "provenance_doi": NEVIN_DOI,
                "source_label": "nevin2026",
                "from_figure": False,
                "value_repeated": False,
            }
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Kurumisawa, Omatu & Yamashina, Materials and Structures 54(4):169 (2021)
# doi:10.1617/s11527-021-01758-y
#
# This paper was originally REJECTED from the corpus as "a diffusivity study".
# It is in fact a BRIDGE: the same five specimens carry a Cs adsorption capacity
# (Pool A, Fig. 3b) and a Cs diffusivity (Pool B, Fig. 2), across five different
# alkali activators. See merge_adsorption._from_kurumisawa2021 for the Pool A half.
#
# WARNING: this diffusivity is an INGRESS coefficient (Cs diffusing INTO an immersed
# specimen), NOT the ANSI/ANS 16.1 leaching-out De reported by Kim and Nevin. The two
# differ by ~12 orders of magnitude. RetentionType keeps them apart.
# ---------------------------------------------------------------------------
KURUMISAWA_DOI = "10.1617/s11527-021-01758-y"

#: Table 2, p27 — activator composition. Si/Al of the hardened gel is NOT stated
#: directly and is deliberately left null rather than inferred from these ratios.
KURUMISAWA_ACTIVATOR = {
    #  sample: (M2O, M2O/Al2O3, SiO2/Al2O3, H2O/Al2O3)
    "K11":   ("K2O", 1.0, 1.0, 11.0),
    "K9":    ("K2O", 1.0, 1.0, 9.0),
    "0.66K": ("K2O", 1.0, 1.5, 11.0),
    "N11":   ("Na2O", 1.0, 1.0, 11.0),
    "KN11":  ("0.5K2O+0.5Na2O", 1.0, 1.0, 11.0),
}

#: Figure 2, p30 — apparent diffusion coefficient of Cs, x1e-13 m2/s, LOG axis.
#: Read from the bar chart, so precision is roughly +/-10%.
KURUMISAWA_D_INGRESS_E13_M2_S = {
    #  sample: (1 week, 4 week)
    "K11":   (47.0, 40.0),
    "K9":    (7.0, 4.8),
    "0.66K": (44.0, 40.0),
    "N11":   (8.3, 4.7),
    "KN11":  (19.0, 20.0),
}


def _from_kurumisawa2021() -> pd.DataFrame:
    from .immobilisation_schema import M2_S_TO_CM2_S

    rows = []
    for sample, (d1, d4) in KURUMISAWA_D_INGRESS_E13_M2_S.items():
        m2o, m2o_al, sio2_al, h2o_al = KURUMISAWA_ACTIVATOR[sample]
        na = "Na" in m2o and "K" not in m2o
        for weeks, d_e13 in (("1w", d1), ("4w", d4)):
            rows.append(
                {
                    "sample_id": f"kurumisawa2021_{sample}_{weeks}",
                    "matrix_name": sample,
                    "matrix_class": (MatrixClass.NA_GEOPOLYMER if na
                                     else MatrixClass.K_GEOPOLYMER).value,
                    "nuclide": "Cs",
                    "loading_wt_pct": None,      # not doped — Cs enters from solution
                    "retention_value": d_e13 * 1e-13 * M2_S_TO_CM2_S,
                    "retention_type": RetentionType.INGRESS_DIFFUSIVITY.value,
                    "censored": Censoring.NONE.value,
                    "leachant": "CsCl_solution_immersion",
                    "duration_days": 7.0 if weeks == "1w" else 28.0,
                    "interval_label": weeks,
                    "precursor": "metakaolin",
                    "activator": m2o,
                    "provenance_doi": KURUMISAWA_DOI,
                    "source_label": "kurumisawa2021",
                    "leach_state": "n/a",
                    "from_figure": True,          # log-axis bar chart, ~+/-10%
                    "value_repeated": False,
                }
            )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Jang, Park & Lee, J. Hazard. Mater. 318 (2016) 339-346
# doi:10.1016/j.jhazmat.2016.07.003
#
# Surfaced by F25 (cited in the Mukiza review) and found ALREADY ON DISK, registered
# but never mined. A doped-waste-form leach study: Cs+ or Sr2+ dissolved into the
# activator at 10 g/L, then semi-dynamic leaching -> EFFECTIVE (leaching-OUT)
# diffusivity, the same quantity as Kim and Nevin.
#
# Seven specimens: F1/F2/F3 pure fly-ash geopolymers, S1/S3/S5 fly-ash+slag blends,
# PC a Portland-cement baseline. Both Cs AND Sr measured for every specimen.
# ---------------------------------------------------------------------------
JANG_DOI = "10.1016/j.jhazmat.2016.07.003"

#: Table 7, p28 - leachability indexes, published directly. Higher = better.
#: Verified: LI = mean over intervals of -log10(De_n), NOT -log10(mean De).
#: F1 Cs check: mean(-log10 De_n) = 10.02 ~ published 10.0; -log10(mean De) = 9.46 would be wrong.
JANG_LI = {
    #  specimen: (Cs LI, Sr LI)
    "F1": (10.0, 14.1), "F2": (10.1, 14.1), "F3": (10.2, 14.4),
    "S1": (7.1, 11.5),  "S3": (8.0, 12.7),  "S5": (8.0, 12.1),
    "PC": (7.0, 9.8),
}

#: Table 5, p28 - pore structure. (porosity %, capillary pore vol mL/g, critical pore dia nm)
JANG_PORE = {
    "F1": (29.9, 0.0309, 62),   "F2": (33.9, 0.0971, 151), "F3": (31.9, 0.0208, 50),
    "S1": (39.7, 0.2537, 1567), "S3": (31.9, 0.0739, 349), "S5": (25.9, 0.0444, 227),
    "PC": (28.3, 0.1115, 284),
}

JANG_MATRIX = {
    "F1": ("FA1 geopolymer", MatrixClass.FLY_ASH_GEOPOLYMER),
    "F2": ("FA2 geopolymer", MatrixClass.FLY_ASH_GEOPOLYMER),
    "F3": ("FA3 geopolymer", MatrixClass.FLY_ASH_GEOPOLYMER),
    "S1": ("FA3+BFS 90:10", MatrixClass.SLAG_BLEND),
    "S3": ("FA3+BFS 70:30", MatrixClass.SLAG_BLEND),
    "S5": ("FA3+BFS 50:50", MatrixClass.SLAG_BLEND),
    "PC": ("Portland cement", MatrixClass.PORTLAND_CEMENT),
}

#: Precursor-bulk Si/Al (Table 1 oxides x Table 2 blend). NOT stored as si_al: it
#: omits the sodium-silicate activator Si and so is NOT the gel Si/Al, and the F and
#: S series use different silicate loadings (0.25 vs 0.17), so it is not even
#: comparable across specimens. Recorded here for provenance only.
JANG_PRECURSOR_SI_AL_BULK = {
    "F1": 1.549, "F2": 1.915, "F3": 1.986, "S1": 2.009, "S3": 2.060, "S5": 2.125,
}


def _from_jang2016() -> pd.DataFrame:
    rows = []
    for spec, (cs_li, sr_li) in JANG_LI.items():
        name, mclass = JANG_MATRIX[spec]
        por, cpv, cpd = JANG_PORE[spec]
        for nuclide, li in (("Cs", cs_li), ("Sr", sr_li)):
            rows.append(
                {
                    "sample_id": f"jang2016_{spec}_{nuclide}",
                    "matrix_name": name,
                    "matrix_class": mclass.value,
                    "nuclide": nuclide,
                    "loading_wt_pct": None,  # doped at 10 g/L in the LIQUID, not a solid wt%
                    "retention_value": li,
                    "retention_type": RetentionType.LEACHABILITY_INDEX.value,
                    "censored": Censoring.NONE.value,
                    "leachant": "deionised_water",
                    "duration_days": 90.0,
                    "porosity_pct": por,
                    "capillary_pore_volume_mL_g": cpv,
                    "critical_pore_diameter_nm": cpd,
                    "precursor": "fly_ash" if spec.startswith("F") else (
                        "fly_ash_slag" if spec.startswith("S") else "portland_cement"),
                    "activator": None if spec == "PC" else "NaOH_sodium_silicate",
                    "provenance_doi": JANG_DOI,
                    "source_label": "jang2016",
                    "leach_state": "n/a",
                    "from_figure": False,
                    "value_repeated": False,
                }
            )
    return pd.DataFrame(rows)


ADAPTERS = {
    "kim2026": _from_kim2026,
    "nevin2026": _from_nevin2026,
    "kurumisawa2021": _from_kurumisawa2021,
    "jang2016": _from_jang2016,
}


def build() -> pd.DataFrame:
    frames = []
    for label, fn in ADAPTERS.items():
        df = fn()
        if not df.empty:
            frames.append(conform(df))
    if not frames:
        return conform(pd.DataFrame())
    return pd.concat(frames, ignore_index=True)


def main() -> None:  # pragma: no cover - CLI convenience
    from .immobilisation_schema import pooling_warning, validate

    df = build()
    print(f"Pool B: {len(df)} rows / {df['source_label'].nunique()} sources")
    print(df.groupby(["source_label", "nuclide"]).size().to_string())
    print("\nvalidation:")
    rep = validate(df)
    print(rep.to_string(index=False) if len(rep) else "  clean")
    print("\npooling warnings:")
    for w in pooling_warning(df):
        print(f"  ! {w}")


if __name__ == "__main__":  # pragma: no cover
    main()


# ---------------------------------------------------------------------------
# Stanojevic et al., Constr. Build. Mater. 500 (2025) 144217
# doi:10.1016/j.conbuildmat.2025.144217  (Komljenovic/Provis group)
# Batch-4. Fly-ash geopolymer, Cs doped at 2% and 5%, semi-dynamic leach.
#
# Lmean read from Fig. 6b annotations (90-day mean; 5-day values noted). A framework
# system (fly ash, not slag): 29Si shows Q4(mAl); higher Cs loading introduces less-
# crosslinked Q1,2 units (Cs slows condensation). Cumulative Cs leached >70% after 5
# days (71.0% / 76.5%) - passes the LI criterion but Cs remains mobile, consistent
# with the universal Cs<Sr retention pattern.
# ---------------------------------------------------------------------------
STANOJEVIC_DOI = "10.1016/j.conbuildmat.2025.144217"


def _from_stanojevic2025() -> pd.DataFrame:
    # (sample, Cs loading wt%, Lmean 90-day, Lmean 5-day, cumulative Cs leached % @5d)
    ROWS = [
        ("G-FA-2%Cs", 2.0, 10.3, 9.7, 71.0),
        ("G-FA-5%Cs", 5.0, 9.9, 9.3, 76.5),
    ]
    rows = []
    for sample, load, li90, _li5, _leached in ROWS:
        rows.append(
            {
                "sample_id": f"stanojevic2025_{sample}",
                "matrix_name": sample,
                "matrix_class": MatrixClass.FLY_ASH_GEOPOLYMER.value,
                "nuclide": "Cs",
                "loading_wt_pct": load,
                "retention_value": li90,   # 90-day mean LI (matches Jang's basis)
                "retention_type": RetentionType.LEACHABILITY_INDEX.value,
                "censored": Censoring.NONE.value,
                "leachant": "deionised_water",
                "duration_days": 90.0,
                "precursor": "fly_ash",
                "activator": "sodium_silicate",
                "provenance_doi": STANOJEVIC_DOI,
                "source_label": "stanojevic2025",
                "leach_state": "n/a",
                "from_figure": True,   # Lmean from Fig. 6b annotation
                "value_repeated": False,
            }
        )
    return pd.DataFrame(rows)


ADAPTERS["stanojevic2025"] = _from_stanojevic2025


# ---------------------------------------------------------------------------
# Komljenovic et al., J. Hazard. Mater. 388 (2020) 121765  (Q9 acquisition)
# doi:10.1016/j.jhazmat.2019.121765
# Batch-4. Alkali-activated blast-furnace slag (AABFS), Cs doped 2%/5%.
#
# CONFIRMS F19. AABFS is a C-A-S-H (calcium aluminosilicate hydrate) binder: its
# 29Si NMR shows only low-connectivity Qn(mAl) sites (n=1-3, m=0-1) - NO framework
# Q4(mAl) - so the descriptor here is C-A-S-H chain length / AlIV/Si, not ARI.
# Its Cs Lmean (7.8, 7.0; Fig. 5b) is markedly LOWER than the fly-ash/metakaolin
# FRAMEWORK geopolymers (Stanojevic 10.3/9.9; Jang FA ~10; Nevin MK Cs 13.2/13.3):
# the calcium-silicate gel immobilises Cs less well than the aluminosilicate
# framework - quantitative support for F19.
# ---------------------------------------------------------------------------
KOMLJENOVIC_DOI = "10.1016/j.jhazmat.2019.121765"


def _from_komljenovic2020() -> pd.DataFrame:
    # (sample, Cs loading wt%, Lmean; Fig. 5b annotations, text-confirmed 7.8 / 7.0)
    ROWS = [("AABFS-2%Cs", 2.0, 7.8), ("AABFS-5%Cs", 5.0, 7.0)]
    rows = []
    for sample, load, li in ROWS:
        rows.append(
            {
                "sample_id": f"komljenovic2020_{sample}",
                "matrix_name": sample,
                "matrix_class": MatrixClass.SLAG_BLEND.value,  # pure AABFS = C-A-S-H
                "nuclide": "Cs",
                "loading_wt_pct": load,
                "retention_value": li,
                "retention_type": RetentionType.LEACHABILITY_INDEX.value,
                "censored": Censoring.NONE.value,
                "leachant": "deionised_water",
                "duration_days": 5.0,   # ANSI/ANS-16.1 5-day mean (nmax=7)
                "precursor": "blast_furnace_slag",
                "activator": "sodium_silicate",
                "provenance_doi": KOMLJENOVIC_DOI,
                "source_label": "komljenovic2020",
                "leach_state": "n/a",
                "from_figure": True,   # Lmean from Fig. 5b annotation (text-confirmed)
                "value_repeated": False,
            }
        )
    return pd.DataFrame(rows)


ADAPTERS["komljenovic2020"] = _from_komljenovic2020


# ---------------------------------------------------------------------------
# Arbel-Haddad, Harnik, Schlosser & Goldbourt,
# "Cesium immobilization in metakaolin-based geopolymers elucidated by 133Cs
#  solid state NMR spectroscopy" (J. Nucl. Mater., ~2022).
# Batch-4.  DOI NOT verifiable from this author-accepted manuscript: every DOI in
# the file is a bibliography reference. Provenance recorded as a flagged citation
# rather than a guessed DOI (standing no-fabrication rule) - see F31.
#
# Metakaolin geopolymer, Si/Al = 1 (very Al-rich framework), Na activator with Cs
# substituting for Na at 2.5-100%. Target = CUMULATIVE fraction of Cs leached
# (Table 4, 48 h two-step). Lower is better. Introduces the CLF retention type.
# Note the non-monotonic trend: leaching is lowest (best) at 5-25% Cs (0.004-0.008),
# higher at 2.5% (0.044) and rising steeply at high loading (0.139 at 100%).
# ---------------------------------------------------------------------------
ARBELHADDAD_PROV = "Arbel-Haddad 2022 J.Nucl.Mater 133Cs MK-geopolymer (DOI-unverified-AAM)"


def _from_arbelhaddad2022() -> pd.DataFrame:
    # (Cs loading %, cumulative Cs fraction leached at 48 h; Table 4)
    ROWS = [
        (2.5, 0.044), (5.0, 0.008), (7.5, 0.004),
        (25.0, 0.006), (50.0, 0.056), (100.0, 0.139),
    ]
    rows = []
    for load, clf in ROWS:
        rows.append(
            {
                "sample_id": f"arbelhaddad2022_{load:g}pctCs",
                "matrix_name": f"MK-GP {load:g}%Cs",
                "matrix_class": MatrixClass.NA_GEOPOLYMER.value,
                "nuclide": "Cs",
                "loading_wt_pct": None,   # Cs% here is a molar substitution of Na, not a wt%
                "retention_value": clf,
                "retention_type": RetentionType.CUMULATIVE_LEACHED_FRACTION.value,
                "censored": Censoring.NONE.value,
                "leachant": "deionised_water",
                "duration_days": 2.0,     # two 24 h steps (46-48 h)
                "si_al": 1.0,
                "precursor": "metakaolin",
                "activator": "NaOH_CsOH",
                "provenance_doi": ARBELHADDAD_PROV,
                "source_label": "arbelhaddad2022",
                "leach_state": "n/a",
                "from_figure": False,     # Table 4
                "value_repeated": False,
            }
        )
    return pd.DataFrame(rows)


ADAPTERS["arbelhaddad2022"] = _from_arbelhaddad2022


# ---------------------------------------------------------------------------
# Frederickx, Mukiza, Phung et al., Sustainability 17 (2025) 1756
# doi:10.3390/su17041756   (SCK CEN / Belgian nuclear)
# Batch-5. A real Cs/Sr-rich nitrate waste immobilised in a metakaolin (N-A-S-H)
# alkali-activated matrix, at two waste loadings.
#
# LEACHANT CAVEAT: Table 5 gives ACCELERATED-test LIs in NH4NO3 (Cs 6.9/7.0,
# Sr 7.0/6.7) - a harsh medium built for Ca-cement that over-attacks divalent
# cations, so it UNDERSTATES Sr immobilisation and flattens the Cs/Sr difference.
# Stored with leachant="NH4NO3_accelerated" so these are never pooled with the
# deionised-water LIs of the other Pool B sources. The paper's DEIONISED-water
# equivalents (extrapolated from Fig 5: Cs 9.6, Sr 12.5) show Sr >> Cs as usual,
# but are derived/estimated - noted in F35, not ingested.
# ---------------------------------------------------------------------------
FREDERICKX_DOI = "10.3390/su17041756"


def _from_frederickx2025() -> pd.DataFrame:
    # Table 5: accelerated NH4NO3 leachability index. (loading, nuclide, LI)
    ROWS = [
        ("low", "Cs", 6.9), ("low", "Sr", 7.0),
        ("high", "Cs", 7.0), ("high", "Sr", 6.7),
    ]
    rows = []
    for loading, nuclide, li in ROWS:
        rows.append(
            {
                "sample_id": f"frederickx2025_{loading}_{nuclide}",
                "matrix_name": f"MK N-A-S-H waste form ({loading} loading)",
                "matrix_class": MatrixClass.NA_GEOPOLYMER.value,   # EDX: N-A-S-H gel
                "nuclide": nuclide,
                "loading_wt_pct": None,   # categorical low/high; wt% not carried
                "retention_value": li,
                "retention_type": RetentionType.LEACHABILITY_INDEX.value,
                "censored": Censoring.NONE.value,
                "leachant": "NH4NO3_accelerated",   # NOT deionised water - see caveat
                "precursor": "metakaolin_blast_furnace_slag",
                "activator": "sodium_silicate",
                "provenance_doi": FREDERICKX_DOI,
                "source_label": "frederickx2025",
                "leach_state": "n/a",
                "from_figure": False,   # Table 5
                "value_repeated": False,
            }
        )
    return pd.DataFrame(rows)


ADAPTERS["frederickx2025"] = _from_frederickx2025
