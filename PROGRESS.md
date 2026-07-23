# 📌 PROGRESS — pinned status

**Updated:** 2026-07-20 · **Branch:** `dev` · **Pool A:** 141 rows / 14 sources · **Pool B:** 54 rows / 8 sources · **Tests:** 125 passing

> 📋 **Retrospective (plan vs achieved): [`reports/plan-vs-achieved.md`](reports/plan-vs-achieved.md)** — setup brief 7/7; M1/M2/M6 done, M3b re-scoped, M3a/M5 (generative core) blocked; the block became a publishable finding + manuscript.
>
> ✅ **DATA-SUFFICIENCY ANALYSIS (F36/D17): [`reports/data-sufficiency-analysis.md`](reports/data-sufficiency-analysis.md)** — **acquisition has hit NEGATIVE returns. STOP acquiring; advance.** Within-class model LOO-CV R²=**0.81**; pooled cross-lab R²=**−0.09**. The finding is saturated (5 convergent lines). Next stage = the paper + within-class forward model. Generative M5 needs single-protocol data (GEOMIND / own-lab), not more papers.
>
> ⭐ **Batch-4 (11 new papers): [`reports/batch-4-report.md`](reports/batch-4-report.md)** — **F27: a within-sample causal test — leaching strips framework Al and sorption falls with it (corr Δ[Al^IV],ΔK_D = +0.938). Q9 & Q10 closed.**
>
> 🔴 **Q7 descriptor hunt: [`reports/q7-descriptor-hunt-report.md`](reports/q7-descriptor-hunt-report.md)** — **F20: Al^IV scarcity is structural. A PI decision is required on the M4/M5 target property.**
>
> **ARI backfill: [`reports/ari-backfill-report.md`](reports/ari-backfill-report.md)** — descriptor did **not** widen; it gained a structural precondition (F19)
>
> **Isotherm validation: [`reports/isotherm-validation-report.md`](reports/isotherm-validation-report.md)** — 35/35 screened, 3 artefacts excluded
>
> **Full technical report: [`reports/PROJECT-REPORT.md`](reports/PROJECT-REPORT.md)** — discoveries,
> results, methodology and honest limits in depth.
>
> Entry point for any new session. Detail lives in
> [`docs/knowledge-base/`](docs/knowledge-base/README.md) (generated from
> `knowledge_base/registry.yaml`). This file is the *map*, not the territory.

---

## Where the project actually stands

| Milestone | State | Note |
|---|---|---|
| **M1** Paper analysis | ✅ done | Reproduction spec written; authors' code found (no license → clean-room only) |
| **M2** Data cleaning & audit | ✅ done | 32 % of the compiled data failed source audit |
| **M3a** Chemistry layer | ✅ verified | Si/Al, Si/M_sol, Solid/Liquid reproduce the paper within 1–3 % |
| **M3a** Simulator/Formulator VAE | ⬜ not started | Blocked on G1/G2 (loss weights, KL term) |
| **M3b** Cross-system transfer | 🔄 re-scoped | Not a GEOMIND validation — different material system |
| **M4** Adsorption dimension | ✅ **demonstrated** | Within-class forward model built (`src/geomind/model/forward.py`, F37): LOO-CV R²=**0.81**, domain-guarded |
| **M5** Radionuclide design | ⬜ blocked | Needs M4 |
| **M6** Corpus expansion | ✅ **CLOSED (D17)** | Acquisition at negative returns — stop. Broad scraping/crawling would add noise, not signal (F36) |

## The scientific finding so far

**In Q⁴-rich framework aluminosilicates, surface area has little predictive power for cations;
framework aluminium does. Outside that structural class, neither does.**

| Evidence | Result |
|---|---|
| Varon (n=7) | corr(BET, K_d) **+0.19** vs corr(Al^IV, K_d) **+0.95** |
| **Varon leached — causal (F27)** | corr(**Δ[Al^IV], ΔK_d**) **+0.938** — losing framework Al *loses* sorption, same sample |
| Varon [Al^IV] conc. (n=7) | corr(**[Al^IV] mmol/g**, K_d) **+0.946** (+0.986 excl. outlier) — concentration beats % and ARI |
| **Geddes 2025 — atomic mechanism (F34)** | EXAFS + NMR: Sr²⁺ binds at **extra-framework charge-balancing sites bonded to Al^IV** (Si^IV–O–Al^IV) — the descriptor's sites, imaged directly |
| Oulu Ca-free (n=4) | corr(ARI, NH₄⁺) **+0.932** |
| Xiang foams (n=5) | BET ↓ 53.8→37.8 while uptake ↑ 161.8→192.1 (**−0.90**) |
| Lin (n=4) | **−0.90** |
| Oulu NH₄⁺ (n=21) | **−0.47** |
| Tarnovsky (n=6) | **+0.22** — inconclusive |
| **Pooled cations** | **+0.08** |
| **Dyes** | **+0.66** — opposite sign; never pool adsorbate classes |

