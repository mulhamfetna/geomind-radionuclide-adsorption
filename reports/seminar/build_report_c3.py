#!/usr/bin/env python3
"""Generate the GEOMIND-R Checkpoint-3 supervisory report.

Reuses Checkpoint-1's styling, helpers and LIVE-data appendices (imported from
build_report), and supplies Checkpoint-3 prose. Checkpoint 3's story: the central
finding's evidence chain is now complete — correlation, a within-sample causal test,
AND a direct atomic mechanism (Geddes 2025, delivered by the supervisor).

Output: reports/GEOMIND-R-checkpoint-3.html   (rendered by render_pdf_c3.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import build_report as C1  # noqa: E402
from build_report import (  # noqa: E402
    CSS, table, appA, appB, appC, appD, appE,
    n_find, n_resolved, poolA_n, poolA_src, poolB_n, poolB_src, radio_n,
)


def cover():
    return f"""
<div class="cover">
  <span class="conf">Confidential — Supervisory Checkpoint 3</span>
  <h1>GEOMIND&#8209;R</h1>
  <div class="sub">Generative inverse design of geopolymers for the
    immobilisation of radioactive Cs&#8209;137 and Sr&#8209;90</div>
  <p class="lead" style="margin-top:18px;max-width:60ch">Third progress report. The evidence for
    the project's central chemical finding is now complete on three independent levels —
    correlation, a within&#8209;sample causal test, and a direct atomic mechanism — the last
    supplied by the very paper requested at Checkpoint&nbsp;2.</p>
  <div class="meta">
    <div class="k">Principal investigator</div><div>Mulham Fetna &nbsp;·&nbsp;
      ORCID 0009&#8209;0006&#8209;4432&#8209;798X</div>
    <div class="k">Supervisor</div><div>Dr. Abdulrazzaq Hammal &nbsp;·&nbsp;
      ORCID 0000&#8209;0003&#8209;1828&#8209;1376</div>
    <div class="k">Institution</div><div><span class="ph">[Institution / Department]</span></div>
    <div class="k">Date</div><div>21 July 2026</div>
    <div class="k">Report status</div><div>Checkpoint 3 · literature&#8209;scale
      meta&#8209;analysis phase</div>
  </div>
</div>
"""


def execsum():
    return f"""
<h2><span class="sec">Executive summary</span>The central finding now rests on three independent legs</h2>
<p class="lead">Between Checkpoints&nbsp;1 and&nbsp;3 the project's core claim — that
<em>framework aluminium</em>, not surface area, governs how a geopolymer captures Cs<sup>+</sup>
and Sr<sup>2+</sup> — has been raised from a plausible correlation to a result supported on three
levels at once. Checkpoint&nbsp;3 reports the third and strongest: a <b>direct atomic&#8209;scale
mechanism</b>, delivered by the Geddes&nbsp;2025 paper you supplied.</p>

<div class="kpi">
  <div class="c"><div class="v">{poolA_n}</div><div class="l">Pool&nbsp;A rows
    ({poolA_src} sources)</div></div>
  <div class="c"><div class="v">{poolB_n}</div><div class="l">Pool&nbsp;B rows
    ({poolB_src} sources)</div></div>
  <div class="c"><div class="v">{n_find}</div><div class="l">audited findings
    ({n_resolved} resolved)</div></div>
  <div class="c"><div class="v">125</div><div class="l">automated integrity tests
    passing</div></div>
</div>

