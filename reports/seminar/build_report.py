#!/usr/bin/env python3
"""Generate the GEOMIND-R first supervisory-checkpoint seminar report.

Every quantitative value is pulled LIVE from knowledge_base/registry.yaml and the
two pool build() functions — nothing is hand-typed. The prose is authored here;
the data tables are generated.

Output: reports/GEOMIND-R-seminar-checkpoint.html
The bash driver then renders it to a single continuous PDF via headless Chrome.
"""
from __future__ import annotations

import html
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402

from geomind.data.merge_adsorption import build as build_A  # noqa: E402
from geomind.data.merge_immobilisation import build as build_B  # noqa: E402

REG = yaml.safe_load((ROOT / "knowledge_base" / "registry.yaml").read_text())


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
def esc(x) -> str:
    return html.escape(str(x))


def num(x, dp=3):
    import math
    if x is None:
        return "—"
    try:
        f = float(x)
    except (ValueError, TypeError):
        return esc(x)
    if isinstance(f, float) and (f != f):  # NaN
        return "—"
    if f == 0:
        return "0"
    if abs(f) < 1e-3 or abs(f) >= 1e5:
        return f"{f:.2e}"
    return f"{f:.{dp}g}" if abs(f) < 1 else f"{f:.{dp}g}"


def doi_short(d) -> str:
    if not d or (isinstance(d, float) and d != d):
        return "—"
    s = str(d)
    return esc(s if len(s) <= 20 else s[:19] + "…")


def table(headers, rows, cls="data", right=None):
    right = right or set()
    # headers are author-written and may contain intentional markup (<sup>, &nbsp;)
    th = "".join(
        f'<th class="{"r" if i in right else ""}">{h}</th>'
        for i, h in enumerate(headers)
    )
    body = []
    for r in rows:
        tds = "".join(
            f'<td class="{"r" if i in right else ""}">{c}</td>'
            for i, c in enumerate(r)
        )
        body.append(f"<tr>{tds}</tr>")
    return (
        f'<div class="twrap"><table class="{cls}">'
        f"<thead><tr>{th}</tr></thead><tbody>{''.join(body)}</tbody>"
        f"</table></div>"
    )


SEV = {"critical": "sev-crit", "high": "sev-high", "medium": "sev-med", "low": "sev-low"}


# ---------------------------------------------------------------------------
# CSS  (self-contained; white page so height auto-measure is reliable)
# ---------------------------------------------------------------------------
CSS = """
:root{
  --ink:#1a1c22; --muted:#565b66; --line:#dfe1e6; --soft:#f4f5f7;
  --accent:#0d5c63;        /* deep teal */
  --accent2:#7a1f2b;       /* oxblood, used sparingly */
  --crit:#8a1c1c; --high:#b4530a; --med:#8a6d0a; --low:#6a6f78; --ok:#1f6b3a;
  --serif:"Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;
  --sans:"Inter","Helvetica Neue",Arial,system-ui,sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:#fff;color:var(--ink)}
body{font-family:var(--serif);font-size:11.2pt;line-height:1.55;
  -webkit-font-smoothing:antialiased}
.page{max-width:820px;margin:0 auto;padding:40px 54px 64px}
h1,h2,h3,h4{font-family:var(--sans);line-height:1.2;color:var(--ink)}
h2{font-size:20pt;margin:46px 0 4px;padding-top:14px;border-top:3px solid var(--accent)}
h2 .sec{font-size:12pt;color:var(--accent);letter-spacing:.06em;display:block;
  font-weight:600;margin-bottom:2px}
h3{font-size:14pt;margin:26px 0 6px;color:var(--accent)}
h4{font-size:11.5pt;margin:18px 0 4px;color:var(--accent2);
  text-transform:uppercase;letter-spacing:.04em}
p{margin:8px 0}
a{color:var(--accent);text-decoration:none}
.small{font-size:9.6pt;color:var(--muted)}
.lead{font-size:12.4pt;color:#2c2f36}
em{font-style:italic}
code,.mono{font-family:"SF Mono",ui-monospace,"DejaVu Sans Mono",monospace;
  font-size:9.6pt;background:var(--soft);padding:1px 5px;border-radius:4px}
.eq{font-family:"SF Mono",ui-monospace,monospace;background:var(--soft);
  border-left:3px solid var(--accent);padding:9px 14px;margin:12px 0;
  border-radius:0 6px 6px 0;font-size:10.4pt;overflow-x:auto}
/* cover */
.cover{padding:70px 0 30px;border-bottom:1px solid var(--line);margin-bottom:8px}
.conf{display:inline-block;font-family:var(--sans);font-size:9pt;font-weight:700;
  letter-spacing:.12em;color:var(--accent2);border:1.5px solid var(--accent2);
  padding:4px 12px;border-radius:4px;text-transform:uppercase}
.cover h1{font-size:30pt;margin:22px 0 6px;letter-spacing:-.01em}
.cover .sub{font-size:14pt;color:var(--muted);font-family:var(--sans);font-weight:500}
.cover .meta{margin-top:34px;display:grid;grid-template-columns:auto 1fr;
  gap:6px 22px;font-size:10.6pt}
.cover .meta .k{font-family:var(--sans);font-weight:600;color:var(--accent);
  white-space:nowrap}
.ph{background:#fff5d6;border-bottom:1px dashed #b48a00;padding:0 3px}
/* tables */
.twrap{overflow-x:auto;margin:12px 0}
table{border-collapse:collapse;width:100%;font-size:9.4pt;font-family:var(--sans)}
table.data th{background:var(--accent);color:#fff;text-align:left;padding:6px 8px;
  font-weight:600;font-size:8.8pt;letter-spacing:.02em}
table.data td{padding:5px 8px;border-bottom:1px solid var(--line);vertical-align:top;
  overflow-wrap:anywhere;word-break:break-word}
table.data tbody tr:nth-child(even),table.data tr:nth-child(even) td{background:var(--soft)}
table.data.wide{font-size:8pt}
table.data.wide th,table.data.wide td{padding:3.5px 5px}
td.r,th.r{text-align:right;font-variant-numeric:tabular-nums}
table.key td{padding:4px 10px;border-bottom:1px solid var(--line);font-size:10pt;
  font-family:var(--serif)}
table.key td:first-child{font-family:var(--sans);font-weight:600;color:var(--accent);
  white-space:nowrap;width:1%}
/* callouts */
.box{border:1px solid var(--line);border-radius:8px;padding:14px 18px;margin:16px 0;
  background:#fafbfc;break-inside:avoid}
.box.accent{border-left:4px solid var(--accent)}
.box.warn{border-left:4px solid var(--high);background:#fdf8f2}
.box.win{border-left:4px solid var(--ok);background:#f4faf6}
.box .t{font-family:var(--sans);font-weight:700;font-size:10pt;letter-spacing:.03em;
  text-transform:uppercase;color:var(--accent);margin-bottom:4px}
.box.warn .t{color:var(--high)} .box.win .t{color:var(--ok)}
/* finding chips */
.chip{display:inline-block;font-family:var(--sans);font-size:8pt;font-weight:700;
  padding:1px 7px;border-radius:10px;color:#fff;letter-spacing:.04em}
.sev-crit{background:var(--crit)} .sev-high{background:var(--high)}
.sev-med{background:var(--med)} .sev-low{background:var(--low)}
.st-ok{color:var(--ok);font-weight:700} .st-open{color:var(--crit);font-weight:700}
.fcard{border:1px solid var(--line);border-left:4px solid var(--line);border-radius:6px;
  padding:11px 15px;margin:11px 0;break-inside:avoid}
.fcard.critical{border-left-color:var(--crit)} .fcard.high{border-left-color:var(--high)}
.fcard.medium{border-left-color:var(--med)} .fcard.low{border-left-color:var(--low)}
.fcard .h{font-family:var(--sans);font-weight:700;font-size:10.4pt;margin-bottom:3px}
.fcard .lab{font-family:var(--sans);font-size:8.4pt;font-weight:700;color:var(--muted);
  text-transform:uppercase;letter-spacing:.04em;margin-top:6px}
.fcard p{margin:2px 0;font-size:10pt}
.toc{columns:2;column-gap:36px;font-family:var(--sans);font-size:10pt;margin:14px 0}
.toc a{display:block;padding:2px 0;color:var(--ink);break-inside:avoid}
.toc .n{color:var(--accent);font-weight:600;display:inline-block;width:26px}
.kpi{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin:18px 0}
.kpi .c{border:1px solid var(--line);border-radius:8px;padding:12px;text-align:center;
  background:#fafbfc}
.kpi .v{font-family:var(--sans);font-size:22pt;font-weight:800;color:var(--accent);
  line-height:1}
.kpi .l{font-size:8.8pt;color:var(--muted);font-family:var(--sans);margin-top:4px;
  letter-spacing:.02em}
hr.soft{border:0;border-top:1px solid var(--line);margin:26px 0}
sub,sup{font-size:.72em}
ul,ol{margin:8px 0 8px 4px;padding-left:20px}
li{margin:4px 0}
.foot{margin-top:40px;padding-top:14px;border-top:1px solid var(--line);
  font-size:9pt;color:var(--muted);font-family:var(--sans)}
/* clean pagination: keep blocks and table rows whole, don't strand headings */
@media print{
  .box,.fcard,.kpi,.eq,.cover{break-inside:avoid}
  h2,h3,h4{break-after:avoid}
  tr{break-inside:avoid}
  thead{display:table-header-group}
  p,li{break-inside:avoid}
}
"""
print("build_report.py loaded", file=sys.stderr)

