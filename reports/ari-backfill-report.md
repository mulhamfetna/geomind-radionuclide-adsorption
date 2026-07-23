# ARI Backfill — the descriptor did not widen, and the reason is the result

**Completed:** 2026-07-20 · **Findings:** F18, F19 · **Decisions:** D11, D12
**Outcome:** hypothesis **not** confirmed as stated; replaced by a sharper, gated claim

---

## 1. What was attempted, and the prediction made

Framework aluminium — not surface area — is the descriptor that tracks cation uptake
(Varon: corr(Al^IV, K_d) = **+0.95** against corr(BET, K_d) = **+0.19**). Its problem was
scarcity: **Al^IV existed in 7 of 121 pooled rows**, all from one source, one adsorbate, one
material family.

F18 established that Table 2 of Hossain 2026 publishes the deconvolved ²⁹Si environments for
**12 further sorbents**. The prediction was explicit:

> Backfilling ARI from F18 takes the descriptor from 7 rows / 1 sorbent family to roughly
> **43 rows / 19 distinct sorbents** … takes the central claim from n = 11 sorbents to n = 19.

**That prediction was wrong.** It is recorded here rather than quietly revised.

---

## 2. The transcription, and how it was checked

All 12 rows of Table 2 were transcribed into `src/geomind/data/nmr_ari.py` from a rendered
page image. Transcription is the weak link — so it carries its own integrity test:

> **11 of the 12 rows sum to exactly 100.0 %.** The twelfth (`Si10Al1Na1Ca11`) sums to
> **99.0**, which is how it is published — that row has a blank Q²(1Al) cell where every other
> row carries an explicit dash.

A mistyped digit almost always breaks the sum. This is checked per-row in
`tests/test_nmr_ari.py`, and the 99.0 row is declared in `KNOWN_INCOMPLETE` rather than
silently normalised to 100.

The index itself weights each environment by its Al count:

```
ARI  =  Σ_m ( m · I_m ) / 100          # mean Al neighbours per Si
```

**One deliberate understatement:** Q¹ carries no `(mAl)` label in the source and is weighted
`m = 0`. That is a *lower bound* — an unlabelled Q¹ may still carry Al. Only the Ca-bearing
rows have appreciable Q¹, so the series where the descriptor is tested is unaffected.

The join attached ARI to **39 rows / 12 sorbents** — not 43 / 19. The first error was
arithmetic: 12 sorbents × 3 adsorbates, not 19.

---

## 3. The result, pooled — and why pooling was the wrong move

| descriptor | NH₄⁺ | methylene blue | rhodamine 6G |
|---|---|---|---|
| **ARI** | **+0.536** | −0.280 | −0.493 |
| Q⁴ % | +0.071 | +0.474 | −0.133 |
| Si/Al | −0.618 | +0.575 | +0.877 |
| BET | −0.586 | **+0.965** | +0.438 |

ARI at **+0.536** for NH₄⁺ — down from **+0.932** on the Ca-free subset. On its face, the
descriptor weakened when tested more broadly, which is the ordinary fate of a small-*n* claim.

**It is not what happened.** Splitting the 12 sorbents by structure:

| | n | ARI | framework-only ARI | Si/Al | BET | uptake |
|---|---|---|---|---|---|---|
| **Ca-free** (Q⁴ 45–73 %) | 4 | **+0.932** | **+0.940** | −0.954 | −0.984 | 2.13 – 11.53 mg/g (sd **3.98**) |
| **Ca-bearing** (Q⁴ 0–26 %) | 8 | **−0.108** | — | −0.135 | +0.462 | 5.33 – 8.87 mg/g (sd **1.31**) |

In the Ca-bearing series **nothing predicts uptake** — not ARI, not Si/Al, not Ca/Al (−0.104),
not BET. Uptake is nearly flat at **7.27 ± 1.31 mg/g** across a threefold range of Si/Al and a
twentyfold range of Ca/Al.

---

## 4. F19 — the descriptor has a structural precondition

The authors state it themselves: **Ca acts as a network modifier**, disrupting silicate linkages
and promoting Q⁰, Q¹ and Q² environments. Our own transcription shows the consequence
quantitatively — **seven of the eight Ca-bearing samples have Q⁴ ≡ 0**.

So there is no condensed aluminosilicate framework for a framework descriptor to measure. ARI
is not *weak* in those samples; it is **measuring something that does not exist**. Their
aluminium sits in a C-A-S-H gel, and uptake evidently proceeds by a different, largely
composition-independent mechanism — which is exactly what a flat 7.27 ± 1.31 mg/g looks like.

> **The pooled +0.536 is not a weakened correlation. It is two unrelated regimes averaged
> together — +0.932 and −0.108 — reported as one number.**

This generalises **F9** one level down. F9 established that adsorbate classes must never be
pooled (cations +0.08, dyes +0.66 — opposite signs). F19 establishes the same for **sorbent
structural classes**. Recorded as **D11** (ARI claims gated on Q⁴-rich frameworks) and **D12**
(never pool structural classes in a correlation).

---

## 5. Honest accounting of what this cost the project

The backfill was proposed as the cheap move that would widen the descriptor's evidence base
without new data acquisition. It did not.

| | before | after |
|---|---|---|
| Rows carrying an Al-coordination descriptor | 7 | 39 |
| **Sorbents in the regime where it applies** | **11** | **11** |

Of the 12 sorbents gained, **8 fall outside the descriptor's domain of validity** and 4 were
already counted. **The evidence base is unchanged: Varon n = 7 (Sr, K_d) plus Oulu n = 4
(NH₄⁺).** Al^IV scarcity remains the binding constraint on M4 and M5, and is now logged as
open question **Q7**.

### What was nonetheless gained

- The domain of validity is now **stated and testable** rather than assumed. A descriptor with
  a known precondition is more useful than one with an unexamined range.
- The Ca-bearing flatness is itself a finding: **composition-driven design has no purchase on
  C-A-S-H gels**, which bears directly on M5 — a generative model would waste its search there.
- The Ca-free series still shows Si/Al (−0.954) and BET (−0.984) tracking as tightly as ARI.
  **This dataset cannot separate them** — the designed series varies Al as its single axis. Only
  Varon and Katada can, and it is there that Si/Al fails while Al^IV does not.

---

## 6. Publication statement

> Deconvolved ²⁹Si MAS NMR populations were converted to an Al-richness index (mean Al
> neighbours per Si) for 12 alkali-activated sorbents. Across all 12, ARI correlates only
> moderately with NH₄⁺ uptake (r = +0.54). Stratifying by structure resolves this into two
> regimes: in Q⁴-rich Ca-free frameworks ARI predicts uptake strongly (r = +0.93, n = 4),
> whereas in Ca-bearing gels — in which Q⁴ environments are absent — no compositional
> descriptor correlates with uptake (|r| ≤ 0.46, n = 8) and capacity is approximately constant
> at 7.3 ± 1.3 mg/g. Framework-aluminium descriptors therefore carry a structural
> precondition, and pooling sorbents across structural classes conceals it.
