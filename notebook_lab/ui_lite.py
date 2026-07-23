"""Notebook Gradio app — mirrors the desktop app/lab.py's eight tabs against engine_lite.

Self-contained: reads lab_bundle.json (via engine_lite) and the bundled figure PNGs. Launches
Colab-internal (a plain demo.launch(), no public tunnel). Embedded verbatim into the notebook.
"""
from __future__ import annotations

import base64
import json
import os
import tempfile
from pathlib import Path

import gradio as gr
import pandas as pd

try:
    from notebook_lab import engine_lite as E
except ImportError:  # top-level (Colab) context
    import engine_lite as E

_FLAG_BADGE = {
    E.Confidence.VALIDATED: "🟢 VALIDATED",
    E.Confidence.EXPLORATORY: "🟡 EXPLORATORY",
    E.Confidence.UNSUPPORTED: "🔴 UNSUPPORTED",
}

_CLASSES = ["metakaolin geopolymer", "fly-ash geopolymer", "slag geopolymer",
            "Ca-rich (C-A-S-H) gel", "zeolite"]
_ADSORBATES = ["Sr", "Cs"]


def _bundle():
    return E._bundle()


# --- handlers (mirror app/lab.py) -----------------------------------------------------------
def _predict_handler(al_iv_mmol_g, structural_class, adsorbate):
    card = E.predict_kd(al_iv_mmol_g, structural_class=structural_class, adsorbate=adsorbate)
    badge = _FLAG_BADGE[card.flag]
    value_str = f"{card.value:,.0f} {card.unit}" if card.value is not None else "—"
    label = f"{badge}  ·  K_D ≈ {value_str}"
    lines = [f"**Predicted Sr K_D:** {value_str}  ({badge})", ""]
    if card.uncertainty is not None:
        lines.append(f"**Uncertainty (LOO-CV RMSE):** ±{card.uncertainty:,.0f} {card.unit}")
    lines += ["", f"**Why:** {card.why}", "", f"**Provenance:** {card.provenance}"]
    if card.flag is not E.Confidence.VALIDATED:
        lines.insert(1, "> ⚠️ This value is shown for exploration; it is **not** a "
                        "prediction the project stands behind here. Read the flag.")
    return label, "\n".join(lines)


def _screen_handler(b_L_mg, c0_mg_L):
    card = E.screen_saturation(b_L_mg, c0_mg_L)
    return (f"**θ = {card.value:.2f}**  (R_L = {card.extra['R_L']:.2f}) — "
            f"verdict: **{card.extra['verdict']}**\n\n{card.why}\n\n_{card.provenance}_")


def _pooling_handler(sources):
    card = E.pooled_loo_r2(sources)
    if card.value is None:
        return f"**{card.extra['verdict']}** — {card.why}\n\n_{card.provenance}_"
    verdict = card.extra["verdict"]
    mark = "✓ predictive" if verdict == "predictive" else "✗ worse-than-mean"
    return (f"**LOO-CV R^2 = {card.value:+.2f}**  ({mark}, n = {card.extra['n']})\n\n"
            f"{card.why}\n\n_{card.provenance}_")


def _structural_handler(include_ca):
    card = E.structural_precondition(include_ca=bool(include_ca))
    return (f"**r = {card.value:+.2f}**  (n = {card.extra['n']}; "
            f"framework-only r = {card.extra['framework_r']:+.2f})\n\n"
            f"{card.why}\n\n_{card.provenance}_")


def _pool_handler(name):
    return E.load_pool(name)


def _findings_table(query: str):
    rows = E.load_findings()
    q = (query or "").strip().lower()
    if q:
        rows = [r for r in rows
                if q in " ".join(str(r.get(k, "")) for k in
                                  ("id", "severity", "title", "evidence", "action", "status")).lower()]
    return pd.DataFrame([{"id": r.get("id"), "severity": r.get("severity"),
                          "title": r.get("title"), "status": r.get("status"),
                          "action": r.get("action")} for r in rows])