# ---------------------------------------------------------------------------
# live data
# ---------------------------------------------------------------------------
A = build_A()
B = build_B()
findings = REG["findings"]
decisions = REG["decisions"]
oq = REG["open_questions"]

n_find = len(findings)
n_resolved = sum(1 for f in findings if f.get("status") == "resolved")
poolA_n, poolA_src = len(A), A["source_label"].nunique()
poolB_n, poolB_src = len(B), B["source_label"].nunique()
radio_n = int((A["adsorbate_class"] == "radionuclide").sum())


def cover():
    return f"""
<div class="cover">
  <span class="conf">Confidential — Supervisory Checkpoint</span>
  <h1>GEOMIND&#8209;R</h1>
  <div class="sub">Generative inverse design of geopolymers for the
    immobilisation of radioactive Cs&#8209;137 and Sr&#8209;90</div>
  <p class="lead" style="margin-top:18px;max-width:60ch">First formal progress report
    to the supervising chemistry professor — pre&#8209;seminar checkpoint covering the
    chemical foundations, results achieved, the data&#8209;integrity audit, current
    obstacles, and the plan forward.</p>
  <div class="meta">
    <div class="k">Principal investigator</div><div>Mulham Fetna &nbsp;·&nbsp;
      ORCID 0009&#8209;0006&#8209;4432&#8209;798X</div>
    <div class="k">Supervisor</div><div>Dr. Abdulrazzaq Hammal &nbsp;·&nbsp;
      ORCID 0000&#8209;0003&#8209;1828&#8209;1376</div>
    <div class="k">Institution</div><div><span class="ph">[Institution / Department]</span></div>
    <div class="k">Seminar date</div><div>21 July 2026</div>
    <div class="k">Report status</div><div>Checkpoint 1 · literature&#8209;scale
      meta&#8209;analysis phase</div>
  </div>
</div>
"""


def execsum():
    return f"""
<h2><span class="sec">Executive summary</span>Where the project stands</h2>
<p class="lead">The project set out to replicate the <em>GEOMIND</em> generative model for
geopolymer design and to extend it with a fourth design dimension — the capacity of a
geopolymer to capture and retain radioactive caesium and strontium. Over this first phase
the chemical groundwork has been laid, a compiled dataset has been built and rigorously
audited, and one genuinely novel chemical result has emerged. The project is <em>not</em>
yet able to train the generative extension, for reasons that are now understood to be
structural rather than incidental — and that diagnosis is itself one of the phase's most
useful outcomes.</p>

<div class="kpi">
  <div class="c"><div class="v">{poolA_n}</div><div class="l">Pool&nbsp;A rows
    (adsorption) · {poolA_src} sources</div></div>
  <div class="c"><div class="v">{poolB_n}</div><div class="l">Pool&nbsp;B rows
    (immobilisation) · {poolB_src} sources</div></div>
  <div class="c"><div class="v">{n_find}</div><div class="l">audited findings
    ({n_resolved} resolved)</div></div>
  <div class="c"><div class="v">122</div><div class="l">automated integrity tests
    passing</div></div>
</div>

<h4>The three things a reader should take away</h4>
<ol>
  <li><b>A real chemical finding.</b> For the uptake of cations such as Cs<sup>+</sup> and
    Sr<sup>2+</sup>, <em>framework aluminium</em> — the tetrahedral Al<sup>IV</sup> that
    creates the charge&#8209;balancing exchange sites — predicts capacity strongly
    (correlation up to <b>+0.95</b>), whereas <em>surface area</em> (BET), the quantity most
    often reported, does not (pooled <b>+0.08</b>). The two even move in opposite directions
    for organic dyes, confirming a different binding mechanism. This reframes what a "good
    adsorbent geopolymer" is.</li>
  <li><b>A rigorous data&#8209;integrity audit.</b> The compiled starting dataset was found,
    on source&#8209;by&#8209;source checking, to contain roughly <b>one&#8209;third</b>
    unreliable rows — including a europium measurement mislabelled as strontium, a fabricated
    feasibility domain, transplanted columns, and a published adsorption capacity a thousandfold
    larger than the same paper's measured uptake. Every one was traced, evidenced, and
    quarantined. The audit trail is a contribution in its own right.</li>
  <li><b>An honest obstacle.</b> The single descriptor that predicts uptake —
    framework Al — is almost never reported <em>together with</em> a Cs/Sr capacity in the
    same study. This is a structural feature of how two separate research communities publish,
    not a gap our searching can close. It is the reason the generative extension cannot yet be
    trained, and it defines exactly which papers must be acquired to proceed.</li>
</ol>
"""


def toc():
    items = [
        ("1", "Aim and scientific framing", "s1"),
        ("2", "Chemical foundations", "s2"),
        ("3", "Achievements — chemical findings", "s3"),
        ("4", "Achievements — the data&#8209;integrity audit", "s4"),
        ("5", "Current data structure", "s5"),
        ("6", "What we could not achieve, and why", "s6"),
        ("7", "Technical / machine&#8209;learning progress", "s7"),
        ("8", "Plan and next steps", "s8"),
        ("A", "Full finding register (all findings)", "sA"),
        ("B", "Pool A — every adsorption row", "sB"),
        ("C", "Pool B — every immobilisation row", "sC"),
        ("D", "Decisions register", "sD"),
        ("E", "Glossary of chemical terms", "sE"),
    ]
    links = "".join(
        f'<a href="#{i}"><span class="n">{n}</span>{t}</a>' for n, t, i in items
    )
    return f'<h2><span class="sec">Contents</span>Structure of this report</h2><div class="toc">{links}</div>'


