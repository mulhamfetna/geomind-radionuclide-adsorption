"""Export the compiled data the notebook mirror needs into lab_bundle.json.

Runs against the LIVE pipeline via app.engine so the bundle is always consistent with the
desktop app at export time. Only project-owned compiled data is written — no raw third-party
files, no warehouse DB.
"""
from __future__ import annotations

import base64
import io
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT))

import matplotlib  # noqa: E402
matplotlib.use("Agg")

from app import engine as E  # noqa: E402


def _records(df):
    """DataFrame -> JSON-safe list of dicts (NaN -> null, numpy -> native)."""
    return json.loads(df.to_json(orient="records"))


def _figures() -> dict:
    sys.path.insert(0, str(_ROOT / "manuscript"))
    import figures as F
    out = {}
    for key, fn in (("fig1", "fig1_concept"), ("fig2", "fig2_correlation_and_causal"),
                    ("fig4", "fig4_structural_precondition"), ("fig6", "fig6_pooling_limit")):
        fig = getattr(F, fn)()
        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
        out[key] = base64.b64encode(buf.getvalue()).decode("ascii")
    return out


def build_bundle() -> dict:
    m = E._model()
    from geomind.model import forward as FW
    from geomind.data.merge_adsorption import build as build_A
    tdf = FW.training_data(build_A())
    training = [{"al_iv": float(r[FW.DESCRIPTOR]), "kd": float(r[FW.TARGET])}
                for _, r in tdf.iterrows()]

    cs = E._cs_langmuir_pool()[["source_label", "si_al", "capacity_mg_g"]]

    # structural-precondition points (same query as app.engine.structural_precondition)
    from geomind.data import nmr_ari as N
    A = N.attach(build_A())
    o = A[(A["source_label"] == "oulu2026") & (A["adsorbate"] == "NH4+")].copy()
    o["ca_free"] = o["ca_al"].fillna(0) == 0
    cf = o[o["ca_free"]].dropna(subset=["ari", "capacity_mg_g"])
    cb = o[~o["ca_free"]].dropna(subset=["ari", "capacity_mg_g"])
    struct = {
        "framework": [{"ari": float(a), "cap": float(c)} for a, c in
                      zip(cf["ari"], cf["capacity_mg_g"])],
        "ca": [{"ari": float(a), "cap": float(c)} for a, c in
               zip(cb["ari"], cb["capacity_mg_g"])],
    }

    return {
        "forward": {"slope": float(m.slope), "intercept": float(m.intercept),
                    "x_min": float(m.x_min), "x_max": float(m.x_max),
                    "r2_loo": float(m.r2_loo), "rmse_loo": float(m.rmse_loo),
                    "training": training},
        "cs_pool": _records(cs),
        "struct": struct,
        "pool_a": _records(E.load_pool("A")),
        "pool_b": _records(E.load_pool("B")),
        "audit": _records(E.load_audit_summary()),
        "findings": E.load_findings(),
        "decisions": E.load_decisions(),
        "figures": _figures(),
    }


def write_bundle(path=None) -> str:
    path = Path(path) if path else _ROOT / "notebook_lab" / "lab_bundle.json"
    path.write_text(json.dumps(build_bundle()))
    return str(path)


if __name__ == "__main__":
    print("wrote", write_bundle())