def _audit_summary_md() -> str:
    df = E.load_audit_summary()
    if len(df) == 0:
        return "_Audit trail unavailable._"
    g = df.groupby("veracity").agg(files=("source_file", "count"),
                                   rows=("n_rows", "sum")).reset_index()
    lines = ["| veracity | files | rows |", "|---|---:|---:|"]
    for _, r in g.iterrows():
        lines.append(f"| {r['veracity']} | {int(r['files'])} | {int(r['rows'])} |")
    total = int(g["files"].sum())
    kept = int(g[g["veracity"].isin(["VERIFIED_TRUE", "PROBABLE"])]["files"].sum())
    lines += ["", f"**{total} tables audited; {total - kept} set aside** "
              "(UNVERIFIED / REDUNDANT / FALSE) — every one with a recorded reason."]
    return "\n".join(lines)


def _rerun_handler() -> str:
    h = E.rerun_headline_numbers()
    return (
        "### Recomputed live from the bundle\n"
        f"- **Forward model (within-class):** K_D = {h['forward_slope']:.0f}·[Al^IV] "
        f"− {abs(h['forward_intercept']):.0f} mL/g, **LOO-CV R² = {h['forward_r2_loo']:.2f}** "
        "— predicts held-out samples.\n"
        f"- **Pooled across laboratories (F36):** LOO-CV R² = **{h['pooled_r2']:+.2f}** "
        "— worse than the mean.\n"
        f"- **Structural precondition (F19):** framework ARI r = **{h['framework_r']:+.2f}**, "
        f"degrading to {h['pooled_struct_r']:+.2f} when Ca gels are pooled in.\n"
    )


def _figure_paths() -> dict:
    """Decode the bundled figure PNGs to temp files; return {key: path}."""
    figs = _bundle().get("figures", {})
    out = {}
    d = Path(tempfile.gettempdir()) / "geomind_lab_figs"
    d.mkdir(exist_ok=True)
    for key, b64 in figs.items():
        p = d / f"{key}.png"
        p.write_bytes(base64.b64decode(b64))
        out[key] = str(p)
    return out


