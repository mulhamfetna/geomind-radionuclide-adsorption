# Laboratory campaign protocol — extending the framework-Al descriptor beyond n = 7

**Prepared:** 2026-07-24 · For: Dr. Abdulrazzaq Hammal, Dept. of Basic Science – Chemistry
**Basis:** finding F43 (`reports/n7-ceiling-analysis.md`) · **Status:** proposal for review

---

## 1. Why this campaign, in one paragraph

Our forward model — Sr K_D from framework aluminium — predicts held-out samples with leave-one-out
R² = 0.81, but it is fit on **n = 7**. We have now proven exhaustively (F43) that **no additional
row exists anywhere in the published literature**: framework Al^IV is reported alongside Cs/Sr
uptake in exactly one laboratory's series, and every route to enlarging it fails. The ceiling is
structural, not an oversight. Only new laboratory data breaks it — and the amount required is
modest.

**What this campaign is not:** it is not "more data". It is *composition-varying data measured under
one protocol in one preparation state* — the one thing the literature cannot supply.

---

## 2. What the existing n = 7 looks like, and the gap to fill

Varon's series (the entire published basis of the model):

| sample | Si/Al | [Al^IV] mmol g⁻¹ | Al^IV % of total Al | BET m² g⁻¹ | Sr K_D mL g⁻¹ |
|---|---|---|---|---|---|
| K-0.5-16 | 1.14 | **4.77** | 96.0 | 72 | 4100 |
| K-1-16 | 1.55 | 4.14 | 93.8 | 163 | 2500 |
| K-1.2-12 | 1.63 | 3.83 | 92.4 | 182 | 1900 |
| K-1.2-16 | 1.67 | 3.94 | 94.0 | 188 | 1800 |
| Na-1.2-16 | 1.67 | 3.45 | 84.7 | 38 | 900 |
| K-1.5-16 | 1.79 | 3.71 | 91.4 | 212 | 1100 |
| K-1.2-8 | 1.83 | **3.61** | 88.0 | 15 | 70 |

**Three deficiencies this campaign fixes:**

1. **The window is narrow.** Si/Al spans only 1.14–1.83; [Al^IV] only 3.45–4.77 mmol g⁻¹. Any
   prediction outside that band is extrapolation, and our software flags it as such.
2. **The sorption conditions were never reported** — C₀, solid/liquid dose, pH and contact time are
   all absent from the source. We must record every one of them.
3. **A cation confound sits inside the series.** `Na-1.2-16` has the same Si/Al (1.67) as
   `K-1.2-16` but a much lower Al^IV (3.45 vs 3.94) and half the K_D. **Hold the activator cation
   fixed** (all K⁺) so this cannot contaminate the new series.

---

## 3. Two versions — choose by available effort

| | **A — Minimum viable** | **B — Full campaign** |
|---|---|---|
| Samples | **8** (6 compositions + 2 replicates) | **14** (11 compositions + 3 replicates) |
| Si/Al range | 1.0 – 2.25 | 1.0 – 2.5 |
| What it buys | Independent **reproduction** in a second laboratory: converts *"holds in one lab's 7 samples"* into *"reproduces"* | n ≈ 20 combined; a genuinely estimable LOO-CV; a widened validated domain; **the paired data a generative model needs** (reopens M4-generative, M5) |
| NMR sessions | 8 × (²⁹Si + ²⁷Al) | 14 × (²⁹Si + ²⁷Al) |

**Version A is the recommended starting point.** It is the smaller ask and buys most of the
credibility; version B can follow if A succeeds.

---

## 4. Design of the composition series

**The single design knob is the activator silicate modulus**, which sets Si/Al, which sets framework
Al^IV. In Varon's series the modulus (the middle number in their labels: 0.5 → 1.5) maps
monotonically onto Si/Al (1.14 → 1.79). We use the same lever and push it **wider at both ends**.

**Version A — 6 compositions, each in the form K-x:**

| ID | target Si/Al | expected position | purpose |
|---|---|---|---|
| GR-1 | **1.00** | below Varon's minimum | extends the domain upward in Al^IV |
| GR-2 | 1.25 | inside | overlap — direct comparison with Varon |
| GR-3 | 1.50 | inside | overlap |
| GR-4 | 1.75 | inside | overlap |
| GR-5 | 2.00 | above Varon's maximum | extends the domain downward in Al^IV |
| GR-6 | **2.25** | well above | tests where the relationship ends |
| GR-3r, GR-5r | replicates of GR-3 and GR-5 | — | **within-laboratory reproducibility** |

**Version B** adds Si/Al = 1.15, 1.40, 1.65, 1.90, 2.50 and a third replicate.

