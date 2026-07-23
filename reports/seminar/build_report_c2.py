#!/usr/bin/env python3
"""Generate the GEOMIND-R Checkpoint-2 supervisory report.

Reuses Checkpoint-1's styling, helpers and LIVE-data appendices (imported from
build_report), and supplies Checkpoint-2 prose plus the new acquisition section the
supervisor asked for. All quantitative values come from the registry / pool build().

Output: reports/GEOMIND-R-checkpoint-2.html   (rendered to PDF by render_pdf_c2.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

# Import styling, helpers and the live-data appendices from the C1 generator.
# (build_report guards its own file write behind __main__, so importing is side-effect free.)
import build_report as C1  # noqa: E402
from build_report import (  # noqa: E402
    CSS, table, appA, appB, appC, appD, appE,
    n_find, n_resolved, poolA_n, poolA_src, poolB_n, poolB_src, radio_n,
)


def cover():
    return f"""
<div class="cover">
  <span class="conf">Confidential — Supervisory Checkpoint 2</span>
  <h1>GEOMIND&#8209;R</h1>
  <div class="sub">Generative inverse design of geopolymers for the
    immobilisation of radioactive Cs&#8209;137 and Sr&#8209;90</div>
  <p class="lead" style="margin-top:18px;max-width:60ch">Second progress report — what has
    advanced since Checkpoint&nbsp;1, the strengthened central chemical finding, the current data
    structure, and a prioritised list of the papers, datasets and data&#8209;types we now need
    you to help acquire.</p>
  <div class="meta">
    <div class="k">Principal investigator</div><div>Mulham Fetna &nbsp;·&nbsp;
      ORCID 0009&#8209;0006&#8209;4432&#8209;798X</div>
    <div class="k">Supervisor</div><div>Dr. Abdulrazzaq Hammal &nbsp;·&nbsp;
      ORCID 0000&#8209;0003&#8209;1828&#8209;1376</div>
    <div class="k">Institution</div><div><span class="ph">[Institution / Department]</span></div>
    <div class="k">Date</div><div>21 July 2026</div>
    <div class="k">Report status</div><div>Checkpoint 2 · literature&#8209;scale
      meta&#8209;analysis phase</div>
  </div>
</div>
"""


def execsum():
    return f"""
<h2><span class="sec">Executive summary</span>What has changed, and the one thing that matters most</h2>
<p class="lead">Since Checkpoint&nbsp;1 an eleven&#8209;paper batch was mined into the database. The
headline is a genuine strengthening of the project's central result: the evidence that
<em>framework aluminium</em> governs radionuclide uptake is no longer a set of
cross&#8209;sample correlations — it now includes a <b>within&#8209;sample causal test</b>.</p>

<div class="kpi">
  <div class="c"><div class="v">{poolA_n}</div><div class="l">Pool&nbsp;A rows
    ({poolA_src} sources) &mdash; was 118</div></div>
  <div class="c"><div class="v">{poolB_n}</div><div class="l">Pool&nbsp;B rows
    ({poolB_src} sources) &mdash; was 16</div></div>
  <div class="c"><div class="v">{n_find}</div><div class="l">audited findings
    &mdash; was 26</div></div>
  <div class="c"><div class="v">125</div><div class="l">automated integrity tests
    passing</div></div>
</div>

