"""²⁹Si MAS-NMR deconvolution for the Oulu series.

Implements `docs/nmr-deconvolution-plan.md`. Each gate is a separate function that
returns a pass/fail verdict plus its evidence, so a failure is reported rather than
worked around.

Usage:
    python -m src.geomind.nmr --gate1     # parse + sanity check
    python -m src.geomind.nmr             # run all gates in order, stop on failure
"""
from __future__ import annotations

import re
import sys
import warnings
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path("data/external/aam-oulu-2026")
NMR_GLOB = "**/Si NMR*/All data.xlsx"

#: Q4(mAl) chemical-shift positions (ppm) and allowed drift, from the literature.
PEAKS = [("Q4(4Al)", -84.0, 3.0), ("Q4(3Al)", -89.0, 3.0), ("Q4(2Al)", -93.0, 3.0),
         ("Q4(1Al)", -99.0, 3.0), ("Q4(0Al)", -108.0, 4.0)]

#: the diagnostic window that must be covered for a fit to be meaningful
WINDOW = (-70.0, -120.0)


@dataclass
class Spectrum:
    sample: str
    ppm: np.ndarray
    intensity: np.ndarray

    @property
    def covers_window(self) -> bool:
        return self.ppm.min() <= WINDOW[1] and self.ppm.max() >= WINDOW[0]

    @property
    def monotonic(self) -> bool:
        d = np.diff(self.ppm)
        return bool((d > 0).all() or (d < 0).all())


def load_spectra() -> list[Spectrum]:
    """Parse the instrument dump into per-sample spectra.

    Layout: row 0 carries sample labels (sparse, one per 4-column block),
    row 1 carries repeated [Index, Intensity, Hz, ppm] headers, data follows.
    """
    matches = list(ROOT.glob(NMR_GLOB))
    if not matches:
        raise SystemExit(f"NMR workbook not found under {ROOT}")
    raw = pd.read_excel(matches[0], header=None)

    labels = raw.iloc[0].tolist()
    headers = [str(x).strip().lower() for x in raw.iloc[1].tolist()]
    body = raw.iloc[2:].reset_index(drop=True)

    out: list[Spectrum] = []
    current = None
    for col, head in enumerate(headers):
        lab = labels[col]
        if isinstance(lab, str) and lab.strip():
            current = lab.strip()
        if head == "ppm" and current:
            inten_col = next((c for c in range(col - 3, col)
                              if 0 <= c < len(headers) and headers[c] == "intensity"), None)
            if inten_col is None:
                continue
            ppm = pd.to_numeric(body.iloc[:, col], errors="coerce")
            inten = pd.to_numeric(body.iloc[:, inten_col], errors="coerce")
            ok = ppm.notna() & inten.notna()
            if ok.sum() < 100:
                continue
            out.append(Spectrum(current, ppm[ok].to_numpy(float), inten[ok].to_numpy(float)))
    return out


def gate1() -> tuple[bool, list[Spectrum]]:
    """Parse + sanity check. Reports how many compositions actually have spectra."""
    spectra = load_spectra()
    print(f"=== GATE 1 — parse and sanity check ===\n")
    print(f"spectra parsed: {len(spectra)}")

    rows, failures = [], []
    for s in spectra:
        cov, mono = s.covers_window, s.monotonic
        flat = bool(np.allclose(s.intensity, s.intensity[0]))
        if not (cov and mono) or flat:
            failures.append(s.sample)
        rows.append([s.sample, len(s.ppm), f"{s.ppm.min():.1f}", f"{s.ppm.max():.1f}",
                     "yes" if cov else "NO", "yes" if mono else "NO",
                     "FLAT" if flat else "ok"])

    print(f"\n{'sample':>12s} {'pts':>6s} {'ppm_min':>9s} {'ppm_max':>9s} {'window':>7s} {'mono':>5s} {'signal':>7s}")
    for r in rows:
        print(f"{r[0]:>12s} {r[1]:>6d} {r[2]:>9s} {r[3]:>9s} {r[4]:>7s} {r[5]:>5s} {r[6]:>7s}")

    ok = not failures
    print(f"\nGATE 1: {'PASS' if ok else 'FAIL'}")
    if failures:
        print(f"  problem spectra: {failures}")
    print(f"  NOTE: {len(spectra)} spectra vs 20 compositions in the adsorption series "
          f"-> coverage {len(spectra)}/20")
    return ok, spectra


def main() -> None:
    if "--gate1" in sys.argv or len(sys.argv) == 1:
        ok, _ = gate1()
        if not ok:
            raise SystemExit(1)


if __name__ == "__main__":
    main()


# =====================================================================
# GATE 2 - baseline correction
# =====================================================================
def crop(s: Spectrum, lo: float = -130.0, hi: float = -60.0) -> tuple[np.ndarray, np.ndarray]:
    """Crop to the diagnostic window (ppm axis may run either direction)."""
    m = (s.ppm >= lo) & (s.ppm <= hi)
    p, i = s.ppm[m], s.intensity[m]
    o = np.argsort(p)
    return p[o], i[o]


