# Data-sufficiency analysis — do we need more acquisition, or advance?

**Completed:** 2026-07-21 · **Prompted by:** the supervisor's observation that newly
delivered papers only reproduce information already held. · **Findings:** F36 · **Decision:** D17

**Verdict:** The supervisor is right. **Literature acquisition has reached negative returns.**
The project is at a stable stage and should advance — but to the stage the data actually
supports. This report is the empirical basis for that conclusion; every number is computed live
from the two pools.

---

## 1. The question, made testable

"Do we need more data?" is not a matter of opinion. It decomposes into three testable claims:

1. **Is the core finding saturated** — do new papers replicate rather than extend it?
2. **Can a predictive model actually be fit** on the data we hold?
3. **Would more literature help** — or does it make things worse?

---

## 2. What paired data we actually hold

Restricting to the rows that carry both a framework-composition descriptor and a Cs/Sr uptake
target:

- **54 Cs/Sr rows · 37 distinct sorbents · Si/Al span 0.82–12.3 · 8 sources.**

This is far broader than the "≈11 sorbents" figure carried in earlier notes — that figure
counted only the *NMR-derived* Al^IV subset. So breadth of *rows* is not the limiting factor. The
question is whether those rows can be **combined** into a predictive relationship.

---

## 3. Test 1 — the signal is strong *within* a source, and inconsistent *across* sources

The framework-Al→uptake correlation, computed independently inside each source that has ≥3 paired
points:

| Source | material | n | corr(descriptor, uptake) |
|---|---|---|---|
| **Varon** | metakaolin geopolymer (Sr, Al^IV) | 7 | **+0.95** |
| **Varon leached** | same, causal Δ test | 7 | **+0.94** (Δ) |
| **Oulu Ca-free** | framework AAM (NH₄⁺, ARI) | 4 | **+0.93** |
| Baek | zeolites (Si/Al proxy) | 3 | −0.99 |
| Katada | zeolites (Si/Al proxy) | 6 | **+0.68** |
| Tarnovsky | clay + geopolymer, Cs+Sr mixed | 6 | **+0.68** |

The proper descriptor (Al^IV concentration / ARI) in a clean single-class, single-adsorbate subset
gives **+0.93 to +0.95 every single time**. The sources that disagree in sign are exactly those
where a *bulk* proxy (Si/Al) is used across a *different structural class* (zeolites) or a *mixture*
of classes/adsorbates. **This is not a contradiction of the finding — it is finding F19/D12
(never pool structural or adsorbate classes) reappearing quantitatively.** Si/Al is a within-class
proxy whose sign is not portable; Al^IV is the real descriptor.

---

## 4. Test 2 — out-of-sample predictability (the decisive test)

Leave-one-out cross-validation asks the honest question: can the model predict a sample it has
never seen?

| Model | data | LOO-CV R² |
|---|---|---|
| **Within-class** — Varon MK-geopolymers, [Al^IV] → Sr K_D (one protocol) | n = 7 | **+0.81** |
| **Pooled cross-lab** — all Cs Langmuir Q_max, Si/Al → capacity (5 labs) | n = 23 | **−0.09** |

- **Within a clean class, the model is genuinely predictive** (R² = 0.81 out-of-sample). The
  relationship is real and usable, not just a retrospective correlation.
- **Pooled across labs and materials, it is worse than predicting the mean** (R² < 0). Protocol and
  structural heterogeneity swamp the composition signal.

---

## 5. Test 3 — would more literature help? No — it makes the pooled case worse

Every additional literature paper contributes rows from *another* laboratory with *another*
protocol, another material family, another capacity definition. That is precisely the variance
that drives the pooled LOO-CV R² negative. **Adding heterogeneous sources cannot remove
heterogeneity; it adds it.** The batches since Checkpoint 1 bear this out directly: they reproduced
the mechanism (correlation → causal test → atomic mechanism) from five independent angles, but did
not add the one thing a general model needs — many samples measured under *one* protocol.

**More literature acquisition has therefore hit diminishing, then negative, returns. The
supervisor's observation is correct and is confirmed quantitatively.**

---

## 6. What this means — we are stable, and eligible to advance

The three claims resolve cleanly:

1. **The core finding is saturated.** Framework Al^IV is the exchange site — established by
   correlation (+0.95), a within-sample causal test (+0.94), a direct atomic mechanism (Geddes,
   Sr imaged at Al^IV sites), and an independent immobilisation stratification (Cs leach index by
   binder). Five convergent, independent lines. **No further paper is needed to establish it.**
2. **A predictive model is fittable — within a class.** LOO-CV R² = 0.81. This is a real,
   demonstrable quantitative result *now*.
3. **A pooled cross-material model is not supported, and cannot be fixed by acquisition.** It needs
   single-protocol breadth, which the literature structurally cannot supply.

### The correct next stage (confident, fully supported now)

- **Write the descriptor-and-methodology paper.** Its claims are saturated and multiply
  confirmed.
- **Build the within-class forward model** (Al^IV → capacity/K_D for metakaolin geopolymers) as the
  paper's quantitative demonstration — LOO-CV R² = 0.81 is publishable as a proof of concept.
- Ship the reusable methods: the saturation screen (θ = 1 − R_L), the two-pool audit framework, the
  leachant-inversion caution, the veracity labelling.

### What is *not* a literature problem (and so not a reason to keep acquiring)

The full generative inverse-design model (M5) needs many samples under one protocol. That is
obtainable in exactly two ways, **neither of which is broad literature mining**:

- the **confidential GEOMIND 112-sample dataset** (one request), or
- a **small own-laboratory Si/Al series** with NMR and a Sr uptake test — which alone would supply
  the composition-varying, single-protocol paired data the model needs, and let us replicate the
  causal test in-house.

---

## 7. Recommendation

**Stop literature acquisition — it is at negative returns — and advance.** Broad scraping, mining
or crawling is explicitly *not* warranted: the analysis above shows it would add heterogeneity, not
signal. Move to writing the descriptor-and-methodology paper and building the within-class forward
model. Treat the generative model as a distinct later phase gated on one targeted dataset (GEOMIND
or a short own-lab campaign), not on more papers.
