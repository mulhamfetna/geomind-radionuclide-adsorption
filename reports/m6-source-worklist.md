# M6 — Data-source worklist (literature sweep, 2026-07-19)

**Method:** automated multi-agent sweep — 101 agents, 643 tool calls, ~21 min. Claims were
adversarially verified (3-vote); several plausible-sounding claims were **refuted and dropped**,
and those are noted below because they matter as much as the positives.

---

## 🔴 Headline result — read this before planning M4/M5

> **No large, ready-made open dataset of Cs/Sr adsorption on geopolymers exists.**

The sweep's single tier-1 open deposit is the Mendeley record `10.17632/9fxcs77ywr.1` — which is
**the Oulu dataset we already have**, and it contains **no Cs or Sr at all**.

**Realistic yield from everything below: ~30–60 new rows, not hundreds.** Growth must come from
extracting individual papers one at a time. This constrains what M4/M5 can honestly claim, and it
should be stated in any publication rather than discovered by a reviewer.

**Second structural finding:** the field reports at least five different quantities — Langmuir
*Q*max, Freundlich max, single-point uptake, **ion-exchange capacity (meq/g)** and **K_d (mL/g)**.
`CapacityType` in `adsorption_schema.py` was extended to cover all five. K_d is *not* a capacity
and must never be pooled with mg/g values.

---

## Ranked worklist

### 🥇 Tier A — new, open access, extract first

| # | Source | What it gives | Licence | Extraction |
|---|---|---|---|---|
| **A1** | **Varon et al. (2025)**, *Interplay between geopolymer formulation, microstructure, and strontium sorption properties*, Cleaner Materials **17**:100331, `10.1016/j.clema.2025.100331` | **Best new Sr source.** Designed sweep of **Si/Al and H₂O/M₂O** in K-geopolymers, with **BET** + **²⁷Al/²⁹Si NMR** (Al^IV, Q⁴(mAl)) on the same samples | gold OA, **CC BY-NC 4.0** | PDF tables |
| **A2** | **Katada et al. (2024)**, Langmuir **40**(37), open at **PMC11411716** | **Easiest extraction found.** Open **HTML table**: 6 Na-form zeolites with Si/Al, Al content, **Cs ion-exchange capacity**, equilibrium constant. Selectivity FAU < LTA < MFI < YFI < MOR (K = 3.41–187) | open on PMC | **HTML table — trivial** |

> ⚠️ A2 reports **meq/g**, not mg/g → convert with `meq_g_to_mg_g()` and tag
> `capacity_type=iec_meq_g`. Its headline point — that **Si/Al alone cannot explain selectivity** —
> is directly relevant to our feature design.

### 🥈 Tier B — new but paywalled

| # | Source | What it gives | Note |
|---|---|---|---|
| **B1** | *Next Sustainability* (2025), `S2950631X25000024` | Clean **activator-molarity → performance** mapping: NaOH **1–5 M** → K_d ~10²→10⁴ (Sr²⁺) and ~10²→10³ (Cs⁺), with ²⁹Si NMR, PALS free-volume, EXAFS | K_d, **not** capacity |
| **B2** | **Baek et al. (2018)**, Micropor. Mesopor. Mater. **264**:159–166, `10.1016/j.micromeso.2018.01.025` | 3 natural zeolites (chabazite, stilbite, heulandite), Cs isotherms fitted Langmuir **and** Freundlich, with **CEC and Si/Al** stated | composition-linkable |

### 🥉 Tier C — bulk reservoir, analogue materials only

| # | Source | Reality check |
|---|---|---|
| **C1** | **JAEA-SDB** (JAEA Sorption Database) | Covers **Cs and Sr** among 79 elements — but its solid phases are bentonite, rocks, clay minerals, cement/concrete, soils. **Zero occurrences of "geopolymer" or "alkali-activated".** Stores **K_d**, not *Q*max; solids described mineralogically, not by Si/Al or activator molarity |

**Verified-false claims worth recording:** the sweep *refuted* (0–3 votes) that JAEA-SDB records
carry BET/CEC/composition descriptors, and that its >86,000 entries make it the largest relevant
aluminosilicate source. Treat C1 as an **analogue-material** reservoir needing a separate K_d
target — not a shortcut to rows.