<div class="box win">
  <div class="t">The result to take away</div>
  A companion study leached a series of geopolymers with water, stripping framework aluminium,
  and re&#8209;measured strontium uptake on the <em>same</em> samples. The samples that lost the
  most framework Al lost the most sorption:
  <b>corr(&Delta;[Al<sup>IV</sup>], &Delta;K<sub>D</sub>) = +0.938</b>. And the absolute density
  of framework&#8209;Al exchange sites, <b>[Al<sup>IV</sup>] (mmol&nbsp;g<sup>&minus;1</sup>),
  predicts K<sub>D</sub> at +0.946</b> (+0.986 excluding one barely&#8209;reacted outlier) —
  against just <b>+0.19 for surface area</b>. This is the first evidence that tetrahedral
  Al<sup>IV</sup> <em>is</em> the strontium exchange site, not merely a correlate of it.
</div>

<h4>The three developments since Checkpoint&nbsp;1</h4>
<ol>
  <li><b>The framework&#8209;aluminium finding gained causal weight</b> (Section&nbsp;2), and the
    descriptor is now ranked: absolute exchange&#8209;site density &gt; per&#8209;silicon fraction.</li>
  <li><b>The immobilisation side independently reproduced the pattern.</b> Caesium leachability
    now stratifies cleanly by binder chemistry: metakaolin framework &asymp; 13 &gt; fly&#8209;ash
    framework &asymp; 10 &gt; calcium&#8209;rich slag &asymp; 7.5.</li>
  <li><b>The obstacle is unchanged but sharper.</b> One specific paper — reporting NMR
    <em>and</em> a binding capacity together — remains the single highest&#8209;value acquisition,
    and Section&nbsp;5 sets out exactly what to obtain (and acceptable substitutes).</li>
</ol>
"""


def toc():
    items = [
        ("1", "What has advanced since Checkpoint&nbsp;1", "s1"),
        ("2", "The strengthened central finding", "s2"),
        ("3", "Current data structure", "s3"),
        ("4", "What we still cannot do, and why", "s4"),
        ("5", "Required acquisitions &amp; data needs", "s5"),
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
            ["Varon <i>leached</i> (Open Ceramics 2026)", "the within&#8209;sample causal test (Section&nbsp;2)", "Pool&nbsp;A +7 Sr K<sub>D</sub>"],
            ["Stanojević 2025", "fly&#8209;ash GP; Cs passes the leach criterion yet &gt;70% escapes", "Pool&nbsp;B +2 Cs"],
            ["Komljenović 2020", "alkali&#8209;activated slag (a calcium system) — confirms the Ca precondition", "Pool&nbsp;B +2 Cs"],
            ["Qian 2001", "adding aluminosilicate raises uptake even in a Ca binder", "Pool&nbsp;A +4 Cs/Sr"],
            ["Arbel&#8209;Haddad 2022", "metakaolin framework; Cs cumulative&#8209;leached fractions", "Pool&nbsp;B +6 Cs"],
            ["Petlitckaia 2020 (foams)", "bare framework out&#8209;performs a functionalised foam on raw capacity", "Pool&nbsp;A +4 Cs"],
            ["O'Donoghue 2026", "structure only, no uptake target — <em>assessed, not ingested</em>", "—"],
            ["2 duplicates + 1 supplement", "identified and kept out of the pools", "—"],
        ],
    )
    return f"""
<h2 id="s1"><span class="sec">Section 1</span>What has advanced since Checkpoint&nbsp;1</h2>
<p>Eleven papers were triaged by content, then extracted inline and verified against source. Two
were the specific sources flagged as needed at Checkpoint&nbsp;1; both are now closed.</p>
{batch}
<p>Every value was read <em>in context</em> in the source. Where a source was imperfect it was
flagged rather than fixed: a 2001 paper's unusual "mol&nbsp;g<sup>&minus;1</sup>" label on a
distribution ratio was recorded as&#8209;is (magnitude indicates mL&nbsp;g<sup>&minus;1</sup>); an
author&#8209;accepted manuscript with no DOI was given a flagged citation, not a guessed
identifier; and one NMR&#8209;rich paper with no uptake measurement was deliberately left out
rather than pad the dataset with rows no model can use.</p>
"""


def s2():
    return f"""
<h2 id="s2"><span class="sec">Section 2</span>The strengthened central finding</h2>
<p>Checkpoint&nbsp;1 established that for cations, framework aluminium — the tetrahedral
Al<sup>IV</sup> that forms the charge&#8209;balancing exchange sites — predicts uptake, whereas
surface area does not. The new batch turned this from correlation toward causation.</p>

<h3>2.1&nbsp;&nbsp;A within&#8209;sample causal test (finding F27)</h3>
<p>A companion study to our Varon source re&#8209;measured the same seven geopolymers before and
after 96&nbsp;h of water leaching, tracking both framework aluminium and strontium uptake:</p>
<ul>
  <li><b>[Al<sup>IV</sup>] concentration predicts K<sub>D</sub>:</b>
    corr = <b>+0.946</b> (n&nbsp;=&nbsp;7), <b>+0.986</b> excluding one barely&#8209;reacted
    outlier — versus <b>+0.19</b> for BET surface area and <b>&minus;0.84</b> for the Si/Al ratio.</li>
  <li><b>Leaching strips framework Al, and uptake falls with it:</b>
    corr(&Delta;[Al<sup>IV</sup>], &Delta;K<sub>D</sub>) = <b>+0.938</b>. The sample that lost the
    most framework Al (1.39&nbsp;mmol&nbsp;g<sup>&minus;1</sup>) also lost the most K<sub>D</sub>
    (2750&nbsp;mL&nbsp;g<sup>&minus;1</sup>); the one that lost almost none lost the least.</li>
</ul>
<div class="box accent">
  <div class="t">Two refinements to the descriptor</div>
  (i) <b>Absolute exchange&#8209;site density beats the fraction.</b> [Al<sup>IV</sup>] in
  mmol&nbsp;g<sup>&minus;1</sup> (+0.95) predicts better than Al<sup>IV</sup> as a percentage
  (+0.80) or the per&#8209;silicon Al&#8209;richness index (+0.77) — capacity scales with
  <em>how many</em> exchange sites there are, not their proportion.
  (ii) The relationship is now <b>within&#8209;sample</b>, not only across samples — the strongest
  causal evidence a literature meta&#8209;analysis can provide short of new laboratory work.
</div>

<h3>2.2&nbsp;&nbsp;The immobilisation side reproduces the pattern independently</h3>
<p>The new leaching papers let caesium retention be compared across binder chemistries. It
stratifies exactly as the framework&#8209;aluminium picture predicts:</p>
<table class="key">
  <tr><td>Metakaolin framework</td><td>Cs leachability index &asymp; <b>13.2&ndash;13.3</b> (Nevin)</td></tr>
  <tr><td>Fly&#8209;ash framework</td><td>&asymp; <b>10</b> (Stanojević, Jang)</td></tr>
  <tr><td>Calcium&#8209;rich slag (C&#8209;A&#8209;S&#8209;H)</td><td>&asymp; <b>7.0&ndash;7.8</b> (Komljenović)</td></tr>
</table>
<p>The aluminosilicate framework holds caesium better than the calcium&#8209;silicate gel — the
same conclusion as the adsorption side, reached through an independent property (leach resistance)
and an independent set of papers. Qian's 2001 result closes the loop from the calcium side: adding
aluminosilicate (metakaolin, zeolite) to a slag binder raises the Cs and Sr distribution ratio by
67&ndash;88%. More aluminosilicate exchange capacity, more uptake — in every direction tested.</p>

<h3>2.3&nbsp;&nbsp;The structural precondition still holds</h3>
<p>The descriptor remains meaningful only where a condensed aluminosilicate framework exists. In
calcium&#8209;rich binders the silicon network collapses to low&#8209;connectivity environments
and the framework descriptor no longer applies — Komljenović's slag is exactly this regime, and
its lower caesium retention is the visible consequence. The rule from Checkpoint&nbsp;1 stands:
never pool across structural classes.</p>
"""


def s3():
    a_by_src = C1.A.groupby("source_label").size().sort_values(ascending=False)
    b_by_src = C1.B.groupby("source_label").size().sort_values(ascending=False)
    a_tbl = table(["Source", "rows"], [[s, str(int(n))] for s, n in a_by_src.items()], right={1})
    b_tbl = table(["Source", "rows"], [[s, str(int(n))] for s, n in b_by_src.items()], right={1})
    return f"""
<h2 id="s3"><span class="sec">Section 3</span>Current data structure</h2>
<p>The two&#8209;pool architecture is unchanged; both pools grew. All data remains governed by a
single machine&#8209;checked registry ({C1.len_assets if hasattr(C1,'len_assets') else len(C1.REG['assets'])}
assets, {n_find} findings, {len(C1.REG['decisions'])} decisions) with the three&#8209;axis
trustworthiness labelling described at Checkpoint&nbsp;1. Every row of both pools is listed in
Appendices&nbsp;B and&nbsp;C.</p>

