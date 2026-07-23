"""Molar chemistry of a geopolymer mixture, derived from precursor mass fractions.

This is the quantitative core of GEOMIND's expert-knowledge block: the paper's
Feasibility Controller works on molar ratios computed *from* the precursor mass
fractions, so this layer must be right before any model is trained on top of it.

Written independently from `docs/paper-analysis/reproduction-spec.md`. The reference
implementation (github.com/Geopolymer-AI/GEOMIND) carries **no license**, so no code
from it is used here; only the paper's *published numbers* serve as an oracle
(see tests/test_chemistry.py).

Composition data: paper Table 1.
"""
from __future__ import annotations

from dataclasses import dataclass

# --- molar masses (g/mol) -------------------------------------------------
M_SIO2 = 60.084
M_AL2O3 = 101.961
M_K2O = 94.196
M_NA2O = 61.979
M_KOH = 56.106
M_NAOH = 39.997


@dataclass(frozen=True)
class Precursor:
    """A raw material and its oxide composition in wt %."""

    name: str
    kind: str  # "metakaolin" | "silicate" | "hydroxide"
    sio2: float = 0.0
    al2o3: float = 0.0
    h2o: float = 0.0
    m2o: float = 0.0  # alkali oxide, K2O or Na2O per `alkali`
    purity: float = 0.0  # hydroxides only
    alkali: str | None = None  # "K" | "Na"


# Paper Table 1. The five metakaolins, four silicate solutions (S1/S3/S3' are
# potassium-based, SNa is sodium-based) and two alkali hydroxides.
PRECURSORS: dict[str, Precursor] = {
    "M1": Precursor("M1", "metakaolin", sio2=55.0, al2o3=40.0),
    "M2": Precursor("M2", "metakaolin", sio2=54.0, al2o3=39.0),
    "M3": Precursor("M3", "metakaolin", sio2=54.0, al2o3=46.0),
    "M4": Precursor("M4", "metakaolin", sio2=52.4, al2o3=45.3),
    "M5": Precursor("M5", "metakaolin", sio2=59.9, al2o3=35.3),
    "S1": Precursor("S1", "silicate", sio2=14.3, h2o=79.3, m2o=6.4, alkali="K"),
    "S3": Precursor("S3", "silicate", sio2=18.7, h2o=59.4, m2o=21.9, alkali="K"),
    "S3'": Precursor("S3'", "silicate", sio2=23.4, h2o=54.9, m2o=21.7, alkali="K"),
    "SNa": Precursor("SNa", "silicate", sio2=27.5, h2o=64.2, m2o=8.3, alkali="Na"),
    "KOH": Precursor("KOH", "hydroxide", purity=85.2, alkali="K"),
    "NaOH": Precursor("NaOH", "hydroxide", purity=97.0, alkali="Na"),
}

#: canonical ordering of the 11 precursor features
PRECURSOR_ORDER: list[str] = list(PRECURSORS)


@dataclass(frozen=True)
class MolarFeatures:
    """Molar quantities and the three ratios that drive the feasibility check.

    Absolute mole counts are on a 100 mass-unit basis. The paper reports these
    columns under a different (unstated) normalisation, so only the **ratios**
    are directly comparable to the published values — see the module test.
    """

    n_si_met: float
    n_si_sol: float
    n_al: float
    n_m_sol: float
    n_m_moh: float
    n_si: float
    n_m: float
    si_al: float
    si_m_sol: float
    solid_liquid: float


def compute_molar_features(mass_fractions: dict[str, float]) -> MolarFeatures:
    """Convert precursor mass fractions into molar quantities and ratios.

    Args:
        mass_fractions: precursor name -> mass fraction. Values normally sum to
            1.0; any consistent scale works since the outputs of interest are ratios.

    Raises:
        KeyError: on an unknown precursor name.
    """
    unknown = set(mass_fractions) - set(PRECURSORS)
    if unknown:
        raise KeyError(f"unknown precursor(s): {sorted(unknown)}")

    basis = 100.0  # mass units; ratios are invariant to this choice
    n_si_met = n_si_sol = n_al = n_m_sol = n_m_moh = 0.0
    mass_solid = mass_liquid = 0.0

    for name, frac in mass_fractions.items():
        if not frac:
            continue
        p = PRECURSORS[name]
        mass = frac * basis

        if p.kind == "metakaolin":
            # metakaolin is the solid aluminosilicate source
            mass_solid += mass
            n_si_met += mass * p.sio2 / 100.0 / M_SIO2
            n_al += 2.0 * mass * p.al2o3 / 100.0 / M_AL2O3  # 2 Al per Al2O3

        elif p.kind == "silicate":
            # activator solutions count as the liquid phase
            mass_liquid += mass
            n_si_sol += mass * p.sio2 / 100.0 / M_SIO2
            m_oxide = M_K2O if p.alkali == "K" else M_NA2O
            n_m_sol += 2.0 * mass * p.m2o / 100.0 / m_oxide  # 2 M per M2O

        elif p.kind == "hydroxide":
            # hydroxides are dissolved into the activator -> liquid phase
            mass_liquid += mass
            m_hyd = M_KOH if p.alkali == "K" else M_NAOH
            n_m_moh += mass * p.purity / 100.0 / m_hyd

    n_si = n_si_met + n_si_sol
    n_m = n_m_sol + n_m_moh

    return MolarFeatures(
        n_si_met=n_si_met,
        n_si_sol=n_si_sol,
        n_al=n_al,
        n_m_sol=n_m_sol,
        n_m_moh=n_m_moh,
        n_si=n_si,
        n_m=n_m,
        # Si/Al: total silicon over total aluminium -> governs network type
        si_al=n_si / n_al if n_al else float("nan"),
        # Si/M_sol: *solution-derived* silicon over TOTAL alkali (verified
        # against the published samples; it is not n_si_sol / n_m_sol)
        si_m_sol=n_si_sol / n_m if n_m else float("nan"),
        # Solid/Liquid: metakaolin mass over activator mass (silicates + hydroxides)
        solid_liquid=mass_solid / mass_liquid if mass_liquid else float("nan"),
    )


def molar_ratios(mass_fractions: dict[str, float]) -> tuple[float, float, float]:
    """Convenience: just the three ratios the loss and feasibility block use."""
    f = compute_molar_features(mass_fractions)
    return f.si_al, f.si_m_sol, f.solid_liquid
