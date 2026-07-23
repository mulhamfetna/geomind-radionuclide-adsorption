"""Deconvolved 29Si MAS NMR Si environments -> Al-richness index (ARI).

Source: Hossain et al., *Materials & Design* **262** (2026) 115471, **Table 2**
("The different Si environments present in the AAMs/geopolymers"), page 6.
Transcribed by rendering the page and reading it directly (finding **F18**).

Why this module exists
----------------------
Framework aluminium -- not surface area -- is the descriptor that tracks cation
uptake (Varon: corr(Al^IV, K_d) = +0.95 vs corr(BET, K_d) = +0.19). Al^IV was
present in only **7 of 121** pooled rows, all from a single source and a single
adsorbate. Table 2 supplies the equivalent information for **12 further sorbents**
in a different material family and three different adsorbates.

The Al-richness index
---------------------
Each Si environment Q^n(mAl) has *m* aluminium atoms bonded to the central Si via
bridging oxygens. Weighting each environment's population by its *m* gives the
mean number of Al neighbours per Si::

    ARI  =  sum_m ( m * I_m ) / 100

which is the Engelhardt numerator -- i.e. it is proportional to framework Al in
tetrahedral coordination, without requiring 27Al NMR.

Caveats carried by the data itself, not editorial
-------------------------------------------------
* Q^1 carries no ``(mAl)`` label in the source table and is weighted **m = 0**.
  This is a *lower bound* for that column: an unlabelled Q^1 may still carry Al.
  Only rows 5-12 (Ca-containing) have appreciable Q^1, so the Ca-free series --
  where the descriptor is tested -- is unaffected.
* ``Si10Al1Na1Ca11`` sums to 99.0 %, not 100.0. The published row has a blank
  Q^2(1Al) cell where the other rows carry an explicit dash. Reproduced verbatim;
  :func:`validate` reports it rather than silently normalising it.
"""

from __future__ import annotations

import pandas as pd

DOI = "10.1016/j.matdes.2026.115471"

#: Number of Al neighbours *m* implied by each Q^n(mAl) column label.
M_WEIGHT: dict[str, int] = {
    "Q0": 0,
    "Q1": 0,  # unlabelled in the source table -- see module docstring
    "Q2_1Al": 1,
    "Q2_0Al": 0,
    "Q4_4Al": 4,
    "Q3_1Al": 1,
    "Q4_3Al": 3,
    "Q3Q4_2Al": 2,
    "Q3Q4_1Al": 1,
    "Q4_0Al": 0,
}

#: Table 2, verbatim. ``None`` is a dash (or blank) in the published table.
#: Column order matches :data:`M_WEIGHT`.
TABLE2: dict[str, dict[str, float | None]] = {
    # --- Ca-free series -------------------------------------------------
    "Si2Al1Na1":      {"Q4_4Al": 45.1, "Q3Q4_2Al": 26.6, "Q4_0Al": 28.3},
    "Si4Al1Na1":      {"Q4_4Al": 24.9, "Q3Q4_1Al": 45.0, "Q4_0Al": 30.1},
    "Si10Al1Na1":     {"Q3Q4_1Al": 50.0, "Q4_0Al": 50.0},
    "Si20Al1Na1":     {"Q3Q4_1Al": 54.1, "Q4_0Al": 45.9},
    # --- Ca-containing, Si/Al varied -------------------------------------
    "Si2Al1Na1Ca3":   {"Q0": 27.5, "Q1": 30.2, "Q2_1Al": 21.1, "Q2_0Al": 21.2},
    "Si4Al1Na1Ca5":   {"Q0": 10.5, "Q1": 29.2, "Q2_1Al": 32.1, "Q2_0Al": 23.7,
                       "Q3_1Al": 4.5},
    "Si10Al1Na1Ca11": {"Q0": 9.9, "Q1": 59.6, "Q3_1Al": 29.5},
    "Si20Al1Na1Ca21": {"Q0": 11.8, "Q1": 15.8, "Q2_1Al": 41.6, "Q3_1Al": 10.6,
                       "Q3Q4_1Al": 20.2},
    # --- Ca-containing, Ca varied at fixed Si/Al = 4 ----------------------
    "Si4Al1Na1Ca1":   {"Q0": 0.6, "Q2_1Al": 7.4, "Q2_0Al": 22.5, "Q4_3Al": 22.0,
                       "Q3Q4_2Al": 7.4, "Q3Q4_1Al": 35.7, "Q4_0Al": 4.4},
    "Si4Al1Na1Ca2":   {"Q0": 0.3, "Q2_1Al": 21.5, "Q3_1Al": 33.80,
                       "Q3Q4_2Al": 41.0, "Q4_0Al": 3.4},
    "Si4Al1Na1Ca3":   {"Q2_1Al": 26.6, "Q2_0Al": 45.7, "Q3_1Al": 27.7},
    "Si4Al1Na1Ca4":   {"Q0": 11.3, "Q2_1Al": 38.7, "Q2_0Al": 19.7, "Q3_1Al": 30.3},
}