### ✅ Already held (no action)

El-Naggar & Amin 2018 (`10.1016/j.jhazmat.2017.11.049`, 4 sorbents, Cs 74.95 mg/g) ·
Tian & Sasaki 2019 (`10.2166/wst.2019.209`) · Lei et al. 2021 (`10.1016/j.jhazmat.2020.124292`,
Cs 103.74 / Sr 54.90 mg/g) · Lin et al. 2026 (`10.3390/ceramics9020021`, CC BY, Cs 0.41 / Sr
5.07 **meq/g**) · Oulu (`10.1016/j.matdes.2026.115471`)

> Lin et al. is **CC BY** and reports **meq/g** — re-extract it under the corrected capacity type.

---

## Systematic mining strategy going forward

**Repositories to query directly** (the sweep confirms generic web search under-serves this):
Mendeley Data · Zenodo · figshare · Dryad · OSF · Harvard Dataverse — query
`geopolymer AND (cesium OR strontium) AND (adsorption OR sorption)`, and the same with
`alkali-activated`, `metakaolin`, `zeolite` substituted.

**Highest-yield levers, in order:**
1. **Data-in-Brief / supplementary** of the papers we already hold — supplements often carry the
   full isotherm tables the article only summarises. Cheapest rows available.
2. **Citation-graph expansion** from A1, A2 and Lei 2021 — forward and backward citations.
3. **Analogue expansion** (NH₄⁺, K⁺, Rb⁺ on aluminosilicates) — larger literature, but every row
   must be tagged `adsorbate_class=analogue`.

**Standing benchmark check:** no curated aluminosilicate ion-exchange benchmark comparable to
matbench / QM9 was found for this domain. There is no dataset to simply download — which is
itself a reason the work has novelty value.

---

## Recommended actions

1. **A2 first** — an open HTML table is hours of work, not days.
2. **A1 second** — the best Sr composition series available, and OA.
3. **Re-extract Lin et al.** under `iec_meq_g`.
4. **Mine supplements** of the five papers already held.
5. **Decide on K_d** — B1 and C1 are only usable if we model K_d as a separate target. Recommend
   keeping it out of the mg/g pool entirely for now.
6. **Re-run the letter action (A1 in the M1 spec)** — the GEOMIND authors' 112-sample dataset
   remains a larger single win than everything in this worklist combined.

---

# ⚠️ Extraction finding (Katada 2024): Si/Al alone is the WRONG feature

Extracting A2 produced a result that changes the M4 feature design, so it is recorded here
rather than buried in a commit message.

Across the six Na-form zeolites, Cs capacity correlates:

| Predictor | Correlation with Cs capacity |
|---|---|
| **Si/Al** | **+0.68** |
| **Al content (mol/kg)** | **−0.81** |

That is the **opposite** of the naive model "more Al → more exchange sites → more capacity".

The reason is **site accessibility, not site count**:

| Sorbent | Si/Al | Al (mol/kg) | Cs capacity (mg/g) | **% of Al sites actually used** |
|---|---|---|---|---|
| LTA 6.7 | 1.12 | 6.69 | 23.9 | **2.7 %** |
| FAU 6.1 | 1.37 | 6.08 | 73.1 | **9.0 %** |
| YFI 1.3 | 11.1 | 1.33 | 110.3 | 62.4 % |
| MFI 1.2 | 12.3 | 1.22 | 132.9 | 82.0 % |
| MOR 1.5 | 9.88 | 1.48 | 191.4 | **97.3 %** |
| MOR 1.7 | 8.37 | 1.71 | 211.3 | **93.0 %** |

High-Al frameworks (LTA, FAU) carry abundant exchange sites that Cs⁺ largely **cannot reach**;
high-Si frameworks (MOR, MFI) have fewer sites but use nearly all of them.

## Reconciling this with the Oulu NH₄⁺ trend

Oulu showed the *opposite*: lower Si/Al → higher NH₄⁺ uptake. Both are correct, because they vary
different things:

* **Oulu** varies composition **within one amorphous AAM family** — lowering Si/Al genuinely adds
  accessible framework charge.
