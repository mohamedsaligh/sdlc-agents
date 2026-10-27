# sdlc-agents — the Platform Map and agent harness for `__PLATFORM_NAME__`

Turns a business Jira into a reviewed, evidence-scored implementation plan, and an approved plan
into a tested pull request — for a large event-driven payment platform, by any engineer, in any region,
without injecting the whole codebase into an AI context.

**Shape in the map, data live · Thin agents, thick map · Evidence gates · Everything is a file.**

```
Jira ──► Solution Agent ──► Proposal + Confidence + Plan ──► BA & Engineer approve ──► Builder Agent ──► PR + Coverage + Traceability
             ▲                                                                             │
             └──────────── Platform Map (manifests · design docs · __DEVCTL__) ◄── Maintenance Agent ◄───┘
```

## Quick start (engineering lead, one time)

```bash
# 1. tell the repo about your environment (edit the right-hand sides, then run ONE of these)
notepad config\platform.env   &&  scripts\init-project.cmd            # Windows
$EDITOR config/platform.env   &&  bash scripts/init-project.sh         # Mac / Linux / Git Bash

# 2. generate harness adapters for Copilot and Claude Code
python scripts/sync-agents.py

# 3. in VS Code (Copilot agent mode) or Claude Code, with Jira + __DEVCTL__ MCP servers connected:
#    paste prompts/00-discover.md  →  01-build-manifests.md (batches)  →  02-triangulate.md  →  03-validate-repo.md
```

Then, for every Jira: `prompts/10-run-solution-agent.md` → review → `prompts/20-run-builder-agent.md`.
Full order of operations with exit tests: **`docs/runbook.md`**. Presentation: **`docs/design-canvas.html`**.

## Repository layout

| Path | What | Edit? |
|---|---|---|
| `AGENTS.md` | Operating rules for every agent (Copilot reads it directly; `CLAUDE.md` imports it) | yes |
| `agents/` | Canonical definitions: `solution-agent.md` (6 sub-agents), `builder-agent.md`, `maintenance-agent.md` | yes |
| `.github/agents/`, `.claude/agents/` | Generated adapters — `python scripts/sync-agents.py` | **no** |
| `config/` | `platform.env` (tokens), `tools.md` (MCP registry), `thresholds.yaml` (confidence lanes & gate) | yes |
| `schema/` | Manifest schema/template/example, Jira fields, controlled vocabulary, `__DEVCTL__` contracts, run record | rarely |
| `manifests/` | One YAML per service — the map (shape only) | via prompts 01/02 and the maintenance agent |
| `templates/` | The shapes of every output document (standard header included) | yes |
| `prompts/` | Operator prompts: `00` discover · `01` manifests · `02` triangulate · `03` validate · `10` solution · `20` builder · `30` maintenance | yes |
| `scripts/` | `init-project` · `sync-agents` · `new-run` · `validate-manifests` · `check-drift` (stdlib; validator needs `pyyaml`) | yes |
| `runs/` | Audit trail: `runs/<JIRA-KEY>/<EXECUTION_ID>/` | agents only |
| `docs/` | Design canvas, runbook, decisions, discovery outputs, readiness report | yes |

External (referenced by absolute path, never copied): `__CODE_ROOT__` (parent folder of all service
repos) and `__DESIGN_DOCS_ROOT__` (reviewed design markdowns, one per service).

## The three agents

| Agent | In | Out | Rule of thumb |
|---|---|---|---|
| **solution-agent** | Jira key (+ optional work package, guidance) | `solution-proposal.md` (functional, with flow diagrams) · `confidence-report.md` (4 evidence lanes) · `implementation-plan.md` (diffs, data scripts with rollback) — or `questions.md` | Thinks. Never writes code. Stops below the gate. |
| **builder-agent** | Approved plan (two approvals + plan hash) | PR(s) · `coverage-delta.md` · `traceability-matrix.md` | Boring on purpose. Executes literally, stops on failure. |
| **maintenance-agent** | Changed design docs / code / completed runs | `maintenance-report.md` + manifest patches | Keeps the map true. Proposes, never silently applies. |

## Change buckets

`ONBOARDING` (new market or new market × clearing × product; base pass + work-package slices) ·
`MINOR_INITIATIVE` (new service/feature in an existing flow) · `ENHANCEMENT` · `BUG_FIX`.
Classification rules: `agents/solution-agent.md §01`.

## Confidence and the gate

Lanes **MAP 0.30 · CODE 0.30 · DATA 0.25 · MODEL 0.15**, each 100 minus evidence-backed deductions.
Plan is written only when overall ≥ 70 **and** every lane ≥ 50; otherwise the agent asks precise questions.
Tune in `config/thresholds.yaml`; record changes in `docs/decisions.md`.

## Compatibility

- **VS Code Copilot**: custom agents in `.github/agents/*.agent.md`; repo instructions in `.github/copilot-instructions.md` and `AGENTS.md`. (Older VS Code: copy the agent files to `.github/chatmodes/*.chatmode.md`.)
- **Claude Code**: `CLAUDE.md` → `AGENTS.md`; sub-agents in `.claude/agents/*.md`.
- Prompts are written so a mid-tier model follows them step by step; a stronger model simply finishes faster.

## Status

Phase 1 scaffold complete. Next: run `scripts/init-project`, then `prompts/00-discover.md` inside the firm network.