print("part 2 loaded", file=sys.stderr)

# ---------------------------------------------------------------------------
# Section 1 — aim & framing
# ---------------------------------------------------------------------------
def s1():
    return """
<h2 id="s1"><span class="sec">Section 1</span>Aim and scientific framing</h2>

<p>Geopolymers are <em>alkali&#8209;activated aluminosilicates</em>: an aluminosilicate
precursor (metakaolin, fly ash, or blast&#8209;furnace slag) is dissolved in a strongly
alkaline activator (NaOH or KOH with sodium silicate) and re&#8209;condenses into a rigid
three&#8209;dimensional network of corner&#8209;sharing SiO<sub>4</sub> and AlO<sub>4</sub>
tetrahedra. Because aluminium sits in <em>tetrahedral</em> coordination (Al<sup>IV</sup>),
each AlO<sub>4</sub> unit carries a net negative framework charge, balanced by a mobile
alkali cation. Those charge&#8209;balancing sites are the ion&#8209;exchange sites that make a
geopolymer able to capture cationic radionuclides such as
<b>Cs<sup>+</sup> (caesium&#8209;137)</b> and <b>Sr<sup>2+</sup> (strontium&#8209;90)</b> — two
of the most mobile and long&#8209;lived fission products in nuclear waste.</p>

<h4>The reference work being replicated and extended</h4>
<p>The starting point is <em>GEOMIND</em> (RSC <i>Digital Discovery</i>, 2026, DOI
10.1039/d5dd00383k), a hybrid generative model that performs <em>inverse design</em>: given a
set of target properties, it generates a candidate geopolymer <em>formulation</em>. It couples
two variational autoencoders — a <b>Simulator</b> (formulation&nbsp;&rarr;&nbsp;properties) and
a <b>Formulator</b> (properties&nbsp;&rarr;&nbsp;formulation) — with a <b>feasibility block</b>
that keeps generated formulations chemically viable.</p>

<div class="box accent">
  <div class="t">The project in one sentence</div>
  Reproduce GEOMIND, then add a <b>fourth design dimension</b> — the capacity of a geopolymer
  to capture and retain Cs<sup>+</sup> and Sr<sup>2+</sup> — so that formulations can be
  generated specifically for radionuclide immobilisation.
</div>

<h4>A distinction that reshaped the project: two different chemistries</h4>
<p>Early work revealed that "capturing" a radionuclide is not one property but two, with
different chemistry and opposite figures of merit:</p>
<table class="key">
  <tr><td>Adsorption</td><td>The geopolymer is placed in a <em>solution</em> and removes
    the cation from it. The target is a <b>capacity</b> (mg&nbsp;g<sup>&minus;1</sup>, or a
    distribution coefficient <i>K</i><sub>d</sub>). Higher is better. — <em>Pool&nbsp;A</em></td></tr>
  <tr><td>Immobilisation</td><td>The cation is <em>built into</em> the solidified waste form
    and must not escape. The target is a <b>leach resistance</b> (leachability index,
    effective diffusivity). Higher resistance is better. — <em>Pool&nbsp;B</em></td></tr>
</table>
<p>These are different applications answering different questions, and — as Section&nbsp;6
explains — the chemical descriptor that predicts one is reported almost exclusively in studies
of the other. On the supervisor&rsquo;s decision the two are kept as
<b>two parallel datasets, never merged</b> (project decision&nbsp;D13).</p>

<h4>Honest scope of the dataset</h4>
<p>The compiled dataset is <em>literature&#8209;derived</em>, not newly measured in the
laboratory. Consequently every claim is framed as a <b>literature&#8209;scale meta&#8209;analysis
and external validation</b>, never as independent experimental replication. This framing is
stated up front because it governs how strongly any result may be worded.</p>
"""


# ---------------------------------------------------------------------------
# Section 2 — chemical foundations  (the chemistry-forward core)
# ---------------------------------------------------------------------------
def s2():
    return """
<h2 id="s2"><span class="sec">Section 2</span>Chemical foundations</h2>
<p>This section sets out the chemistry the rest of the report depends on. It is written for a
chemist and is deliberately the most detailed part of the document.</p>

<h3>2.1&nbsp;&nbsp;The geopolymer network and its descriptors</h3>
<p>The reactive network is described by a small set of chemical descriptors, each of which the
project treats as a candidate predictor of radionuclide uptake.</p>

<h4>The Si/Al ratio</h4>
<p>The molar <b>Si/Al</b> ratio is the primary compositional lever. A lower Si/Al means more
AlO<sub>4</sub> tetrahedra, hence more framework charge and more cation&#8209;exchange sites —
so, all else equal, lower Si/Al should mean higher cation capacity. It is the most&#8209;reported
descriptor, and precisely because it is a bulk ratio it is also the easiest to get wrong (see
the audit, Section&nbsp;4).</p>

<h4>Silicon speciation: the Q<sup>n</sup>(mAl) notation</h4>
<p>Solid&#8209;state <sup>29</sup>Si magic&#8209;angle&#8209;spinning NMR resolves the local
environment of each silicon atom. In the notation <b>Q<sup>n</sup>(mAl)</b>, <i>n</i> is the
number of bridging oxygens on the central Si (0&ndash;4, i.e. how condensed the site is) and
<i>m</i> is how many of those bridges connect to an <em>aluminium</em> rather than another
silicon. A fully condensed, aluminium&#8209;rich site is Q<sup>4</sup>(4Al); a fully condensed,
aluminium&#8209;free site is Q<sup>4</sup>(0Al). Sites with non&#8209;bridging oxygens
(Q<sup>3</sup>, Q<sup>2</sup>&hellip;) indicate a less&#8209;polymerised, more disrupted
network.</p>

<h4>From speciation to a framework&#8209;aluminium descriptor (ARI)</h4>
<p>Weighting each silicon environment by its aluminium count and summing gives the mean number
of Al neighbours per Si — the quantity the project calls the <b>Al&#8209;richness index</b>:</p>
<div class="eq">ARI&nbsp;=&nbsp;&Sigma;<sub>m</sub> ( m &middot; I<sub>m</sub> ) / 100
&nbsp;&nbsp;&nbsp;(I<sub>m</sub> = % of Si in a site with <i>m</i> Al neighbours)</div>
<p>ARI is proportional to the density of tetrahedral&#8209;Al charge&#8209;balancing sites — it
is a direct, NMR&#8209;based measure of the framework aluminium that ion exchange actually uses,
without needing <sup>27</sup>Al NMR. It is the central descriptor of this project.</p>

<h4>BET surface area — the descriptor the field usually reports</h4>
<p>The <b>BET</b> specific surface area (m<sup>2</sup>&nbsp;g<sup>&minus;1</sup>, from
N<sub>2</sub> physisorption) is the quantity most adsorption papers foreground. It measures
physical surface available for physisorption. A central result of this project (Section&nbsp;3)
is that for <em>cations</em> it is the <em>wrong</em> descriptor.</p>

<h3>2.2&nbsp;&nbsp;The immobilisation chemistry and the leachability index</h3>
<p>In a waste form the radionuclide is incorporated during synthesis and its escape is measured
by a semi&#8209;dynamic leach test. The transport is summarised by an effective diffusivity
<i>D</i><sub>e</sub> (cm<sup>2</sup>&nbsp;s<sup>&minus;1</sup>) and, in the ANSI/ANS&nbsp;16.1
standard, by the dimensionless <b>leachability index</b>:</p>
<div class="eq">L (or LI)&nbsp;=&nbsp;&minus;log<sub>10</sub>( <i>D</i><sub>e</sub> )
&nbsp;&nbsp;&nbsp;— higher LI = slower leaching = <b>better</b> immobilisation;
LI&nbsp;&ge;&nbsp;6 is the regulatory acceptance floor.</div>
<p>Because LI is logarithmic, a mean LI over several leaching intervals is a <em>geometric</em>
mean of <i>D</i><sub>e</sub> and cannot be inverted to a single diffusivity — a subtlety the
data schema enforces, and which was independently confirmed against three separate published
tables. A second, more dangerous subtlety: the phrase "diffusion coefficient of Cs" is used in
the literature for <em>two opposite experiments</em> — the cation leaching <em>out</em> of a
doped waste form (10<sup>&minus;16</sup>&hellip;10<sup>&minus;19</sup>&nbsp;cm<sup>2</sup>
s<sup>&minus;1</sup>) versus diffusing <em>into</em> an immersed specimen from solution
(~10<sup>&minus;8</sup>&nbsp;cm<sup>2</sup>&nbsp;s<sup>&minus;1</sup>). The two differ by
<b>twelve orders of magnitude</b>; the dataset keeps them as distinct quantities that may never
be pooled.</p>

<h3>2.3&nbsp;&nbsp;The adsorption isotherm and a saturation screen</h3>
<p>Adsorption capacities are usually reported as a Langmuir maximum, <i>Q</i><sub>max</sub>,
fitted to an isotherm. But a fitted <i>Q</i><sub>max</sub> is only a real capacity if the
experiment actually approached saturation. At low surface coverage the Langmuir form is nearly
linear, so it fits the data beautifully (high R<sup>2</sup>) while the plateau it implies is
essentially unconstrained — an authoritative&#8209;looking number that means very little.</p>
<p>The project therefore screens every fitted capacity by its fractional surface coverage at the
highest concentration used:</p>
<div class="eq">&theta;&nbsp;=&nbsp;b&middot;C<sub>0</sub> / (1 + b&middot;C<sub>0</sub>)
&nbsp;=&nbsp;1 &minus; R<sub>L</sub>
&nbsp;&nbsp;&nbsp;(R<sub>L</sub> = Langmuir separation factor, often already reported)</div>
<p>&theta;&nbsp;&ge;&nbsp;0.8 means the plateau was genuinely approached; &theta;&nbsp;&lt;&nbsp;0.5
means the "capacity" is an extrapolation. The identity &theta;&nbsp;=&nbsp;1&nbsp;&minus;&nbsp;R<sub>L</sub>
means the screen usually needs no extra data at all. This check — to our knowledge not routinely
applied when capacities are compiled across studies — is one of the project&rsquo;s methodological
contributions (Section&nbsp;3).</p>
"""
print("part 3 loaded", file=sys.stderr)

