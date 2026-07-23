# GEOMIND — Reproduction Specification

**Milestone:** M1 · **Epic:** #1 · **Status:** draft for review
**Source:** Rousseau, S.; Bouzid, A.; Rossignol, S.; Gharzouni, A. *GEOMIND: a hybrid generative
artificial intelligence model for geopolymer design and optimization.* RSC **Digital Discovery**,
published 05 June 2026. DOI [10.1039/d5dd00383k](https://doi.org/10.1039/d5dd00383k) · CC-BY-NC 4.0
(14 pp + 7 pp SI)

> **Purpose.** A specification precise enough to implement GEOMIND from scratch and to reproduce
> every published number. Section 11 lists the gaps that must be resolved before implementation.

---

## 1. Critical discovery — the authors published code, trained models, and data

| Resource | Location |
|---|---|
| Reference implementation | `github.com/Geopolymer-AI/GEOMIND` |
| Zenodo archive | [10.5281/zenodo.20286234](https://doi.org/10.5281/zenodo.20286234) |
| Published data subset | `data/geopolymers_23_07.csv` — **10 samples**, full 26-column schema |
| **Trained weights** | `saved_models/Simulator/`, `saved_models/Formulator/` (TF SavedModel) |
| Main notebook | `GEOMIND.ipynb` (3 MB) |
| Supporting modules | `cross_validation/stratified_k_fold.py`, `data_preprocessing/{classification,normalization,viscosity}/` |

### 🔴 Legal constraint — read before writing any code

**That repository carries NO LICENSE**, i.e. **all rights reserved**. We may *read and study* it,
but we **must not copy, adapt, or vendor any of its code** into this project. All implementation
here must be **written independently from this specification**. Their published artefacts are used
only as (a) a comprehension aid and (b) an **oracle** to check our numbers against.

### Consequence for M3a

The replication strategy improves substantially: rather than reproducing blind, we can
**numerically verify our independent implementation against their published trained models and
their 10-sample subset.** Recommend a three-way check: *our implementation* vs *their weights* vs
*published tables*.

### Full dataset is obtainable

The complete **112-sample** dataset is confidential (patented compositions) but the paper states it
is **"available upon reasonable request to the corresponding author"**
(ameni.gharzouni@unilim.fr). **Action: request it.** This would remove the feature-space gap that
currently constrains M3b entirely.

---

## 2. The design problem

GEOMIND performs **inverse design**: user supplies target properties → model returns a *feasible
formulation* → and the *properties actually achievable*, correcting unrealistic requests to the
nearest Pareto-optimal achievable point.

- **Input space:** 11 precursor mass ratios ∈ [0,1], summing to 1.
- **Output space:** 4 properties — initial viscosity η₀, fresh **mixture density**, consolidated
  **material density**, **compressive strength**.

## 3. Precursors (11 classes)

| Class | Members | Role |
|---|---|---|
| Metakaolins | M1, M2, M3, M4, M5 | aluminosilicate source |
| Silicate solutions | S1, S3, S3′, SNa | alkaline activator (SNa = sodium-based) |
| Hydroxides | KOH, NaOH | modify Si/M molar ratio |

**Table 1 — chemical composition (wt %)**

| Precursor | Supplier | SiO₂ | Al₂O₃ | H₂O | M₂O (M=K/Na) | Purity % |
|---|---|---|---|---|---|---|
| M1 | Imerys | 55.0 | 40.0 | | | |
| M2 | | 54.0 | 39.0 | | | |
| M3 | | 54.0 | 46.0 | | | |
| M4 | | 52.4 | 45.3 | | | |
| M5 | Argeco | 59.9 | 35.3 | | | |
| S1 | Woellner | 14.3 | | 79.3 | 6.4 | |
| S3′ | | 23.4 | | 54.9 | 21.7 | |
| S3 | | 18.7 | | 59.4 | 21.9 | |
| SNa | | 27.5 | | 64.2 | 8.3 | |
| KOH | Sigma-Aldrich | | | | | 85.2 |
| NaOH | | | | | | 97.0 |

## 4. Database

- **112 samples** total = **98 feasible** + **14 deliberately infeasible** (do not form a geopolymer network).
- Infeasible samples carry **−1** in every property field — this is a *sentinel*, not a measurement.
- All produced under identical experimental conditions (in-house; 20 °C, sealed polystyrene moulds).
- Samples span the geopolymer domain of the **Al–Si–M/O ternary diagram**; each precursor class
  appears in 9–61 % of samples (deliberately balanced).
- **Missing data:** < 5 % (20 entries) — viscosity 5.4 %, mixture density 2.7 %, compressive
  strength 3.6 %, material density 6.2 %.

**Schema** (from the published CSV — note `;` separator and **European decimal commas**):

```
Sample | M1..M5 (wt.%) | S1, S3, SNa, S3' (wt.%) | KOH, NaOH (wt.%)
      | n Si met, n Sisol, nMSol, nMMOH, n Si, n Al, nM (mol)
      | Si, Al, M (mol.%) | Si/M Sol | Si/Al | Solid/Liquid
      | mixture density (g/cm3) | viscosity (Pa.s) | material density (g/cm3) | compressive strength (MPa)
```

The `Sample` field encodes the mixture family (e.g. `S1kSNaM1`, where `k` = KOH added).

**Measurement:** viscosity — Brookfield DV2T, LV-04(64) spindle, 100→1 rpm, Ø28 mm vessel.
Compression — Instron 5969, 50 kN cell, 10 cylinders (Ø15 × h30 mm, aspect ratio 2), after **7 days**
endogenous consolidation at room temperature, crosshead 0.5 mm min⁻¹.

## 5. Preprocessing

1. **Properties** → standardised to mean 0, std 1 — **except viscosity**.
2. **Viscosity is categorised, not standardised.** Range 0.2 – 1314 Pa·s is too wide.
   - **low** < 2 Pa·s (projectable) · **medium** 2–100 Pa·s · **high** > 100 Pa·s
   - Encoded as a **length-3 vector**: the active class holds the value normalised to [0,1];
     the other two positions are set to **−1**.
   - The model therefore predicts the viscosity *range* first, then its value. The paper states
     performance was materially worse without this trick.
3. **Precursors** — mass ratios in [0,1]; the vector sums to 1.
4. **Data augmentation** — the ~20 missing entries are *imputed by the trained Simulator*: affected
   samples are excluded from training, then predicted from the converged model and re-added.
   Verified beneficial (Table 2).

## 6. Architecture

### 6.1 Simulator — precursors → properties

VAE, densely connected feed-forward, **plus a terminal expert-knowledge (feasibility) block**.

| Stage | Layers |
|---|---|
| Encoder | Dense 128 PReLU → 128 PReLU → 64 PReLU → 64 PReLU |
| Latent | Dense μ **32** Linear · Dense log σ² **32** Linear |
| Decoder | Dense 64 PReLU → 64 PReLU → 128 **ReLU** → 128 **ReLU** |
| Heads | viscosity **3** Linear · mixture density 1 Linear · compressive strength 1 Linear · material density 1 Linear — all MAE |

**Optimizer** RMSprop · **lr** 5 × 10⁻⁴ · **epochs 250** · **batch 16**

### 6.2 Feasibility Controller (expert-knowledge block)

Computes molar ratios (silica, alumina, alkali cation, water) **from precursor mass ratios**, then
tests the mixture against established geopolymer existence domains (refs 34, 35). If chemically
infeasible → the model **returns −1 for all properties**.

Constraints named in the conclusion: **silica/alumina, silica/alkali, solid/liquid**.

*Measured value:* without this block only **5 of 9** generated samples were synthesisable
(**55.6 %**), and nMAE on strength/material density rose to ~15 % (Table 5).

### 6.3 Formulator — properties → precursors

Same VAE skeleton; **no** molar-ratio block (ratios derive from the precursors, which are the
*outputs* here).

| Stage | Layers |
|---|---|
| Encoder | Dense 128 PReLU → 128 PReLU → 64 PReLU → 64 PReLU |
| Latent | Dense μ **32** Linear · Dense log σ² **32** Linear |
| Decoder | Dense 64 PReLU → 64 PReLU → 128 ReLU → 128 ReLU |
| Heads | precursors **11 Sigmoid** · Lambda: sums 1 · Si/M 1 · Si/Al 1 · solid/liquid 1 — all MAE |

**Optimizer** RMSprop · **lr** 5 × 10⁻⁴ · **epochs 310** · **batch 16**
**Post-hoc L1 normalisation** forces predicted fractions to sum to 1.0 (stated to have negligible
effect on property predictions).

Trained *alone*, the Formulator is **unstable** — different precursor sets can yield near-identical
properties (a one-to-many inverse problem), producing large, erratic training error.

### 6.4 GEOMIND framework

Formulator trained **inside** a frozen Simulator:

```
target properties → [Formulator] → precursors → [Simulator (frozen)] → predicted properties
                                        ↓                                        ↓
                              Feasibility Controller ──────────► custom loss L
```

- The Simulator is trained **first**; its weights are **fixed** during Formulator training.
- Explicitly **not a GAN**: no adversarial objective, no minimax, no alternating updates. The
  analogy to a discriminator is *architectural only*.
- Distinct from conditional/bi-directional VAEs: **no labels** steer generation; properties are
  controlled directly from the model input, not from the latent space.

**Custom loss (eqn 1):**

```
L = w₁·MAE_precursors + w₂·MAE_sums + w₃·MAE_(Si/M_sol) + w₄·MAE_(Si/Al)
                      + w₅·MAE_(Solid/Liquid) + w₆·MAE_properties
```

where `MAE_sums = |Σ precursor fractions − 1|`, forcing a complete (100 %) composition.
**w₁–w₆ were set by trial and error, and their values are NOT published** (see §11).

## 7. Training & evaluation protocol

- **Stratified k-fold cross-validation, k = 28**, stratified by **metakaolin type** (≈ 4 samples per
  fold) — chosen to maximise training-set size on a 112-sample database. The authors note this may
  limit generalisation to novel inputs.
- All reported predictions come from **validation folds** (never seen in training).
- **nMAE** = MAE ÷ (max − min of that property in the dataset).
- **Uncertainty:** non-parametric **bootstrap, 5000 iterations**, resampling
  (prediction, observation) pairs with replacement; 95 % CI from the 2.5th/97.5th percentiles.

## 8. Reproduction targets

**Table 2 — effect of data augmentation**

| Property | Missing % | MAE w/o aug | MAE w/ aug |
|---|---|---|---|
| Viscosity (Pa·s) | 5.4 | 39.2 | **24.5** |
| Mixture density (g cm⁻³) | 2.7 | 0.097 | **0.093** |
| Compressive strength (MPa) | 3.6 | 7.9 | **7.6** |
| Material density (g cm⁻³) | 6.2 | 0.142 | **0.121** |

**Table 3 — Simulator vs XGBR (112 samples)**

| Model | Metric | Viscosity | Mixture density | Compressive strength | Material density |
|---|---|---|---|---|---|
| Simulator | MAE | 24.5 | 0.09 | 7.6 | 0.12 |
| Simulator | nMAE % | 1.9 | 14 | 9.4 | 15.5 |
| XGBR | MAE | 44.3 | 0.17 | 13.3 | 0.28 |
| XGBR | nMAE % | 3.4 | 36 | 16.5 | 37 |

**Table 4 — GEOMIND on 15 held-out synthesised samples**

| Property | Exp vs target MAE (nMAE %) | Exp vs predicted MAE [95 % CI] (nMAE %) |
|---|---|---|
| Initial viscosity (Pa·s) | 14.09 (1.07) | **8.44** [1.08, 22.2] (0.64) |
| Mixture density (g cm⁻³) | 0.17 (26.87) | **0.05** [0.04, 0.06] (8.37) |
| Compressive strength (MPa) | 11.40 (14.07) | **7.60** [4.73, 10.8] (9.39) |
| Material density (g cm⁻³) | 0.17 (21.94) | **0.02** [0.01, 0.03] (3.40) |

**Table 5 — ablation: GEOMIND *without* the feasibility controller** (5 feasible of 9 = 55.6 %)

| Property | Exp vs target MAE (nMAE %) | Exp vs predicted MAE (nMAE %) |
|---|---|---|
| Initial viscosity (Pa·s) | 17.32 (1.32) | 9.43 (0.72) |
| Compressive strength (MPa) | 24.20 (29.88) | 12.00 (14.81) |
| Material density (g cm⁻³) | 0.21 (26.41) | 0.12 (15.64) |

**Table S3 — Formulator loss** · with GEOMIND 0.092/0.094 (train/val) · without 0.118/0.123

**Table S4 — generative-head variants (within GEOMIND)**

| Model | Precursor MAE train/val | Property MAE train/val |
|---|---|---|
| MLP | 0.087 / 0.096 | 0.275 / 0.261 |
| **Gaussian VAE** (chosen) | 0.092 / 0.094 | 0.282 / **0.249** |
| Student's-t VAE | 0.091 / 0.098 | 0.284 / 0.291 |

**Table S7 — Bayesian-optimisation baseline** (BO over precursor ratios on top of the Simulator,
minimising target-vs-predicted MAE; single target set per run)

| Property | Exp vs target MAE (nMAE %) | Exp vs predicted MAE (nMAE %) |
|---|---|---|
| Initial viscosity (Pa·s) | 102 (7.7) | 150 (11.4) |
| Mixture density (g cm⁻³) | 0.26 (39) | 0.112 (17) |
| Compressive strength (MPa) | 18 (22) | 5.7 (7) |
| Material density (g cm⁻³) | 0.156 (20) | 0.088 (11) |

**Table S5** gives the full target/predicted/experimental triplets for all 15 test samples —
already present in our `data/raw/GEOMIND_RADIOACTIVE_MASTER.xlsx → Validation_Samples`
(45 rows = 15 samples × 3 property types). ✅

**Figures:** Fig 3A ternary feasibility map · Fig 4 2-D property histograms · Figs 6, 8, 10, 11 loss
curves · Fig 12 three use-cases on the property heat map · Figs S1–S2 parity plots + bootstrap
distributions.

## 9. Headline claims to test

1. Overall **nMAE < 10 %** across all four properties on experimental validation.
2. Simulator error ≈ **half** that of XGBR.
3. The feasibility block raises synthesisability from **55.6 % → ~100 %**.
4. GEOMIND-trained Formulator beats a standalone Formulator (0.094 vs 0.123 val MAE).
5. GEOMIND outperforms Bayesian optimisation (qualitative comparison only in the paper).

## 10. Cross-check against our data

| Paper artefact | Our file | Status |
|---|---|---|
| 10-sample public subset | `GEOMIND_RADIOACTIVE_MASTER.xlsx → GEOMIND_Samples` (10 × 26) | ✅ matches schema |
| Table S5 (15 test samples) | `→ Validation_Samples` (45 × 6) | ✅ present |
| Feasibility domains | `→ Feasibility_Ranges` (9 × 5) | ⚠️ verify against refs 34/35 |
| Full 112 samples | — | ❌ confidential; request from author |
| 867-row compilation | `Physical_Data` | ⚠️ different feature space (see README) |

## 11. Gaps, ambiguities & risks

| # | Gap | Severity | Resolution |
|---|---|---|---|
| G1 | **Loss weights w₁–w₆ are not published** ("trial and error"). | 🔴 blocking | Infer from `GEOMIND.ipynb`; else treat as hyperparameters and tune. Document as a deviation. |
| G2 | **KL-divergence term not specified.** Tables list only MAE heads; a VAE normally needs reconstruction + KL, with a β weight. | 🔴 blocking | Determine from reference notebook / saved models. |
| G3 | **Feasibility rules not fully stated** — thresholds for Si/Al, Si/M, solid/liquid and the ternary existence domain come from refs 34–35. | 🟠 high | Extract from refs 34/35 + `Feasibility_Ranges`; validate against the 14 known-infeasible samples. |
| G4 | Viscosity "normalised between 0 and 1" **within its class** — exact scaling ambiguous. | 🟠 high | Recover from `data_preprocessing/viscosity/split.py` behaviour (read-only). |
| G5 | Only **10 of 112** samples public → we cannot reproduce Tables 2/3 at full scale. | 🟠 high | Request full dataset; otherwise reproduce structure and report on the subset only, clearly labelled. |
| G6 | Latent sampling/reparameterisation and whether the Simulator is used stochastically or at the mean is unstated. | 🟡 medium | Inspect saved models. |
| G7 | Stratified 28-fold on 112 samples → ~4 per fold; high variance. Bootstrap CIs are wide for viscosity ([1.08, 22.2]). | 🟡 medium | Reproduce CIs; do not over-read point estimates. |
| G8 | Paper's own numbers are internally inconsistent for the final MAEs: conclusion quotes 12.2 Pa·s / 0.063 / 7.2 MPa / 0.024 vs Table 4's 8.44 / 0.05 / 7.60 / 0.02. | 🟡 medium | Flag; ask the authors when requesting data. |

## 12. Implementation plan (feeds M3a, issue #3)

1. **Independent reimplementation** in PyTorch from this spec — no code copied (§1).
2. Ingest `geopolymers_23_07.csv` (`;` sep, comma decimals, −1 sentinels) into our schema.
3. Build the Feasibility Controller first and validate it on the 14 known-infeasible samples.
4. Implement Simulator → reproduce parity plots on available samples.
5. Implement Formulator; then wrap in GEOMIND with the frozen Simulator.
6. Resolve G1/G2 by comparing our outputs to their **published trained weights** as an oracle.
7. Reproduce Tables 3–5 as far as the 10-sample subset allows; report honestly what cannot be
   reproduced without the confidential 112.

---

### Recommended immediate actions

- **A1 — Email the corresponding author** requesting the 112-sample dataset. Highest-leverage
  single action in the project: it removes G5 and unblocks a true M3b.
- **A2 — Study `GEOMIND.ipynb`** read-only to close G1, G2, G4, G6. Record findings here; copy no code.
- **A3 — Extract feasibility domains** from refs 34–35 to close G3.