**Fixed for every sample (non-negotiable — this is the whole point):**

- one metakaolin batch · one activator cation (**K⁺**) · one alkali/Al ratio (K₂O/Al₂O₃ = 1.0)
- one water content (H₂O/K₂O ≈ 11) · one cure (sealed, 40 °C, 24 h, then 20 °C to 28 d)
- one preparation state — **no leaching, no post-treatment** (F43: the descriptor does not survive a
  change of state)
- **Ca-free throughout** — no slag, no Portland, no high-Ca fly ash (F19/F41: Ca²⁺ competes for the
  very sites we are counting)

### Mix calculation

Si/Al is computed on a molar basis over the whole mix:

$$\mathrm{Si/Al} = \frac{n_{\mathrm{SiO_2}}^{\text{metakaolin}} + n_{\mathrm{SiO_2}}^{\text{activator}}}{2\,n_{\mathrm{Al_2O_3}}^{\text{metakaolin}}}$$

Obtain the metakaolin's SiO₂ and Al₂O₃ content by **XRF on the actual batch** (do not assume the
ideal Al₂O₃·2SiO₂), then solve for the mass of potassium silicate solution needed per target Si/Al.
Our repository can do this calculation and check it — `geomind.chemistry` computes Si/Al, Si/M_sol
and solid/liquid from mass fractions and is verified to 1–3 %.

---

## 5. Synthesis

1. **Metakaolin** — calcine kaolin at **750 °C for 3 h** (heating rate 5 °C min⁻¹), cool in a
   desiccator. Use **one batch** for the whole series. Record XRF composition, and XRD to confirm
   the kaolinite reflections are gone (amorphous halo only).
2. **Activator** — KOH pellets + potassium silicate solution + deionised water, prepared to each
   target modulus. **Prepare 24 h in advance** and let it equilibrate to room temperature (silicate
   speciation is not instantaneous, and this is a common source of irreproducibility).
3. **Mixing** — add activator to metakaolin, mix mechanically 10 min to a homogeneous paste. Record
   the exact masses.
4. **Casting and curing** — cast in sealed polypropylene moulds, cure **40 °C / 24 h sealed**, then
   demould and keep sealed at 20 °C until **28 d**.
5. **Preparation for testing** — crush and sieve to a **single, recorded size fraction** (e.g.
   100–200 µm) for every sample. Particle size affects both BET and sorption kinetics; it must not
   vary across the series.

---

## 6. Characterisation — the measurements that matter

### 6.1 Solid-state NMR (this is the measurement no published paper provides alongside uptake)

- **²⁷Al MAS NMR** → fraction of aluminium in **tetrahedral** coordination (Al^IV, δ ≈ 55 ppm)
  versus octahedral (δ ≈ 0 ppm). Reference: 1.0 M aqueous Al(NO₃)₃ at 0 ppm.
- **²⁹Si MAS NMR** → **Q⁴(mAl) deconvolution** giving the Q⁴(4Al), Q⁴(3Al), Q⁴(2Al), Q⁴(1Al),
  Q⁴(0Al) populations. Reference: TMS at 0 ppm.

**Then:**

$$[\mathrm{Al^{IV}}]\ (\mathrm{mmol\,g^{-1}}) = \text{total Al (mmol g}^{-1}\text{)} \times f_{\mathrm{Al^{IV}}} \qquad
\mathrm{ARI} = \frac{\sum_m m \cdot I_m}{100}$$

where total Al comes from XRF and $f_{\mathrm{Al^{IV}}}$ from the ²⁷Al spectrum. Our
`geomind.data.nmr_ari` module computes ARI from the Q⁴ populations and **refuses to compute it when
the m-assignment is ambiguous** (decision D16) — send us the deconvolution and it will be checked
automatically.

> **Deconvolution discipline (learned the hard way — findings F23, F18):** fit the **minimum**
> number of Gaussian peaks; keep the isotropic shift and FWHM consistent across the series; and
> report the populations, not only a derived ratio. An ambiguous deconvolution can fork ARI by a
> factor of 2.7, which is worse than no value at all.

### 6.2 Supporting characterisation