* **Katada** varies **crystalline framework topology**, where Si/Al is *confounded* with pore
  structure. Topology dominates.

## Consequences

1. **Si/Al is not a sufficient feature.** M4 needs accessibility descriptors — BET surface area,
   pore aperture, and ideally the fraction of Al that is exchange-accessible.
2. **Never pool geopolymers and zeolites into one Si/Al → capacity model.** The relationship has
   **opposite sign** in the two families; a pooled fit would be confidently wrong. This is exactly
   what the new `sorbent_class` field exists to prevent.
3. Capacities measured against a **1000 mg/L Na background** (as here) are *selectivity-limited*,
   not clean single-ion maxima — recorded via `competing_ion` / `competing_ion_mg_L`.

---

# Extraction round 2 — two negative results (2026-07-19)

## A1 Varon 2025 — cannot be retrieved automatically

Confirmed **gold OA, CC BY-NC** (OpenAlex + Unpaywall). But:

* ScienceDirect returns **HTTP 403** to automated fetches;
* Unpaywall lists a publisher and a repository location, but **`url_for_pdf` is `None` for both**;
* HAL indexes the record (`10.1016/j.clema.2025.100331`) with **no deposited full text**.

**There is no automated retrieval path.** The article is free to *read* — it needs a
**manual download** into `papers/references/`, after which extraction is straightforward.
→ **Action for Mulham:** download it; then this becomes the best Sr source we have.

## Tian & Sasaki supplement — rejected, adds nothing usable

`wst2019209supp.docx` (already held) contains a 24-row comparison table across Cs⁺, Sr²⁺ and
AsO₄³⁻. **It was NOT ingested**, deliberately:

1. Its three "Present work" rows (fly-ash geopolymer **Cs 111.90**, **Sr 24.18** mg/g) are
   **already in the pool** via the literature compilation — ingesting would duplicate them.
2. The remaining ~21 rows are **not aluminosilicates** (Prussian blue, magnetite, magnetic
   graphene oxide, irradiated yeast, hydroxyapatite, dolomite, chitosan…).
3. Decisively: the table reports only solid/liquid ratio, concentration, pH and capacity —
   **no Si/Al, no framework, no composition of any kind.**

Ingesting them would have grown the pool 100 → ~124 rows while contributing **zero usable
features**, and would leave composition-free rows sitting in a database whose purpose is
composition → capacity modelling. **Row count is not progress.** Recorded here so the decision
is not silently revisited.

## Where the remaining yield actually is

| Action | Est. rows | Blocker |
|---|---|---|
| **GEOMIND authors' 112-sample dataset** | **112** | the unsent letter — still the single biggest win |
| Varon 2025 (Sr, designed series) | ~10–20 | manual download |
| Baek 2018 (3 zeolites, CEC + Si/Al) | ~6–12 | paywall |
| Next Sustainability 2025 (NaOH 1–5 M) | ~10 | paywall; reports K_d, needs separate target |

---

# 🎯 Varon 2025 extracted — the feature question is now answered

Seven K-geopolymers, each with BET, ²⁷Al NMR (Al^IV) and ²⁹Si Q⁴(mAl) measured on the **same
samples** as the Sr sorption tests. Correlating each candidate descriptor against K_D:

| Predictor | corr with K_D(Sr) |
|---|---|
| **BET surface area** | **+0.19** — essentially no explanatory power |
| Si/Al | −0.95 |
| **[Al^IV] (mmol/g)** | **+0.95** |

The sample with the **highest** surface area (212 m²/g) has among the **lowest** K_D (1100),
while a 72 m²/g sample has the **highest** (4100).

## This closes the loop across all four datasets

| Dataset | System varied | Observation |
|---|---|---|
| Oulu (NH₄⁺) | composition **within one amorphous family** | lower Si/Al → more uptake |
| **Varon (Sr)** | composition **within one family**, with NMR | **[Al^IV] → K_D, r = +0.95** |
| Tarnovsky (Cs/Sr) | two geopolymers | BET 88 → *lower* Cs than BET 26 |
| Katada (Cs) | **across crystalline frameworks** | topology dominates; Si/Al misleads |

