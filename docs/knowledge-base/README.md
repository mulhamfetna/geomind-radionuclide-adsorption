# GEOMIND-R — Knowledge Base

> **Generated from `knowledge_base/registry.yaml` — do not edit these files by hand.**
> Regenerate with `python -m src.geomind.kb`.

**Updated:** 2026-07-20 · **Pool:** 121 rows / 9 sources

## Contents
| Document | Purpose |
|---|---|
| [Data registry](01-data-registry.md) | Every data asset, its status and its usage constraints |
| [Sources](02-sources.md) | Every paper, with extraction status and row contribution |
| [Findings](03-findings.md) | Every finding, its evidence and what was done about it |
| [Decisions](04-decisions.md) | Standing decisions and the reason for each |
| [Open questions](05-open-questions.md) | What is unresolved and what it blocks |

## At a glance
- **Assets registered:** 17 — 🔧 derived 2, ♻️ duplicate 2, 📦 external 1, 🟡 partial 2, ❌ rejected 1, ⬜ unmined 2, ✅ verified 7
- **Findings:** 37 (10 critical)
- **Still open:** 7 finding(s), 4 question(s)

## The rule this exists to enforce

> **No data enters an analysis unless it is registered here with an explicit
> `status` and `usage`.** Statuses are a closed vocabulary; the generator rejects
> anything else. Every error in this project so far came from implicit knowledge —
> which sheet had been checked, which rows were verified, what must not be pooled.