⚠️ An earlier claim of *"six datasets confirm a negative BET correlation"* was an **overstatement**,
corrected as finding **F9**. The defensible claim is the narrower one above.

⚠️ **F19 — the descriptor has a structural precondition.** In Ca-bearing gels (Q⁴ ≈ 0)
**nothing** predicts uptake: ARI −0.108, Si/Al −0.135, Ca/Al −0.104, BET +0.462, with capacity
nearly flat at **7.27 ± 1.31 mg/g**. Pooling all 12 NMR-characterised sorbents yields ARI
**+0.536** — an average of two unrelated regimes (+0.932 and −0.108), not a weak correlation.
**Never pool sorbent structural classes** (D12), just as adsorbate classes must not be pooled.

## Hard constraints (do not re-litigate)

1. **52 Cs/Sr rows.** Inverse design is not reachable. Forward modelling is marginal.
2. **The Al descriptor applies to 11 sorbents, and the ARI backfill did not change that.**
   39 rows now carry ARI, but 8 of the 12 sorbents gained fall outside its domain of validity
   (F19). Evidence base remains Varon n=7 (Sr) + Oulu n=4 (NH₄⁺). Logged as **Q7**.
3. **GEOMIND's 112 samples are confidential.** Faithful replication is blocked without them.
4. **Our data is fly-ash concrete, not metakaolin paste** — M3b cannot claim replication.

---

## 🔴 Blocked on Mulham — nothing proceeds without these

| # | Action | Why it matters |
|---|---|---|
| 1 | **Send** `docs/correspondence/2026-07-19-geomind-dataset-request.md` | 112 samples — bigger than every scraping avenue combined |
| ~~2~~ | ~~Send the Oulu NMR letter~~ | ✅ **UNNECESSARY 2026-07-20** — F18: the values are published in Table 2 of the same paper |
| 3 | Acquire ***Next Sustainability* 2025** (`S2950631X25000024`) | Only 1–5 M activator axis anywhere, with Cs *and* Sr *and* NMR |
| ~~4~~ | ~~Purge GitHub PR refs~~ | ✅ **DONE 2026-07-20** — repo deleted + recreated; 0 PR refs, old commit unfetchable. Record archived to `docs/github-archive/` first |
| ~~Q8~~ | ~~Acquire Geddes 2025~~ | ✅ **DELIVERED by supervisor 2026-07-21** — F34: the atomic mechanism (Sr at Al^IV charge-balancing sites). The Checkpoint-2 §5 top ask is now fulfilled. |
| ~~5~~ | ~~Mint the Checkpoint-1 restricted DOI~~ | ✅ **SUPERSEDED 2026-07-23** — the project went **public** under AGPL-3.0. The DOI is now minted automatically by Zenodo from a public GitHub Release (see `docs/zenodo-deposit-instructions.md`). The manuscript is withheld pending peer review. |

---

## 📥 Batch 3 — extraction outcome (2026-07-20)