**The unifying variable is accessible tetrahedral aluminium — the charge-bearing sites — not
surface area and not Si/Al.** Si/Al works *within* a family only because it proxies Al content
there; it fails across frameworks because topology decides which Al is reachable.

## Consequences for M4

1. **Primary feature should be [Al^IV] or accessible-Al**, with Si/Al secondary and BET weak.
2. ²⁹Si/²⁷Al NMR speciation is the highest-value characterisation to seek in new sources —
   and the **Oulu dataset already contains ²⁹Si NMR** for all 20 of its compositions.
3. **BET must not be assumed a good predictor.** Four datasets now say otherwise.

## Data-handling note

Varon reports **K_D (mL/g)**, a distribution coefficient, *not* a capacity. Those 7 rows carry
`kd_mL_g` and leave `capacity_mg_g` **NULL**, so they cannot be swept into an mg/g regression.
`validate()` now accepts a row carrying *either* target.

---

# Oulu BET mined — surface area is *negatively* related to uptake

The 20-sample designed series now carries BET (1.0–248.6 m²/g), extracted from the ASAP-2020
instrument files. Against NH₄⁺ uptake:

| Subset | corr(BET, uptake) | corr(Si/Al, uptake) |
|---|---|---|
| All 20 samples | −0.50 | −0.62 |
| **Ca-free series (n=8)** | **−0.97** | −0.91 |

`Si20Al1Na1` has the **highest** surface area in the set (**248.6 m²/g**) and the **lowest**
uptake (2.13 mg/g). `Si1Al1Na1` has **8.3 m²/g** and the **highest** uptake (13.73 mg/g).

## ⚠️ What this dataset can and cannot show

**Cannot disentangle BET from Si/Al.** In the Ca-free series the two are almost perfectly
collinear — raising Si raises surface area *and* lowers framework charge simultaneously. Worse,
the design fixes **Al = 1** and varies Si, so *Al content and Si/Al are the same axis*. No
regression on this dataset alone can separate them.

**Can show** — decisively — that **high surface area does not imply high cation uptake.** The
relationship is strongly negative.

## The mechanism is now consistent across five datasets

Raising Si/Al *increases* surface area (more silica network, more mesoporosity) while *decreasing*
framework charge (fewer tetrahedral Al sites). **Cation exchange is governed by charge, not
area** — so BET rises while uptake falls.

| Dataset | Evidence |
|---|---|
| Oulu (NH₄⁺, n=20) | corr(BET, uptake) = **−0.97** (Ca-free) |
| Varon (Sr, n=7) | corr(BET, K_D) = +0.19; corr(Al^IV, K_D) = **+0.95** |
| Tarnovsky (Cs, n=3) | BET 88 → *lower* Cs than BET 26 |
| Katada (Cs, n=6) | LTA uses **2.7 %** of its Al sites; MOR **97 %** |
| Lin (Cs/Sr) | consistent |

**Conclusion for M4: use accessible framework charge (Al^IV / accessible-Al) as the primary
feature. BET is not merely weak — it is actively misleading as a proxy.**

## Extraction lesson recorded

The BET files are ASAP-2020 **BIFF2** binaries. `BET Surface Area:` is *not* a contiguous
substring after decoding (control bytes interleave), so a naive regex silently fails — and a loose
fallback captures `single point surface area at p/p₀ = 0.30`, returning **0.3 m²/g for every
sample**. That produced a plausible-looking but entirely false correlation before it was caught.
`extract_bet()` now uses a tolerant pattern plus a `> 0.5` guard.

---

# Download batch 2 — 4 of 5 contain no sorption data

Five open-access papers retrieved manually and screened **inline**. Only one carries adsorption
capacity; the other four are **waste-form immobilisation / leaching** studies, which the sweep's
keyword matching could not distinguish from sorption studies.

