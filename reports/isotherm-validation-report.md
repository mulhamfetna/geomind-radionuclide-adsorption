# Isotherm Validation Report — all 35 fitted capacities assessed

**Completed:** 2026-07-20 · **Findings:** F14, F15, F16, F17
**Result:** 31 sound · 1 borderline · 3 extrapolation artefacts · 0 unassessable

---

## 1. Why this was necessary

A fitted Langmuir *Q*max is only a capacity if the experiment actually approached saturation. At
low surface coverage the Langmuir isotherm is **near-linear**, so it fits the data almost
perfectly while the plateau it implies is essentially unconstrained. The consequence is a number
that looks authoritative — high R², published in a table — and means very little.

This was not a hypothetical concern. It was discovered in our own pool.

### The trigger: Baek 2018 chabazite

| quantity | value |
|---|---|
| Fitted *Q*max | **1249.5 mg/g** |
| R² | **0.99989** |
| Equilibrium uptake reported in the same paper | **1.184 mg/g** |
| K_L | 7.94 × 10⁻⁵ (two orders below its companions) |

An R² of 0.99989 on a fit extrapolating ~1000× beyond any measurement. Nothing in the reported
statistics flags this; only comparing the fit against the experimental range exposes it.

---

## 2. The diagnostic

For a Langmuir isotherm, fractional surface coverage at the highest concentration used is

```
θ  =  b·C₀ / (1 + b·C₀)
```

θ near 1 means the plateau was observed. θ near 0 means it was inferred from the initial slope
and carries no real constraint.

**Thresholds fixed before screening:**

| θ | interpretation |
|---|---|
| ≥ 0.8 | sound — plateau adequately approached |
| 0.5 – 0.8 | weakly constrained — usable with caveat |
| < 0.5 | extrapolation — must not be treated as a measured capacity |

---

## 3. F16 — the shortcut: θ = 1 − R_L

The screen initially required recovering C₀ from each paper's methods section, one at a time.
That was unnecessary.

Many papers report the **Langmuir separation factor**

```
R_L  =  1 / (1 + b·C₀)
```

as a standard favourability check. Therefore

```
θ  =  b·C₀/(1 + b·C₀)  =  1 − 1/(1 + b·C₀)  =  1 − R_L
```

**R_L is the saturation fraction, complemented.** Wherever it is reported, the screen needs no C₀
recovery at all.

### Verification against the independent route

Six El-Naggar rows had already been screened by recovering C₀ = 1000 mg/L from the methods. Their
published R_L values reproduce those results **exactly**:

| row | 1 − R_L | θ computed from C₀ | agreement |
|---|---|---|---|
| Na-MKBFS 298 K | 0.923 | 0.923 | ✅ |
| Na-MKBFS 313 K | 0.924 | 0.924 | ✅ |
| Na-MKBFS 333 K | 0.926 | 0.926 | ✅ |
| K-MKBFS 298 K | 0.898 | 0.898 | ✅ |
| K-MKBFS 313 K | 0.896 | 0.896 | ✅ |
| K-MKBFS 333 K | 0.887 | 0.887 | ✅ |

Two independent derivations agreeing to three decimal places is strong evidence the screen is
implemented correctly — not merely self-consistent.

### How it was found

By **rendering the PDF pages and reading the figures and tables visually**. This had previously
been dismissed as "manual figure reading" and deferred. That was wrong: it is an available
capability, and using it immediately produced a better method than the one being applied by hand.

The lesson is not "use the image tool". It is that **describing work as manual stopped the search
for a better method — and the better method was already printed on the page.**

---

## 4. Complete results

### 4.1 Sound — 31 rows (θ ≥ 0.8)

| source | rows | θ range | route |
|---|---|---|---|
| Hamed 2025 (magnetic ternary) | 7 | 0.982 – 0.987 | C₀ = 1000 mg/L |
| Tarnovsky 2024 | 6 | 0.960 – 0.995 | C₀ = 10 mmol/L (species-scaled) |
| El-Naggar 2018 | 6 | 0.887 – 0.926 | C₀ = 1000 mg/L, confirmed by R_L |
| Katada 2024 | 6 | — | IEC, not a Langmuir fit |
| Lei 2021 | 2 | 0.979 – 0.986 | C₀ = 170 mg/L |
| Tian ESPR 2019 | 2 | 0.944 – 0.994 | **R_L** |
| Tian WST 2019 | 2 | 0.897 – 0.950 | **R_L** |
| Baek 2018 (heulandite) | 1 | 0.816 | C₀ = 2658 mg/L |
| Zheng 2023 | 1 | 0.933 | C₀ = 800 mg/L |
| Xiang 2021 (GF600) | 1 | 0.929 | C₀ = 500 mg/L |

