# Implementation plan — ²⁹Si NMR deconvolution (Oulu series)

**Goal:** convert raw ²⁹Si MAS-NMR spectra into **Q⁴(mAl) populations**, and from those a
per-sample **framework-charge descriptor** (accessible tetrahedral Al). This is the one variable
that actually predicted uptake (r = +0.95 in Varon), and it currently exists in **7 of 118** rows.

**Why it is worth the risk:** the data is already on disk, it is a *designed* composition series
(Si/Al 1–20), and it would take the key descriptor from 7 rows to ~19.

---

## ⚠️ The core risk

Deconvolution is **under-determined**. Five overlapping peaks can fit the same curve many ways;
different constraints shift the Q⁴(mAl) populations substantially. A careless fit returns
confident numbers that are artifacts — the same failure mode as the `0.3 m²/g` BET bug, but far
harder to detect because the output *looks* physically plausible.

**Therefore this plan is built around one non-negotiable idea: an independent ground truth.**

---

## 🔑 The validation gate that makes this defensible

For a Q⁴(mAl) distribution, the framework Si/Al ratio follows the **Engelhardt relation**:

```
Si/Al  =  Σ(m=0..4) I_m  /  Σ(m=0..4) 0.25 · m · I_m
```

where `I_m` is the intensity fraction of the Q⁴(mAl) peak.

**We independently know the true Si/Al for every Oulu sample** — they were synthesised to
designed molar ratios (Si1Al1Na1 … Si20Al1Na1), and confirmed by XRF.

So: **deconvolve → compute Si/Al from the fitted populations → compare against the known
synthesis Si/Al.** If the fit is wrong, this comparison fails. That is a genuine, falsifiable
check, not a self-consistency argument.

> **Accept/reject criterion, fixed in advance:** the deconvolution is accepted only if
> NMR-derived Si/Al tracks designed Si/Al with **r ≥ 0.9** and no systematic bias in the residual.
> If it fails, the result is reported as failed — not tuned until it passes.

Pre-registering the threshold matters: with enough freedom, any fit can be massaged into
agreement. Fixing the criterion before fitting is what stops that.

---

## Steps, each with its own gate

### Step 1 — Parse and sanity-check the raw spectra
- Read `Si NMR AAMs & geopolymers/All data.xlsx` (2050 × 48 = 12 samples × [Index, Intensity, Hz, ppm]).
- Map each spectrum to its sample ID via the synthesis sheet.
- **Gate 1:** every spectrum covers the diagnostic window (≈ −70 to −120 ppm); ppm axis is
  monotonic; no all-zero or truncated traces. Report how many of the 20 compositions actually
  have NMR (first inspection suggested **12**, not 20 — confirm and state it).

### Step 2 — Baseline correction
- Fit and subtract a low-order polynomial baseline using signal-free regions only.
- **Gate 2:** post-correction, signal-free regions have mean ≈ 0 (within noise σ). Plot for
  visual confirmation; do not proceed on a numeric check alone.

### Step 3 — Constrained peak fitting
- Five Gaussian components at literature Q⁴(mAl) positions, **constrained**:
  | Component | centre (ppm) | allowed drift |
  |---|---|---|
  | Q⁴(4Al) | −84 | ±3 |
  | Q⁴(3Al) | −89 | ±3 |
  | Q⁴(2Al) | −93 | ±3 |
  | Q⁴(1Al) | −99 | ±3 |
  | Q⁴(0Al) | −108 | ±4 |
- Shared line width across components (physically motivated; also reduces free parameters from
  15 → 11 and materially reduces the under-determination).
- Amplitudes ≥ 0.
- **Gate 3:** fit R² ≥ 0.98 **and** residuals show no systematic structure (a high R² with
  patterned residuals means the peak model is wrong).

### Step 4 — Stability / non-uniqueness test
- Refit each spectrum from **≥ 20 randomised initial conditions**.
- **Gate 4:** report the spread of each Q⁴(mAl) population across restarts. If a population
  varies by more than **±5 % absolute**, it is **not identifiable** from this data and must be
  reported with that uncertainty — or withheld.

*This step is what distinguishes a real measurement from a plausible-looking artifact, and it is
the step most often skipped.*

### Step 5 — External validation (the decisive one)
- Compute Si/Al from the fitted populations via Engelhardt.
- Compare against the known synthesis Si/Al.
- **Gate 5:** r ≥ 0.9, no systematic bias. **Fail ⇒ stop and report failure.**

### Step 6 — Derive the descriptor and merge
- `al_iv_mmol_g` (or a normalised framework-charge proxy) per sample.
- Attach to the Oulu rows via the existing adapter; **flag every value as NMR-derived**, with its
  restart-spread as uncertainty, so downstream code can never mistake it for a measured quantity.
- **Gate 6:** pooled `validate()` clean; row count unchanged (we are adding a column, not rows).