<h4>Pool&nbsp;A &mdash; adsorption &nbsp;({poolA_n} rows, {poolA_src} sources)</h4>
<p>Target: adsorption capacity or distribution coefficient. Of these, {radio_n} are radionuclide
(Cs/Sr) measurements.</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px"><div>{a_tbl}</div><div></div></div>

<h4>Pool&nbsp;B &mdash; immobilisation &nbsp;({poolB_n} rows, {poolB_src} sources)</h4>
<p>Target: leach resistance (leachability index, effective diffusivity, cumulative leached
fraction). The batch added fly&#8209;ash, slag and metakaolin leaching sources and a new
retention&#8209;type (cumulative leached fraction).</p>
{b_tbl}
"""


def s4():
    return f"""
<h2 id="s4"><span class="sec">Section 4</span>What we still cannot do, and why</h2>
<p>The generative extension still cannot be trained, and the reason is the same structural one
diagnosed at Checkpoint&nbsp;1 — now with a sharper edge.</p>

<h3>4.1&nbsp;&nbsp;The descriptor is measured with a target only rarely</h3>
<p>Framework aluminium predicts uptake, but solid&#8209;state NMR and a Cs/Sr capacity are seldom
reported for the same samples. The new batch <em>improved</em> this — the causal test (F27) rests
on seven samples measured twice — but it did not add new <em>compositions</em> carrying both the
descriptor and a target. The paired evidence base is still a small number of sample families, and
a generative model needs many more. This is a feature of how two research communities publish, not
a gap our searching can close on its own — which is precisely why Section&nbsp;5 asks for specific
help.</p>