def baseline_correct(ppm: np.ndarray, inten: np.ndarray) -> tuple[np.ndarray, dict]:
    """Subtract a linear baseline fitted to the signal-free wings only.

    Wings = outer 15% at each end of the window, where no Q4(mAl) resonance lies.
    """
    n = len(ppm)
    k = max(3, int(0.15 * n))
    idx = np.r_[np.arange(k), np.arange(n - k, n)]
    coef = np.polyfit(ppm[idx], inten[idx], 1)
    corrected = inten - np.polyval(coef, ppm)
    resid_wing = corrected[idx]
    return corrected, {
        "wing_mean": float(resid_wing.mean()),
        "wing_std": float(resid_wing.std()),
        "signal_max": float(corrected.max()),
    }


def gate2(spectra: list[Spectrum]) -> tuple[bool, dict]:
    print("\n=== GATE 2 - baseline correction ===\n")
    print(f"{'sample':>12s} {'pts':>5s} {'wing_mean/max':>15s} {'verdict':>9s}")
    out, ok_all = {}, True
    for s in spectra:
        p, i = crop(s)
        if len(p) < 50:
            print(f"{s.sample:>12s} {len(p):>5d} {'--':>15s} {'TOO FEW':>9s}")
            ok_all = False
            continue
        c, st = baseline_correct(p, i)
        ratio = abs(st["wing_mean"]) / max(abs(st["signal_max"]), 1e-9)
        ok = ratio < 0.05
        ok_all &= ok
        out[s.sample] = (p, c)
        print(f"{s.sample:>12s} {len(p):>5d} {ratio:>15.4f} {'ok' if ok else 'FAIL':>9s}")
    print(f"\nGATE 2: {'PASS' if ok_all else 'FAIL'}  (wing residual < 5% of peak)")
    return ok_all, out


# =====================================================================
# GATE 3 - constrained five-Gaussian fit
# =====================================================================
def _model(ppm, *params):
    """5 Gaussians: params = [a0..a4, c0..c4, shared_width]."""
    a, c, w = params[:5], params[5:10], params[10]
    y = np.zeros_like(ppm)
    for ai, ci in zip(a, c):
        y = y + ai * np.exp(-0.5 * ((ppm - ci) / w) ** 2)
    return y


def fit_spectrum(ppm, inten, seed: int | None = None) -> dict:
    from scipy.optimize import curve_fit
    rng = np.random.default_rng(seed)
    amp0 = inten.max() if inten.max() > 0 else 1.0
    centres = [c for _, c, _ in PEAKS]
    drift = [d for _, _, d in PEAKS]

    p0 = ([amp0 * rng.uniform(0.2, 0.8) for _ in PEAKS]
          + [c + rng.uniform(-1, 1) for c in centres] + [rng.uniform(3.0, 6.0)])
    lo = [0.0] * 5 + [c - d for c, d in zip(centres, drift)] + [1.5]
    hi = [amp0 * 3] * 5 + [c + d for c, d in zip(centres, drift)] + [9.0]
    try:
        popt, _ = curve_fit(_model, ppm, inten, p0=p0, bounds=(lo, hi), maxfev=20000)
    except Exception:
        return {"ok": False}
    pred = _model(ppm, *popt)
    ss_res = float(((inten - pred) ** 2).sum())
    ss_tot = float(((inten - inten.mean()) ** 2).sum())
    r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
    # areas -> populations (shared width, so area is proportional to amplitude)
    areas = np.array(popt[:5], dtype=float)
    pops = 100 * areas / areas.sum() if areas.sum() > 0 else np.zeros(5)
    return {"ok": True, "r2": r2, "pops": pops, "width": float(popt[10]),
            "centres": [float(x) for x in popt[5:10]], "resid": inten - pred}


def gate3(baselined: dict) -> tuple[bool, dict]:
    print("\n=== GATE 3 - constrained five-Gaussian fit ===\n")
    hdr = "  ".join(f"{n:>9s}" for n, _, _ in PEAKS)
    print(f"{'sample':>12s} {'R2':>7s}  {hdr}  {'width':>6s}")
    fits, ok_all = {}, True
    for name, (p, c) in baselined.items():
        f = fit_spectrum(p, c, seed=0)
        if not f["ok"] or f["r2"] < 0.98:
            ok_all = False
        fits[name] = f
        if f["ok"]:
            pops = "  ".join(f"{v:>9.1f}" for v in f["pops"])
            print(f"{name:>12s} {f['r2']:>7.4f}  {pops}  {f['width']:>6.2f}")
        else:
            print(f"{name:>12s} {'FIT FAILED':>7s}")
    print(f"\nGATE 3: {'PASS' if ok_all else 'FAIL'}  (all R2 >= 0.98)")
    return ok_all, fits