| Paper | Langmuir | Freundlich | leaching | Verdict |
|---|---|---|---|---|
| **Zhang 2021**, Appl. Sci. 11:8407 (`10.3390/app11188407`) | 20 | 19 | 0 | ✅ **ingested** |
| JRNC 2025 wasteform (`10.1007/s10967-025-10405-7`) | 1 | 0 | **101** | ❌ leaching study |
| AAC immobilisation 2023 | 0 | 0 | 0 | ❌ no quantitative sorption |
| Costa-Silva 2025, Jamt (`10.31258/Jamt.6.1.1-13`) | 0 | 0 | **43** | ❌ leaching study |
| O'Donoghue 2025, Dalton Trans. 54:11337 (`10.1039/d5dt01087j`) | 1 | 0 | 1 | ❌ synthesis mechanisms, not sorption |

**Ingested — Zhang 2021 Table 4 (Cs, verified inline):**

| Sorbent | q_max (mg/g) | K_L (L/mg) | R² |
|---|---|---|---|
| Fly-ash geomaterial | **89.32** | 0.1665 | 0.9948 |
| Slag geomaterial | **44.52** | 0.02126 | 0.9954 |

## Lesson for future sweeps

"Geopolymer + Cs/Sr" is **not** a sufficient query. A large share of that literature concerns
**immobilising** radionuclides in a waste form (leaching, diffusivity, durability) rather than
**adsorbing** them from solution. Future queries must require isotherm vocabulary
(`Langmuir`, `Freundlich`, `adsorption capacity`, `q_max`) and exclude `leachability index`,
`ANSI/ANS-16.1`, `ASTM C1308`.

**Still outstanding — the two paywalled priorities:** Baek 2018 (`10.1016/j.micromeso.2018.01.025`)
and *Next Sustainability* 2025 (`S2950631X25000024`). Neither is in this batch.

---

# F14 retroactive screen — the screen cannot run (2026-07-20)

Applied the chabazite lesson to all **35** fitted-isotherm rows. Saturation at the measured
concentration is θ = K·C₀/(1+K·C₀); a Langmuir plateau is only constrained when θ is high.

**Result: 32 of 33 rows with a usable K_L have no recorded C₀.** The screen runs on exactly one
row (GF600, θ = 0.93, sound).

## What that means

This is a **worse** outcome than finding more artifacts. Chabazite was caught only because Baek's
kinetics section happened to state the equilibrium uptake in prose. For every other fitted row we
**cannot tell** whether Qmax is a measured plateau or an extrapolation — the schema captured
`langmuir_b_L_mg` but not the concentration range the fit was performed over.

K_L alone is suggestive but not sufficient. The rows now sorted lowest-K_L first are the ones to
re-check by hand:

| sorbent | Qmax (mg/g) | K_L | risk |
|---|---|---|---|
| chabazite | 1249.5 | 7.9e-05 | **confirmed artifact** |
| stilbite | 76.3 | 1.3e-03 | high — same paper, same protocol |
| heulandite | 59.5 | 1.7e-03 | high — same paper, same protocol |
| K-MKBFS ×3 | 42–62 | ~8e-03 | moderate |
| Na-MKBFS ×3 | 76–82 | ~1.2e-02 | moderate |

## Action taken

`initial_conc_mg_L` is now a **required field for any fitted-isotherm row**. Sources already
ingested keep their rows, but each is flagged `c0_unknown` so a model cannot silently treat an
unconstrained extrapolation as a measurement.

## Honest statement of impact

The pool holds **35 fitted capacities of which 1 is verifiably sound, 1 is a confirmed artifact,
and 33 are unassessable.** That is the single largest quality caveat in the dataset and belongs in
any publication's limitations section — not because the numbers are wrong, but because we cannot
currently demonstrate they are right.

---

# Foams 2020 — capacity present but figure-derived, NOT ingested

`10.1016/j.jclepro.2020.122400` reports Cs capacities in prose read off figures, and they are
**condition-dependent and mutually inconsistent** without their context:

- "sorption capacity is about **150** mg g⁻¹ and **100** mg g⁻¹ for GF and FGF respectively" (Fig. 7)
- "maximal exchange capacity is about **80** mg g⁻¹ for GF and **65** mg g⁻¹ for FGF"
- "equal to **250** mg g⁻¹ and **175** mg g⁻¹ in pure water"

Three different pairs for two materials, each under a different solution matrix, all approximate
("about"), none in a table. Assigning them without the figures would be guesswork.