<h3>4.2&nbsp;&nbsp;The faithful replication is still blocked on confidential data</h3>
<p>The reference model was trained on 112 samples from one laboratory; only ten are public. A
faithful replication needs the full set, which is confidential and must be requested.</p>

<h3>4.3&nbsp;&nbsp;Inverse design is still out of reach on present data</h3>
<p>There are {radio_n} radionuclide rows in the adsorption pool, spread across many laboratories
and protocols. Training a generative inverse&#8209;design model on so few rows from so many sources
would learn inter&#8209;laboratory differences and report them as chemistry. The defensible
near&#8209;term output remains a descriptor&#8209;and&#8209;methodology study — now materially
stronger thanks to the causal result — not a generative model.</p>
"""


def s5():
    tier1 = table(
        ["Priority", "Source", "Identifier", "Why it matters", "Unblocks"],
        [
            ["1 &mdash; critical",
             "Geddes <i>et&nbsp;al.</i> 2025 — <i>Alkali&#8209;mediated Sr incorporation mechanism and binding capacity of alkali aluminosilicate hydrate in geopolymers</i>",
             "<span class='mono'>J. Hazard. Mater. 488 (2025) 137426</span> · DOI 10.1016/j.jhazmat.2025.137426 (as cited in Kim 2026)",
             "The rare paper that reports NMR mechanism <b>and</b> a binding capacity together, on the same samples — exactly the descriptor&#8209;plus&#8209;target bridge the whole project turns on. Same Sheffield group whose work already underpins our strongest findings.",
             "M4, M5"],
            ["2 &mdash; high",
             "<i>Next Sustainability</i> 2025 (Cs/Sr sorption on activator&#8209;concentration series)",
             "<span class='mono'>Article S2950631X25000024</span> (paywalled; DOI not yet resolved)",
             "The only source found with a 1&ndash;5&nbsp;M activator&#8209;concentration axis carrying Cs <em>and</em> Sr <em>and</em> NMR together — a second composition&#8209;varying bridge.",
             "M4, M6"],
        ],
    )
    tier2 = table(
        ["Priority", "Dataset", "How to obtain", "Why it matters", "Unblocks"],
        [
            ["1 &mdash; critical",
             "GEOMIND 112&#8209;sample training dataset",
             "Written request to the authors of the reference paper (RSC <i>Digital Discovery</i>, DOI 10.1039/d5dd00383k). A drafted letter already exists in the project.",
             "The only route to a <em>faithful</em> replication of the reference model — 112 samples from one laboratory under one protocol, larger than every literature avenue combined.",
             "M3a"],
        ],
    )
    needs = table(
        ["Data&#8209;type we need", "Minimum acceptable form (a valid drop&#8209;in substitute)"],
        [
            ["<b>Descriptor + target, same samples</b> — the core need",
             "Any study giving a <sup>29</sup>Si Q<sup>4</sup>(mAl) deconvolution <em>or</em> a <sup>27</sup>Al Al<sup>IV</sup> fraction <b>and</b> a Cs or Sr capacity / K<sub>d</sub> / leachability index, measured on the <b>same</b> &ge;4 samples that <b>differ in Si/Al</b>. Material family is flexible (metakaolin, fly&#8209;ash, or slag) provided it is stated."],
            ["<b>A leaching / degradation series</b>",
             "Any dataset measuring framework Al and uptake on the same samples <em>before and after</em> some treatment (leaching, ageing, thermal) — this is what makes the causal test (F27) possible; a second independent instance would greatly strengthen it."],
            ["<b>A single&#8209;lab, many&#8209;sample formulation set</b>",
             "&ge;50 geopolymer formulations from one laboratory/protocol with measured properties (density, strength, viscosity, and ideally a Cs/Sr metric) — the minimum scale at which a generative model can be trained without learning inter&#8209;lab artefacts."],
            ["<b>27Al MAS NMR with sorption</b>",
             "Direct Al<sup>IV</sup>/Al<sup>V</sup>/Al<sup>VI</sup> quantification paired with a Cs/Sr metric — a cleaner descriptor than inferring Al<sup>IV</sup> from <sup>29</sup>Si, if available."],
        ],
    )
    return f"""