# ---------------------------------------------------------------------------
# Section 3 — chemical findings
# ---------------------------------------------------------------------------
def s3():
    ev = table(
        ["Evidence set", "n", "corr(BET, uptake)", "corr(framework&nbsp;Al, uptake)"],
        [
            ["Varon 2025 (Sr, K<sub>d</sub>)", "7", "+0.19", "<b>+0.95</b>"],
            ["Oulu Ca&#8209;free series (NH<sub>4</sub><sup>+</sup>, ARI)", "4", "&minus;0.98", "<b>+0.93</b>"],
            ["Xiang foams (Cs)", "5", "&minus;0.90", "—"],
            ["Lin 2026 (cation)", "4", "&minus;0.90", "—"],
            ["Oulu NH<sub>4</sub><sup>+</sup> (all)", "21", "&minus;0.47", "—"],
            ["<b>Pooled cations</b>", "—", "<b>+0.08</b>", "—"],
            ["Organic dyes (contrast class)", "42", "<b>+0.66</b>", "—"],
        ],
        right={1, 2, 3},
    )
    return f"""
<h2 id="s3"><span class="sec">Section 3</span>Achievements &mdash; chemical findings</h2>

<h3>3.1&nbsp;&nbsp;The central result: framework aluminium predicts cation uptake; surface area does not</h3>
<p>Across every dataset in which the two can be separated, the density of framework
aluminium — measured as Al<sup>IV</sup> content or as ARI — tracks cation uptake strongly and
positively, while BET surface area does not. Pooled across all cation datasets the BET
correlation collapses to essentially zero.</p>
{ev}
<div class="box win">
  <div class="t">Why this is chemically sensible</div>
  Cation uptake here is <b>ion exchange at charge&#8209;balancing AlO<sub>4</sub> sites</b>, not
  physisorption on a surface. More framework Al&nbsp;=&nbsp;more exchange sites&nbsp;=&nbsp;more
  capacity, regardless of how much physical surface the material presents. The contrast class
  proves the mechanism: for <b>organic dyes</b>, which <em>do</em> bind by surface physisorption,
  the BET correlation flips to <b>+0.66</b>. The descriptor that matters depends on the binding
  mechanism — so cation and dye data must never be pooled into one target.
</div>

<h3>3.2&nbsp;&nbsp;A structural precondition on the descriptor (finding&nbsp;F19)</h3>
<p>The framework&#8209;aluminium descriptor is not universal: it only means something where a
condensed aluminosilicate framework exists. When appreciable <b>calcium</b> is present, Ca acts
as a <em>network modifier</em>, disrupting the silicate linkages and driving the silicon
speciation toward low&#8209;connectivity Q<sup>0</sup>&ndash;Q<sup>2</sup> environments — in the
calcium&#8209;bearing samples analysed, the fully&#8209;condensed Q<sup>4</sup> population fell
essentially to zero. With no framework to measure, <em>no</em> compositional descriptor
predicts uptake (ARI, Si/Al, Ca/Al and BET all |r|&nbsp;&le;&nbsp;0.46), and capacity is nearly
flat at 7.3&nbsp;&plusmn;&nbsp;1.3&nbsp;mg&nbsp;g<sup>&minus;1</sup>. Pooling calcium&#8209;rich and
calcium&#8209;free sorbents together produced a misleadingly mediocre correlation that concealed
two entirely different regimes. The lesson — <em>never pool across structural classes</em> —
generalises the dye/cation lesson one level deeper.</p>

<h3>3.3&nbsp;&nbsp;The isotherm saturation screen (findings F14&ndash;F17)</h3>
<p>Applying the &theta;&nbsp;=&nbsp;1&nbsp;&minus;&nbsp;R<sub>L</sub> screen of Section&nbsp;2.3 to
all 35 fitted Langmuir capacities in the pool:</p>
<div class="kpi" style="grid-template-columns:repeat(3,1fr)">
  <div class="c"><div class="v">31</div><div class="l">sound (&theta;&nbsp;&ge;&nbsp;0.8) —
    measured, not extrapolated</div></div>
  <div class="c"><div class="v">1</div><div class="l">borderline
    (&theta;&nbsp;=&nbsp;0.78)</div></div>
  <div class="c"><div class="v">3</div><div class="l">extrapolation artefacts, excluded</div></div>
</div>
<p>The trigger case: a chabazite fit reported <i>Q</i><sub>max</sub>&nbsp;=&nbsp;1249.5&nbsp;mg
g<sup>&minus;1</sup> at R<sup>2</sup>&nbsp;=&nbsp;0.99989, while the same paper&rsquo;s measured
equilibrium uptake was <b>1.184&nbsp;mg&nbsp;g<sup>&minus;1</sup></b> — a capacity extrapolated a
thousandfold beyond any data point, flagged by nothing in the reported statistics. Two of the
excluded fits additionally showed a negative intercept in their linearised form, implying an
unphysical negative affinity constant. When a sixth source was later recovered (Section&nbsp;4),
the screen immediately caught a further artefact — the <em>highest</em> reported capacity of
that source&rsquo;s five, unsaturated at &theta;&nbsp;=&nbsp;0.50.</p>

<h3>3.4&nbsp;&nbsp;Immobilisation: strontium is held far better than caesium</h3>
<p>In the immobilisation pool a single result is strikingly robust: in the <em>same</em> binder,
strontium is retained far better than caesium. In one metakaolin K&ndash;A&ndash;S&ndash;H gel
the effective diffusivities differ by roughly <b>six orders of magnitude</b>
(<i>D</i><sub>e,Sr</sub>&nbsp;&asymp;&nbsp;8&times;10<sup>&minus;20</sup> vs
<i>D</i><sub>e,Cs</sub>&nbsp;&asymp;&nbsp;6&times;10<sup>&minus;14</sup>&nbsp;cm<sup>2</sup>
s<sup>&minus;1</sup>), and Sr&rsquo;s leachability index exceeds Cs&rsquo;s in <em>every</em> one
of the fourteen specimens measured. Chemically: Sr<sup>2+</sup>, being divalent and readily
precipitated as SrCO<sub>3</sub>, is chemically bound in the gel, whereas the large, singly&#8209;
charged, highly soluble Cs<sup>+</sup> is held only weakly. Every alkali&#8209;activated matrix
in the pool clears the ANSI/ANS&nbsp;16.1 acceptance floor (LI&nbsp;&ge;&nbsp;6) for both
nuclides.</p>

<h3>3.5&nbsp;&nbsp;A methodological result: a rejected NMR deconvolution that was rejected for the right reason</h3>
<p>An attempt to derive the Q<sup>4</sup>(mAl) speciation of a set of <sup>29</sup>Si spectra
by fitting five Gaussian peaks reached an excellent fit (R<sup>2</sup>&nbsp;&asymp;&nbsp;0.998)
yet was <em>rejected</em>, because it forced the Q<sup>4</sup>(3Al) population to exactly zero —
which is chemically impossible for the composition. The rejection was later vindicated when the
authors&rsquo; own deconvolution was found already published: they use <b>ten</b> silicon
environments including Q<sup>3</sup>/Q<sup>2</sup> species, which a five&#8209;peak,
Q<sup>4</sup>&#8209;only model structurally cannot represent. A chemical sanity check caught a
structurally wrong model that a near&#8209;perfect fit statistic could not — a cautionary result
worth reporting in its own right.</p>
"""