### Step 7 — Test the hypothesis
- With Al^IV available for ~19 Oulu samples, test whether it out-predicts BET and Si/Al for NH₄⁺
  uptake, using **grouped CV by composition** (replicates must not leak).
- Report the result **whichever way it comes out**. A negative result here is still a finding —
  it would mean Varon's r = +0.95 does not generalise.

---

## What this does *not* do

- It does **not** produce Cs/Sr capacities. The Oulu adsorbates remain NH₄⁺ and two dyes.
- It does **not** rescue inverse design; 52 Cs/Sr rows remain the binding constraint.
- Derived values are **model output, not measurement**, and stay labelled as such forever.

## Honest prior

I would put this at roughly **60–70 %** to clear Gate 5. Amorphous geopolymer ²⁹Si spectra are
broad and heavily overlapped — considerably harder than crystalline zeolites. If it fails, the
correct outcome is a recorded negative result plus a request for the authors' already-deconvolved
values, not a tuned fit.

## Effort

Steps 1–3 are straightforward. **Step 4 is the expensive one** and must not be skipped. Step 5 is
quick and decides everything.

---

# Amendment 1 — second pre-registered criterion (2026-07-20, BEFORE any fitting)

Gate 1 revealed that only **4 of the 12** spectra vary Si/Al (the Ca-free set); six of the
remaining eight sit at a single Si/Al = 4. The Engelhardt check would therefore rest on **n = 4**,
where one poor fit flips the verdict either way.

Adding a **second, independent** criterion. Both must pass.

## Gate 5a — Engelhardt agreement *(as originally registered)*
NMR-derived Si/Al vs designed Si/Al, Ca-free set: **r ≥ 0.9**, no systematic bias.

## Gate 5b — chemical monotonicity *(new)*
As Si/Al **decreases** (more framework Al), the fitted populations must shift toward
Al-rich silicon environments. Formally, define the **Al-richness index**

```
ARI = Σ(m=0..4) m · I_m / 100        (mean Al neighbours per Si)
```

**Criterion:** ARI must be **strictly monotonically decreasing** with Si/Al across the Ca-free
series (Si2 → Si4 → Si10 → Si20), i.e. Spearman ρ = **−1.0** on those four points.

**Why this is a genuinely independent test.** Engelhardt is an *algebraic* transform of the same
populations — a fit can satisfy it while the individual peaks are badly apportioned, because the
ratio is a lumped quantity. Monotonic ordering constrains the *shape* of the distribution across
samples and cannot be satisfied by a fit that mis-assigns intensity between neighbouring peaks.
A wrong deconvolution can fake one criterion; faking both simultaneously is much harder.

**Ca-series use:** the six Si4-Ca samples are *not* used for either criterion (Si/Al is constant,
and Ca perturbs the framework). They serve only as a **consistency observation** — their ARI
should cluster near the Ca-free Si4 value. Divergence is reported, not corrected for.

## Combined verdict
- **Both pass** → descriptor accepted, still labelled model-derived with restart uncertainty.
- **Either fails** → reported as a failed deconvolution. No tuning to recover.

## Independent ground truth requested in parallel
The Oulu authors report ²⁹Si results in their paper, so deconvolved populations exist. A request
for those values has been drafted (`docs/correspondence/`). If received, they become the real
external check and both gates above become secondary.

---

# RESULT (2026-07-20): deconvolution REJECTED

| Gate | Criterion | Result | |
|---|---|---|---|
| 1 | spectra parse, cover window, monotonic | 12/12 clean | ✅ PASS |
| 2 | wing residual < 5 % of peak | all 0.0000 | ⚠️ **vacuous — see below** |
| 3 | all R² ≥ 0.98 | 8/12 pass; Ca-bearing 0.69–0.97 | ❌ **FAIL** |
| 5a | r(designed, NMR Si/Al) ≥ 0.90, no systematic bias | r = **+0.985**, but **large systematic bias** | ❌ **FAIL on the bias clause** |
| 5b | ARI monotonic with Si/Al, ρ = −1.0 | ρ = **−1.00** | ✅ PASS |

## Verdict: REJECTED — three independent reasons

**1. Q⁴(3Al) fitted to exactly 0.0 in all four validation samples.**
Chemically impossible. Q⁴(4Al) and Q⁴(2Al) are both substantially populated, so the
intermediate environment cannot be empty — silicon with three Al neighbours must exist between
sites with four and with two. The optimiser is pushing intensity to the outer peaks. This is
**mis-apportionment despite R² ≥ 0.998**, exactly the failure mode Gate 3's R² threshold cannot
detect on its own.

**2. Systematic bias in Gate 5a.**

| designed Si/Al | NMR-derived | ratio |
|---|---|---|
| 20.0 | 8.16 | 0.41 |
| 10.0 | 5.67 | 0.57 |
| 4.0 | 2.87 | 0.72 |
| 2.0 | 1.78 | 0.89 |

The correlation is excellent (r = +0.985) but every value is low, and the gap **widens with
Si/Al**. The registered criterion was *"r ≥ 0.9 **and no systematic bias**"* — the second clause
fails clearly.

