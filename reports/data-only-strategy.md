# Data-only strategy — what to do when there is no laboratory

**Prepared:** 2026-07-24 · **Constraint:** no access to materials or instruments; 100 % literature-based
**Status:** plan, with the applicability test already run

---

## 1. The question

n = 7 is the ceiling on the forward model, and F43 proved it is structural. With no laboratory,
the campaign proposed in `docs/lab-campaign-protocol.md` is not executable. **So what remains?**

This document reports what was checked, what is closed, and the one reframing that **is**
applicable — tested, implemented and passing.

---

## 2. What was checked, and closed ❌

| Route | Result |
|---|---|
| **The Oulu raw dataset** (`data/external/`, 820 files, 23 ²⁹Si NMR sample folders, raw spectra for 12) | **Closed by F18.** The deconvolution is already published (Hossain Table 2) and transcribed into `nmr_ari.py`. Our own re-fit was *correctly rejected*: the authors use ten Si environments including Q³/Q² species; a five-Q⁴ model cannot represent them and scored R² = 0.998 while being structurally wrong. Re-deriving it would reintroduce a known error. |
| **Widening the Oulu series** | **Closed by F19.** Only **4 of 12** samples are Ca-free, and the descriptor is valid only there. |
| **The three papers from 22 Jul** | Already mined — Geddes (F34), Frederickx (F35), and the third is registered. Nothing unworked. |
| **Reframing to leach resistance** (route (b) of F20) | **Tested today, also caps at n=7.** In Pool B, ARI paired with a retention value is only **n = 4** (Nevin); the largest coherent single-source × nuclide × retention-type group is **n = 7** (Vandevenne). The reframe does not break the ceiling. |
| **Adding Ca as a covariate to rescue the Oulu 13** (suggested by F41, where Ca/(Si+Al) predicted Sr retention at r = +0.99) | **Tested today, fails.** Leave-one-out R²: ARI alone −0.041, Ca alone −0.397, ARI + Ca −0.122, with interaction −0.678. F19 stands: in Oulu's Ca-bearing samples nothing predicts. The Ca effect that is near-deterministic in Vandevenne's *designed* series does not transfer to Oulu's confounded one. |
| **Acquiring more papers to add rows** | The two best candidates found today (Vandevenne — already ingested; *Bull. Mater. Sci.* 49, DOI 10.1007/s12034-025-03487-2, NMR + leachability) are both **closed access**. Retrievable through University of Aleppo, but each adds ~n=5–7, not a new order of magnitude. |

---

## 3. The reframing that works ✅

**Change the unit of analysis from the sample to the study.**

F36 says raw values cannot be pooled across laboratories. F43 says no laboratory's series can be
enlarged. Together those look like a dead end — but they are actually a signpost to the standard
tool for exactly this situation: **random-effects meta-analysis of effect sizes.**

Instead of one regression over n rows, ask: *how many independent studies reproduce the same
direction?* Power then comes from **k**, the number of independent replications — and **k is
raisable from the literature, while n is not.**

### Implemented and tested: `geomind.meta`

```
$ python -m geomind.meta
```

| study | n | r | verdict |
|---|---|---|---|
| Framework Al^IV vs Sr K_D (Varon) | 7 | **+0.946** | supports |
| ARI vs NH₄⁺ uptake, Ca-free (Oulu) | 4 | **+0.932** | supports |
| Si/Al vs Cs retention (Vandevenne) | 7 | +0.617 | supports |
| Si/Al vs Sr retention (Vandevenne) | 7 | +0.376 | supports |

**k = 4 independent studies · 4 supporting, 0 opposing · weighted mean r̄ = +0.771 · 25 samples
represented · exact sign test p = 0.0625**

These are four *genuinely independent* replications: different laboratories, different adsorbates
(Sr, Cs, NH₄⁺), different material classes (metakaolin gel, Ca-Si-Al slag), and — critically —
**different regimes** (adsorption from solution *and* immobilisation leaching).

