# Batch-7 report — two papers (delivered 2026-07-24)

**Prepared:** 2026-07-24 · Pool A: 141 rows · **Pool B: 54 → 73 rows** · Findings: 42 · Tests: 190 passing

Two papers landed. Unlike batch-6, **both carry primary quantitative data** — this batch adds **19
new Pool B rows** and two findings, and closes open question **Q12**.

---

## 1. Vandevenne et al. 2018 — the composition-varying series we had been missing

**J. Nucl. Mater. 510, 575–584** · DOI [10.1016/j.jnucmat.2018.08.045](https://doi.org/10.1016/j.jnucmat.2018.08.045) · **14 rows → Pool B**

This is the lead surfaced by Walkley (F38) and recorded as **Q12** — now acquired and ingested.

**Why it is unusually good data.** Six synthetic Ca-Si-Al slag compositions (plus one deliberate
replicate) made from *analytical-grade reagents*, so precursor composition is a **designed variable**
and trace-element effects are excluded. Every sample is activated identically (2 M NaOH, L/S 0.30,
1 wt% loading) and leached by one 28 d / 90 °C protocol. That is the composition-varying,
single-protocol design the published literature almost never provides.

### The result — F41: calcium competition, quantified

Computed inline over the ingested rows (`retention_value` = **% released**, so *lower is better*):

| Correlation with % released | Cs⁺ | Sr²⁺ |
|---|---|---|
| **Ca/(Si+Al)** | +0.826 | **+0.989** |
| **Si/Al** | +0.617 | +0.376 |

Three things follow.

1. **It puts a number on the F38 mechanism.** Ca²⁺ and Sr²⁺ are both alkaline earths competing for
   the same charge-balancing sites, so where Ca is abundant Sr *cannot* be retained — and the
   association is near-deterministic (**r = +0.99**). The split by nuclide is mechanistically
   coherent: Sr²⁺ is governed overwhelmingly by Ca competition, while Cs⁺ (monovalent, substituting
   for Na⁺) is governed more by framework-Al availability via Si/Al.
2. **The Si/Al direction agrees with our descriptor** — lower Si/Al (more framework Al) retains
   better — now in an *independent laboratory*, a *different material class*, and the
   *immobilisation* rather than adsorption regime.
3. **It independently reproduces our BET null result.** The authors state, on their own data: *"no
   clear correlation could be established between the BET values and the immobilisation capacities."*

Our computed correlations reproduce the authors' own qualitative claim exactly ("Cs⁺ immobilisation
is higher at lower Si/Al and Ca/(Si+Al)… Sr²⁺ is higher at a lower Ca/(Si+Al) ratio and independent
of Si/Al").

> **Caution recorded in the data.** These are **Ca-bearing** slag systems — precisely the class
> F19/D12 excludes from the ARI descriptor's domain. The rows carry `ca_si_al` explicitly and must
> never be pooled with the Ca-free framework gels. n = 7 compositions, one laboratory, one protocol:
> strong *within-study*, not a cross-laboratory claim (F36).

---

## 2. Jain, Banthia & Troczynski 2022 — a crystalline route to the same chemistry

**Cem. Concr. Compos. 133, 104679** · DOI [10.1016/j.cemconcomp.2022.104679](https://doi.org/10.1016/j.cemconcomp.2022.104679) · **5 rows → Pool B**

Fly-ash geopolymer, 5 M NaOH, cured 90 °C / 7 d, Cs doped in at 2–20 wt%, leached per ANSI/ANS-16.1.

### F42 — retention *improves* with waste loading

| Cs loading (wt%) | 2 | 5 | 8 | 11 | 20 |
|---|---|---|---|---|---|
| **LX** (leachability index) | 12.5 | 11.5 | 12.3 | 13.4 | **14.5** |
| BET (m² g⁻¹) | 13.66 | 9.45 | 11.43 | 21.77 | 40.00 |

LX dips from 2 → 5 wt%, then **rises steadily** to 20 wt% — inverting the usual dose-response. The
authors attribute this to in-situ crystallisation of **pollucite (CsAlSi₂O₆)** at ≥ 8 wt%.

Pollucite is a caesium **aluminosilicate in which Cs⁺ balances the charge of tetrahedral Al** — the
same charge-balancing chemistry the Al^IV descriptor counts (F34/F38), reached by a *crystalline*
rather than a gel route. So this records a second, distinct retention pathway alongside gel ion
exchange.

> **Confound stated explicitly (and in the code).** BET rises with dosage too (9.45 → 40.00 m² g⁻¹)
> *because* pollucite forms. The positive BET–LX association here is **driven by dosage** and is not
> evidence that surface area causes retention. It neither supports nor contradicts the Pool A BET
> result — a different regime.

Both values were read twice: Table 3 and, independently, the Conclusions — which agree exactly.

---

## 3. What changed in the repository

| | before | after |
|---|---|---|
| Pool B rows | 54 | **73** |
| Pool B sources | 8 | **10** |
| Findings | 40 | **42** |
| Open questions | 5 | **4** (Q12 closed) |
| Tests | 184 | **190** |

**Pool A is untouched** (141 rows) and every headline number is unchanged: forward R²_LOO = 0.811,
pooled R² = −0.092, framework r = 0.932 → 0.550.

Two schema fields were added to carry these data honestly rather than force-fit them:

- **`ca_si_al`** — Ca/(Si+Al), the ratio Ca-bearing slag studies actually report. Kept **separate**
  from the existing `ca_al`: they are different quantities, and mapping one onto the other would be
  exactly the definition error the schema exists to prevent. It carries the F19/D12 structural
  precondition into the pool, so Ca-bearing rows stay auditable.
- **`bet_m2_g`** — so the surface-area hypothesis can be tested in the immobilisation regime too, as
  it already can in Pool A.

---

## 4. Reading for the supervising professor

Batch-6 returned **zero** rows and confirmed the corpus is saturated for *data*. Batch-7 shows the
qualification that matters: **targeted acquisition still pays.** Both papers here were specific
leads — one surfaced by our own finding (F38 → Q12 → F41) — rather than a general sweep, and both
delivered primary data plus mechanism.

The distinction to carry forward: **broad literature sweeps are exhausted; leads generated by the
mechanism are not.** F41 in particular is the strongest quantitative statement yet of *why* the
descriptor has a structural precondition — calcium does not merely coexist with strontium, it
competes for the same sites, and in these data that competition explains Sr retention almost
completely.