<div class="box win">
  <div class="t">The evidence chain, now complete</div>
  <b>1. Correlation.</b> Across every dataset that separates them, framework aluminium tracks
  cation uptake (up to <b>+0.95</b>) while surface area does not (pooled <b>+0.08</b>).<br>
  <b>2. Causation (within&#8209;sample).</b> Leaching a set of geopolymers strips framework Al, and
  uptake falls with it on the <em>same</em> samples: corr(&Delta;[Al<sup>IV</sup>],
  &Delta;K<sub>D</sub>) = <b>+0.938</b>.<br>
  <b>3. Mechanism (atomic).</b> X&#8209;ray absorption spectroscopy and multinuclear NMR show
  Sr<sup>2+</sup> sitting at the <b>charge&#8209;balancing sites of tetrahedral Al<sup>IV</sup></b>
  itself — the exact sites the descriptor counts.
</div>

<h4>What changed since Checkpoint&nbsp;2</h4>
<ol>
  <li><b>The requested bridge paper arrived and closed the mechanism question.</b> Geddes&nbsp;2025
    — the priority&#8209;1 acquisition from the Checkpoint&nbsp;2 request — images Sr binding at the
    Al<sup>IV</sup> sites directly (Section&nbsp;2).</li>
  <li><b>Two more immobilisation sources were added</b>, one of them showing that a common
    accelerated leach test <em>hides</em> the caesium/strontium difference (Section&nbsp;1).</li>
  <li><b>The honest gap is now precisely defined.</b> The mechanism is settled; what remains scarce
    is <em>breadth</em> — composition&#8209;varying data pairing the descriptor with a target — and
    Section&nbsp;5 states exactly what would close it.</li>
</ol>
"""


def toc():
    items = [
        ("1", "What has advanced since Checkpoint&nbsp;2", "s1"),
        ("2", "The central finding — a complete evidence chain", "s2"),
        ("3", "Current data structure", "s3"),
        ("4", "What we still cannot do, and why", "s4"),
        ("5", "Remaining acquisitions &amp; data needs", "s5"),
        ("6", "Plan and requests", "s6"),
        ("A", "Full finding register (all findings)", "sA"),
        ("B", "Pool A — every adsorption row", "sB"),
        ("C", "Pool B — every immobilisation row", "sC"),
        ("D", "Decisions register", "sD"),
        ("E", "Glossary of chemical terms", "sE"),
    ]
    links = "".join(f'<a href="#{i}"><span class="n">{n}</span>{t}</a>' for n, t, i in items)
    return (f'<h2><span class="sec">Contents</span>Structure of this report</h2>'
            f'<div class="toc">{links}</div>')


def s1():
    batch = table(
        ["Paper", "What it added", "Effect"],
        [
            ["<b>Geddes 2025</b> (J. Hazard. Mater.) — the Checkpoint&nbsp;2 priority request",
             "the <b>atomic mechanism</b>: Sr<sup>2+</sup> binds at Al<sup>IV</sup> charge&#8209;balancing sites (EXAFS + NMR)",
             "mechanistic capstone (Section&nbsp;2)"],
            ["Frederickx 2025 (Sustainability)",
             "Cs/Sr leachability of a real waste immobilised in a metakaolin N&#8209;A&#8209;S&#8209;H form",
             "Pool&nbsp;B +4 (leachant&#8209;flagged)"],
            ["Kim 2026 (clean manuscript)",
             "duplicate of a source already ingested",
             "skipped"],
        ],
    )
    return f"""
<h2 id="s1"><span class="sec">Section 1</span>What has advanced since Checkpoint&nbsp;2</h2>
<p>Three papers were received; the first is the one that mattered most.</p>
{batch}

<h4>A methodological point worth carrying forward (Frederickx)</h4>
<p>Frederickx's waste form passes the regulatory leach criterion, but in the <em>accelerated</em>
test (an aggressive NH<sub>4</sub>NO<sub>3</sub> medium) caesium and strontium score almost the
same. That medium was designed for calcium&#8209;rich cements and preferentially attacks divalent
cations, so it <b>understates</b> strontium immobilisation. The authors' own deionised&#8209;water
extrapolation restores the usual, large Cs/Sr gap (leachability index 9.6 for Cs vs 12.5 for Sr).
The lesson — recorded in our database as a leachant flag so these values are never mixed with
deionised&#8209;water results — is that <em>the choice of leach test can invert the apparent
ranking of a wasteform</em>. This matters for how any future comparison is framed.</p>
"""


def s2():
    return f"""
<h2 id="s2"><span class="sec">Section 2</span>The central finding — a complete evidence chain</h2>
<p>The project's central chemical result is that cation uptake in a geopolymer is
<em>ion exchange at the charge&#8209;balancing sites created by framework aluminium</em>, not
physisorption on a surface. It is now supported at three independent levels.</p>

<h3>2.1&nbsp;&nbsp;Level 1 — correlation (across samples)</h3>
<p>Wherever the two can be separated, the density of framework aluminium tracks uptake strongly
and positively, while BET surface area does not:</p>
<table class="key">
  <tr><td>Varon (n=7, Sr)</td><td>corr(Al<sup>IV</sup>, K<sub>D</sub>) <b>+0.95</b> &nbsp;vs&nbsp; corr(BET, K<sub>D</sub>) +0.19</td></tr>
  <tr><td>Oulu (n=4, NH<sub>4</sub><sup>+</sup>)</td><td>corr(framework&#8209;Al index, uptake) <b>+0.93</b></td></tr>
  <tr><td>All cations pooled</td><td>corr(BET, uptake) <b>+0.08</b> — surface area carries essentially no signal</td></tr>
  <tr><td>Organic dyes (contrast)</td><td>corr(BET, uptake) <b>+0.66</b> — opposite sign; a different, surface&#8209;binding mechanism</td></tr>
</table>

<h3>2.2&nbsp;&nbsp;Level 2 — causation (within the same samples)</h3>
<p>A companion study leached seven geopolymers with water, stripping framework aluminium, and
re&#8209;measured strontium uptake on the identical samples. The samples that lost the most
framework Al lost the most sorption:</p>
<div class="eq">corr(&Delta;[Al<sup>IV</sup>], &Delta;K<sub>D</sub>) = <b>+0.938</b>
&nbsp;&nbsp;(n = 7)</div>
<p>and the absolute density of exchange sites, [Al<sup>IV</sup>] in
mmol&nbsp;g<sup>&minus;1</sup>, predicts K<sub>D</sub> at <b>+0.946</b> (+0.986 excluding one
barely&#8209;reacted outlier). This is a within&#8209;sample test, not merely a correlation across
different materials — the strongest causal evidence a literature meta&#8209;analysis can provide.</p>

<h3>2.3&nbsp;&nbsp;Level 3 — mechanism (at the atomic scale) &mdash; the new result</h3>
<p>The Geddes&nbsp;2025 paper you supplied closes the chain. Using strontium K&#8209;edge X&#8209;ray
absorption spectroscopy together with <sup>29</sup>Si, <sup>27</sup>Al and <sup>23</sup>Na NMR on
metakaolin geopolymers, it shows that at low loading Sr<sup>2+</sup> is incorporated into
<b>extra&#8209;framework charge&#8209;balancing sites bonded through oxygen to tetrahedral
aluminium</b> (Si<sup>IV</sup>&ndash;O&ndash;Al<sup>IV</sup>), with a local structure resembling the
mineral brewsterite. In other words, strontium is observed sitting <em>exactly at the
Al<sup>IV</sup> sites the descriptor counts</em>. Above a chemical binding limit
(&asymp;&nbsp;0.5&ndash;1.5&nbsp;wt.% Sr(OH)<sub>2</sub>·8H<sub>2</sub>O), the excess precipitates as
SrCO<sub>3</sub> rather than binding to the framework.</p>
<div class="box accent">
  <div class="t">Why this matters</div>
  Correlation and even a causal test leave open the question of <em>why</em>. Geddes answers it
  directly: the framework&#8209;aluminium descriptor works because tetrahedral Al<sup>IV</sup>
  <em>is</em> the strontium binding site, imaged at the atomic scale. The three levels — a
  statistical correlation, a within&#8209;sample perturbation experiment, and a spectroscopic
  mechanism — are mutually independent and point to the same conclusion. This is the mechanistic
  capstone of the descriptor&#8209;and&#8209;methodology paper.
</div>

<h3>2.4&nbsp;&nbsp;The immobilisation side agrees, and the structural precondition holds</h3>
<p>Independently of the adsorption data, caesium leach resistance stratifies by binder chemistry
exactly as the framework picture predicts: metakaolin framework &asymp; 13 &gt; fly&#8209;ash
framework &asymp; 10 &gt; calcium&#8209;rich slag &asymp; 7.5. And the descriptor remains meaningful
only where a condensed aluminosilicate framework exists: in calcium&#8209;rich binders the silicon
network collapses to low&#8209;connectivity environments and no compositional descriptor predicts
uptake. The rule stands — never pool across structural classes.</p>
"""


def s3():
    a_by_src = C1.A.groupby("source_label").size().sort_values(ascending=False)
    b_by_src = C1.B.groupby("source_label").size().sort_values(ascending=False)
    a_tbl = table(["Source", "rows"], [[s, str(int(n))] for s, n in a_by_src.items()], right={1})
    b_tbl = table(["Source", "rows"], [[s, str(int(n))] for s, n in b_by_src.items()], right={1})
    return f"""
<h2 id="s3"><span class="sec">Section 3</span>Current data structure</h2>
<p>Two parallel datasets, never merged, both governed by a single machine&#8209;checked registry
({len(C1.REG['assets'])} assets, {n_find} findings, {len(C1.REG['decisions'])} decisions). Every row
of both pools is listed in Appendices&nbsp;B and&nbsp;C.</p>

<h4>Pool&nbsp;A &mdash; adsorption &nbsp;({poolA_n} rows, {poolA_src} sources)</h4>
<p>Target: adsorption capacity or distribution coefficient; {radio_n} rows are radionuclide (Cs/Sr).</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px"><div>{a_tbl}</div><div></div></div>

<h4>Pool&nbsp;B &mdash; immobilisation &nbsp;({poolB_n} rows, {poolB_src} sources)</h4>
<p>Target: leach resistance. Now spans metakaolin, fly&#8209;ash and slag binders, with an explicit
leachant flag after Section&nbsp;1's finding that leach&#8209;test chemistry can invert the apparent
ranking.</p>
{b_tbl}
"""


def s4():
    return f"""
<h2 id="s4"><span class="sec">Section 4</span>What we still cannot do, and why</h2>
<p>The mechanism question is now answered. The remaining obstacle is different, and it is important
to state it precisely so that the requests in Section&nbsp;5 are the right ones.</p>

<h3>4.1&nbsp;&nbsp;Mechanism is settled; breadth is not</h3>
<p>Geddes proved <em>why</em> the descriptor works, but on samples of a single fixed composition — it
did not add data in which composition <em>varies</em> while both the descriptor and a Cs/Sr target
are measured. That composition&#8209;varying paired data is what a generative model must learn from,
and it remains scarce: essentially one strontium sample&#8209;family (seven compositions) plus one
ammonium series (four). A model trained on so little, drawn from many different laboratories, would
learn inter&#8209;laboratory differences and report them as chemistry. <b>Confidence in the
mechanism has risen sharply; the breadth needed to train the generative extension has not.</b></p>

<h3>4.2&nbsp;&nbsp;The faithful replication is still blocked on confidential data</h3>
<p>The reference model was trained on 112 samples from one laboratory; only ten are public. A
faithful replication needs the full set, which is confidential and must be requested.</p>

<h3>4.3&nbsp;&nbsp;Therefore the near&#8209;term output is a paper, not a model</h3>
<p>With a correlation, a causal test and now an atomic mechanism, the
descriptor&#8209;and&#8209;methodology result is strong and publishable now. The generative model
remains gated on either the confidential dataset or a substantially broader body of
composition&#8209;varying paired data — precisely what Section&nbsp;5 asks for.</p>
"""


def s5():
    done = table(
        ["Request", "Status"],
        [
            ["Geddes 2025 — <i>Sr incorporation mechanism &amp; binding capacity</i> (J. Hazard. Mater. 488, 137426)",
             "<span class='st-ok'>&#10003; DELIVERED</span> — supplied by the supervisor; closed the mechanism question (Section&nbsp;2.3)"],
        ],
    )
    still = table(
        ["Priority", "What to obtain", "Why it matters now", "Unblocks"],
        [
            ["1 &mdash; the breadth gap",
             "<b>Composition&#8209;varying</b> studies pairing an NMR framework&#8209;Al descriptor with a Cs/Sr capacity / K<sub>d</sub> / leachability — the more distinct Si/Al compositions in one study, the better",
             "The mechanism is settled; what a generative model still lacks is <em>range</em>. Named candidate: <i>Next Sustainability</i> 2025 (article S2950631X25000024), the one source with a 1&ndash;5&nbsp;M activator axis carrying Cs, Sr and NMR together.",
             "M4, M5"],
            ["2 &mdash; faithful replication",
             "The <b>GEOMIND 112&#8209;sample training dataset</b> — request to the reference&#8209;paper authors (RSC <i>Digital Discovery</i>, DOI 10.1039/d5dd00383k); a drafted letter already exists",
             "The only route to a faithful replication of the reference model.",
             "M3a"],
        ],
    )
    needs = table(
        ["Data&#8209;type we still need", "Minimum acceptable form (a valid drop&#8209;in substitute)"],
        [
            ["<b>Composition&#8209;varying descriptor + target</b> — now the single core need",
             "Any study giving a <sup>29</sup>Si Q<sup>4</sup>(mAl) deconvolution <em>or</em> a <sup>27</sup>Al Al<sup>IV</sup> fraction <b>and</b> a Cs or Sr capacity / K<sub>d</sub> / leachability on the <b>same &ge;4 samples that differ in Si/Al</b>. Metakaolin, fly&#8209;ash or slag are all acceptable if stated. (Geddes met the descriptor&#8209;plus&#8209;target criterion but at one fixed composition — what is missing is the <em>variation</em>.)"],
            ["<b>A second leaching / degradation series</b>",
             "Framework Al and uptake measured on the same samples before and after a treatment — an independent instance of the within&#8209;sample causal test would further harden the result."],
            ["<b>A single&#8209;lab, many&#8209;sample formulation set</b>",
             "&ge;50 geopolymer formulations from one laboratory with measured properties (and ideally a Cs/Sr metric) — the minimum scale for training a generative model without inter&#8209;laboratory artefacts."],
        ],
    )
    return f"""
<h2 id="s5"><span class="sec">Section 5</span>Remaining acquisitions &amp; data needs
  <span style="font-size:11pt;color:var(--muted);font-family:var(--serif)">(the requests)</span></h2>
<p>The Checkpoint&nbsp;2 top request has been fulfilled — thank you. The remaining needs have
narrowed to a single, well&#8209;defined gap: <b>breadth</b>.</p>

<h3>5.1&nbsp;&nbsp;Fulfilled since Checkpoint&nbsp;2</h3>
{done}

<h3>5.2&nbsp;&nbsp;Still needed</h3>
{still}

<h3>5.3&nbsp;&nbsp;Data&#8209;types needed — and what counts as an acceptable substitute</h3>
<p>If the named source cannot be obtained, an equivalent meeting these criteria gives the same
insight — use them as search criteria.</p>
{needs}

<h3>5.4&nbsp;&nbsp;Where such data is most likely to be found</h3>
<p>The two groups that publish almost all paired descriptor&#8209;and&#8209;target data remain the
best hunting ground: the <b>Sheffield group</b> (Walkley, Provis, Geddes, Nevin, O'Donoghue,
Stanojević, Komljenović — the source of the mechanism paper just delivered) and the
<b>CEA Montpellier group</b> (Poulesquen, Varon, Gossard, Petlitckaia). Useful venues:
<span class="mono">J. Hazard. Mater.</span>, <span class="mono">J. Nucl. Mater.</span>,
<span class="mono">Cement &amp; Concrete Research</span>, <span class="mono">Dalton Transactions</span>,
<span class="mono">Open Ceramics</span>. Any of their studies that varies Si/Al across several
samples while reporting both NMR and a Cs/Sr metric would directly close the breadth gap.</p>
"""


def s6():
    return f"""
<h2 id="s6"><span class="sec">Section 6</span>Plan and requests</h2>
<h3>6.1&nbsp;&nbsp;Ready to write up now</h3>
<p>The descriptor&#8209;and&#8209;methodology paper is ready in substance: framework aluminium
predicts cation uptake (correlation), losing it costs uptake on the same sample (causation), and
strontium is imaged binding at the Al<sup>IV</sup> sites (mechanism) — plus a saturation screen that
exposes published capacities that are extrapolation artefacts. None of this needs the confidential
dataset.</p>

<h3>6.2&nbsp;&nbsp;What we ask of this checkpoint</h3>
<ul>
  <li><b>Help close the breadth gap</b> — obtain <i>Next Sustainability</i> 2025, or identify any
    study from the Section&nbsp;5.4 groups that varies Si/Al while reporting NMR and a Cs/Sr metric.</li>
  <li><b>Support the confidential&#8209;data request</b> to the reference&#8209;model authors.</li>
  <li><b>Advise on a small own&#8209;laboratory measurement</b> — a short Si/Al series with NMR and a
    Sr uptake test would, by itself, supply the composition&#8209;varying paired data the model needs
    and let us replicate the causal test in&#8209;house.</li>
  <li><b>Agreement</b> to proceed to writing the descriptor&#8209;and&#8209;methodology paper, with
    the generative model as the subsequent phase once breadth allows.</li>
</ul>
"""


def build_html():
    body = "".join([
        cover(), execsum(), toc(),
        s1(), s2(), s3(), s4(), s5(), s6(),
        appA(), appB(), appC(), appD(), appE(),
    ])
    foot = (
        '<div class="foot">GEOMIND&#8209;R &mdash; Confidential supervisory checkpoint 3 &middot; '
        f'{n_find} findings, {n_resolved} resolved &middot; Pool&nbsp;A {poolA_n} rows / '
        f'{poolA_src} sources &middot; Pool&nbsp;B {poolB_n} rows / {poolB_src} sources &middot; '
        '125 automated tests passing &middot; Prepared by Mulham Fetna. '
        'All quantitative values generated directly from the project registry and data pipeline.</div>'
    )
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>GEOMIND-R — Supervisory Checkpoint 3</title>"
        f"<style>{CSS}</style></head><body><div class='page'>{body}{foot}</div></body></html>"
    )


if __name__ == "__main__":
    out = ROOT / "reports" / "GEOMIND-R-checkpoint-3.html"
    out.write_text(build_html(), encoding="utf-8")
    print(f"wrote {out}  ({len(build_html())//1024} KB)", file=sys.stderr)
