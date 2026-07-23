# Findings

Every finding with its evidence and resolution. Ordered by severity, then id.

## 🔴 F1 — Si_Al and Density transplanted from the GEOMIND paper

**Severity:** critical · **Status:** resolved

**Evidence:** 9 of 11 unique Si_Al values match the paper's 10 samples exactly to 3 dp; all 10 published density values appear; 91 of 92 mixes carry a single broadcast value; neither column exists in either upstream source file.

**Action:** Both columns dropped in clean.py. Must never be reinstated as features.

## 🔴 F15 — Fitted capacities cannot be validated - C0 was never captured

**Severity:** critical · **Status:** resolved_with_open_gap

**Evidence:** Applying the F14 screen to all 35 fitted-isotherm rows: 32 of the 33 rows with a usable K_L have NO recorded initial concentration, so Langmuir saturation (theta = K*C0/(1+K*C0)) cannot be computed. The screen runs on exactly one row (GF600, theta = 0.93). Chabazite was caught only because its paper stated the equilibrium uptake in prose.

**Action:** initial_conc_mg_L made required for fitted-isotherm rows going forward; existing rows flagged c0_unknown. PROGRESS 2026-07-20: C0 recovered for Baek (2658 mg/L) and El-Naggar (1000 mg/L), taking screenable rows from 1 to 10 - of which 8 are sound, 1 borderline (stilbite, theta 0.775) and 1 a confirmed artifact (chabazite, theta 0.174). 25 rows still lack C0. COMPLETE 2026-07-20: C0 recovered for 7 sources; 29 of 35 rows now screenable. 27 sound, 1 borderline (stilbite 0.775), 1 artifact (chabazite 0.174). Six rows remain unscreenable because their methods state no isotherm range. Lesson recorded THREE times: K_L alone is not a screen - saturation is K*C0/(1+K*C0), so a small K is compensated by a large C0. The same instinct would have discarded 19 sound rows.

## 🔴 F2 — Dataset far smaller than 867 rows implies

**Severity:** critical · **Status:** resolved

**Evidence:** Only 92 distinct mix designs; Metakaolin constant zero; features have 2-6 unique values.

**Action:** Grouped CV by mix design is mandatory. Metakaolin dropped.

## 🔴 F20 — NMR characterisation and adsorption-capacity measurement are near-disjoint in this literature - Al^IV scarcity is structural, not a sampling accident

**Severity:** critical · **Status:** open

**Evidence:** Corpus-wide classification of all 30 PDFs by keyword balance (adsorption terms vs leaching/immobilisation terms) against NMR content. Of the 6 papers carrying substantial solid-state NMR, FOUR are immobilisation/wasteform studies (Nevin 2026 nmr=54, Kim 2026 nmr=66, Vettese 2025 nmr=33, Kurumisawa 2021 nmr=13), ONE is adsorption (Hossain/Oulu nmr=11, but NH4+ and dyes only - no Cs/Sr), and ONE is mixed (Varon 2025 nmr=32). Meanwhile ALL 13 papers classified as adsorption studies report ZERO solid-state NMR. Varon is the single bridge between the two - which is exactly why Al^IV occurs in precisely 7 pool rows, all from Varon. These are two different research communities: water-treatment groups measure isotherms and BET and never run MAS NMR; nuclear-wasteform groups run full 29Si/27Al/133Cs NMR and measure leach rates and diffusivities, never isotherms.

**Action:** More scraping CANNOT fix Al^IV scarcity - the co-occurrence is rare by the structure of the field, not by chance, so Q7 has no answer within the adsorption literature. Two routes remain: (a) measure NMR ourselves on sorbents of known capacity, or (b) REFRAME the M4/M5 target property from adsorption capacity to leach resistance, where NMR is abundant. Note that route (b) reverses earlier triage - Kurumisawa 2021 and J. Environ. Manage. 370 (2024) were both REJECTED as "diffusivity/leaching studies", i.e. we discarded precisely the papers richest in the descriptor we need. The project aim ("immobilisation of Cs-137/Sr-90") is arguably better served by leach resistance than by adsorption capacity anyway; the two have been conflated. Decision required from PI - see reports/q7-descriptor-hunt-report.md.

## 🔴 F24 — Kurumisawa 2021 recovered - a rejected paper that bridges both pools - and it exposes a 12-order-of-magnitude naming collision in "diffusion coefficient"

**Severity:** critical · **Status:** resolved

**Evidence:** Kurumisawa 2021 (doi:10.1617/s11527-021-01758-y) was REJECTED during batch triage as "a diffusivity study (diffus 65)". Reading it inline shows that verdict was wrong on content: (a) Figure 3b publishes the Langmuir MONOLAYER Cs CAPACITY for five metakaolin geopolymers made with five different alkali activators (K11 0.315, K9 0.425, 0.66K 0.530, N11 0.727, KN11 0.393 mmol/g) - a Pool A capacity WITH real compositional variation, which Pool A is short of. Pool A: 121 -> 126 rows. (b) Figure 2 publishes a Cs diffusivity for the same five specimens - Pool B. Pool B: 16 -> 26 rows. (c) THE COLLISION. Kurumisawa's is an INGRESS coefficient (Cs diffusing INTO an immersed specimen), reported in m2/s and of order 4e-12 m2/s = 4e-8 cm2/s. Kim's and Nevin's are ANSI/ANS 16.1 EFFECTIVE diffusivities (nuclide leaching OUT of a doped wasteform), of order 1e-16 and 1e-19 cm2/s. Same name, opposite experiment, TWELVE orders of magnitude apart. (d) Table 3 is the 29Si NMR of the ACTIVATOR SOLUTION (Q0-Q3 of the silicate), NOT of the hardened gel - so this paper supplies no framework Al^IV despite being NMR-bearing. (e) Applying the F14/F16 saturation screen to the recovered capacities: K11 theta 0.962 sound, KN11 0.847 sound, K9 0.704 borderline, 0.66K 0.608 borderline, and N11 theta 0.499 an EXTRAPOLATION ARTEFACT - N11 being the HIGHEST reported capacity of the five.