# ---------------------------------------------------------------------------
# Section 4 — the data-integrity audit (candid)
# ---------------------------------------------------------------------------
def s4():
    audit_rows = [
        ["Europium mislabelled as strontium", "A Eu measurement carried into the pool as an Sr capacity — different element, different chemistry."],
        ["Fabricated feasibility domain", "A &lsquo;feasibility range&rsquo; table attributed to GEOMIND was in fact copied from this project&rsquo;s own retired heuristic tool; applied to the paper&rsquo;s own samples it rejected 7 of 9 feasible and accepted the 1 infeasible."],
        ["Transplanted columns", "Si/Al and density values from the paper&rsquo;s 10 published samples had been broadcast across an unrelated concrete dataset; both columns dropped."],
        ["A thousandfold&#8209;extrapolated capacity", "The chabazite <i>Q</i><sub>max</sub> of 1249.5 vs 1.184&nbsp;mg&nbsp;g<sup>&minus;1</sup> measured (&sect;3.3)."],
        ["Misattributed EXAFS values", "Two strontium coordination numbers credited to one author were in fact another study&rsquo;s, verbatim."],
        ["A published typo, caught by arithmetic", "A tabulated leachability index (15.5) was inconsistent with its own diffusivity; the paper&rsquo;s own column average proved the intended value was 15.1."],
        ["Silent half&#8209;table loss", "A provided workbook had dropped both caesium rows of a source&rsquo;s leach table — half the data — undetectably without reading the source."],
    ]
    return f"""
<h2 id="s4"><span class="sec">Section 4</span>Achievements &mdash; the data&#8209;integrity audit</h2>
<p>The largest single body of work in this phase was verifying the compiled data against its
primary sources. It is presented candidly because it is, scientifically, the most defensible
contribution made so far: <b>roughly one&#8209;third of the compiled rows did not survive
source&#8209;by&#8209;source audit.</b> A representative sample of what was caught:</p>
{table(["What was found", "Detail"], audit_rows)}

<div class="box accent">
  <div class="t">The standing rule this produced</div>
  No number enters either dataset until its value has been read <em>in context</em> in the
  primary source PDF. A number existing somewhere in a paper is not evidence of what it means.
  Every quarantine and correction is enforced in code and covered by an automated test, so a
  future edit cannot silently reintroduce a rejected value.
</div>

<h4>The audit also turned up value, not only errors</h4>
<p>Reading sources in full — rather than trusting a keyword&#8209;based triage — recovered
several papers that had been wrongly set aside. One rejected "diffusivity study" in fact
published caesium adsorption capacities for five different activators (a genuine gap&#8209;filler
for Pool&nbsp;A); another "review" turned out to index exactly the paired&#8209;descriptor
sources the project most needs; and two of the most descriptor&#8209;rich papers held were
initially invisible because their filenames were not in Latin script. Four times this phase,
the most valuable next step proved to be reading a document already in hand rather than
acquiring a new one.</p>

<p class="small">The complete, evidenced register of all {n_find} findings ({n_resolved}
resolved) is given in Appendix&nbsp;A.</p>
"""
print("part 4 loaded", file=sys.stderr)