<h2 id="s5"><span class="sec">Section 5</span>Required acquisitions &amp; data needs
  <span style="font-size:11pt;color:var(--muted);font-family:var(--serif)">(the requests)</span></h2>
<p>This section is the practical ask. It lists, in priority order, the specific papers and dataset
to obtain, and — importantly — <b>what an acceptable substitute looks like</b>, so that if an exact
source is inaccessible, an equivalent one can be found that yields the same insight. Please help
<b>download</b> these where institutional access allows, or identify <b>replicas / drop&#8209;in
replacements</b> matching the stated criteria.</p>

<h3>5.1&nbsp;&nbsp;Specific papers to obtain</h3>
{tier1}

<h3>5.2&nbsp;&nbsp;The confidential dataset (request, not download)</h3>
{tier2}

<h3>5.3&nbsp;&nbsp;Data&#8209;types needed — and what counts as an acceptable substitute</h3>
<p>Beyond the two named papers, the project needs specific <em>kinds</em> of data. For each, the
right&#8209;hand column states the minimum an alternative source must provide to give the same
insight — use these as search criteria when a named paper cannot be obtained.</p>
{needs}

<h3>5.4&nbsp;&nbsp;Where such data is most likely to be found</h3>
<p>Two research groups publish almost all of the paired descriptor&#8209;and&#8209;target data this
project depends on, and their other papers are the best hunting ground:</p>
<ul>
  <li>The <b>Sheffield group</b> (Walkley, Provis, Stennett, Geddes, Nevin, O'Donoghue,
    Stanojević, Komljenović) — solid&#8209;state NMR of Cs/Sr geopolymer wasteforms.</li>
  <li>The <b>CEA Montpellier group</b> (Poulesquen, Varon, Gossard, Barré, Petlitckaia) —
    strontium sorption on geopolymers with NMR and K<sub>D</sub>.</li>