**Action:** Both halves ingested through separate adapters under D13. RetentionType gains INGRESS_DIFFUSIVITY as a distinct member and pooling_warning() now raises an explicit CATEGORY ERROR if both diffusivity kinds appear together. N11 flagged as an artefact. All Kurumisawa rows carry from_figure=True. LESSON: the batch triage rejected this paper on keyword balance without reading it, and keyword balance cannot see a capacity that lives only in a figure. The other triage rejections should be re-read the same way - starting with J. Environ. Manage. 370 (2024).

## 🔴 F27 — Varon's leaching companion paper provides a WITHIN-SAMPLE causal test - framework Al^IV concentration governs Sr K_D, and destroying it by leaching destroys sorption

**Severity:** critical · **Status:** resolved

**Evidence:** Batch-4 paper Varon et al., Open Ceramics 25 (2026) 100895, doi:10.1016/j.oceram.2025.100895 - the leaching companion to varon2025 (Cleaner Materials). Its 0 h data are IDENTICAL to varon2025 (verified: K-0.5-16 BET 72, AlIV 96.0%, KD 4100) and are NOT re-ingested; the 96 h water-leached state is new. Tables 3-4 give, for all 7 samples at 0 h and 96 h: BET, [AlIV]_exp (mmol/g), AlIV/V/VI %, full Q4(mAl) speciation, Sr KD and Qmax. RESULT: [AlIV] CONCENTRATION (mmol/g) is the strongest predictor of Sr KD: corr = +0.946 (n=7), rising to +0.986 excluding the barely-reacted outlier K-1.2-8 (H2O/M2O=8, BET 15, Qmax 0.02). This beats AlIV% (+0.80), ARI (+0.77) and crushes BET (+0.19, or -0.24 without the outlier) and Si/Al (-0.84). THE CAUSAL TEST: leaching removes framework Al, and corr(Δ[AlIV], ΔKD) = +0.938 - the samples that lose the most framework Al on leaching lose the most sorption. K-0.5-16 loses 1.39 mmol/g AlIV and 2750 mL/g KD (largest of both); K-1.5-16 loses 0.04 mmol/g AlIV and the least KD. This is the same sample losing capacity AS it loses exchange sites - close to a causal demonstration that tetrahedral Al^IV is the Sr exchange site, not merely a correlate.

**Action:** Ingested 7 NEW 96h-leached Sr KD rows via _from_varon_leached2026 (Pool A 126 -> 133 rows / 12 sources), sorbent_name "... (leached 96h)" so they can never be pooled with the fresh varon2025 rows. The "Interplay..." PDF in the same batch is a confirmed DUPLICATE of varon2025 (skipped). Strengthens the project's central finding: framework Al predicts cation uptake, and this is the first WITHIN-SAMPLE (not just cross-sample) evidence for it. Note [AlIV] CONCENTRATION > AlIV% > ARI as the ranking - absolute exchange-site density beats the per-Si fraction.

## 🔴 F34 — Geddes 2025 (Q8) acquired - the ATOMIC-LEVEL MECHANISM behind the framework-Al finding; Sr binds at extra-framework Al^IV charge-balancing sites

**Severity:** critical · **Status:** resolved

**Evidence:** The critical Q8 acquisition, delivered by the supervisor after the Checkpoint-2 request. Geddes, Stennett, Wilkinson, Griffith, Hanna, Provis & Walkley, "Alkali-mediated Sr incorporation mechanism and binding capacity of alkali aluminosilicate hydrate in geopolymers", J. Hazard. Mater. 488 (2025) 137426, doi:10.1016/j.jhazmat.2025.137426 (Sheffield/White Rose). Metakaolin N-A-S-H geopolymer, Si/Al = 1.5, Na (and Na/K) activator, Sr(OH)2.8H2O doped 0-3.5 wt%. Multi-technique: 29Si/27Al/23Na MAS NMR + Sr K-edge XANES/EXAFS. MECHANISM (the key result): at low loading Sr2+ is incorporated into EXTRA-FRAMEWORK CHARGE-BALANCING SITES bonded via oxygen to tetrahedral Al^IV (SiIV-O-AlIV), with a brewsterite-Sr-like local structure - i.e. Sr sits exactly at the Al^IV sites the framework-Al descriptor counts. The N-A-S-H gel is Q4(4Al)/Q4(3Al)-dominant (Al-rich framework, Table 6). BINDING CAPACITY: Sr is chemically bound up to ~0.5-1.5 wt% Sr(OH)2.8H2O (~2-5 mg Sr per g); above the upper bound the excess precipitates as SrCO3 / Sr(OH)2. A doped-in chemical-binding limit set by the framework charge, NOT a sorption-from-solution capacity or a leachability index.

