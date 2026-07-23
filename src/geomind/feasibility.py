"""Feasibility Controller — GEOMIND's expert-knowledge block.

The paper embeds chemical constraints (silica/alumina, silica/alkali, solid/liquid)
so the generator cannot propose unmanufacturable mixtures; without it only 55.6 %
of generated samples were synthesisable (paper Table 5).

## Status of the thresholds  (gap G3 — still OPEN)

| Rule | Source | Trust |
|---|---|---|
| Viscosity class boundaries | paper §3.2.1, stated explicitly | ✅ verified |
| Chemical feasibility domain | refs 34-35 (not reproduced in the paper) | ❌ **unknown** |

`data/raw/.../Feasibility_Ranges` claims to supply the chemical domain and is labelled
`Source: GEOMIND (2026)`. **It is not usable**, and is deliberately NOT read here:

* applied to the paper's own published samples it rejects **7 of 9 feasible** mixtures
  and accepts the **1 infeasible** one — anti-correlated with ground truth;
* its `Si/Al 1.5-3.0` and `Porosity 15-65` values are verbatim constants from the
  project's own retired heuristic tool (git tag `v1.0.0`, `geopolymer_design.py`),
  not from the paper.

Until G3 is closed we therefore use a **provisional empirical envelope** fitted to the
nine feasible published samples, and we say so loudly. A real controller needs either
the paper's 14 infeasible samples (in the confidential dataset) or refs 34-35.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .chemistry import compute_molar_features

# --- viscosity classes: paper §3.2.1, "low < 2 Pa s", "high > 100 Pa s" ----
VISCOSITY_LOW_MAX = 2.0
VISCOSITY_HIGH_MIN = 100.0
#: full observed range in the paper's database
VISCOSITY_RANGE = (0.2, 1314.0)

#: sentinel written into every property field of an infeasible mixture (paper §3.1)
INFEASIBLE = -1.0


class ViscosityClass(str, Enum):
    LOW = "low"       # < 2 Pa s   -> projectable
    MEDIUM = "medium"  # 2-100 Pa s
    HIGH = "high"      # > 100 Pa s


def classify_viscosity(value: float) -> ViscosityClass:
    """Bucket a viscosity in Pa*s. Verified against the paper's stated boundaries."""
    if value < VISCOSITY_LOW_MAX:
        return ViscosityClass.LOW
    if value > VISCOSITY_HIGH_MIN:
        return ViscosityClass.HIGH
    return ViscosityClass.MEDIUM


# --- provisional chemical envelope (G3) -----------------------------------
# Fitted to the 9 feasible samples in the published subset, widened by 10 % to
# avoid over-fitting to n=9. THIS IS NOT THE PAPER'S DOMAIN.
PROVISIONAL_ENVELOPE: dict[str, tuple[float, float]] = {
    "si_al": (1.18, 2.39),
    "si_m_sol": (0.34, 0.96),
    "solid_liquid": (0.53, 1.65),
}


@dataclass(frozen=True)
class FeasibilityVerdict:
    """Outcome of a feasibility check."""

    feasible: bool
    violations: tuple[str, ...]
    si_al: float
    si_m_sol: float
    solid_liquid: float
    provisional: bool = True  # True while G3 is open

    def __bool__(self) -> bool:
        return self.feasible


def check_feasibility(
    mass_fractions: dict[str, float],
    envelope: dict[str, tuple[float, float]] | None = None,
) -> FeasibilityVerdict:
    """Screen a candidate mixture against the chemical envelope.

    Args:
        mass_fractions: precursor name -> mass fraction.
        envelope: override the provisional envelope once G3 is closed.

    Returns:
        A verdict whose ``provisional`` flag is True while the true domain is unknown.

    Warning:
        With the provisional envelope this is a **plausibility screen, not the
        paper's feasibility controller**. Do not report ablation results against it
        as though they reproduced the paper's 55.6 % figure.
    """
    env = envelope or PROVISIONAL_ENVELOPE
    f = compute_molar_features(mass_fractions)
    values = {"si_al": f.si_al, "si_m_sol": f.si_m_sol, "solid_liquid": f.solid_liquid}

    violations = []
    for key, (lo, hi) in env.items():
        v = values[key]
        if v != v:  # NaN -> degenerate mixture (e.g. no activator)
            violations.append(f"{key}=undefined")
        elif not lo <= v <= hi:
            violations.append(f"{key}={v:.3f} outside [{lo}, {hi}]")

    return FeasibilityVerdict(
        feasible=not violations,
        violations=tuple(violations),
        si_al=f.si_al,
        si_m_sol=f.si_m_sol,
        solid_liquid=f.solid_liquid,
        provisional=envelope is None,
    )


def apply_sentinel(properties: dict[str, float], verdict: FeasibilityVerdict) -> dict[str, float]:
    """Overwrite every property with -1 when the mixture is infeasible.

    Mirrors the paper: the Simulator's terminal block returns negative property
    values for mixtures outside the geopolymer domain.
    """
    if verdict.feasible:
        return dict(properties)
    return {k: INFEASIBLE for k in properties}
