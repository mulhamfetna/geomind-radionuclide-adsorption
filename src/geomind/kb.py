"""Knowledge-base engine: validate the registry and generate the reports.

`knowledge_base/registry.yaml` is the single source of truth. This module
(a) VALIDATES it — catching drift, unknown statuses and dangling references —
and (b) RENDERS the human-readable docs, so documentation can never silently
disagree with the registry.

Usage:
    python -m src.geomind.kb            # validate + regenerate docs
    python -m src.geomind.kb --check    # validate only (CI / pre-commit)

Design intent: every mistake in this project so far came from *implicit*
knowledge — which sheet had been checked, which rows were verified, what must
not be pooled. This makes that state explicit and machine-checkable.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

REGISTRY = Path("knowledge_base/registry.yaml")
OUT_DIR = Path("docs/knowledge-base")

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
STATUS_EMOJI = {
    "verified": "✅", "partial": "🟡", "suspect": "⚠️", "rejected": "❌",
    "duplicate": "♻️", "unmined": "⬜", "derived": "🔧", "external": "📦",
}


# ---------------------------------------------------------------- load
def load() -> dict:
    if not REGISTRY.exists():
        raise SystemExit(f"registry not found: {REGISTRY}")
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))


# ------------------------------------------------------------ validate
def validate(kb: dict) -> list[str]:
    """Return a list of problems. Empty list means the registry is coherent."""
    errs: list[str] = []
    vocab = set(kb.get("status_vocab", {}))
    finding_ids = {f["id"] for f in kb.get("findings", [])}
    question_ids = {q["id"] for q in kb.get("open_questions", [])}
    asset_ids = {a["id"] for a in kb.get("assets", [])}

    seen: set[str] = set()
    for a in kb.get("assets", []):
        aid = a.get("id", "<missing id>")
        if aid in seen:
            errs.append(f"asset {aid}: duplicate id")
        seen.add(aid)

        if a.get("status") not in vocab:
            errs.append(f"asset {aid}: status {a.get('status')!r} not in status_vocab")
        for field in ("path", "description", "usage"):
            if not a.get(field):
                errs.append(f"asset {aid}: missing required field {field!r}")
        for fid in a.get("related_findings", []) or []:
            if fid not in finding_ids:
                errs.append(f"asset {aid}: references unknown finding {fid}")
        q = a.get("open_question")
        if q and q not in question_ids:
            errs.append(f"asset {aid}: references unknown question {q}")

    for f in kb.get("findings", []):
        if f.get("severity") not in SEVERITY_ORDER:
            errs.append(f"finding {f.get('id')}: bad severity {f.get('severity')!r}")
        if not f.get("action"):
            errs.append(f"finding {f.get('id')}: no action recorded")

    for q in kb.get("open_questions", []):
        for b in q.get("blocks", []) or []:
            # blockers may be asset ids or milestone labels (M1..M6)
            if b not in asset_ids and not b.startswith("M"):
                errs.append(f"question {q['id']}: blocks unknown target {b!r}")

    return errs


# -------------------------------------------------------------- render
def _table(rows: list[list[str]], header: list[str]) -> str:
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join("---" for _ in header) + "|"]
    out += ["| " + " | ".join(r) + " |" for r in rows]
    return "\n".join(out)


def render_index(kb: dict) -> str:
    m = kb["meta"]
    assets, findings = kb["assets"], kb["findings"]
    by_status: dict[str, int] = {}
    for a in assets:
        by_status[a["status"]] = by_status.get(a["status"], 0) + 1
    open_f = [f for f in findings if f.get("status") not in ("resolved",)]

    return f"""# GEOMIND-R — Knowledge Base

> **Generated from `knowledge_base/registry.yaml` — do not edit these files by hand.**
> Regenerate with `python -m src.geomind.kb`.

**Updated:** {m['updated']} · **Pool:** {m['pool_rows']} rows / {m['pool_sources']} sources

## Contents
| Document | Purpose |
|---|---|
| [Data registry](01-data-registry.md) | Every data asset, its status and its usage constraints |
| [Sources](02-sources.md) | Every paper, with extraction status and row contribution |
| [Findings](03-findings.md) | Every finding, its evidence and what was done about it |
| [Decisions](04-decisions.md) | Standing decisions and the reason for each |
| [Open questions](05-open-questions.md) | What is unresolved and what it blocks |

## At a glance
- **Assets registered:** {len(assets)} — {', '.join(f'{STATUS_EMOJI.get(k,"")} {k} {v}' for k, v in sorted(by_status.items()))}
- **Findings:** {len(findings)} ({len([f for f in findings if f['severity']=='critical'])} critical)
- **Still open:** {len(open_f)} finding(s), {len(kb['open_questions'])} question(s)