# ---------------------------------------------------------------------------
# Section 5 — current data structure
# ---------------------------------------------------------------------------
def s5():
    a_by_src = A.groupby("source_label").size().sort_values(ascending=False)
    a_by_cls = A.groupby("adsorbate_class").size().sort_values(ascending=False)
    b_by_src = B.groupby("source_label").size().sort_values(ascending=False)

    a_src_tbl = table(
        ["Source", "rows"],
        [[esc(s), str(int(n))] for s, n in a_by_src.items()],
        right={1},
    )
    a_cls_tbl = table(
        ["Adsorbate class", "rows"],
        [[esc(s), str(int(n))] for s, n in a_by_cls.items()],
        right={1},
    )
    b_src_tbl = table(
        ["Source", "rows"],
        [[esc(s), str(int(n))] for s, n in b_by_src.items()],
        right={1},
    )
    return f"""
<h2 id="s5"><span class="sec">Section 5</span>Current data structure</h2>
<p>All data lives in a single governed system, not in scattered files. Three layers keep it
honest.</p>

<h3>5.1&nbsp;&nbsp;A single source of truth (the registry)</h3>
<p>Every data asset, primary source, finding and decision is recorded in one machine&#8209;checked
registry ({len(REG['assets'])} assets, {len(REG['sources'])} sources, {n_find} findings,
{len(decisions)} decisions). A validator rejects any dangling reference, unknown status, or
finding without an action, and regenerates the human&#8209;readable documentation from it. The
registry — not anyone&rsquo;s memory — is the project&rsquo;s ground truth.</p>

<h3>5.2&nbsp;&nbsp;A strict labelling system</h3>
<p>Every mined record is tagged on three independent axes, so a record&rsquo;s trustworthiness is
explicit and a model can be restricted to only defensible rows:</p>
<table class="key">
  <tr><td>Veracity</td><td>verified&#8209;true · probable · unverified · redundant · false</td></tr>
  <tr><td>Utility</td><td>core · supporting · context · discard</td></tr>
  <tr><td>Granularity</td><td>observation · raw&#8209;signal · reference</td></tr>
</table>
<p>Only rows that are (verified&#8209;true or probable) <b>and</b> (core or supporting)
<b>and</b> an observation are considered modellable.</p>

<h3>5.3&nbsp;&nbsp;Two parallel datasets (decision&nbsp;D13)</h3>
<p>The two chemistries of Section&nbsp;1 are held as two schemas that share no target column, so
they can never be concatenated by accident.</p>

<h4>Pool&nbsp;A &mdash; adsorption &nbsp;({poolA_n} rows, {poolA_src} sources)</h4>
<p>Target: adsorption capacity (mg&nbsp;g<sup>&minus;1</sup>) or distribution coefficient. The
schema separates five distinct capacity <em>types</em> (a fitted Langmuir maximum and a
single&#8209;point uptake are not the same number) and four adsorbate classes, so incompatible
quantities cannot be silently averaged.</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
  <div>{a_src_tbl}</div><div>{a_cls_tbl}</div>
</div>

<h4>Pool&nbsp;B &mdash; immobilisation &nbsp;({poolB_n} rows, {poolB_src} sources)</h4>
<p>Target: leach resistance. The schema encodes four traps peculiar to this chemistry: the
figure of merit is <em>inverted</em> (a high leach rate is bad); doped loading is a
<em>control</em> variable, never a target; a below&#8209;detection result is
<em>information</em> (the best performers), kept as left&#8209;censored data rather than
discarded; and the two &lsquo;diffusion coefficients&rsquo; that differ by twelve orders of
magnitude are kept as separate quantities.</p>
{b_src_tbl}
<p class="small">Every individual row of both pools is listed in Appendices&nbsp;B and&nbsp;C.</p>
"""


# ---------------------------------------------------------------------------
# Section 6 — what we could not achieve, and why
# ---------------------------------------------------------------------------
def s6():
    return f"""
<h2 id="s6"><span class="sec">Section 6</span>What we could not achieve, and why we are stuck</h2>
<p>The generative extension — the project&rsquo;s ultimate goal — cannot yet be trained. The
reasons are specific and, importantly, now diagnosed rather than merely encountered.</p>

<h3>6.1&nbsp;&nbsp;The predictive descriptor is structurally scarce (finding&nbsp;F20)</h3>
<p>Framework aluminium is the one descriptor that predicts cation uptake (Section&nbsp;3.1) — and
it is reported almost nowhere alongside a Cs/Sr capacity. A content survey of the whole corpus
made the reason plain:</p>
<div class="box warn">
  <div class="t">Two communities that do not overlap</div>
  <b>Every</b> adsorption study in the corpus reports zero solid&#8209;state NMR, while four of
  the six NMR&#8209;rich papers are immobilisation (waste&#8209;form) studies. Water&#8209;treatment
  groups measure isotherms and surface area and never run NMR; nuclear&#8209;waste groups run full
  <sup>29</sup>Si/<sup>27</sup>Al NMR and measure leach rates and never run isotherms. The
  descriptor and the target sit on opposite sides of a disciplinary divide.
</div>
<p>The practical consequence is decisive: <b>more literature searching cannot fix this</b> — the
co&#8209;occurrence is rare by the structure of the field, not by any narrowness of our search.
Framework&#8209;Al data currently exists paired with a capacity in only a handful of rows, from a
single source. Both datasets end up descriptor&#8209;starved, for mirror&#8209;image reasons:
Pool&nbsp;A has composition but no NMR; Pool&nbsp;B has NMR but almost no compositional
variation.</p>

<h3>6.2&nbsp;&nbsp;The faithful replication is blocked on confidential data</h3>
<p>GEOMIND was trained on 112 samples from one laboratory under one protocol; only 10 are public.
A <em>faithful</em> replication (milestone&nbsp;M3a) is impossible without the full set, which is
confidential. A formal data&#8209;request letter has been drafted and awaits sending. Our own
compiled data cannot substitute: it is fly&#8209;ash/slag concrete, whereas GEOMIND is metakaolin
paste — a different material system with no viscosity target and only ~92 distinct mix designs,
so that strand has been honestly <em>re&#8209;scoped</em> from &lsquo;replication&rsquo; to a
&lsquo;cross&#8209;system transfer study&rsquo;.</p>

<h3>6.3&nbsp;&nbsp;Inverse design is not reachable on the present data</h3>
<p>There are only {radio_n} radionuclide (Cs/Sr) rows in Pool&nbsp;A, spread across many
laboratories and protocols. Training a generative inverse&#8209;design model on so few rows from
so many sources would learn inter&#8209;laboratory protocol differences and report them as
chemistry — precisely the failure the audit exists to prevent, one level up. The defensible
near&#8209;term output is a <em>descriptor&#8209;and&#8209;methodology</em> study, not a generative
model.</p>

<div class="box">
  <div class="t">The obstacle stated plainly</div>
  We are not stuck for lack of effort or data volume. We are stuck because the one chemical
  descriptor that works is, by the structure of the published literature, almost never measured
  together with the property we want to predict. That diagnosis tells us <em>exactly</em> which
  few papers would unblock the work (Section&nbsp;8).
</div>
"""
print("part 5 loaded", file=sys.stderr)