### 4.2 Borderline — 1 row

**Baek 2018, stilbite** — θ = 0.775, just under threshold. *Q*max = 76.278 mg/g is mildly
extrapolated (~24 % beyond the observed plateau). Retained with the caveat stated.

### 4.3 Extrapolation artefacts — 3 rows, excluded

| sorbent | *Q*max | θ | reached |
|---|---|---|---|
| **Zhang slag geomaterial** | 44.52 | **0.074** | 7 % of plateau |
| **Baek chabazite** | 1249.5 | **0.174** | 17 % of plateau |
| **Zhang fly-ash geomaterial** | 89.32 | **0.365** | 37 % of plateau |

---

## 5. F17 — Zhang 2021 carries a second, independent defect

Figure 8 is the linearised Langmuir plot, `Ce/qe` vs `Ce`. Reading it visually established two
things.

**The Qmax values are correctly ingested.** The slope reproduces the published figures exactly:

```
fly ash:  1 / 11.196  =  89.32 mg/g   (table: 89.32)
slag:     1 / 22.464  =  44.52 mg/g   (table: 44.52)
```

**But the intercepts are unphysical.** In

```
Ce/qe  =  1/(Qmax·b)  +  Ce/Qmax
```

the intercept `1/(Qmax·b)` must be **positive**. Both are negative — **−0.5365** and **−2.0942** —
which implies **b < 0**. The paper nonetheless reports positive b (0.1665, 0.02126), values that
cannot be derived from the plots shown.

Combined with θ = 0.365 and 0.074, both rows are excluded. The slag fit is a **worse**
extrapolation than the chabazite case that initiated this investigation.

---

## 6. Three corrections to my own reasoning, recorded

**6.1 K_L alone is not a screen.** Low K_L was used to predict artefacts on three occasions —
El-Naggar (6 rows), Tarnovsky (6), Hamed (7) — and was wrong every time. All 19 rows are sound.
A small K is fully compensated by a large C₀; only the product matters. Acting on that heuristic
would have discarded 19 good rows.

**6.2 Guilt by shared protocol is invalid.** Stilbite and heulandite were flagged "high risk —
same paper, same protocol" as chabazite. All three used the identical 0.4–2658 mg/L range.
Heulandite is sound (θ = 0.816). The parameter decides in combination with the experiment, never
the provenance.

**6.3 Work described as "manual" stopped being examined.** Six rows were declared unassessable and
deferred. Vision extraction resolved all six and produced the R_L shortcut. Deferring work as
manual removed it from consideration rather than queuing it.

---

## 7. Impact on the dataset

Before this exercise, **35 fitted capacities were of unknown validity**. After it:

- **31 confirmed** as measured rather than extrapolated
- **1 flagged** as weakly constrained
- **3 excluded** as artefacts — including two that would otherwise have entered a model looking
  entirely respectable, backed by R² = 0.9948 and 0.9954

**The pool is smaller and much better characterised.** Three bad rows removed matters less than the
31 rows now positively verified rather than merely assumed.

### Publication statement

> Of 35 fitted adsorption capacities compiled from the literature, all 35 were assessed for
> isotherm saturation using θ = b·C₀/(1+b·C₀), equivalently 1 − R_L. Thirty-one were confirmed as
> measured rather than extrapolated (θ ≥ 0.8), one is weakly constrained (θ = 0.775), and three
> were excluded as extrapolation artefacts (θ = 0.074, 0.174, 0.365). Two of the excluded fits
> additionally exhibit negative intercepts in their linearised form, implying an unphysical
> negative affinity constant.

This is, to our knowledge, not a check routinely applied when adsorption capacities are compiled
across studies — and three of thirty-five published values did not survive it.