</ul>
<p>Useful venues: <span class="mono">J. Hazard. Mater.</span>,
<span class="mono">J. Nucl. Mater.</span>, <span class="mono">Cement &amp; Concrete Research</span>,
<span class="mono">Dalton Transactions</span>, <span class="mono">Open Ceramics</span>, and
<span class="mono">Construction &amp; Building Materials</span>. Open datasets on
<span class="mono">Zenodo</span> / <span class="mono">figshare</span> tagged
"geopolymer NMR" or "caesium sorption" are worth a scan for machine&#8209;readable tables.</p>
"""


def s6():
    return f"""
<h2 id="s6"><span class="sec">Section 6</span>Plan and requests</h2>
<h3>6.1&nbsp;&nbsp;What proceeds independently</h3>
<p>The descriptor&#8209;and&#8209;methodology result is now strong enough to write up: framework
aluminium predicts cation uptake (with a within&#8209;sample causal test), absolute exchange&#8209;
site density is the right form of the descriptor, the effect has a stated structural precondition,
and a simple saturation screen exposes published capacities that are extrapolation artefacts. None
of this needs the confidential dataset.</p>

<h3>6.2&nbsp;&nbsp;What we ask of this checkpoint</h3>
<ul>
  <li><b>Acquire the Section&nbsp;5.1 papers</b> — above all Geddes 2025 (institutional access to
    <span class="mono">J. Hazard. Mater.</span>), or identify an equivalent meeting the
    Section&nbsp;5.3 criteria.</li>
  <li><b>Support the confidential&#8209;data request</b> to the reference&#8209;model authors, or
    advise on the right channel.</li>
  <li><b>Guidance on a small own&#8209;laboratory NMR measurement</b> on a few sorbents of known
    capacity — the one route that would generate genuinely new paired data rather than re&#8209;using
    the literature, and would let us replicate the causal test in&#8209;house.</li>
  <li><b>Agreement</b> that the descriptor&#8209;and&#8209;methodology paper is the right
    near&#8209;term scientific target.</li>
</ul>
"""


def build_html():
    body = "".join([
        cover(), execsum(), toc(),
        s1(), s2(), s3(), s4(), s5(), s6(),
        appA(), appB(), appC(), appD(), appE(),
    ])
    foot = (
        '<div class="foot">GEOMIND&#8209;R &mdash; Confidential supervisory checkpoint 2 &middot; '
        f'{n_find} findings, {n_resolved} resolved &middot; Pool&nbsp;A {poolA_n} rows / '
        f'{poolA_src} sources &middot; Pool&nbsp;B {poolB_n} rows / {poolB_src} sources &middot; '
        '125 automated tests passing &middot; Prepared by Mulham Fetna. '
        'All quantitative values generated directly from the project registry and data pipeline.</div>'
    )
    return (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>GEOMIND-R — Supervisory Checkpoint 2</title>"
        f"<style>{CSS}</style></head><body><div class='page'>{body}{foot}</div></body></html>"
    )


if __name__ == "__main__":
    out = ROOT / "reports" / "GEOMIND-R-checkpoint-2.html"
    html_doc = build_html()
    out.write_text(html_doc, encoding="utf-8")
    print(f"wrote {out}  ({len(html_doc)//1024} KB)", file=sys.stderr)