**Action:** Q8 CLOSED - the highest-value acquisition of the project, and it delivers exactly the mechanism F20/F27 needed. NOT ingested into either pool: the binding capacity is a distinct doped-in quantity (framework-charge-limited chemical incorporation), and Si/Al is fixed so there is no composition-varying descriptor-vs-target series (same no-shoehorning discipline as O'Donoghue F32). Its value is as the ATOMIC MECHANISM: it upgrades the central finding from "correlation + within-sample causal test (F27)" to "...+ direct atomic-scale proof that Sr binds at the Al^IV charge-balancing sites the descriptor measures". Cite as the mechanistic capstone of the descriptor-and-methodology paper.

## 🔴 F36 — Data-sufficiency analysis - literature acquisition has hit NEGATIVE returns; the project is at a stable stage and should advance

**Severity:** critical · **Status:** resolved

**Evidence:** Prompted by the supervisor's observation that newly delivered papers only reproduce held information. Tested empirically on the live pools (reports/data-sufficiency-analysis.md). (1) SATURATION: the framework-Al finding is confirmed by 5 independent convergent lines (correlation Varon +0.95; within-sample causal test +0.94; atomic mechanism Geddes; Oulu Ca-free ARI +0.93; immobilisation Cs-LI stratification). New sources replicate, they do not extend. (2) OUT-OF-SAMPLE PREDICTABILITY (leave-one-out CV): WITHIN a clean single-protocol class (Varon MK-geopolymers, [AlIV]->Sr KD, n=7) LOO-CV R^2 = +0.81 - genuinely predictive. POOLED across 5 labs (Cs Langmuir Qmax, Si/Al->capacity, n=23) LOO-CV R^2 = -0.09 - worse than the mean. (3) WHY MORE LITERATURE HURTS: each new paper adds another lab/protocol/material, i.e. the exact heterogeneity that drives the pooled CV negative. Si/Al is a within-class-only proxy whose SIGN flips across structural classes (zeolites Katada +0.68 vs geopolymers Varon -0.95) - a quantitative reappearance of F19/D12. Acquisition cannot remove heterogeneity; it adds it.

**Action:** Confirmed: the supervisor is right. STOP literature acquisition (negative returns); broad scraping/mining/crawling is explicitly NOT warranted - it would add noise, not signal. Advance to the stage the data supports: (a) the descriptor-and-methodology paper (saturated, multiply confirmed), (b) a WITHIN-CLASS forward model (LOO-CV R^2=0.81) as its quantitative demonstration, (c) the reusable methods. The full generative model (M5) is a SEPARATE later phase needing single-protocol breadth, obtainable ONLY via the confidential GEOMIND dataset or a short own-lab campaign - not via more papers. See D17.

## 🔴 F6 — Feasibility_Ranges is mislabelled and anti-correlated with truth

**Severity:** critical · **Status:** resolved_with_open_gap

**Evidence:** Rejects 7 of 9 feasible published samples, accepts the 1 infeasible. Its constants are verbatim from the retired tool at tag v1.0.0.

**Action:** Sheet not read. Provisional envelope used instead, flagged provisional=True.

## 🔴 F7 — Compiled data failed source audit - 10 of 31 rows

**Severity:** critical · **Status:** resolved

**Evidence:** (a) 3 rows labelled Sr are Eu-152+154. (b) 4 Niu 2022 rows claim Langmuir Qmax from a paper tabulating none. (c) Na-MK misattributed from another paper. (d) K-MK is a verbatim copy of K-MKBFS - a sorbent that does not exist.

**Action:** Quarantined/relabelled/re-typed as named constants in code.

## 🟠 F10 — Pooling adsorbates flips the sign of the BET relationship

**Severity:** high · **Status:** resolved

**Evidence:** cations corr(BET,capacity) = +0.08; dyes = +0.66.

**Action:** Never pool adsorbate classes. Dyes use surface area; cations use charge sites. pooling_warning() enforces the check.

## 🟠 F11 — Sr_Immobilization_Mechanisms is untraceable and largely duplicated

**Severity:** high · **Status:** resolved

**Evidence:** Audit 2026-07-20 - the ONLY master sheet with no Source column at all, plus 66.7% internal duplication among its numeric cells. Same signature as the fabricated Na-MK/K-MK rows in F7.

**Action:** Relabelled FALSE / DISCARD in the warehouse. Not usable.

## 🟠 F14 — A high R2 Langmuir fit can leave Qmax essentially unconstrained

**Severity:** high · **Status:** open

**Evidence:** Baek 2018 chabazite: Q0L = 1249.5 mg/g with K_L = 7.9e-05 L/mg and R2 = 0.99989, while the paper's own kinetics report equilibrium uptake of just 1.184 mg/g. K_L is two orders of magnitude below the other two zeolites in the same table. At low coverage the Langmuir isotherm is near-linear, so it fits almost perfectly while the plateau is extrapolated ~1000x beyond any measured point.

**Action:** Ingested but flagged - it exceeds the schema bound of 1000 mg/g and validate() reports it. Must be excluded from any fit unless the extrapolation is defended. Generalises: R2 is not evidence that a fitted Qmax is meaningful. Screen future Langmuir rows on K_L and on the measured concentration range, not R2 alone.

## 🟠 F17 — Zhang 2021 rows are extrapolations with an unphysical intercept

**Severity:** high · **Status:** resolved

**Evidence:** Figure 8 read visually. The slope reproduces the published Qmax exactly (1/11.196 = 89.32; 1/22.464 = 44.52), but both intercepts are NEGATIVE (-0.5365, -2.0942), which in Ce/qe = 1/(Qmax*b) + Ce/Qmax implies b < 0 and is unphysical; the table nonetheless reports positive b. Data reach only Ce = 3.45 and 3.75 mg/L, giving theta = 0.365 and 0.074 - the slag fit reaches 7% of its plateau, worse than the chabazite artefact at 17%.

**Action:** Both rows flagged as extrapolations and excluded from modelling alongside chabazite. Screen now COMPLETE at 35 of 35: 31 sound, 1 borderline, 3 extrapolated.

## 🟠 F18 — The Oulu 29Si deconvolution was already published; it explains our failed fit

**Severity:** high · **Status:** resolved

**Evidence:** Table 2 of Hossain 2026 (doi:10.1016/j.matdes.2026.115471, page 6) reports the deconvolved Si environments for all 12 selected samples - the values our own fit attempted to derive. Found by rendering the page and reading it. The authors use TEN environments (Q0, Q1, Q2(1Al), Q2(0Al), Q4(4Al), Q3(1Al), Q4(3Al), Q3/Q4(2Al), Q3/Q4(1Al), Q4(0Al)) including Q3 and Q2 species with non-bridging oxygens. Our model used FIVE Q4(mAl) Gaussians only, which cannot represent that intensity; the optimiser pushed it outward and drove Q4(3Al) to zero.

**Action:** Confirms the NMR rejection was correct AND for the right reason - the chemical sanity check detected a structurally wrong peak model that R^2 = 0.998 and both pre-registered gates could not. Pipeline closed. The Oulu letter is no longer needed for this purpose. Values transcribed into src/geomind/data/nmr_ari.py; 11 of 12 rows sum to exactly 100%, one to 99.0 (published as such).

## 🟠 F19 — The Al-richness descriptor is valid only within a structural class, and the Oulu backfill does not widen its evidence base

**Severity:** high · **Status:** resolved

**Evidence:** Backfilling ARI from F18 attached the descriptor to 39 pool rows / 12 sorbents. Split by structure, the 12 sorbents behave as two different materials. Ca-FREE (n=4, Q4 45-73%): ARI +0.932, framework-only ARI +0.940 - uptake spans 2.13-11.53 mg/g (sd 3.98). Ca-BEARING (n=8, Q4 0-26%, Q0-Q2 dominated): ARI -0.108, Si/Al -0.135, Ca/Al -0.104, Q4% -0.247, BET +0.462 - NOTHING predicts, and uptake is nearly flat at 7.27 +/- 1.31 mg/g regardless of composition. Pooling all 12 gives ARI +0.536, a mediocre value that conceals two regimes. Ca acts as a network modifier: there is no condensed aluminosilicate framework for a framework descriptor to measure, and uptake proceeds by a different mechanism (C-A-S-H exchange), roughly composition-independent.

**Action:** Restrict the ARI claim to Q4-rich framework aluminosilicates and state the structural gate explicitly. Generalises F9 one level down: never pool ADSORBATE classes, and never pool SORBENT structural classes either. IMPORTANT correction to my own estimate - I projected this backfill would widen the descriptor to ~19 sorbents; in fact only 4 of the 12 lie in the regime where it applies, so the evidence base is unchanged at Varon n=7 (Sr) + Oulu n=4 (NH4+). Al^IV scarcity remains the binding constraint on M4/M5.

## 🟠 F21 — Sr_Leaching_Data audited against source for the first time - LI verified, De corrupted to zero, and the Yildirim rows are misattributed

**Severity:** high · **Status:** resolved

**Evidence:** Both cited sources (Kim 2026, Nevin 2026) are now known to be on disk (see F13), so this sheet became auditable. Line-by-line against Kim Table 2 (p10) and Nevin p6: (a) LEACHABILITY INDEX - VERIFIED, 6 of 6 determinable rows exact. Kim NaSr1 15.5, NaSr2 14.8, NaSr3 16.0, KSr3 16.0; Nevin Sr_1 18.7, Sr_3 19.1. KSr1/KSr2 are correctly recorded as below detection - Kim states Sr leachate was under the ICP-OES limit (0.001 ppm), yielding non-detectable De and LI. (b) De_cm2_s - CORRUPTED. Every row reads 0.0, whereas Kim Table 2 reports 8.88E-16, 3.80E-14, 2.10E-16, 6.36E-16, 5.80E-18 and so on. Precision was lost to zero. Kim's De is also TIME-RESOLVED over five points (2 h, 7 h, 7 d, 14 d, 21 d), so no single scalar De pairs with the averaged LI in the first place. (c) CN_Sr_EXAFS on the two Yildirim_2024 rows - MISATTRIBUTED. The sheet gives Sr_Pre_1 = 7.87 and Sr_Post_1 = 7.95 sourced to Yildirim_2024. Kim p26 states the NaSr3 coordination number "was 7.87 +/- 0.69 before the leaching test" and "7.95 +/- 0.43 afterwards" - these are Kim's own NaSr3 pre/post values, and Kim attributes the pre-leach figure to reference [7], which is Geddes et al., J. Hazard. Mater. 488 (2025) 137426 - NOT Yildirim. The KSr3 value 7.55 is correctly attributed.

**Action:** Promote the LI column to VERIFIED_TRUE - it is the first immobilisation target variable in the project to survive source audit. Quarantine De_cm2_s entirely (re-extract from Kim Table 2 as a time series if needed). Quarantine both Yildirim_2024 rows as misattributed - third instance of the F7 pattern.

## 🟠 F22 — Pool B built and audited - LI verified twice over, but it has almost no compositional variation paired with NMR

**Severity:** high · **Status:** resolved

**Evidence:** Pool B v1 = 16 rows / 2 sources (Kim 2026, Nevin 2026), of which 8 carry a retention target, 2 are left-censored, and 6 are structure-only. (a) The LI = -log10(De) relation is now confirmed against TWO independent published tables - Kim Table 2 (12 of 13 cells to within 0.06) and Nevin Table 2 (4 of 4: 18.66/19.11/13.27/13.22 vs published 18.7/19.1/13.3/13.2). (b) A PUBLISHED ERRATUM was found. Kim Table 2 cell NaSr1 @ 2 h prints "8.88 E-16 (15.5)" but -log10(8.88e-16) = 15.05. Kim's own column Average LI of 15.5 equals mean(15.05, 15.94) exactly; had the cell truly been 15.5 the average would read 15.7. The printed (15.5) is a typo for (15.1). Verified at 430 dpi, so it is not a rendering artefact. The column average is unaffected. (c) The master sheet Sr_Leaching_Data carried only Nevin's two Sr rows and SILENTLY DROPPED both Cs rows (Cs_1 LI 13.3, Cs_3 LI 13.2) - a 50% loss of that table, undetectable without reading the source. (d) Nevin's headline result is preserved: in the SAME K-A-S-H gel, Sr is retained roughly six orders of magnitude better than Cs (De 7.8e-20 vs 6.0e-14). Nuclide identity dominates structure entirely at fixed composition.

**Action:** LIMITATION, stated plainly: only 4 rows pair an NMR descriptor with a retention target, and across those 4 the ARI is nearly constant (2.738-2.855) because Nevin is ONE formulation at Si/Al = 3. Kim varies activator (Na vs K) and loading but reports no Q4 deconvolution. So Pool B is currently as descriptor-starved as Pool A, for the opposite reason - Pool A has composition without NMR, Pool B has NMR without composition. Neither supports a descriptor model yet. This raises the priority of Q8 (Geddes 2025) further: it is the only identified source that may carry composition, NMR and a retention/binding measure together.

## 🟠 F3 — Adsorption data has extensive internal duplication

**Severity:** high · **Status:** resolved

**Evidence:** 24 Qmax_Cs rows contain only 16 distinct values; Qmax_Sr has 7 rows.

**Action:** Repeats flagged (not deleted) via cs/sr_value_repeated.

## 🟠 F37 — Within-class forward model built - the M4 quantitative demonstration; it predicts held-out samples (LOO-CV R2 = 0.81)

**Severity:** high · **Status:** resolved

**Evidence:** Following F36/D17. Module src/geomind/model/forward.py fits the within-class relationship K_D = 2812*[AlIV] - 9258 (mL/g) on Varon's seven metakaolin geopolymers (Sr, one protocol). In-sample R2 = 0.895; LEAVE-ONE-OUT CV R2 = 0.811, RMSE 522 mL/g (mean KD 1767); domain [AlIV] in [3.45, 4.77] mmol/g. A straight line by design (n=7, mechanistically monotonic - Geddes/F34). Input is framework AlIV concentration, not Si/Al (F36: Si/Al sign flips across classes). predict() hard- guards its domain of validity and refuses out-of-class extrapolation unless asked.

**Action:** This is the concrete M4 output: proof that the descriptor->property relationship is PREDICTIVE (not just correlational) when class and protocol are held fixed - the quantitative backbone of the descriptor-and-methodology paper. 8 tests, including test_pooled_cross_lab_data_is_deliberately_NOT_used, which asserts pooling drives LOO R2 < 0 and so guards D17 in code. The same recipe is the template any future single-lab series (GEOMIND set / own-lab campaign) would slot into for a general model.

## 🟠 F9 — Surface area does not predict CATION uptake

**Severity:** high · **Status:** open

**Evidence:** Cation-only, per source - lin2026 -0.90 (n=4), xiang2021 -0.90 (n=5), oulu2026 -0.47 (n=21), tarnovsky2024 +0.22 (n=6, inconclusive). Pooled cations +0.08. Varon: BET +0.19 vs Al-IV +0.95.

**Action:** Al-IV is the candidate primary feature. NOTE - an earlier claim of "six datasets confirm a negative BET correlation" was an OVERSTATEMENT, corrected here.

## 🟡 F12 — The v2 "conflict" was precision, not disagreement

**Severity:** medium · **Status:** resolved

**Evidence:** All 22 differing cells are Comp_Strength in rows 843-866 and differ only by rounding (34.36 vs 34.35777). N data.xls genuinely reports up to 6 dp, and 18 of the 24 v2 values appear verbatim upstream. So v2 preserved source precision and Physical_Data rounded to 2 dp.

**Action:** Q1 closed. v2 status suspect -> verified. Physical_Data remains canonical; the difference (<=0.005 MPa) is immaterial for modelling.

## 🟡 F13 — Several context sheets cite papers we do not hold

**Severity:** medium · **Status:** open

**Evidence:** Audit 2026-07-20 - Kim_2026, Yildirim_2024 and Duque_Redondo_2023 are cited by Surface_Complexation_Sr, MD_Simulation_Sr_Cs, Zeolite_Comparison_Sr_Cs, Sr_Leaching_Data, EXAFS and XRD sheets. None are in papers/references. Surface_Complexation cites "Eq. (10)-(12)" - equations, not sources, so those rows are model output rather than measurement. FTIR is 88.9% duplicated, XRD 72.7%.

**Action:** All remain UNVERIFIED and excluded from modelling. Acquiring the three papers is the only way to promote them; recorded as Q6.

## 🟡 F16 — theta = 1 - R_L, so the saturation screen needs no C0

**Severity:** medium · **Status:** resolved

**Evidence:** The Langmuir separation factor R_L = 1/(1+b*C0) is reported by many papers as a favourability check. Our saturation measure theta = b*C0/(1+b*C0) is exactly 1 - R_L. Verified against the independent C0 route on six El-Naggar rows: the two derivations agree to three decimals. Resolved Tian ESPR (theta 0.944 Cs, 0.994 Sr) with back-calculated C0 5.25 and 9.77 mmol/L, matching the Fig. 5 axes.

**Action:** Use R_L as the PRIMARY screen and C0 recovery only as fallback. Found by rendering PDF figures and reading them visually - a capability previously and wrongly described as "manual figure reading" and deferred to Mulham.

## 🟡 F23 — Not every published deconvolution assigns m uniquely - Vettese's ARI is indeterminate and must not be computed

**Severity:** medium · **Status:** resolved

**Evidence:** Vettese 2025 Table 4 (p7) reports a 29Si deconvolution, but its first two columns carry AMBIGUOUS assignments: "Q3(1Al) or Q4(4Al)" (m = 1 or 4) and "Q3 or Q4(3Al)" (m = 0 or 3). Computing the Al-richness index therefore has two permitted answers for the unleached sample: ARI = 2.289 if the Q4 readings are taken, or 0.861 if the Q3 readings are - a factor of 2.66. Populations do sum correctly (100.0 / 100.1 / 100.1), so the table is internally sound; it is the ASSIGNMENT that is undetermined, not the fit. Hossain and Nevin both assign m uniquely; Vettese does not.

**Action:** Do NOT compute or store an ARI for Vettese. A pipeline that derived ARI from any Q^n(mAl) table without checking assignment uniqueness would silently inject a 2.7x error into the one descriptor the project depends on. Vettese can still contribute structure-only rows (raw populations) and its Cs leach data, which is figure-only and single-formulation. Any future adapter must carry an assignment-ambiguity flag.

## 🟡 F25 — The last triage rejection (J. Environ. Manage. 370) is upheld as data, but it is a high-value BIBLIOGRAPHY that names the paired-data sources both pools lack

**Severity:** medium · **Status:** resolved

**Evidence:** D15 re-read of Mukiza et al., J. Environ. Manage. 370 (2024) 122746, "Recent advances in immobilization of Cs/Sr-bearing wastes in AAMs: a review". It is a REVIEW, not primary data: zero Langmuir/Qmax/Kd of its own, and its Table 2 explicitly states "the data are not directly comparable". So the batch rejection was CORRECT for direct ingestion - none of its tabulated numbers may enter either pool as primary rows. BUT reading it surfaced exactly the paired-descriptor sources F20/F22 said were rare: (a) Komljenovic et al. 2020, J. Hazard. Mater. 388, doi:10.1016/j.jhazmat.2019.121765, "Immobilization of cesium with alkali-activated blast furnace slag" - the review states it ties 29Si NMR speciation (Q1, Q2(0Al), Q2(1Al) sites, Al^IV/Si of C-A-S-H) to strength AND Cs. NMR + composition + Cs in one paper. Same group (Provis) as Nevin/Geddes. A second candidate F20 bridge alongside Geddes 2025. (b) Qian et al. 2001, J. Nucl. Mater. 299, 199-204, doi:10.1016/S0022-3115(01)00700-0 - Cs and Sr distribution ratios R_d (3.9e3->6.4e3 mol/g Cs; 6.4e3->1.2e4 mol/g Sr). A K_d measure = Pool A. (c) Jang et al. 2016, J. Hazard. Mater. 318, 339-346, doi:10.1016/j.jhazmat.2016.07.003, "Physical barrier effect ... on diffusivity of Cs and Sr" - a Cs/Sr diffusivity (Pool B) source, and it is ALREADY ON DISK (papers/references/Physical barrier effect ...pdf), registered but never mined.

**Action:** Keep the review out of both pools as a data source. Use it as a source index. Q9 opened for Komljenovic 2020 (acquire), Q10 for Qian 2001 (acquire), and Jang 2016 queued for Pool B extraction since it is already held. This is the third time (after F24 Kurumisawa and the Kim/Nevin content-index miss) that real value was found by reading a document already in hand rather than acquiring a new one.

## 🟡 F26 — Jang 2016 mined into Pool B - 14 rows, both nuclides, with pore structure; and it confirms the LI aggregation trap a third time

**Severity:** medium · **Status:** resolved

**Evidence:** Jang, Park & Lee, J. Hazard. Mater. 318 (2016) 339-346, doi:10.1016/j.jhazmat.2016.07.003 - the Q11 source, already on disk, now extracted. Seven doped waste forms (F1/F2/F3 fly-ash geopolymers, S1/S3/S5 fly-ash+slag blends, PC Portland baseline), each with Cs AND Sr leachability indices (Table 7) and pore structure (Table 5). Pool B: 26 -> 40 rows / 4 sources. (a) LI AGGREGATION CONFIRMED a third time. Jang's LI = mean over intervals of -log10(De_n): F1 Cs interval De's give 10.02 ~ published 10.0, whereas -log10(mean De) = 9.46 would be wrong by 0.5. Vindicates schema trap 4. (b) Sr LI > Cs LI in EVERY one of the 7 specimens - the universal Cs<Sr retention result, now across 7 more matrices, consistent with Nevin's ~6-order gap. (c) Si/Al deliberately NOT stored. The precursor-bulk Si/Al is computable (1.55-2.13) but omits the sodium-silicate activator Si, so it is not the gel Si/Al, and the F/S series use different silicate loadings (0.25 vs 0.17) so it is not even comparable across specimens. Storing it would repeat the F1 transplant error in a new form. Recorded as provenance-only constants. (d) Three new pore-structure columns added (porosity, capillary pore volume, critical pore diameter); Jang links these to De. corr(porosity, Cs LI) = -0.27 across the 6 geopolymers - weak, consistent with Jang's own point that critical pore DIAMETER matters more than total porosity.

**Action:** Ingested via _from_jang2016 as 14 LI rows. Mean De values retained as documented adapter constants (uncorrupted, unlike Kim's) but not emitted as separate rows, to avoid implying an independent measurement - a diffusivity target can regenerate them later. PC baseline flagged matrix_class=portland_cement, trivially filterable. Q11 closed. Fourth on-disk recovery of the session.

## 🟡 F28 — Stanojevic 2025 - 2 Cs leachability rows for a fly-ash geopolymer; Cs passes the LI criterion yet >70% leaches, reaffirming Cs mobility

**Severity:** medium · **Status:** resolved

**Evidence:** Batch-4. Stanojevic et al., Constr. Build. Mater. 500 (2025) 144217, doi:10.1016/j.conbuildmat.2025.144217 (Komljenovic/Provis group). Fly-ash geopolymer, Cs doped at 2% and 5%, semi-dynamic leach. Lmean (Fig. 6b) = 10.3 (2%Cs) and 9.9 (5%Cs) over 90 days (9.7/9.3 over the first 5 days) - both clear the ANSI/ANS-16.1 / NRC floor of 6. BUT cumulative Cs leached exceeds 70% after 5 days (71.0% / 76.5%): the LI criterion is passed while most of the Cs still leaves - Cs remains highly mobile. 29Si shows Q4(mAl) (fly-ash framework), and the higher 5% Cs loading introduces less-crosslinked Q1,2 units (Cs slows condensation), a qualitative echo of the framework story.

**Action:** Ingested 2 Pool B rows via _from_stanojevic2025 (40 -> 42 rows / 5 sources), from_figure=True (Lmean read from the Fig. 6b annotation). One fly-ash geopolymer at two Cs LOADINGS (a control variable), so no composition variation; the Q4 data is figure-only and not digitised into per-sample descriptor rows. Reinforces the universal Cs<Sr pattern: even a passing LI hides >70% Cs release.

## 🟡 F29 — Komljenovic 2020 (Q9) closed - it is a Ca-system (C-A-S-H) and QUANTITATIVELY confirms F19 - the aluminosilicate framework immobilises Cs better than a Ca gel

**Severity:** medium · **Status:** resolved

**Evidence:** Batch-4, Q9 acquisition. Komljenovic et al., J. Hazard. Mater. 388 (2020) 121765, doi:10.1016/j.jhazmat.2019.121765. Alkali-activated blast-furnace slag (AABFS), Cs doped 2%/5%. The hoped-for "framework NMR + Cs" bridge it is NOT: AABFS is a C-A-S-H binder whose 29Si NMR shows only low-connectivity Qn(mAl) sites (n=1-3, m=0-1) with NO framework Q4(mAl) - exactly the Ca-modifier regime of F19, so the descriptor is C-A-S-H chain length / AlIV/Si, not ARI. Cs preferentially associates with the N-(C)-A-S-H gel over the C-A-S-H gel. QUANTITATIVE F19 CONFIRMATION: Cs Lmean (Fig. 5b) = 7.8 (2%) and 7.0 (5%), both above the ANSI/ANS-16.1 floor of 6, but markedly LOWER than the framework geopolymers - fly-ash (Stanojevic 10.3/9.9; Jang ~10) and metakaolin (Nevin Cs 13.2/13.3). The calcium-silicate gel holds Cs less well than the aluminosilicate framework.

**Action:** Q9 CLOSED. Ingested 2 Pool B Cs LI rows via _from_komljenovic2020 (42 -> 44 rows / 6 sources), matrix_class slag_blend, from_figure. Note for the eventual paper: Cs leachability index now stratifies cleanly by binder chemistry - framework MK ~13 > framework FA ~10 > Ca-rich slag ~7.5 - the immobilisation-side echo of the adsorption-side framework-Al finding (F27). Komljenovic is the Provis group; same lineage as Stanojevic, Nevin, Geddes.

## 🟡 F30 — Qian 2001 (Q10) closed - Sr/Cs distribution ratios from a scanned 2001 paper, read visually; supports the framework-Al story from the Ca side

**Severity:** medium · **Status:** resolved

**Evidence:** Batch-4, Q10 acquisition. Qian, Sun & Tay, J. Nucl. Mater. 299 (2001) 199-204, doi:10.1016/S0022-3115(01)00700-0. SCANNED PDF (no text layer) - values read visually from the page-4 body text. Aluminium-rich alkali-activated slag (AAS) and M-AAS (AAS + metakaolin + zeolite + NaOH-treated attapulgite clay), a Ca-rich C-A-S-H binder. Distribution ratio Rd (0.002 M CsCl/SrCl2, 7 d): AAS Cs 3.9e3, Sr 6.4e3; M-AAS Cs 6.4e3, Sr 1.2e4. Adding Al-rich metakaolin/clay RAISES Rd for both ions (M-AAS > AAS by 67-88%), and both beat OPC by 1.5-3x - i.e. more aluminosilicate exchange capacity = more uptake, even in a calcium-silicate binder. This is the framework-Al mechanism seen from the Ca side. UNIT FLAG: the paper labels Rd "mol/g", but Rd is a distribution coefficient whose magnitude (3.9e3-1.2e4) is consistent with mL/g. Stored in kd_mL_g with the caveat recorded, not silently "corrected".

**Action:** Q10 CLOSED. Ingested 4 Pool A KD rows (AAS/M-AAS x Cs/Sr) via _from_qian2001 (133 -> 137 rows / 13 sources), sorbent_class AAM (slag C-A-S-H, not framework). Fifth on-disk/visual recovery of the batch; second successful visual read of a scanned/figure-locked source this session.

## 🟡 F31 — Arbel-Haddad 2022 mined - 6 Cs cumulative-leached rows for MK framework geopolymers; DOI unverifiable from the AAM and flagged as such

**Severity:** medium · **Status:** resolved

**Evidence:** Batch-4. Arbel-Haddad, Harnik, Schlosser & Goldbourt, "Cesium immobilization in metakaolin-based geopolymers elucidated by 133Cs solid state NMR spectroscopy" (J. Nucl. Mater., ~2022). Metakaolin geopolymer, Si/Al = 1 (very Al-rich framework), Na activator with Cs substituting Na at 2.5-100%. Table 4 gives the cumulative fraction of Cs leached (48 h, two-step): 2.5% 0.044, 5% 0.008, 7.5% 0.004, 25% 0.006, 50% 0.056, 100% 0.139. Leaching is LOWEST (best immobilisation) at 5-25% Cs and rises steeply at high loading - a non-monotonic loading effect. The 133Cs NMR resolves Cs SITES (structural water / framework-bound), not a Si framework descriptor, so this yields a target but no ARI. DATA-INTEGRITY NOTE: no DOI is present in this author-accepted manuscript (every DOI in the file is a bibliography reference). Provenance is recorded as a flagged citation string, NOT a guessed DOI, per the standing no-fabrication rule.

**Action:** Ingested 6 Pool B rows via _from_arbelhaddad2022 (44 -> 50 rows / 7 sources), introducing the CUMULATIVE_LEACHED_FRACTION retention type (lower = better). Provenance flagged "(DOI-unverified-AAM)"; confirm and correct the DOI when the published version is available. Loading recorded as null (Cs% is a molar Na substitution, not a wt%).

## 🟡 F33 — Foams 2020 (Petlitckaia) extracted at last - and the bare framework foam out-capacities the ferrocyanide-functionalised one in pure water

**Severity:** medium · **Status:** resolved

**Evidence:** Petlitckaia et al., J. Cleaner Production 269 (2020) 122400, doi:10.1016/j.jclepro.2020.122400 (CEA/Poulesquen). The batch-3 deferred item (mangled text layer), now read visually. Two metakaolin K-geopolymer foams: GF (bare) and FGF (functionalised with K2Cu(Fe(CN)6), a Prussian-blue analogue). Cs capacity is matrix-dependent, so THREE distinct quantities appear and are kept apart: isotherm MAX in pure water (GF 250, FGF 175 mg/g); single-point uptake at 100 ppm (GF 80, FGF 65 - a kinetics endpoint, NOT ingested); fresh-water capacity with competitive K/Na/Mg/Ca (GF 150, FGF 100). The isotherm reaches and passes saturation (capacity declines beyond Cs_eq 3.92e-3 mol/L), so the F14/theta screen is satisfied - these are genuine maxima, not extrapolations. MECHANISM SPLIT worth noting: GF removes Cs by FRAMEWORK ion exchange (Na<->Cs); FGF adds ferrocyanide (K<->Cs). In pure water the BARE FRAMEWORK out-capacities the functionalised foam (250 > 175 mg/g); FGF wins only on SELECTIVITY (Kd ~3.5e5 vs ~3.5e4 mL/g). Consistent with the framework-Al story - the aluminosilicate exchange sites carry the raw capacity; functionalisation trades some for selectivity.

**Action:** Ingested 4 Pool A rows via _from_petlitckaia2020 (137 -> 141 rows / 14 sources): 2 pure-water maxima + 2 fresh-water (competing_ion flagged). Single-point 80/65 not ingested (redundant kinetics endpoint). from_figure. Batch-3 Foams deferral CLOSED. FGF is a functionalised sorbent - flag before pooling its capacity with bare framework geopolymers.

## 🟡 F35 — Frederickx 2025 mined - 4 Cs/Sr leachability rows for a real-waste N-A-S-H form; and the accelerated NH4NO3 test is shown to flatten the Cs/Sr difference

**Severity:** medium · **Status:** resolved

**Evidence:** Batch-5. Frederickx, Mukiza, Phung et al., Sustainability 17 (2025) 1756, doi:10.3390/su17041756 (SCK CEN). A real Cs/Sr-rich nitrate waste immobilised in a metakaolin N-A-S-H alkali-activated matrix at two waste loadings. Table 5 gives accelerated (NH4NO3) leachability indices: Cs 6.9/7.0, Sr 7.0/6.7, all above the ACRIA floor of 6. METHODOLOGICAL POINT worth citing: in the accelerated NH4NO3 test Cs and Sr LIs are the same scale (~7), but the paper's own deionised-water extrapolation (Fig 5, one month) gives Cs 9.6 and Sr 12.5 - Sr >> Cs, the usual pattern. The NH4NO3 medium was built for Ca-cement and over-attacks divalent Sr, so the accelerated test UNDERSTATES Sr immobilisation and hides the Cs/Sr gap.

**Action:** Ingested 4 Pool B rows via _from_frederickx2025 (50 -> 54 rows / 8 sources) with leachant="NH4NO3_accelerated" so they are never pooled with the deionised-water LIs of the other sources (same leachant-confound discipline as the ingress/effective diffusivity split, F24). The deionised-water equivalents (Cs 9.6, Sr 12.5) are derived/extrapolated and NOT ingested, only noted. ALSO: the third file in this batch (CEMCON-D-25-01825, doi:10.1016/j.cemconres.2026.108214) is the clean manuscript of Kim 2026 - a DUPLICATE of the already-ingested kim2026 source; skipped.

## 🟡 F4 — Redundancy and version disagreement

**Severity:** medium · **Status:** partially_resolved

**Evidence:** CSV/XLSX byte-identical; 18 duplicate rows; v2 disagrees in 22 cells.

**Action:** CSV declared canonical; duplicates removed; v2 unresolved.

## 🟡 F8 — Unmined master sheets add nothing

**Severity:** medium · **Status:** resolved

**Evidence:** Adsorption_Isotherms and Cs_Isotherms duplicate Functional_Data with the same fabricated rows; only 3 new values, which are cobalt.

**Action:** Marked duplicate. Not ingested.

## 🟢 F32 — O'Donoghue 2026 assessed but NOT ingested - a purely structural study with no sorption or retention target on any sample

**Severity:** low · **Status:** resolved

**Evidence:** Batch-4. O'Donoghue, Geddes, Wilkinson, Stennett, Kim, Iuga, Hayes & Walkley, "High-field multinuclear MAS NMR and synchrotron XANES reveal the influence of strontium salt chemistry on geopolymer nanostructure", Dalton Trans. 55 (2026) 10673, doi:10.1039/d6dt00775a (the Sheffield group; same lineage as Nevin/Geddes). It varies the Sr SALT (Sr(OH)2.8H2O, SrCO3, Sr(NO3)2, SrSO4) and Sr LOADING (Sr/Al 0.025-0.125) at FIXED Si/Al = 1.5, and reports full Q4(mAl) deconvolutions (SI Tables S1-S4, 3 d and 28 d) plus XANES. But there is NO quantitative Sr target anywhere - no capacity, K_d, leachability index or diffusivity (searched: all zero). Every row would be descriptor-only.

**Action:** NOT INGESTED, by the same discipline as D7 (do not pad a pool with rows that have no usable target). Unlike Nevin's structure-only rows - which sit alongside companion rows that DO carry an LI - none of O'Donoghue's samples have a target, and Si/Al is fixed so even the descriptor does not vary across the design. It remains a useful structural reference (how Sr salt chemistry and SrCO3 formation perturb the K-A-S-H framework) and is catalogued in papers/MANIFEST.md. If a Sr uptake/retention measurement on these exact samples ever appears, revisit.

## 🟢 F5 — Metadata.csv is cp1256, not UTF-8

**Severity:** low · **Status:** resolved

**Action:** Handled in the ingestion layer.