**Not ingested.** Requires reading Figs. 7–8 directly and recording the matrix for each value.
Logged rather than half-mined, consistent with the standing rule.

---

# Manual re-check: stilbite and heulandite (2026-07-20) — my suspicion was wrong

Recovered the isotherm range from Baek's methods: **3.0×10⁻⁶ to 2.0×10⁻² M**, i.e.
**0.40 – 2658 mg/L** for Cs. With C₀max recorded, the F15 saturation screen runs on all three.

| sorbent | Qmax (mg/g) | K_L | K·C₀ | **θ** | q reached at C₀max | verdict |
|---|---|---|---|---|---|---|
| chabazite | 1249.5 | 7.94e-05 | 0.21 | **0.174** | 218 | ❌ **extrapolated — confirmed artifact** |
| stilbite | 76.3 | 1.29e-03 | 3.44 | **0.775** | 59 | 🟡 weakly constrained (just under 0.8) |
| heulandite | 59.5 | 1.67e-03 | 4.45 | **0.816** | 49 | ✅ **adequately constrained** |

## I was wrong about these two

I had flagged stilbite and heulandite as *"high risk — same paper, same protocol"*. That
reasoning was faulty: **the protocol was fine.** All three were measured over the same
0.4–2658 mg/L range. Chabazite's problem is its own **weak binding** — K_L two orders of
magnitude below the others — so it reaches only **17 %** of its fitted plateau at the highest
concentration used, while heulandite reaches **82 %**.

Guilt by shared protocol was the wrong inference. **The parameter, not the paper, decides.**

## Actions

- **heulandite** — accepted, θ = 0.82.
- **stilbite** — retained but flagged; θ = 0.775 sits just below the 0.8 threshold, so its Qmax is
  mildly extrapolated (~24 % beyond the measured plateau). Usable with the caveat stated.
- **chabazite** — remains excluded; 1249.5 mg/g is an extrapolation from 17 % saturation and still
  breaches the schema's plausibility bound.
- `initial_conc_mg_L` now recorded for all Baek rows, so **4 of 35** fitted rows are screenable
  (was 1). The other 31 still need their C₀ recovered from their sources — that is the F15 backlog.

---

# F15 backlog progress — El-Naggar 2018 recovered (2026-07-20)

Methods: *"10 mL of the desired dilutions of radioactive stock solution (10²–10³ mg/L)"*,
0.1 g sorbent → **C₀max = 1000 mg/L, dose 10 g/L**.

All six rows clear the screen comfortably:

| sorbent | Qmax | K_L | θ | verdict |
|---|---|---|---|---|
| K-MKBFS ×3 | 42–62 | ~8.8e-03 | **0.886–0.898** | ✅ sound |
| Na-MKBFS ×3 | 76–82 | ~1.2e-02 | **0.923–0.926** | ✅ sound |

My K_L-based suspicion was again too pessimistic — these were the next-lowest K_L rows after
Baek's, and all six are adequately constrained. The pattern is becoming clear: **K_L alone is a
poor screen; it only bites when paired with a low C₀max.** Chabazite remains the only failure
because its K_L is two orders below everything else in the pool.

## Screen status: 10 of 35 fitted rows

| | n |
|---|---|
| ✅ sound (θ ≥ 0.8) | **8** |
| 🟡 borderline (0.5 ≤ θ < 0.8) | 1 — stilbite |
| ❌ extrapolated (θ < 0.5) | 1 — chabazite |
| ⬜ unscreenable (no C₀) | **25** |

Remaining backlog, by source: Hamed 2025 (7), Tarnovsky (6), Zhang (2), Lei (2), Tian ×2 (2),
Zheng (1), Xiang GF600 already done, plus the Katada IEC rows which are not Langmuir fits.

---

# F15 screen — COMPLETE for 29 of 35 fitted rows (2026-07-20)

C₀ recovered from each source's methods section:

| source | C₀max | rows | outcome |
|---|---|---|---|
| Baek 2018 | 2658 mg/L (2.0e-2 M) | 3 | 1 sound, 1 borderline, **1 artifact** |
| El-Naggar 2018 | 1000 mg/L | 6 | all sound (θ 0.886–0.926) |
| Tarnovsky 2024 | 10 mmol/L → 1329 (Cs) / 876 (Sr) | 6 | all sound (θ 0.960–0.995) |
| Hamed 2025 | 1000 mg/L | 7 | all sound (θ 0.982–0.987) |
| Lei 2021 | 170 mg/L | 2 | sound (0.979, 0.986) |
| Zheng 2023 | 800 mg/L | 1 | sound (0.933) |
| Xiang 2021 | 500 mg/L | 1 | sound (0.929) |

## Verdict

| | n |
|---|---|
| ✅ sound (θ ≥ 0.8) | **27** |
| 🟡 borderline | 1 — stilbite (0.775) |
| ❌ extrapolated | 1 — chabazite (0.174) |
| ⬜ C₀ not found | **6** |

**The dataset is in far better shape than the chabazite discovery suggested.** 27 of 29
assessable fitted capacities are properly constrained; exactly one is an artifact.

## Where my reasoning kept failing

Three times I used low K_L to predict an artifact, and three times the rows turned out sound
(El-Naggar ×6, Tarnovsky ×6, Hamed ×7). **K_L alone is not a screen.** Saturation is
θ = K·C₀/(1+K·C₀) — a small K is entirely compensated by a large C₀. Chabazite fails not because
its K is small but because its K is small *and* even 2658 mg/L only reaches 17 % of its plateau.

Recording this because the same instinct would have discarded 19 sound rows.

## Remaining 6 rows — C₀ genuinely not stated

`10.1007/s11356-019-05612-1` (Tian ESPR, 2) · `10.3390/app11188407` (Zhang, 2) ·
`Tian_2019` WST (2). Their methods sections do not give an explicit isotherm concentration range
in the extractable text. These stay flagged `c0_unknown` — not assumed sound.

## F15 final: the last 6 rows cannot be recovered from text

Two extraction passes over the three remaining sources found **no explicit isotherm concentration
range** in their extractable text:

| Source | Rows | What the text yields |
|---|---|---|
| Tian ESPR `10.1007/s11356-019-05612-1` | 2 | *"isotherm experiments, 50 mL of metal…"* — volume only, no range |
| Tian WST `10.2166/wst.2019.209` | 2 | isotherm models named; no C₀ stated |
| Zhang `10.3390/app11188407` | 2 | Freundlich equation given; no C₀ stated |

These papers plot their isotherms and never tabulate the concentration range. Recovering C₀ needs
the **figure x-axes read manually** — the same manual step Foams 2020 requires.

**Closing F15 at 29 of 35 screened.** The six stay flagged `c0_unknown`. They are *not* assumed
sound, and the limitations statement counts them explicitly.

### Final screen result

| | n | share |
|---|---|---|
| ✅ sound (θ ≥ 0.8) | **27** | 77 % |
| 🟡 borderline (stilbite, θ = 0.775) | 1 | 3 % |
| ❌ extrapolation artefact (chabazite, θ = 0.174) | 1 | 3 % |
| ⬜ unassessable — no C₀ in text | 6 | 17 % |

**Of the capacities we can assess, 96 % are properly constrained.** The single artefact was found
and excluded. That is the strongest statement the data supports, and it is stronger than the
chabazite discovery initially suggested.

---

# F16 — θ = 1 − R_L: the saturation screen needs no C₀ at all

**Found by rendering the PDF figures and reading them visually** — a capability I had wrongly
described as "manual figure reading" and deferred to Mulham. It was not manual.

Tian ESPR's Table 2 reports the Langmuir **separation factor R_L**, defined in the paper as

```
R_L = 1 / (1 + b·C₀)      with C₀ the highest initial concentration
```

Our saturation measure is

```
θ = b·C₀ / (1 + b·C₀)  =  1 − 1/(1 + b·C₀)  =  1 − R_L
```

**R_L is the saturation fraction, complemented.** Where a paper reports R_L — which is common,
because it is the standard favourability check — the screen requires no C₀ recovery whatsoever.

## Verified against the independent route

