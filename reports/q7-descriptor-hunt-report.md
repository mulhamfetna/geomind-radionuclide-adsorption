# Q7 — the hunt for Al^IV alongside Cs/Sr uptake

**Completed:** 2026-07-20 · **Findings:** F20 (new, critical), F13 (updated)
**Outcome:** Q7 has **no answer within the adsorption literature**, and the reason is structural

---

## 1. The question

F19 established that the Al-richness descriptor is the project's only predictive feature for
cation uptake, and that it exists in **7 of 121 pool rows** — all from Varon, all Sr, one
material family. Q7 asked where more could be found: papers reporting ²⁹Si or ²⁷Al NMR **and**
Cs/Sr capacity **on the same samples**.

The search began on disk. That decision was not a preference — it is now three-for-three
(the R_L shortcut, Zhang's Figure 8, and Hossain's Table 2 were all already held), and it paid
again here.

---

## 2. What the corpus scan found

All 30 PDFs were classified by keyword balance — adsorption vocabulary (Langmuir, Freundlich,
isotherm, capacity, K_d) against immobilisation vocabulary (leach, wasteform, immobilise,
diffusivity) — and cross-tabulated against NMR content.

| Paper | class | NMR mentions |
|---|---|---|
| **Kim 2026** — Sr immobilisation, geopolymer wasteforms | immobilisation | **66** |
| **Nevin 2026** — Cs/Sr mass transport in geopolymer cements | immobilisation | **54** |
| **Vettese 2025** — Cs leachability, spent-resin wasteform | immobilisation | **33** |
| **Varon 2025** — formulation, microstructure, Sr sorption | *mixed* | **32** |
| **Kurumisawa 2021** — alkali activator effect on diffusivity | immobilisation | 13 |
| **Hossain 2026 (Oulu)** — composition, properties, adsorption | adsorption | 11 |
| *the other 13 adsorption papers* | adsorption | **0** |

> **Every one of the 13 adsorption studies in the corpus reports zero solid-state NMR.
> Four of the six NMR-rich papers are immobilisation studies. Varon is the only bridge.**

That is why Al^IV occurs in exactly 7 rows — all Varon. **It is not a sampling accident.**

---

## 3. F20 — two communities, two vocabularies, two target properties

The literature splits along a line that runs straight through this project:

| | water-treatment / adsorption | nuclear wasteform / immobilisation |
|---|---|---|
| How the cation meets the solid | **adsorbed from solution** | **doped in during synthesis** (1, 3 wt%) |
| What is measured | Langmuir *Q*max, K_d, BET | leach rate, cumulative leached fraction, *D*_eff |
| Structural characterisation | XRD, FTIR, BET | **²⁹Si / ²⁷Al / ¹³³Cs MAS NMR, XAS, MQMAS** |
| Descriptor availability | none | **abundant** |

Nevin is the clearest illustration. It has a full five-site Q⁴(mAl) deconvolution pre- and
post-leach, ¹³³Cs MAS and MQMAS, ²⁷Al MAS, and Sr K-edge XANES/EXAFS — and it reports **no
capacity at all**, because Cs and Sr were *added at fixed 1 and 3 wt% loadings*. There is no
uptake to correlate against.

**The consequence: more scraping cannot fix Al^IV scarcity.** The co-occurrence is rare because
of how the field is organised, not because our search was too narrow. Q7, as posed, is closed
with a negative answer.

---

## 4. The uncomfortable part: we rejected exactly the right papers

The triage log has been discarding immobilisation studies as off-target:

- `Kurumisawa 2021 + supplement` — ❌ *"diffusivity study (diffus 65)"*
- `J. Environ. Manage. 370 (2024)` — ❌ *"leaching study (leach 67, Langmuir 0)"*

Both rejections were **correct given an adsorption-capacity target**. Both discarded papers
that are **rich in the one descriptor the project cannot otherwise obtain**. The recurring
"~40 % hit rate" noted in the batch logs was never noise — it was the literature reporting,
consistently, that geopolymer + Cs research is mostly immobilisation research.

---

## 5. The decision this forces

The project aim is *"immobilisation of radioactive species (Cs-137, Sr-90)"* — but the
adsorption dimension added in M4 measures **removal from solution**. These are different
applications with different target properties, and they have been used interchangeably.

| | **Route A — keep adsorption capacity** | **Route B — reframe to leach resistance** |
|---|---|---|
| Target | Langmuir *Q*max, K_d | leach rate, *D*_eff, cumulative leached fraction |
| Existing pool | 118 rows, 52 Cs/Sr | must be rebuilt from the immobilisation corpus |
| Descriptor availability | **7 rows, one source** | **4–5 papers, NMR-characterised throughout** |
| Matches the stated aim? | partially — removal, not immobilisation | **directly** |
| Cost | none, but M4/M5 stay descriptor-starved | re-extraction; the 118-row pool does not transfer |
| Risk | the modelling target has no predictive feature | small *n* per paper (~5–10 samples each) |

**Route B is not obviously right** — it discards a pool that took the whole project to build and
audit, and the immobilisation papers are individually small. But Route A leaves M4 and M5
permanently blocked on a descriptor that the adsorption literature structurally does not report.

A third option exists and should be weighed: **measure ²⁹Si NMR ourselves** on sorbents whose
capacity is already known. That is the only route that produces new paired data rather than
re-partitioning existing data.

**This decision belongs to the PI and is not taken here.**

---

## 6. Incidental audit result — F13 updated

**Kim 2026 was on disk the whole time**, filed under a non-Latin filename (`ذري 2.pdf`), which
is why an earlier filename-based check recorded it as "not held". Reading it does **not** clear
the F13 quarantine, and partly deepens it:

- Contains EXAFS (8 mentions) and XRD (15) → those two sheets are **plausibly** sourced
- Contains **zero** occurrences of *"surface complexation"* and **zero** of
  *"molecular dynamics"* / *"MD simulation"*

…yet `Surface_Complexation_Sr` and `MD_Simulation_Sr_Cs` both cite `Kim_2026` as their source.
Either a different Kim 2026 is meant, or this is **misattribution of the same class as F7**.
Both sheets remain quarantined. The EXAFS and XRD sheets are now checkable line by line.

**Process lesson:** the corpus was indexed by filename, and two of its most descriptor-rich
papers were invisible to that index because their filenames were not in Latin script.
Content-based scanning found them in one pass.