| measurement | purpose |
|---|---|
| **XRF** (metakaolin + each product) | total Al and Si — needed to convert NMR fractions into mmol g⁻¹ |
| **XRD** | confirm amorphous gel; flag any zeolite crystallisation (a separate uptake pathway — cf. F42) |
| **BET N₂** | to test the surface-area hypothesis *in our own data*. Expect it **not** to predict uptake (this is our central negative result — Varon's BET correlates only +0.19 with K_D, and Vandevenne independently found no BET–retention correlation) |
| **pH of the pore solution / leachate** | a control variable that must be recorded, not assumed |

---

## 7. Sr uptake — the batch sorption test

**Every parameter below must be identical across the series and recorded.** (Their absence in the
published source is precisely the provenance weakness we are correcting.)

| parameter | value | note |
|---|---|---|
| Adsorbate | **Sr(NO₃)₂** in deionised water | non-radioactive Sr²⁺ as the ⁹⁰Sr surrogate |
| C₀ | **fixed**, e.g. 50 mg L⁻¹ | one value for the comparative series |
| Solid/liquid dose | **fixed**, e.g. 1.0 g L⁻¹ | |
| Contact time | **24 h** | justify with one kinetics run (below) |
| Temperature | 25 ± 1 °C | |
| pH | measure at start **and** end; do not adjust unless you adjust for all | |
| Agitation | fixed rpm, end-over-end or orbital | |
| Separation | 0.45 µm filtration | record whether centrifuged first |
| Analysis | **ICP-OES** (or AAS) for Sr | run a blank and a spike recovery |
| Replicates | **triplicate per sample** | report mean ± standard deviation |

$$K_D = \frac{C_0 - C_e}{C_e}\cdot\frac{V}{m}\quad(\mathrm{mL\,g^{-1}})$$

**Two additional runs, once each (not per sample):**

- **Kinetics** — one mid-series sample sampled at 0.5, 1, 2, 4, 8, 24, 48 h, to justify the chosen
  contact time as equilibrium.
- **Isotherm** — one mid-series sample at 5–6 values of C₀, to fit a Langmuir capacity **and** apply
  our own saturation screen (below).

---

## 8. Quality gates — apply our own screens before the data enters the database

1. **Saturation screen (F14–F17).** If a Langmuir capacity is fitted, compute
   θ = b·C₀ / (1 + b·C₀) = 1 − R_L. **Require θ ≥ 0.8.** If θ < 0.5, the fitted q_max is an
   extrapolation artefact and must not be reported as a capacity — this is the exact error we
   identify in **4 of the 31** fitted capacities we screened from the literature (13 %), so our own
   data must clear the same bar.
2. **Mass balance.** Sr recovered + Sr in solution should close to within ~10 %.
3. **Replicate agreement.** The two replicate compositions should agree within the analytical
   uncertainty. If they do not, the synthesis is not yet controlled enough for the series to mean
   anything — fix that before proceeding.
4. **Al^IV plausibility.** Expect ~85–96 % of Al tetrahedral (Varon's range). A much lower value
   suggests incomplete geopolymerisation.
5. **Blank and spike recovery** on the ICP run.

---

## 9. What to record — one row per sample

Send the data in any tabular form containing these fields; it maps directly onto our schema and can
be ingested and checked immediately:

```
sample_id, target_si_al, measured_si_al_xrf, metakaolin_batch,
activator_cation, silicate_modulus, k2o_al2o3, h2o_k2o,
cure_temp_C, cure_days, particle_size_um,
al_total_mmol_g, al_iv_fraction, al_iv_mmol_g,
q4_4al_pct, q4_3al_pct, q4_2al_pct, q4_1al_pct, q4_0al_pct, ari,
bet_m2_g, xrd_phases,
sr_c0_mg_L, dose_g_L, contact_time_h, pH_initial, pH_final, temp_C,
sr_ce_mg_L_rep1, rep2, rep3, kd_mL_g_mean, kd_sd
```

---

## 10. What success looks like

- **Version A (n = 8):** the descriptor reproduces in a second, independent laboratory under fully
  reported conditions. Combined with Varon, n ≈ 15. This is the difference between *"we found a
  relationship in one published series"* and *"the relationship reproduces"* — the single strongest
  improvement available to the paper.
- **Version B (n = 14):** n ≈ 20 combined, a widened validated domain, and the composition ↔
  structure ↔ property triples that a **generative** inverse-design model requires — reopening the
  milestones currently blocked (M4-generative, M5).

**A negative result is also a result.** If the relationship does *not* reproduce, that is a genuine
and publishable finding about descriptor transferability — and far better learned in our own
laboratory, under controlled conditions, than assumed.

---

## 11. Open decisions for the PI

1. **Version A or B** to start.
2. **NMR access** — is ²⁹Si/²⁷Al MAS NMR available in-house, or does it need an external facility?
   *This is the critical-path item; everything else is standard wet chemistry.*
3. **Sr analysis** — ICP-OES available, or AAS?
4. Whether to include a **small Na⁺ sub-series** later, to quantify the cation effect visible in
   Varon's data as a deliberate factor rather than a confound.