The six El-Naggar rows were screened earlier by recovering C₀ = 1000 mg/L from the methods.
Their published R_L values reproduce those θ figures **exactly**:

| row | 1 − R_L | θ from C₀ | match |
|---|---|---|---|
| Na-MKBFS 298/313/333 | 0.923 / 0.924 / 0.926 | 0.923 / 0.924 / 0.926 | ✅ |
| K-MKBFS 298/313/333 | 0.898 / 0.896 / 0.887 | 0.898 / 0.896 / 0.887 | ✅ |

Two independent derivations agreeing to three decimals is strong confirmation the screen is
implemented correctly.

## Tian ESPR resolved

| ion | Qm (mmol/g) | b (L/mmol) | R_L | **θ** | verdict |
|---|---|---|---|---|---|
| Cs | 2.12 | 3.21 | 0.056 | **0.944** | ✅ sound |
| Sr | 1.93 | 16.96 | 0.006 | **0.994** | ✅ sound |

Back-calculated C₀: **5.25 mmol/L (Cs)**, **9.77 mmol/L (Sr)** — consistent with the Fig. 5 x-axes
(data reaching Ce ≈ 5.3 and ≈ 9 mmol/L respectively), an independent visual confirmation.

## Consequence

Screened rows **29 → 31**. More importantly, **R_L should be the primary screen** and C₀ recovery
only the fallback. Any future source reporting R_L is screenable immediately.

## F16 applied: Tian WST resolved by reading Table 2

| ion | Qm (mmol/g) | = mg/g | b | R_L | **θ = 1−R_L** | verdict |
|---|---|---|---|---|---|---|
| Cs | 0.842 | **111.90** | 2.003 | 0.103 | **0.897** | ✅ sound |
| Sr | 0.276 | **24.18** | 11.045 | 0.050 | **0.950** | ✅ sound |

The mg/g conversions reproduce our pool values exactly (111.90, 24.18), confirming the rows are
correctly ingested as well as correctly constrained.

**Screened: 33 of 35.** Only Zhang 2021 (2 rows) remains — its Table 4 reports Langmuir K_L and R²
but no R_L, so it still needs a C₀ or an R_L from elsewhere in the paper.

## F17 — 🔴 Zhang 2021: negative Langmuir intercepts and very low saturation

Read Figure 8 (linearised Langmuir, `Ce/qe` vs `Ce`) visually. Two independent problems.

**1. Qmax is confirmed, but the intercept is unphysical.**

The slope reproduces the table exactly — `1/11.196 = 89.32 mg/g` (fly ash) and
`1/22.464 = 44.52 mg/g` (slag), matching the published Qmax. So the linearisation and our
ingested values are consistent.

But in `Ce/qe = 1/(Qmax·b) + Ce/Qmax` the intercept must be **positive** for any physical
Langmuir isotherm. Both are **negative** (−0.5365 and −2.0942), which implies **b < 0**. The table
nonetheless reports positive b (0.1665, 0.02126) — values that cannot be derived from these plots.

**2. Saturation is very low.**

Data reach only `Ce ≈ 3.45` (fly ash) and `3.75` mg/L. Using the table's own b:

| sorbent | Qmax | b | Ce max | **θ** |
|---|---|---|---|---|
| Fly-ash geomaterial | 89.32 | 0.1665 | 3.45 | **0.365** |
| Slag geomaterial | 44.52 | 0.02126 | 3.75 | **0.074** |

The slag fit reaches **7 % of its plateau** — worse than chabazite (17 %), the artefact already
excluded.

**Verdict:** both Zhang rows are **extrapolations**, and the fit has an internal inconsistency on
top. They are flagged and should be excluded from modelling alongside chabazite.

## Screen complete: 35 of 35

| | n | share |
|---|---|---|
| ✅ sound (θ ≥ 0.8) | **31** | 89 % |
| 🟡 borderline (stilbite 0.775) | 1 | 3 % |
| ❌ extrapolated | **3** — chabazite 0.174, Zhang fly ash 0.365, Zhang slag 0.074 | 9 % |

**Every fitted capacity in the pool is now assessed.** Three are extrapolation artefacts; 31 are
properly constrained.
