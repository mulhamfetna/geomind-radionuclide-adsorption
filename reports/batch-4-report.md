# Batch-4 extraction report — 11 new papers

**Completed:** 2026-07-21 · **Findings:** F27–F32 · **Pool A:** 133 → **137** rows / 13 sources ·
**Pool B:** 40 → **50** rows / 7 sources · **Tests:** 122 → **125**

Eleven papers landed in `papers/references/`. They were triaged by content (not filename), then
extracted inline and verified against source. **This batch directly attacked the F20/F22 wall** —
the finding that framework-Al data is almost never reported with a Cs/Sr target — and produced the
strongest single result of the project so far.

---

## The headline: a within-sample causal test (F27)

Varon's **leaching companion paper** (Open Ceramics 25, 2026, doi:10.1016/j.oceram.2025.100895)
is the same 7 samples as our existing Varon source, re-measured **before and after 96 h of water
leaching**. That turns a cross-sample correlation into a **within-sample causal test**:

- **[Al^IV] concentration governs Sr K_D:** corr = **+0.946** (n=7), **+0.986** excluding the
  barely-reacted outlier — beating Al^IV % (+0.80), ARI (+0.77), and crushing BET (+0.19) and
  Si/Al (−0.84).
- **Leaching strips framework Al, and sorption falls with it:** corr(Δ[Al^IV], ΔK_D) = **+0.938**.
  K-0.5-16 lost the most framework Al (1.39 mmol/g) *and* the most K_D (2750 mL/g); K-1.5-16 lost
  almost neither. The same sample loses capacity *as* it loses exchange sites.

This is the first within-sample (not merely cross-sample) evidence that tetrahedral **Al^IV *is*
the Sr exchange site**, not just a correlate — and that **absolute exchange-site density
([Al^IV] mmol/g) beats the per-Si fraction** (Al^IV %, ARI).

---

## What each paper contributed

| Paper | Verdict | Into pool |
|---|---|---|
| **Varon leached** (Open Ceramics) | ⭐ **F27** — the causal test | Pool A **+7** post-leach Sr K_D rows |
| **Stanojević 2025** (F28) | fly-ash GP; Cs passes LI (~10) yet >70 % leaches | Pool B **+2** Cs LI |
| **Komljenović 2020** (F29, **Q9 closed**) | slag = Ca C-A-S-H; **confirms F19**; Cs LI 7.8/7.0 < framework | Pool B **+2** Cs LI |
| **Qian 2001** (F30, **Q10 closed**) | scanned; read visually; Al-rich slag, more Al → higher R_d | Pool A **+4** Cs/Sr K_d |
| **Arbel-Haddad 2022** (F31) | MK framework, Cs cumulative-leached fractions | Pool B **+6** CLF |
| **O'Donoghue 2026** (F32) | **structure-only, no target** — assessed, not ingested | — |
| Interplay… (Varon) | **duplicate** of varon2025 | skipped |
| Mukiza review | **duplicate** (already F25) | skipped |
| …mmc1.docx | supplement only, main paper absent | noted |

---

## Two results worth carrying into the paper

**1. Cs leachability stratifies cleanly by binder chemistry** — the immobilisation-side echo of the
adsorption-side framework-Al finding:

| Binder | Cs L / LI | source |
|---|---|---|
| Metakaolin framework | ~13.2–13.3 | Nevin |
| Fly-ash framework | ~10 | Stanojević, Jang |
| **Ca-rich slag (C-A-S-H)** | **~7.0–7.8** | **Komljenović** |

The aluminosilicate framework holds Cs better than the calcium-silicate gel — F19 seen through the
leaching lens.

**2. Adding aluminosilicate raises uptake even in a Ca system** (Qian): M-AAS (slag + metakaolin +
clay) beats plain AAS R_d by 67–88 % for both Cs and Sr. More Al → more exchange capacity, the same
mechanism as F27, from the Ca side.

---

## Data-integrity notes recorded (not silently fixed)

- **Qian R_d unit** — the paper labels R_d "mol/g", but the magnitudes (10³–10⁴) are consistent with
  mL/g. Stored in `kd_mL_g` with the caveat flagged, not silently converted.
- **Arbel-Haddad DOI** — none present in the author-accepted manuscript (every DOI in the file is a
  bibliography reference). Provenance recorded as a flagged citation string, **not a guessed DOI**.
- **Two duplicates and a lone supplement** identified and kept out of the pools.

---

## Effect on the project's central question

F20/F22 held that both pools were descriptor-starved because framework-Al and a Cs/Sr target rarely
co-occur. **This batch improves that materially:** the descriptor evidence is no longer a single
cross-sample correlation but includes a within-sample causal test (F27), the descriptor is now
ranked ([Al^IV] conc. > Al^IV % > ARI), and the immobilisation side independently reproduces the
pattern by binder chemistry. The still-open bridge is **Geddes 2025 (Q8)** — mechanism/NMR *and*
binding capacity in one paper — which remains the highest-value acquisition.