| Paper | Verdict |
|---|---|
| **Baek 2018** `10.1016/j.micromeso.2018.01.025` | ✅ **ingested (3 rows)** — Cs Langmuir + CEC + Si/Al for chabazite/stilbite/heulandite |
| **Foams 2020** `10.1016/j.jclepro.2020.122400` | ✅ **extracted (F33)** — Petlitckaia foams; 4 Cs rows. Bare framework (250) out-capacities functionalised foam (175) in pure water |
| J. Environ. Manage. 370 (2024) | ✅ **re-read (F25)** — rejection upheld (it's a review), but it *names* the paired-data sources both pools lack |
| **Kurumisawa 2021** | 🔄 **REJECTION OVERTURNED (F24)** — Fig. 3b publishes Cs monolayer capacities for 5 activators. Now in **both** pools |

**3 of 5 carry capacity data** after Kurumisawa was re-read. ⚠️ **The triage was keyword-based,
and a capacity that lives only in a figure is invisible to keyword counts.** Every remaining
triage rejection must be re-read inline before the rejection is trusted (**D15**).

### ⚠️ F14 — a high R² does not mean a meaningful Qmax
Baek's chabazite fits **Q0L = 1249.5 mg/g at R² = 0.99989** — yet the same paper reports
equilibrium uptake of **1.184 mg/g**. Its K_L (7.9e-05) is two orders below the other two
zeolites. At low coverage the Langmuir form is near-linear, so it fits almost perfectly while the
plateau is extrapolated ~1000× beyond any measured point. Ingested but **flagged** — it breaches
the schema bound and `validate()` reports it.

**Generalises:** screen future Langmuir rows on **K_L and the measured concentration range**, not
R² alone.


## Verification record — the audit trail is a contribution in itself

| Finding | What it was |
|---|---|
| **F1** | `Si_Al`/`Density` transplanted from the paper into concrete data |
| **F6** | `Feasibility_Ranges` fabricated from the retired tool; anti-correlated with truth |
| **F7** | 32 % of compiled rows failed audit — **europium labelled as strontium**, a fabricated sorbent, a misattribution |
| **F11** | `Sr_Immobilization_Mechanisms` untraceable, 66.7 % duplicated |
| **F12** | The v2 "conflict" was precision, not disagreement — resolved |
| **NMR** | Deconvolution **rejected despite both pre-registered gates passing** — Q⁴(3Al) ≡ 0 is chemically impossible |

**Standing rule:** no row enters the pool without its value being read *in context* in the source
PDF. A number existing somewhere in a paper is not evidence of what it means.

## Next action when work resumes

**The data is sufficient for a descriptor + methodology paper. It is not sufficient for M5
inverse design — and Q7 established that more scraping will not make it sufficient.**

### ✅ PI decision taken 2026-07-20 (D13) — two parallel pools, never merged

Al^IV and adsorption capacity are **near-disjoint in the literature** (F20): all 13 adsorption
papers report zero solid-state NMR, while 4 of the 6 NMR-rich papers are immobilisation studies.
Varon is the only bridge — which is exactly why Al^IV sits in 7 rows.

| Pool | Target | Status |
|---|---|---|
| **Pool A — adsorption** | Langmuir *Q*max, K_d | ✅ **126 rows / 11 sources** — audited, isotherm-screened |
| **Pool B — immobilisation** | leachability index, *D*_eff, CLF | ✅ **40 rows / 4 sources** — 22 LI + 10 ingress-D + 6 structure-only. [`report`](reports/pool-b-immobilisation-report.md) |

**⚠️ Both pools are descriptor-starved, for opposite reasons (F22).**
Pool A has composition without NMR; Pool B has NMR without composition — Nevin is one
formulation at Si/Al = 3, so ARI is nearly constant (2.738–2.855) across its 4 paired rows.
**Neither pool supports a descriptor model yet.**

**Pool B audit results (F21, F22).** `Sr_Leaching_Data` was audited against source for the
first time, and Pool B was then built from the papers directly:

- ✅ **`LI = −log₁₀(De)` confirmed against two independent tables** — Kim (12/13 cells to ±0.06)
  and Nevin (4/4). The LI column is the first immobilisation target to survive audit.
- 📄 **A published erratum found.** Kim Table 2 cell `NaSr1 @ 2 h` prints `8.88 E-16 (15.5)`,
  but −log₁₀(8.88e-16) = **15.05**. Kim's own column average of 15.5 equals mean(15.05, 15.94)
  exactly; a true 15.5 would average to 15.7. **The paper's own arithmetic convicts the cell.**
  Verified at 430 dpi — not a rendering artefact.
- ❌ **`De_cm2_s` corrupted to 0.0** in every master row (Kim reports 8.88e-16 … 5.80e-18, and
  time-resolved at that, so no scalar De pairs with an averaged LI).
- ❌ **Both `Yildirim_2024` rows misattributed** — 7.87 / 7.95 are Kim's own NaSr3 pre/post
  EXAFS coordination numbers, credited by Kim to Geddes 2025. Third instance of the F7 pattern.
- ❌ **The master sheet silently dropped Nevin's two Cs rows** (LI 13.3, 13.2) — a 50 % loss of
  that table, undetectable without reading the source.
- 🔬 **Nevin's headline preserved:** in the *same* K–A–S–H gel, Sr is retained ~**6 orders of
  magnitude** better than Cs (De 7.8e-20 vs 6.0e-14). At fixed composition, nuclide identity
  dominates structure entirely.

### Next

0. ✅ **Done — J. Environ. Manage. 370 re-read (F25).** Upheld as data, but it surfaced 3 leads:
   **Komljenović 2020** (NMR+Cs bridge, **Q9**), **Qian 2001** (Cs/Sr K_d, **Q10**), and
   **Jang 2016** — a Pool B diffusivity source **already on disk**, unmined (**Q11**).
**🔴 The next moves need Mulham — see the full list at [`docs/acquisition-worklist.md`](docs/acquisition-worklist.md).**

1. 🔴 **Acquire Geddes 2025 (Q8) and Komljenović 2020 (Q9)** — the two identified NMR+composition+
   retention bridges. The only routes past the descriptor deadlock (F20/F22). Highest leverage
   after the GEOMIND dataset.
2. **Acquire Qian 2001 (Q10)** — Cs/Sr K_d for Pool A.
3. **Foams 2020 table pass** — capacity data behind a mangled text layer (on disk, no acquisition).
4. **Send the GEOMIND letter** (blocker #1) — still the highest-leverage unactioned item.