#: Table 2 sample IDs -> ``sorbent_name`` as it appears in the merged pool.
#: The workbook spells the Ca-containing samples with spaces.
POOL_NAME: dict[str, str] = {
    "Si2Al1Na1": "Si2Al1Na1",
    "Si4Al1Na1": "Si4Al1Na1",
    "Si10Al1Na1": "Si10 Al1 Na1",
    "Si20Al1Na1": "Si20 Al1 Na1",
    "Si2Al1Na1Ca3": "Si2 Al1 Na1 Ca3",
    "Si4Al1Na1Ca5": "Si4 Al1 Na1 Ca5",
    "Si10Al1Na1Ca11": "Si10 Al1 Na1 Ca11",
    "Si20Al1Na1Ca21": "Si20 Al1 Na1 Ca21",
    "Si4Al1Na1Ca1": "Si4 Al1 Na1 Ca1",
    "Si4Al1Na1Ca2": "Si4 Al1 Na1 Ca2",
    "Si4Al1Na1Ca3": "Si4 Al1 Na1 Ca3",
    "Si4Al1Na1Ca4": "Si4 Al1 Na1 Ca4",
}

#: The one row whose published populations do not sum to 100 %.
KNOWN_INCOMPLETE = {"Si10Al1Na1Ca11": 99.0}


def ari(sample: str) -> float:
    """Al-richness index: mean number of Al neighbours per Si."""
    env = TABLE2[sample]
    return sum(M_WEIGHT[col] * pct for col, pct in env.items()) / 100.0


def q4_fraction(sample: str) -> float:
    """Fraction of Si in fully-condensed Q^4 environments (%)."""
    env = TABLE2[sample]
    return sum(pct for col, pct in env.items() if col.startswith("Q4"))


def validate() -> list[str]:
    """Integrity checks on the transcription. Empty list == clean."""
    problems: list[str] = []
    for sample, env in TABLE2.items():
        for col in env:
            if col not in M_WEIGHT:
                problems.append(f"{sample}: unknown environment column {col!r}")
        total = sum(env.values())
        expected = KNOWN_INCOMPLETE.get(sample, 100.0)
        if abs(total - expected) > 0.05:
            problems.append(f"{sample}: populations sum to {total:.1f}%, expected {expected}")
        if sample not in POOL_NAME:
            problems.append(f"{sample}: no pool sorbent_name mapping")
    return problems


def build() -> pd.DataFrame:
    """One row per NMR-characterised sorbent, keyed on the pool's sorbent_name."""
    rows = [
        {
            "sorbent_name": POOL_NAME[s],
            "nmr_sample_id": s,
            "ari": ari(s),
            "q4_pct": q4_fraction(s),
            "ari_source_doi": DOI,
        }
        for s in TABLE2
    ]
    return pd.DataFrame(rows)


def attach(pool: pd.DataFrame) -> pd.DataFrame:
    """Left-join ARI onto a merged adsorption pool. Non-Oulu rows get NaN."""
    return pool.merge(build(), on="sorbent_name", how="left")