*A caveat in the other direction:* NMR measures **framework** Si/Al while the design ratio is
**batch** Si/Al. At high silica loading, unreacted colloidal silica need not sit in the
aluminosilicate framework, so framework < batch is physically expected. Part of this deviation is
therefore probably real, not artifact — which is precisely why this cannot adjudicate the fit on
its own, and why reason 1 is decisive.

**3. Gate 3 failed outright** for the Ca-bearing spectra (R² 0.69–0.97), with two degenerate fits
placing 100 % of intensity in a single peak. Calcium introduces Si environments the five-peak
Q⁴(mAl) model does not represent.

## Why "two gates passed" does not rescue it

Both registered criteria are computed from the **same fitted populations**. Q⁴(3Al) ≡ 0 shifts
intensity outward roughly symmetrically, which preserves both the lumped Engelhardt ratio's
correlation *and* the monotonic ordering. This is the concrete lesson: **two criteria derived from
one fit are not two independent tests.** Gate 5b was intended to be independent and is not
independent enough.

**Gate 2 was also vacuous:** fitting a least-squares line to the wings forces the wing residual
mean to ≈0 by construction, so the check could not fail. It tested arithmetic, not baseline
quality.

## What was NOT done

No constraint was relaxed, no peak dropped, no criterion reinterpreted after seeing the numbers.
The pre-registration held.

## Path forward

1. **Await the Oulu authors' own deconvolved values** (letter drafted). External ground truth
   settles this; our internal criteria demonstrably cannot.
2. If self-fitting is required, the model needs work an R² threshold cannot supervise: a
   Q⁴(3Al) > 0 physical prior, per-peak line widths, and a separate model for Ca-bearing samples.
3. **The Al^IV descriptor stays at 7 of 118 rows.** It is not extended by this attempt.

---

# F18 — the deconvolution was already published, and it explains the failure

**Table 2 of the Oulu paper reports the deconvolved Si environments for all 12 samples.** The
values I attempted to derive were on page 6 of a paper already on disk. Found by rendering the
page and reading it.

## Why my fit failed — now diagnosable

My model was **five Q⁴(mAl) Gaussians**. The authors' deconvolution uses **ten environments**:

```
Q⁰ · Q¹ · Q²(1Al) · Q²(0Al) · Q⁴(4Al) · Q³(1Al) · Q⁴(3Al) · Q³/Q⁴(2Al) · Q³/Q⁴(1Al) · Q⁴(0Al)
```

The spectra contain **Q³ and Q² species** — silicons with non-bridging oxygens — which a Q⁴-only
model cannot represent. Forced to fit that intensity with five Q⁴ peaks, the optimiser pushed it
to the outer components and drove **Q⁴(3Al) to zero**.

**The rejection was correct, and for the right reason.** The chemical sanity check (Q⁴(3Al) ≡ 0 is
impossible) detected a structurally wrong peak model — precisely what R² and both pre-registered
gates could not.

## The descriptor, from the authors' values

Al-richness index `ARI = Σ m·Iₘ / 100`, Ca-free series:

| sample | Si/Al | Q⁴(4Al) | Q³/Q⁴(1Al) | Q⁴(0Al) | **ARI** | NH₄⁺ (mg/g) |
|---|---|---|---|---|---|---|
| Si2Al1Na1 | 2 | 45.1 | — | 28.3 | **2.336** | 11.53 |
| Si4Al1Na1 | 4 | 24.9 | 45.0 | 30.1 | **1.446** | 8.07 |
| Si10Al1Na1 | 10 | — | 50.0 | 50.0 | **0.500** | 5.47 |
| Si20Al1Na1 | 20 | — | 54.1 | 45.9 | **0.541** | 2.13 |

```
corr(ARI,   NH4 uptake) = +0.932
corr(Si/Al, NH4 uptake) = −0.955
```

**Al-richness predicts uptake strongly (+0.93)** — independent support for the Varon result
(+0.95 for Al^IV vs K_D) in a different material family with a different adsorbate.

## Honest limits

- **n = 4.** Four Ca-free samples with usable Q⁴ data. Suggestive, not conclusive.
- **Si/Al is not beaten here** (−0.955 vs +0.932). In this designed series the two are near-perfectly
  confounded — Al content *is* the varied axis. This dataset cannot separate them; Varon and
  Katada can, and it is there that Si/Al fails and Al^IV does not.
- **ARI is not monotonic**: Si10 (0.500) sits below Si20 (0.541), a mild inversion at the low-Al end.
- The eight Ca-containing samples are dominated by Q⁰–Q² environments and carry almost no Q⁴,
  so they contribute no Al^IV signal.

## Status

The pinned NMR pipeline is **closed**. The descriptor was obtained from the authors' published
deconvolution rather than from our own fit, which remains rejected. The letter requesting these
values is now unnecessary for this purpose.