### The negative controls, which make the claim falsifiable

| control | n | r | reading |
|---|---|---|---|
| BET surface area (Varon) | 7 | +0.189 | the displaced hypothesis does not predict |
| ARI in **Ca-bearing** gels (Oulu) | 9 | −0.012 | outside the F19 precondition the descriptor is dead |
| ARI vs **dye** uptake (Oulu) | 4 | **−0.984** | a dye is not exchanged at Al^IV sites |

The dye control is the strongest specificity evidence in the project: framework Al is *inversely*
related to dye uptake. The descriptor tracks **cation exchange**, not adsorption in general —
exactly what the mechanism predicts, and exactly what an accidental correlation would not do.

---

## 4. What this changes about acquisition

This is the strategic payoff, and it inverts the previous goal.

| | old framing | new framing |
|---|---|---|
| Goal | more **rows** for one model | more **independent studies** |
| Unit | sample | study |
| Blocked by | F43 — no rows exist | not blocked |
| A new paper is useful if… | it reports Al^IV **and** Cs/Sr uptake (near-nonexistent, F20) | it has an **internal composition series** and any framework-Al proxy vs any uptake/retention measure |
| Power | LOO-CV R², stuck at n = 7 | sign test on k, **halving with each study** |

**Acquisition target profile (much broader than before):**

- a series of ≥ 3 compositions from **one** laboratory and protocol;
- **any** framework-aluminium proxy — Al^IV, ARI, Q⁴(mAl), or even Si/Al within a fixed class;
- **any** cation uptake or retention measure — K_D, capacity, LI, % leached;
- Cs, Sr **or** another exchangeable cation (NH₄⁺ already qualifies).

Papers previously rejected as "no Al^IV" may qualify under this profile. **Re-triaging the existing
corpus against it is the single cheapest next action** — it requires no acquisition at all.

**Power projection (exact sign test):**

| k | p | interpretation |
|---|---|---|
| 4 | 0.0625 | current — suggestive |
| 5 | 0.031 | conventionally significant |
| 6 | 0.016 | solid |
| 8 | 0.004 | strong |

**One or two more qualifying studies takes the result from "suggestive" to "significant."** That is
a realistic literature target, unlike n ≥ 15, which is not.

---

## 5. Honest limits of this approach

State these in the paper; they are real.

- **k = 4 is small.** p = 0.0625 is suggestive, not conclusive. It is presented as such.
- **The four studies are not fully independent in construct** — two are the same paper
  (Vandevenne Cs and Sr on the same seven materials). A conservative reading counts
  **k = 3 papers** (p = 0.125). Both counts should be reported; the code reports every study
  separately so the reader can choose.
- **Effect sizes are heterogeneous** (+0.376 to +0.946), as expected when regimes differ — which
  is *why* a random-effects framing is appropriate and a fixed-effect pooled fit is not.
- **A meta-analysis of directions is weaker than a validated quantitative model.** It supports
  *"framework aluminium governs cation uptake"*; it does **not** license predicting a K_D outside
  the Varon domain. The forward model keeps its existing domain guard, unchanged.

---

## 6. Recommended sequence

1. **Re-triage the existing corpus** against the broader profile in §4. No acquisition needed;
   may add k immediately. ← *cheapest, do first*
2. **Targeted acquisition of 2–4 qualifying studies** via institutional access, prioritising
   composition series in the NMR-rich immobilisation literature (F20: 4 of 6 NMR papers are
   immobilisation studies). Named candidate: DOI 10.1007/s12034-025-03487-2.
3. **Report the meta-analysis alongside the forward model** in the manuscript — the model as the
   quantitative demonstration within one series, the meta-analysis as the evidence that the
   direction reproduces across independent laboratories, adsorbates and regimes.
4. Keep `docs/lab-campaign-protocol.md` on file. If laboratory access ever appears — a
   collaborator, a visiting arrangement, a student project — it is ready to execute, and it
   remains the only route to a *quantitative* model beyond n = 7.