# --- app ------------------------------------------------------------------------------------
def build_app():
    with gr.Blocks(title="GEOMIND-R Virtual Lab — Notebook Mirror") as demo:
        gr.Markdown(
            "# GEOMIND-R Virtual Chemistry Lab\n"
            "A **glass box, not an oracle.** Every prediction shows its confidence flag, its "
            "reason, and its source. Trustworthy only for **metakaolin geopolymers / Sr** inside "
            "the trained [Al^IV] range (3.45–4.77 mmol g⁻¹); everything else is flagged. "
            "*Runs entirely inside this notebook — nothing leaves your session.*"
        )

        with gr.Tab("Sr K_D prediction"):
            with gr.Row():
                with gr.Column():
                    al_iv = gr.Slider(1.0, 10.0, value=4.0, step=0.05,
                                      label="Framework [Al^IV] (mmol g⁻¹)")
                    sclass = gr.Dropdown(_CLASSES, value=_CLASSES[0], label="Structural class")
                    ads = gr.Dropdown(_ADSORBATES, value="Sr", label="Adsorbate")
                    go = gr.Button("Predict K_D", variant="primary")
                with gr.Column():
                    out_label = gr.Label(label="Result")
                    out_detail = gr.Markdown()
            go.click(_predict_handler, [al_iv, sclass, ads], [out_label, out_detail])

        with gr.Tab("Saturation advisor (θ = 1 − R_L)"):
            gr.Markdown("Does a reported Langmuir fit actually reach the plateau? Enter its *b* "
                        "and the highest C₀ tested.")
            with gr.Row():
                b_in = gr.Number(value=0.05, label="Langmuir b (L mg⁻¹)")
                c0_in = gr.Number(value=1000.0, label="C₀ (mg L⁻¹)")
            screen_btn = gr.Button("Screen")
            screen_out = gr.Markdown()
            screen_btn.click(_screen_handler, [b_in, c0_in], screen_out)

        with gr.Tab("Teaching · Pooling fails (F36)"):
            gr.Markdown("Within one laboratory the descriptor predicts held-out samples. Pool "
                        "across laboratories and it falls apart. Pick sources and watch the "
                        "leave-one-out R² drop below zero.")
            pool_pick = gr.CheckboxGroup(E.pooling_sources(), value=E.pooling_sources(),
                                         label="Laboratories pooled (Cs Langmuir q_max)")
            pool_out = gr.Markdown()
            pool_pick.change(_pooling_handler, pool_pick, pool_out)

        with gr.Tab("Teaching · Structural precondition (F19)"):
            gr.Markdown("The Al-richness descriptor tracks uptake **within a structural class**. "
                        "Toggle in the real Ca-bearing gels and watch the correlation weaken.")
            ca_toggle = gr.Checkbox(value=False, label="Include the real Ca-bearing gels")
            struct_out = gr.Markdown()
            ca_toggle.change(_structural_handler, ca_toggle, struct_out)

        with gr.Tab("Teaching · Saturation reveal"):
            gr.Markdown("A Langmuir fit can report R² = 0.9999 and still be an artefact. Enter "
                        "its *b* and highest C₀ and reveal how little of the isotherm it saw.")
            with gr.Row():
                rb = gr.Number(value=7.94e-5, label="Langmuir b (L mg⁻¹)")
                rc0 = gr.Number(value=2658.0, label="C₀ (mg L⁻¹)")
            reveal_btn = gr.Button("Reveal θ")
            reveal_out = gr.Markdown()
            reveal_btn.click(_screen_handler, [rb, rc0], reveal_out)

        with gr.Tab("Teaching · Figures & concepts"):
            gr.Markdown("The paper's argument, rendered from the pipeline.")
            gr.Markdown(_concept_cards())
            paths = _figure_paths()
            for key, title in (("fig1", "Concept (Fig 1)"), ("fig2", "Three levels (Fig 2)"),
                               ("fig4", "Structural precondition (Fig 4)"),
                               ("fig6", "Pooling limit (Fig 6)")):
                if key in paths:
                    gr.Markdown(f"**{title}**")
                    gr.Image(paths[key], show_label=False)

        with gr.Tab("Console · Pool explorer"):
            gr.Markdown("The two audited pools, browsable. Pool A = adsorption (141 rows), "
                        "Pool B = immobilisation (54). They are never merged.")
            pool_pick2 = gr.Radio(["A", "B"], value="A", label="Pool")
            pool_df = gr.DataFrame(value=E.load_pool("A"), wrap=True)
            pool_pick2.change(_pool_handler, pool_pick2, pool_df)

        with gr.Tab("Console · Finding register"):
            gr.Markdown("37 findings, searchable. Each carries its evidence and the action taken.")
            find_q = gr.Textbox(label="Filter (id, word in title/evidence/action)", value="")
            find_df = gr.DataFrame(value=_findings_table(""), wrap=True)
            find_q.change(_findings_table, find_q, find_df)

        with gr.Tab("Console · Audit trail"):
            gr.Markdown("Every ingested table got an explicit verdict and a reason — the ~a-fifth "
                        "set aside is the point, not a footnote.")
            gr.Markdown(_audit_summary_md())
            gr.DataFrame(value=E.load_audit_summary(), wrap=True)

        with gr.Tab("Console · Re-run analyses"):
            gr.Markdown("Recompute the paper's headline numbers live from the bundle.")
            rerun_btn = gr.Button("Re-run", variant="primary")
            rerun_out = gr.Markdown()
            rerun_btn.click(_rerun_handler, None, rerun_out)

    return demo


def _concept_cards() -> str:
    return (
        "### Concept cards\n"
        "- **Framework Al^IV** — tetrahedral aluminium in the aluminosilicate network. Each "
        "Al^IV carries a negative charge balanced by an exchangeable cation — the actual uptake "
        "site. Not the same as surface area.\n"
        "- **ARI (Al-richness index)** — framework Al per Si from the Q⁴(mAl) NMR deconvolution; "
        "the composition-side proxy for exchange-site density.\n"
        "- **Qⁿ(mAl)** — ²⁹Si NMR speciation: a Si tetrahedron with *n* bridging oxygens, *m* of "
        "them to Al. The deconvolution that yields ARI.\n"
        "- **θ = 1 − R_L** — fraction of Langmuir saturation reached at the highest C₀ tested. "
        "θ ≥ 0.8 sound; θ < 0.5 the fitted capacity is an extrapolation artefact.\n"
        "- **Two pools** — Pool A (adsorption K_D / q_max) and Pool B (immobilisation / "
        "leachability) are audited separately and never merged.\n"
    )


def main():  # pragma: no cover — Colab entry point
    build_app().launch()   # Colab-internal; no public tunnel


if __name__ == "__main__":  # pragma: no cover
    main()
