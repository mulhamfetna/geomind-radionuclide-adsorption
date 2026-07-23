# Batch-6 report — five papers (delivered 2026-07-23)

**Prepared:** 2026-07-23 · Pool A: 141 rows · Pool B: 54 rows · Findings: 40 · Tests: 181 passing

Five papers landed in `papers/references/`. Each was triaged for extractable quantities, then read
inline against its primary text. **Headline: zero new data rows — and two new mechanism findings.**

---

## 1. What each paper is, and its verdict

| File | Paper | Verdict | Why |
|---|---|---|---|
| `walkley2020.pdf` | Walkley, Ke, Hussein, Bernal, **Provis** — *Incorporation of strontium and calcium in geopolymer gels*, **J. Hazard. Mater.** 382 (2020) 121015 | **Mechanism → F38** | ²⁹Si/²⁷Al MAS NMR only; makes **no** uptake or leach measurement (states leaching is future work) |
| `blackford2007.pdf` | Blackford, Hanna, Pike, Vance, Perera — *TEM and NMR studies of geopolymers…*, **J. Am. Ceram. Soc.** 90[4] (2007) 1193 | **Mechanism → F39** | TEM + NMR at 5 wt% loading; its leach numbers are second-hand citations, not measured here |
| `perera2004.pdf` | Perera et al. (ANSTO) — *Geopolymers for the Immobilization of Radioactive Waste*, **MRS Symp. Proc.** 824, CC8.35 (2004) | **No data** | States outright: *"Leaching measurements need to be carried out."* |
| `822897.pdf` | Weigelt — *Synthese und Charakterisierung von Geopolymeren für die Entsorgung der Spaltprodukte ¹³⁷Cs und ⁹⁰Sr*, RWTH Aachen dissertation / FZ Jülich IEK-6 (2020), 202 pp. | **No data** | Purely structural (XRD/PDF/Raman/IR/MAS-NMR); has **no** adsorption or leaching chapter |
| `Muracchioli_Mattia_1128630.pdf` | Muracchioli — MSc thesis, Univ. Padua (2019), porous geopolymers for water purification, 128 pp. | **Rejected — out of scope** | Adsorbates are heavy metals (Cu, Ni, Pb, Cd), not Cs/Sr |

---

## 2. The two mechanism findings (this batch's real value)

### F38 — independent confirmation that Sr²⁺ binds at the Al^IV charge-balancing sites, and that Ca²⁺ competes for the same sites

Walkley 2020 states, from ²⁹Si/²⁷Al MAS NMR of metakaolin geopolymer gels, that the product is a
*"fully polymerised Al-rich (N,K)-A-S-H gel… with Si in Q⁴(4Al) and Q⁴(3Al) sites, and Na⁺ and K⁺
balancing the negative charge resulting from Al³⁺ in tetrahedral coordination."* On loading,
*"incorporation of Sr²⁺ or Ca²⁺ displaces some Na⁺ and K⁺ from the charge-balancing sites,"* and
*"Ca²⁺ and Sr²⁺ induce essentially the same structural changes."*

This is a **fourth independent evidence level** for the framework-aluminium mechanism — a different
group and a different technique than Geddes 2025 (F34). More importantly, it supplies the *missing
mechanism for F19*: Ca²⁺ is not a spectator in Ca-bearing systems, it **competes for the very
exchange sites the Al-richness descriptor counts** — which is exactly why the ARI→uptake relation
degrades when Ca gels are pooled in. This goes into the manuscript Discussion.

### F39 — at waste-loading concentrations Sr partitions to crystalline SrCO₃, not the gel — structural support for keeping the two pools separate (D13)

Blackford 2007, TEM + NMR at 5 wt% loading: *"Cs inhabited the amorphous phase, whereas Sr was
incorporated only partly, being preferentially partitioned to crystalline SrCO₃."*

This marks a genuine boundary on the descriptor. **Pool A** measures *dilute-solution* uptake, where
Sr exchanges at Al^IV sites; at the **Pool B** waste-loading regime a competing crystalline carbonate
sink appears that the descriptor neither does nor should predict. Independent structural evidence for
D13 (never merge the pools), and a limitation to state plainly: the forward model is a
**dilute-uptake** model, not a waste-loading model.

---

## 3. F40 — batch-6 returns zero rows: a third confirmation of the saturation thesis (F36/D17)

This is the third consecutive tranche to confirm the data-sufficiency finding — and in a sharper
form. Earlier batches returned *redundant* rows; batch-6 returns **no rows at all**, while still
adding real mechanistic value. The reading for the supervising professor is precise:

> **The literature is saturated for DATA, but not for MECHANISM.** Keep accepting mechanism papers
> (they strengthen the argument, as F38/F39 just did); stop expecting new measurements from the
> published corpus.

The only routes to *new rows* remain single-protocol data — the GEOMIND 112-sample request (Q2) or
an own-laboratory campaign — plus one specific new lead this batch surfaced.

---

## 4. The one acquisition lead worth chasing → Q12

Walkley 2020 cites **Vandevenne et al. 2018** (*J. Nucl. Mater.* 510, 575–584, *"Alkali-activated
materials for radionuclide immobilisation and the effect of precursor composition on Cs/Sr
retention"*) for the result that Sr retention rises as Si/Al falls — the same direction as our
descriptor. It is the one title in this batch that plausibly carries **quantitative Cs/Sr retention
versus precursor composition**, so it is the only paper here worth acquiring for possible Pool-A/B
rows. Recorded as open question **Q12**.

---

## 5. Provenance discipline applied

No datum was ingested from a **second-hand citation**. Blackford's and Perera's leach figures are
quotations of other authors' work; per the project's verify-against-primary-source rule they are
recorded as context, not as rows. That discipline is *why* the batch yields zero rows rather than a
handful of unverifiable ones — and it is the same discipline the whole database is built on.
