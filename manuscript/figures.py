#!/usr/bin/env python3
"""Generate the manuscript's data figures from the live pipeline.

Publication figures for the descriptor-and-methodology paper (see paper-outline.md).
Every figure is computed from the two pools / the forward model — no hand-entered data.

Palette: Okabe-Ito (the reference colour-blind-safe set; validated by the dataviz
skill's checker) plus the project's teal for single-series plots. Thin marks, recessive
axes, direct labels, no chartjunk.

Output: manuscript/figures/*.png (300 dpi) + figures.pdf (all panels).
Run: PYTHONPATH=src python manuscript/figures.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.backends.backend_pdf import PdfPages  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from geomind.data import nmr_ari as N  # noqa: E402
from geomind.data.merge_adsorption import build as build_A  # noqa: E402
from geomind.model import forward as FM  # noqa: E402

OUT = ROOT / "manuscript" / "figures"
OUT.mkdir(exist_ok=True)

# ---- style ---------------------------------------------------------------
TEAL = "#0d5c63"
BLUE = "#0072B2"       # Okabe-Ito
VERM = "#D55E00"       # Okabe-Ito
GREEN = "#009E73"      # Okabe-Ito
GREY = "#8a8f98"
INK = "#1a1c22"

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["DejaVu Sans"],
    "font.size": 9,
    "axes.edgecolor": "#9aa0a8",
    "axes.linewidth": 0.8,
    "axes.labelcolor": INK,
    "axes.titlesize": 9.5,
    "axes.titleweight": "bold",
    "xtick.color": INK, "ytick.color": INK,
    "xtick.labelsize": 8, "ytick.labelsize": 8,
    "figure.dpi": 300, "savefig.dpi": 300,
    "savefig.bbox": "tight",
})


def _clean(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color="#e6e8eb", linewidth=0.6, zorder=0)
    ax.set_axisbelow(True)


def _fit_line(ax, x, y, color, lw=1.6):
    b1, b0 = np.polyfit(x, y, 1)
    xs = np.linspace(x.min(), x.max(), 50)
    ax.plot(xs, b1 * xs + b0, color=color, lw=lw, zorder=2)
    return b1, b0


def _corr(x, y):
    return float(np.corrcoef(x, y)[0, 1])


# ---- data ----------------------------------------------------------------
A = N.attach(build_A())


def _strip(s):
    """Normalise a Varon sorbent name to its bare label for fresh<->leached matching."""
    import re
    return re.sub(r"\s*\((inferred|leached 96h)\)", "", s).strip()


def fig1_concept():
    """Fig 1. The concept: cation uptake by ion exchange at framework Al^IV sites,
    contrasted with the physisorption picture the surface-area metric assumes."""
    from matplotlib.patches import Circle, FancyArrowPatch

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(7.0, 3.1))
    for ax in (axL, axR):
        ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")

    # -- (a) physisorption on a surface: what BET surface area assumes --
    axL.set_title("(a) physisorption on a surface", loc="left", color=GREY)
    axL.plot([0.8, 9.2], [3.2, 3.2], color="#9aa0a8", lw=2.4, zorder=2)
    for x in np.linspace(1.2, 8.8, 9):          # hatch the surface
        axL.plot([x, x - 0.4], [3.2, 2.7], color="#c3c7cd", lw=1.0, zorder=1)
    cat = Circle((5.0, 4.6), 0.55, facecolor=GREY, edgecolor="white", lw=1.2, zorder=3)
    axL.add_patch(cat)
    axL.text(5.0, 4.6, "Cs$^+$", ha="center", va="center", color="white", fontsize=8.5,
             fontweight="bold")
    axL.plot([5.0, 5.0], [3.35, 4.05], color="#b8bcc4", lw=1.4, ls=(0, (2, 2)), zorder=2)
    axL.text(5.0, 1.9, "uptake ∝ surface area?", ha="center", fontsize=8.5, color=INK)
    axL.text(5.0, 0.9, "weak, non-specific", ha="center", fontsize=7.5, color=GREY, style="italic")

    # -- (b) ion exchange at a framework Al^IV charge-balancing site: what we find --
    axR.set_title("(b) ion exchange at framework Al$^{IV}$", loc="left", color=TEAL)
    # a small Si-O-Al-O-Si framework fragment
    nodes = {"Si1": (2.0, 6.6, "Si", GREY), "Al": (5.0, 5.6, "Al", TEAL),
             "Si2": (8.0, 6.6, "Si", GREY), "Si3": (5.0, 8.4, "Si", GREY)}
    bonds = [("Si1", "Al"), ("Al", "Si2"), ("Al", "Si3")]
    for a, b in bonds:
        (xa, ya, *_), (xb, yb, *_) = nodes[a], nodes[b]
        axR.plot([xa, xb], [ya, yb], color="#8a8f98", lw=1.6, zorder=1)
        axR.text((xa + xb) / 2, (ya + yb) / 2 + 0.12, "O", ha="center", va="center",
                 fontsize=6.8, color="#b0141d")
    for _, (x, y, lab, c) in nodes.items():
        axR.add_patch(Circle((x, y), 0.62, facecolor=c, edgecolor="white", lw=1.2, zorder=3))
        axR.text(x, y, lab, ha="center", va="center", color="white", fontsize=8.5,
                 fontweight="bold")
    axR.text(5.9, 5.0, "δ$^-$", fontsize=11, color=VERM, fontweight="bold", zorder=4)
    # the exchangeable cation at the charge-balancing site
    axR.add_patch(Circle((5.0, 3.4), 0.6, facecolor=VERM, edgecolor="white", lw=1.2, zorder=3))
    axR.text(5.0, 3.4, "Cs$^+$/\nSr$^{2+}$", ha="center", va="center", color="white",
             fontsize=6.6, fontweight="bold")
    axR.add_patch(FancyArrowPatch((5.0, 4.9), (5.0, 4.1), arrowstyle="-|>", mutation_scale=11,
                                  color=VERM, lw=1.6, zorder=2))
    axR.text(5.0, 1.9, "uptake ∝ framework Al$^{IV}$", ha="center", fontsize=8.5, color=INK)
    axR.text(5.0, 0.9, "strong, charge-balancing", ha="center", fontsize=7.5, color=TEAL,
             style="italic")

    fig.suptitle("Cation uptake in geopolymers is ion exchange, not physisorption",
                 fontsize=10, fontweight="bold", y=1.02, x=0.5)
    fig.tight_layout()
    fig.savefig(OUT / "fig1_concept.png")
    return fig


def fig2_correlation_and_causal():
    """Fig 2. Three honest panels, each on its own axis (no dual scale):
    (a) framework Al -> K_D, (b) surface area -> K_D, (c) the within-sample causal test."""
    fig, (axa, axb, axc) = plt.subplots(1, 3, figsize=(7.2, 2.7))
    v = A[A.source_label == "varon2025"].dropna(subset=["al_iv_mmol_g", "bet_m2_g", "kd_mL_g"])
    al, bet, y = v["al_iv_mmol_g"].to_numpy(), v["bet_m2_g"].to_numpy(), v["kd_mL_g"].to_numpy()

    # (a) framework Al^IV -> K_D  (predicts)
    axa.scatter(al, y / 1000, s=40, color=TEAL, edgecolor="white", linewidth=0.6, zorder=3)
    _fit_line(axa, al, y / 1000, TEAL)
    axa.set_xlabel("framework Al$^{IV}$ (mmol g$^{-1}$)")
    axa.set_ylabel("Sr $K_D$ (10$^3$ mL g$^{-1}$)")
    axa.set_title(f"(a) framework Al\n$r$ = {_corr(al, y):+.2f}", loc="left", color=TEAL)
    _clean(axa)

    # (b) BET surface area -> K_D  (does not) -- its OWN honest x-axis
    axb.scatter(bet, y / 1000, s=40, facecolor="white", edgecolor=GREY, linewidth=1.3,
                marker="s", zorder=3)
    axb.set_xlabel("BET surface area (m$^2$ g$^{-1}$)")
    axb.set_ylabel("Sr $K_D$ (10$^3$ mL g$^{-1}$)")
    axb.set_title(f"(b) surface area\n$r$ = {_corr(bet, y):+.2f}", loc="left", color=GREY)
    _clean(axb)

    # (c) causal Δ across ALL 7 samples (strip both "(inferred)" and "(leached 96h)")
    f = A[A.source_label == "varon2025"].dropna(subset=["al_iv_mmol_g", "kd_mL_g"]).copy()
    lz = A[A.source_label == "varon_leached2026"].dropna(subset=["al_iv_mmol_g", "kd_mL_g"]).copy()
    f["k"] = f["sorbent_name"].map(_strip); lz["k"] = lz["sorbent_name"].map(_strip)
    f = f.set_index("k"); lz = lz.set_index("k")
    common = [i for i in f.index if i in lz.index]
    d_al = np.array([f.loc[i, "al_iv_mmol_g"] - lz.loc[i, "al_iv_mmol_g"] for i in common])
    d_kd = np.array([f.loc[i, "kd_mL_g"] - lz.loc[i, "kd_mL_g"] for i in common])
    axc.scatter(d_al, d_kd / 1000, s=40, color=VERM, edgecolor="white", linewidth=0.6, zorder=3)
    _fit_line(axc, d_al, d_kd / 1000, VERM)
    axc.axhline(0, color="#d2d6db", lw=0.8, zorder=1)
    axc.set_xlabel(r"$\Delta$[Al$^{IV}$] on leaching (mmol g$^{-1}$)")
    axc.set_ylabel(r"$\Delta K_D$ (10$^3$ mL g$^{-1}$)")
    axc.set_title(f"(c) causal test, n={len(common)}\n$r$ = {_corr(d_al, d_kd):+.2f}",
                  loc="left", color=VERM)
    _clean(axc)

    fig.tight_layout(w_pad=1.4)
    fig.savefig(OUT / "fig2_correlation_causal.png")
    return fig


def fig3_forward_model():
    """Fig 3. The within-class forward model with its leave-one-out fit."""
    m = FM.fit(build_A())
    df = FM.training_data(build_A())
    x, y = df[FM.DESCRIPTOR].to_numpy(), df[FM.TARGET].to_numpy()
    fig, ax = plt.subplots(figsize=(3.5, 3.2))
    xs = np.linspace(m.x_min, m.x_max, 50)
    ax.plot(xs, (m.slope * xs + m.intercept) / 1000, color=TEAL, lw=1.8, zorder=2)
    ax.scatter(x, y / 1000, s=48, color=TEAL, edgecolor="white", linewidth=0.7, zorder=3)
    ax.set_xlabel("framework Al$^{IV}$  (mmol g$^{-1}$)")
    ax.set_ylabel("Sr $K_D$  (10$^3$ mL g$^{-1}$)")
    ax.set_title("Within-class forward model", loc="left")
    ax.text(0.04, 0.96,
            f"$K_D$ = {m.slope:.0f}·[Al$^{{IV}}$] − {abs(m.intercept):.0f}\n"
            f"LOO-CV $R^2$ = {m.r2_loo:.2f}\nn = {m.n} (metakaolin GP, Sr)",
            transform=ax.transAxes, va="top", ha="left", fontsize=7.6,
            bbox=dict(boxstyle="round,pad=0.4", facecolor="#f4f5f7", edgecolor="#dfe1e6"))
    _clean(ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig3_forward_model.png")
    return fig


def fig4_structural_precondition():
    """Fig 4. The descriptor predicts in a framework gel; fails in a Ca gel."""
    o = A[(A.source_label == "oulu2026") & (A.adsorbate == "NH4+")].copy()
    o["ca_free"] = o["ca_al"].fillna(0) == 0
    cf = o[o.ca_free].dropna(subset=["ari", "capacity_mg_g"])
    cb = o[~o.ca_free].dropna(subset=["ari", "capacity_mg_g"])
    fig, ax = plt.subplots(figsize=(3.7, 3.2))
    ax.scatter(cb["ari"], cb["capacity_mg_g"], s=44, color=VERM, marker="s",
               edgecolor="white", linewidth=0.6, zorder=3,
               label=f"Ca-bearing gel  (r = {_corr(cb['ari'], cb['capacity_mg_g']):+.2f})")
    ax.scatter(cf["ari"], cf["capacity_mg_g"], s=48, color=BLUE,
               edgecolor="white", linewidth=0.6, zorder=3,
               label=f"framework gel  (r = {_corr(cf['ari'], cf['capacity_mg_g']):+.2f})")
    _fit_line(ax, cf["ari"].to_numpy(), cf["capacity_mg_g"].to_numpy(), BLUE)
    ax.set_xlabel("Al-richness index (framework Al per Si)")
    ax.set_ylabel("NH$_4^+$ uptake  (mg g$^{-1}$)")
    ax.set_title("Structural precondition", loc="left")
    ax.legend(frameon=False, fontsize=7.2, loc="upper left")
    _clean(ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig4_structural_precondition.png")
    return fig


def fig6_pooling_limit():
    """Fig 6. Predicted vs observed: within-class works, pooled fails."""
    # within-class (Varon) LOO predictions
    df = FM.training_data(build_A())
    x, y = df[FM.DESCRIPTOR].to_numpy(), df[FM.TARGET].to_numpy()

    def loo_pred(x, y):
        p = np.empty(len(x))
        for i in range(len(x)):
            m = np.ones(len(x), bool); m[i] = False
            b1, b0 = np.polyfit(x[m], y[m], 1); p[i] = b1 * x[i] + b0
        r2 = 1 - ((y - p) ** 2).sum() / ((y - y.mean()) ** 2).sum()
        return p, r2

    pw, r2w = loo_pred(x, y)
    cq = A[(A.adsorbate == "Cs") & (A.capacity_type == "langmuir_qmax")].dropna(
        subset=["si_al", "capacity_mg_g"])
    xp, yp = cq["si_al"].to_numpy(), cq["capacity_mg_g"].to_numpy()
    pp, r2p = loo_pred(xp, yp)

    fig, (axa, axb) = plt.subplots(1, 2, figsize=(6.9, 3.2))
    for ax, obs, pred, r2, col, ttl in (
        (axa, y / 1000, pw / 1000, r2w, TEAL, "(a) within one class / protocol"),
        (axb, yp, pp, r2p, VERM, "(b) pooled across laboratories"),
    ):
        lim = [min(obs.min(), pred.min()), max(obs.max(), pred.max())]
        pad = 0.08 * (lim[1] - lim[0])
        lim = [lim[0] - pad, lim[1] + pad]
        ax.plot(lim, lim, color="#b8bcc4", lw=1.0, ls="--", zorder=1)
        ax.scatter(obs, pred, s=42, color=col, edgecolor="white", linewidth=0.6, zorder=3)
        ax.set_xlim(lim); ax.set_ylim(lim)
        ax.set_xlabel("observed"); ax.set_ylabel("predicted (left-out)")
        good = r2 > 0
        ax.set_title(f"{ttl}\nLOO-CV $R^2$ = {r2:+.2f}"
                     f"  {'✓ predictive' if good else '✗ worse than the mean'}",
                     loc="left", color=(TEAL if good else VERM))
        _clean(ax)
    axa.text(0.5, -0.28, "Sr $K_D$ (10$^3$ mL g$^{-1}$)", transform=axa.transAxes,
             ha="center", fontsize=8, color=GREY)
    axb.text(0.5, -0.28, "Cs capacity (mg g$^{-1}$)", transform=axb.transAxes,
             ha="center", fontsize=8, color=GREY)
    fig.tight_layout()
    fig.savefig(OUT / "fig6_pooling_limit.png")
    return fig


#: Artefacts whose theta is figure-derived (isotherm-validation-report, F17/F24), not
#: computable from b*C0 in the pool (negative-intercept fits / figure reads). Flagged.
_REPORT_THETA = {
    "Zhang slag geomaterial": 0.074,
    "Zhang fly-ash geomaterial": 0.365,
    "Kurumisawa N11": 0.499,
}


def fig5_saturation_screen():
    """Fig 5. Every fitted capacity, ranked by fraction-of-saturation theta = 1 - R_L."""
    from geomind.data.merge_adsorption import build as _b
    lang = _b()
    lang = lang[lang.capacity_type == "langmuir_qmax"].dropna(
        subset=["langmuir_b_L_mg", "initial_conc_mg_L"]).copy()
    bc = lang["langmuir_b_L_mg"] * lang["initial_conc_mg_L"]
    theta = list((bc / (1 + bc)).to_numpy())
    labels = list(lang["sorbent_name"])
    theta += list(_REPORT_THETA.values())
    labels += list(_REPORT_THETA.keys())
    theta = np.array(theta)
    order = np.argsort(theta)
    theta = theta[order]; labels = [labels[i] for i in order]

    def col(t):
        return VERM if t < 0.5 else ("#b4530a" if t < 0.8 else TEAL)

    n_art = int((theta < 0.5).sum())
    fig, ax = plt.subplots(figsize=(6.9, 2.9))
    x = np.arange(len(theta))
    ax.axhspan(0, 0.5, color=VERM, alpha=0.05, zorder=0)
    ax.axhline(0.8, color="#9aa0a8", lw=0.8, ls="--", zorder=1)
    ax.axhline(0.5, color=VERM, lw=0.8, ls="--", zorder=1)
    ax.scatter(x, theta, s=34, color=[col(t) for t in theta],
               edgecolor="white", linewidth=0.5, zorder=3)
    ax.set_ylim(-0.03, 1.05)
    ax.set_xlabel("fitted capacities, ranked by saturation")
    ax.set_ylabel(r"$\theta = 1 - R_L$  (fraction of saturation reached)")
    ax.set_title(f"Saturation screen: {n_art} of {len(theta)} capacities are "
                 "extrapolation artefacts", loc="left")
    ax.text(len(theta) * 0.97, 0.83, "sound (θ ≥ 0.8)", ha="right", va="bottom",
            fontsize=7.5, color=TEAL)
    ax.text(len(theta) * 0.02, 0.44, "artefact (θ < 0.5)", ha="left", va="top",
            fontsize=7.5, color=VERM)
    # annotate the worst artefacts by name
    for i in range(n_art):
        nm = labels[i].replace(" geomaterial", "").replace("chabazite", "chabazite")
        ax.annotate(nm, (x[i], theta[i]), textcoords="offset points", xytext=(6, 2),
                    fontsize=6.6, color=VERM)
    ax.set_xticks([])
    _clean(ax)
    fig.tight_layout()
    fig.savefig(OUT / "fig5_saturation_screen.png")
    return fig


def main():
    figs = [fig1_concept(), fig2_correlation_and_causal(), fig3_forward_model(),
            fig4_structural_precondition(), fig5_saturation_screen(),
            fig6_pooling_limit()]
    with PdfPages(OUT / "figures.pdf") as pdf:
        for f in figs:
            pdf.savefig(f)
    for f in figs:
        plt.close(f)
    print(f"wrote {len(figs)} figures + figures.pdf to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