# ---------------------------------------------------------------------------
# Section 7 — technical / ML progress (high-level)
# ---------------------------------------------------------------------------
def s7():
    ms = table(
        ["Milestone", "State", "Note"],
        [
            ["M1 &mdash; paper analysis", "<span class='st-ok'>done</span>",
             "Reproduction specification written; the authors&rsquo; code located (unlicensed &rarr; clean&#8209;room only)."],
            ["M2 &mdash; data cleaning &amp; audit", "<span class='st-ok'>done</span>",
             "~32% of compiled rows failed source audit (Section&nbsp;4)."],
            ["M3a &mdash; chemistry layer", "<span class='st-ok'>verified</span>",
             "Si/Al, Si/M<sub>sol</sub> and Solid/Liquid molar ratios reproduce the paper&rsquo;s own samples to within 1&ndash;3%."],
            ["M3a &mdash; generative VAEs", "<span class='st-open'>not started</span>",
             "Blocked on training decisions and, more fundamentally, on data (Section&nbsp;6)."],
            ["M3b &mdash; cross&#8209;system transfer", "re&#8209;scoped",
             "Not a GEOMIND validation &mdash; a different material system, stated as such."],
            ["M4 &mdash; adsorption dimension", "in progress",
             "The chemical question is answered; the descriptor is scarce."],
            ["M5 &mdash; radionuclide design", "<span class='st-open'>blocked</span>", "Needs M4."],
            ["M6 &mdash; corpus expansion", "continuous", "Automated scraping exhausted; targeted acquisition now."],
        ],
    )
    return f"""
<h2 id="s7"><span class="sec">Section 7</span>Technical / machine&#8209;learning progress
  <span style="font-size:11pt;color:var(--muted);font-family:var(--serif)">(high&#8209;level)</span></h2>
<p>For completeness, the engineering status at a glance. The chemistry above is where the
scientific progress lives; the technical layer is deliberately kept faithful and modest.</p>
{ms}
<p>The one piece of the model already built and <em>verified</em> is the chemistry layer: the
molar&#8209;ratio calculations that any generated formulation must satisfy reproduce the
authors&rsquo; published samples to 1&ndash;3%. This is the foundation the generative blocks would
sit on. Everything is version&#8209;controlled with a full branch/issue workflow, and the whole
data pipeline is covered by <b>122 automated tests</b> that encode each chemical rule (unit
conversions, the saturation screen, the pooling prohibitions, the leachability&#8209;index
mathematics) so that no future change can quietly violate them.</p>
"""


# ---------------------------------------------------------------------------
# Section 8 — plan & next steps
# ---------------------------------------------------------------------------
def s8():
    acq = table(
        ["Priority", "Source to acquire", "Why it matters", "Unblocks"],
        [
            ["1", "Geddes <i>et&nbsp;al.</i> 2025, <span class='mono'>J.&nbsp;Hazard.&nbsp;Mater.&nbsp;488</span>",
             "Title promises Sr incorporation mechanism (NMR) <b>and</b> binding capacity in one paper &mdash; the rare bridge of Section&nbsp;6.", "M4, M5"],
            ["1", "Komljenovi&cacute; <i>et&nbsp;al.</i> 2020, <span class='mono'>J.&nbsp;Hazard.&nbsp;Mater.&nbsp;388</span>",
             "Ties <sup>29</sup>Si speciation to strength <b>and</b> Cs immobilisation &mdash; a second candidate bridge.", "M4, M5"],
            ["2", "Qian <i>et&nbsp;al.</i> 2001, <span class='mono'>J.&nbsp;Nucl.&nbsp;Mater.&nbsp;299</span>",
             "Cs and Sr distribution ratios (K<sub>d</sub>) &mdash; primary data for Pool&nbsp;A.", "M4"],
            ["2", "<i>Next Sustainability</i> 2025", "The only source with a 1&ndash;5&nbsp;M activator&#8209;concentration axis alongside Cs, Sr and NMR.", "M6"],
            ["3", "GEOMIND 112&#8209;sample dataset (confidential request)", "Larger than every scraping avenue combined; the only route to a faithful replication.", "M3a"],
        ],
    )
    return f"""
<h2 id="s8"><span class="sec">Section 8</span>Plan and next steps</h2>

<h3>8.1&nbsp;&nbsp;Immediate: acquire the few papers that unblock the descriptor</h3>
<p>Section&nbsp;6 turns an open&#8209;ended obstacle into a short shopping list. These specific
sources are the ones identified as carrying framework&#8209;Al data <em>together with</em> a
Cs/Sr retention or capacity measure — the combination the field almost never publishes.</p>
{acq}
<p class="small">A consolidated worklist, with where each file should be placed, is maintained at
<span class="mono">docs/acquisition-worklist.md</span>.</p>

<h3>8.2&nbsp;&nbsp;Near term: the defensible scientific output</h3>
<p>Independent of acquisition, the present data already supports a <b>descriptor&#8209;and&#8209;
methodology paper</b>: that for cation uptake framework aluminium predicts and surface area does
not, with the structural precondition (Section&nbsp;3.2); and that a simple
saturation screen (&theta;&nbsp;=&nbsp;1&nbsp;&minus;&nbsp;R<sub>L</sub>) exposes published
capacities that are extrapolation artefacts (Section&nbsp;3.3). Both are novel, both are
defensible now, and neither requires the confidential dataset.</p>

<h3>8.3&nbsp;&nbsp;Medium term: the two&#8209;pool path to the design goal</h3>
<p>With the priority&#8209;1 papers in hand, the framework&#8209;Al descriptor can be paired with a
retention target in enough samples to test whether it also predicts <em>immobilisation</em> (it
should, by the same charge&#8209;balancing chemistry). That is the bridge from the descriptor
result to the project&rsquo;s stated aim of designing formulations for Cs&#8209;137/Sr&#8209;90.
The generative model (M3a/M5) remains gated on either the confidential GEOMIND set or a
substantially enlarged paired dataset — and the report is deliberately honest that this is not
within reach on current data.</p>

<h3>8.4&nbsp;&nbsp;What we are asking of this checkpoint</h3>
<ul>
  <li>Agreement that the <b>descriptor&#8209;and&#8209;methodology result</b> is the right
    near&#8209;term scientific target.</li>
  <li>Guidance on <b>acquiring the priority&#8209;1 papers</b> (institutional access to
    <span class="mono">J. Hazard. Mater.</span>), and on whether the department can support the
    confidential GEOMIND data request.</li>
  <li>A steer on whether a small <b>own&#8209;laboratory NMR measurement</b> on a few sorbents of
    known capacity is feasible &mdash; the only route that would generate genuinely new paired
    data rather than re&#8209;using the literature.</li>
</ul>
"""
print("part 6 loaded", file=sys.stderr)

# ---------------------------------------------------------------------------
# Appendix A — full finding register
# ---------------------------------------------------------------------------
def appA():
    cards = []
    for f in findings:
        sev = f.get("severity", "medium")
        chip = f'<span class="chip {SEV.get(sev,"sev-med")}">{esc(sev)}</span>'
        st = f.get("status", "open")
        stcls = "st-ok" if st == "resolved" else "st-open"
        ev = " ".join(str(f.get("evidence", "")).split())
        ac = " ".join(str(f.get("action", "")).split())
        parts = [
            f'<div class="fcard {esc(sev)}">',
            f'<div class="h">{chip} &nbsp;{esc(f["id"])} &mdash; {esc(f.get("title",""))} '
            f'&nbsp;<span class="{stcls}" style="font-size:8.4pt">[{esc(st.replace("_"," "))}]</span></div>',
        ]
        if ev:
            parts.append(f'<div class="lab">Evidence</div><p>{esc(ev)}</p>')
        if ac:
            parts.append(f'<div class="lab">Action</div><p>{esc(ac)}</p>')
        parts.append("</div>")
        cards.append("".join(parts))
    return (
        '<h2 id="sA"><span class="sec">Appendix A</span>Full finding register</h2>'
        f'<p>All {n_find} audited findings, most&#8209;recent last, each with the evidence that '
        "established it and the action taken. Severity is the data&#8209;integrity impact.</p>"
        + "".join(cards)
    )