## The rule this exists to enforce

> **No data enters an analysis unless it is registered here with an explicit
> `status` and `usage`.** Statuses are a closed vocabulary; the generator rejects
> anything else. Every error in this project so far came from implicit knowledge —
> which sheet had been checked, which rows were verified, what must not be pooled.
"""


def render_assets(kb: dict) -> str:
    parts = ["# Data registry", "",
             "Every data asset. **`usage` is binding** — widening it requires a recorded decision.",
             ""]
    for origin, label in [("provided", "Originally provided"),
                          ("provided_later", "Provided later"),
                          ("derived", "Derived by our code")]:
        group = [a for a in kb["assets"] if a.get("origin") == origin]
        if not group:
            continue
        parts += [f"## {label}", ""]
        for a in group:
            sh = a.get("shape") or [None, None]
            shape = f"{sh[0]} × {sh[1]}" if sh[0] and sh[1] else (str(sh[0]) if sh[0] else "—")
            parts += [
                f"### {STATUS_EMOJI.get(a['status'],'')} `{a['id']}` — {a['status']}",
                "",
                f"- **Path:** `{a['path']}`",
                f"- **Shape:** {shape}",
                f"- **Description:** {' '.join(a['description'].split())}",
                f"- **Usage:** {' '.join(a['usage'].split())}",
            ]
            if a.get("related_findings"):
                parts.append(f"- **Findings:** {', '.join(a['related_findings'])}")
            if a.get("open_question"):
                parts.append(f"- **Blocked by:** {a['open_question']}")
            parts.append("")
    return "\n".join(parts)


def render_sources(kb: dict) -> str:
    rows = []
    for s in sorted(kb["sources"], key=lambda x: -(x.get("rows") or 0)):
        rows.append([
            f"`{s['id']}`",
            f"`{s['doi']}`" if s.get("doi") else "—",
            f"{STATUS_EMOJI.get(s['status'],'')} {s['status']}",
            str(s.get("rows", 0)),
            " ".join(str(s.get("note", "")).split()),
        ])
    total = sum(s.get("rows") or 0 for s in kb["sources"])
    return ("# Sources\n\n"
            f"{len(kb['sources'])} sources contributing **{total} rows**.\n\n"
            + _table(rows, ["id", "DOI", "status", "rows", "note"]) + "\n")


def render_findings(kb: dict) -> str:
    parts = ["# Findings", "",
             "Every finding with its evidence and resolution. "
             "Ordered by severity, then id.", ""]
    for f in sorted(kb["findings"], key=lambda x: (SEVERITY_ORDER[x["severity"]], x["id"])):
        mark = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}[f["severity"]]
        parts += [f"## {mark} {f['id']} — {f['title']}", "",
                  f"**Severity:** {f['severity']} · **Status:** {f.get('status','open')}", ""]
        if f.get("evidence"):
            parts += [f"**Evidence:** {' '.join(f['evidence'].split())}", ""]
        parts += [f"**Action:** {' '.join(f['action'].split())}", ""]
    return "\n".join(parts)


def render_decisions(kb: dict) -> str:
    rows = [[d["id"], d["decision"], d["reason"]] for d in kb["decisions"]]
    return ("# Decisions\n\nStanding decisions. Reversing one requires a new entry, "
            "not an edit.\n\n" + _table(rows, ["id", "decision", "reason"]) + "\n")


def render_questions(kb: dict) -> str:
    rows = [[q["id"], q["question"], ", ".join(q.get("blocks") or []) or "—"]
            for q in kb["open_questions"]]
    return ("# Open questions\n\n" + _table(rows, ["id", "question", "blocks"]) + "\n")


# ---------------------------------------------------------------- main
def main() -> None:
    check_only = "--check" in sys.argv
    kb = load()

    errs = validate(kb)
    if errs:
        print("REGISTRY VALIDATION FAILED:")
        for e in errs:
            print(f"  ✗ {e}")
        raise SystemExit(1)
    print(f"registry valid: {len(kb['assets'])} assets, {len(kb['sources'])} sources, "
          f"{len(kb['findings'])} findings, {len(kb['decisions'])} decisions")

    if check_only:
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, text in [
        ("README.md", render_index(kb)),
        ("01-data-registry.md", render_assets(kb)),
        ("02-sources.md", render_sources(kb)),
        ("03-findings.md", render_findings(kb)),
        ("04-decisions.md", render_decisions(kb)),
        ("05-open-questions.md", render_questions(kb)),
    ]:
        (OUT_DIR / name).write_text(text, encoding="utf-8")
        print(f"  wrote {OUT_DIR / name}")


if __name__ == "__main__":
    main()