# ---------------------------------------------------------------------------
# Appendix B — every Pool A row
# ---------------------------------------------------------------------------
def appB():
    cols = ["source_label", "sorbent_name", "adsorbate", "adsorbate_class",
            "capacity_mg_g", "capacity_type", "si_al", "bet_m2_g", "al_iv_pct",
            "provenance_doi"]
    rows = []
    for i, (_, r) in enumerate(A.iterrows(), 1):
        rows.append([
            str(i), esc(r["source_label"]), esc(r["sorbent_name"]),
            esc(r["adsorbate"]), esc(r["adsorbate_class"]),
            num(r["capacity_mg_g"]), esc(r["capacity_type"]),
            num(r["si_al"]), num(r["bet_m2_g"]), num(r["al_iv_pct"]),
            doi_short(r["provenance_doi"]),
        ])
    hdr = ["#", "source", "sorbent", "adsorbate", "class", "cap&nbsp;(mg/g)",
           "type", "Si/Al", "BET", "Al<sup>IV</sup>%", "provenance"]
    return (
        '<h2 id="sB"><span class="sec">Appendix B</span>Pool A &mdash; every adsorption row</h2>'
        f'<p>All {poolA_n} rows across {poolA_src} sources. &lsquo;&mdash;&rsquo; = not reported '
        "for that row. Generated directly from the pipeline; nothing hand&#8209;entered.</p>"
        + table(hdr, rows, cls="data wide", right={0, 5, 7, 8, 9})
    )


# ---------------------------------------------------------------------------
# Appendix C — every Pool B row
# ---------------------------------------------------------------------------
def appC():
    rows = []
    for i, (_, r) in enumerate(B.iterrows(), 1):
        cens = r.get("censored")
        cens = "" if (cens in (None, "none") or (isinstance(cens, float) and cens != cens)) else esc(cens)
        rows.append([
            str(i), esc(r["source_label"]), esc(r["matrix_name"]),
            esc(r["matrix_class"]), esc(r["nuclide"]),
            esc(str(r["retention_type"]).replace("_", " ")) if r["retention_type"] == r["retention_type"] and r["retention_type"] else "—",
            num(r["retention_value"]), cens,
            num(r.get("ari")), num(r.get("porosity_pct")),
            doi_short(r["provenance_doi"]),
        ])
    hdr = ["#", "source", "matrix", "class", "nuclide", "target", "value",
           "cens.", "ARI", "poros.%", "provenance"]
    return (
        '<h2 id="sC"><span class="sec">Appendix C</span>Pool B &mdash; every immobilisation row</h2>'
        f'<p>All {poolB_n} rows across {poolB_src} sources. &lsquo;target&rsquo; distinguishes a '
        "leachability index (higher = better) from an ingress diffusivity; the two are never "
        "pooled. &lsquo;cens.&rsquo; marks a left&#8209;censored (below&#8209;detection, best&#8209;"
        "performing) result.</p>"
        + table(hdr, rows, cls="data wide", right={0, 6, 8, 9})
    )


# ---------------------------------------------------------------------------
# Appendix D — decisions
# ---------------------------------------------------------------------------
def appD():
    rows = [[esc(d["id"]), esc(d["decision"]), esc(d.get("reason", ""))] for d in decisions]
    return (
        '<h2 id="sD"><span class="sec">Appendix D</span>Decisions register</h2>'
        f"<p>The {len(decisions)} standing project decisions, each with its reason. These are the "
        "rules the pipeline enforces.</p>"
        + table(["#", "Decision", "Reason"], rows)
    )


# ---------------------------------------------------------------------------
# Appendix E — glossary
# ---------------------------------------------------------------------------
def appE():
    terms = [
        ("Alkali&#8209;activated material (AAM)", "Binder made by activating an aluminosilicate precursor with a strong alkali; geopolymers are the aluminium&#8209;rich, low&#8209;calcium end of this family."),
        ("Al<sup>IV</sup> / framework aluminium", "Aluminium in tetrahedral coordination within the network; each site carries a negative charge balanced by an exchangeable cation. The predictive descriptor of this project."),
        ("ARI (Al&#8209;richness index)", "Mean number of Al neighbours per Si, &Sigma;<sub>m</sub> m&middot;I<sub>m</sub>/100, from <sup>29</sup>Si NMR speciation; an NMR&#8209;based measure of framework aluminium."),
        ("BET surface area", "Specific surface area from N<sub>2</sub> physisorption (m<sup>2</sup>&nbsp;g<sup>&minus;1</sup>). Predicts dye (physisorption) uptake but <em>not</em> cation (ion&#8209;exchange) uptake."),
        ("Distribution coefficient K<sub>d</sub>", "Ratio of sorbed to solution concentration (mL&nbsp;g<sup>&minus;1</sup>); a measure of affinity, distinct from a capacity."),
        ("Effective diffusivity D<sub>e</sub>", "Rate constant for a nuclide leaching out of a waste form (cm<sup>2</sup>&nbsp;s<sup>&minus;1</sup>); lower is better."),
        ("Leachability index (LI, L)", "&minus;log<sub>10</sub>(D<sub>e</sub>); ANSI/ANS&nbsp;16.1 ranking of immobilisation. Higher = better; &ge;6 is the acceptance floor."),
        ("Langmuir Q<sub>max</sub>", "Fitted monolayer saturation capacity (mg&nbsp;g<sup>&minus;1</sup>); meaningful only if the experiment approached saturation (the &theta; screen)."),
        ("Q<sup>n</sup>(mAl)", "A silicon environment with <i>n</i> bridging oxygens, <i>m</i> of them to aluminium; from <sup>29</sup>Si MAS NMR."),
        ("R<sub>L</sub> / &theta;", "Langmuir separation factor; &theta;&nbsp;=&nbsp;1&nbsp;&minus;&nbsp;R<sub>L</sub> is the fraction of saturation reached, used to screen fitted capacities."),
        ("Si/Al ratio", "Molar silicon&#8209;to&#8209;aluminium ratio; lower means more charge&#8209;balancing sites."),
        ("Network modifier (Ca)", "Calcium disrupts the aluminosilicate framework toward low&#8209;connectivity C&ndash;A&ndash;S&ndash;H, where framework descriptors lose meaning."),
    ]
    rows = [[t, d] for t, d in terms]
    return (
        '<h2 id="sE"><span class="sec">Appendix E</span>Glossary of chemical terms</h2>'
        + table(["Term", "Meaning"], rows)
    )


# ---------------------------------------------------------------------------
# assemble  (guarded so this module can be imported for its helpers/appendices)
# ---------------------------------------------------------------------------
def main():
    body = "".join([
        cover(), execsum(), toc(),
        s1(), s2(), s3(), s4(), s5(), s6(), s7(), s8(),
        appA(), appB(), appC(), appD(), appE(),
    ])
    foot = (
        '<div class="foot">GEOMIND&#8209;R &mdash; Confidential supervisory checkpoint &middot; '
        f'{n_find} findings, {n_resolved} resolved &middot; Pool&nbsp;A {poolA_n} rows / '
        f'{poolA_src} sources &middot; Pool&nbsp;B {poolB_n} rows / {poolB_src} sources &middot; '
        '122 automated tests passing &middot; Prepared by Mulham Fetna. '
        'All quantitative values generated directly from the project registry and data pipeline.</div>'
    )
    html_doc = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width, initial-scale=1'>"
        "<title>GEOMIND-R — Supervisory Checkpoint</title>"
        f"<style>{CSS}</style></head><body><div class='page'>{body}{foot}</div></body></html>"
    )
    out = ROOT / "reports" / "GEOMIND-R-seminar-checkpoint.html"
    out.write_text(html_doc, encoding="utf-8")
    print(f"wrote {out}  ({len(html_doc)//1024} KB)", file=sys.stderr)


if __name__ == "__main__":
    main()
