# Runbook — from empty repo to first PR

Each step names the command or prompt, the person, and the exit test. Do them in order.
Timelines are yours; the order is not negotiable because each step feeds the next.

## Phase 1 — The map

| # | Do | Who | Exit test |
|---|----|-----|-----------|
| 1.1 | Edit `config/platform.env`, then `scripts\init-project.cmd` (Windows) or `bash scripts/init-project.sh` | Eng lead | `config/.initialized` exists; `python scripts/init-project.py --verify` reports no unreplaced placeholders |
| 1.2 | `python scripts/sync-agents.py` | Eng lead | `.github/agents/` and `.claude/agents/` contain three agents each |
| 1.2b | `python scripts/make-workspace.py` and open the generated `.code-workspace` in VS Code (or start Claude Code with the printed `--add-dir` flags) | Eng lead | the chat can list files under `__CODE_ROOT__` and `__DESIGN_DOCS_ROOT__` |
| 1.2c | Edit the team handles in `.github/CODEOWNERS`, then ask the repo admin to enable "Require review from Code Owners" and "Require signed commits" on `main`. (No file to create: `approval.json` only appears per run, in phase 3.) | Eng lead + repo admin | branch protection shows both rules on |
| 1.3 | Connect Jira and `__DEVCTL__` MCP servers in VS Code / Claude Code | Eng lead | tools visible in the chat's tool list |
| 1.4 | Run `prompts/00-discover.md` | Eng lead | `config/tools.md` and `schema/devctl-contracts.md` filled; `docs/discovery/discovery-report.md` Readiness clear |
| 1.5 | Ask the Jira admin for the four dropdown fields (`schema/jira-fields.md`) | Eng lead / BA | fields exist, or the `agent-fields:` fallback agreed with BAs |
| 1.6 | Run `prompts/01-build-manifests.md` in batches of 4–6 services | Eng lead (+ service owners for review) | `python scripts/validate-manifests.py` → 0 errors; every design doc has a manifest |
| 1.7 | Run `prompts/02-triangulate.md` for the main product, then RTP, then batch | Eng lead | every product verdict `READY`; `python scripts/check-drift.py` → 0 HIGH |
| 1.8 | Run `prompts/03-validate-repo.md` in a fresh session | A second engineer | `docs/readiness-report.md` says `READY FOR FIRST REAL RUN` |
| 1.9 | Commit; tag `map-v1` | Eng lead | tag exists; `run.json.map_version` (short SHA) resolves to it |

## Phase 2 — Solution Agent demo

| # | Do | Who | Exit test |
|---|----|-----|-----------|
| 2.1 | Pick the demo Jira (ENHANCEMENT touching 2–3 services, or a NEW feature). Write down privately which services you expect. | Eng lead | note kept |
| 2.2 | BA fills Market / Clearing / Product / Direction and acceptance criteria | BA | fields non-empty |
| 2.3 | Run `prompts/10-run-solution-agent.md` | Engineer | run folder has three outputs or `questions.md`; `run.json.status` COMPLETED or BLOCKED |
| 2.4 | Compare the radius to your private note; read the three documents as the BA and as a junior engineer | Eng lead + BA | radius matches or the difference is explained by evidence; plan is executable by a junior |
| 2.5 | Iterate: tune `config/thresholds.yaml`, fix manifests, improve `docs/discovery/design-doc-map.md`; re-run with `SUPERSEDES` | Eng lead | two consecutive runs on different Jiras need no manual correction of the radius |
| 2.6 | Record the demo run id in `docs/decisions.md` | Eng lead | — |

## Phase 3 — Builder Agent

| # | Do | Who | Exit test |
|---|----|-----|-----------|
| 3.1 | BA commits `approval.json` (own identity), then engineer commits their block (see `prompts/20-run-builder-agent.md`) | BA + Engineer | hash matches the plan; `git log -- approval.json` shows two humans |
| 3.2 | Run `prompts/20-run-builder-agent.md` with `DRY_RUN: true` | Engineer | builds and tests pass; artefacts produced; no PR |
| 3.3 | Run again with `DRY_RUN: false` | Engineer | PR(s) raised with `pr-summary.md`; Jira has attachments; traceability matrix has 0 unmapped files |
| 3.4 | Human code review and merge as usual | Team | merged |
| 3.4b | Data scripts: engineer raises the change ticket named in plan §3, the owning team executes apply (and keeps rollback ready) per environment | Engineer + data owners | ticket closed; `run.json.notes` records ticket id |
| 3.5 | Run `prompts/30-run-maintenance-agent.md` with `TRIGGER: RUN_FEEDBACK` | Eng lead | radius accuracy recorded; any manifest fixes applied |

## Phase 4 — Distribution (design only for now)

- On every merge to `main`, CI runs `sync-agents --check`, `validate-manifests`, and publishes a tagged bundle (`manifests/`, `schema/`, `agents/`, `templates/`, `config/thresholds.yaml`, `config/tools.md`) to `__AI_PLATFORM__`.
- The local CLI pulls the bundle by tag and exposes it over MCP as resources, so engineers in any region run the same agents against the same map version. `run.json.map_version` keeps runs comparable.
- Onboarding base runs publish `onboarding-context.md` to `__AI_PLATFORM__` so slices in other regions never redo discovery.

## Day-to-day

- New Jira → prompt 10. Questions → BA answers → prompt 10 again with `SUPERSEDES`.
- Approved plan → prompt 20.
- Design doc changed → prompt 30 with `TRIGGER: DESIGN_DOC_CHANGED` (CI's drift check will remind you).
- Weekly → prompt 30 with `TRIGGER: SCHEDULED`.
- Changing an agent → edit `agents/*.md`, run `python scripts/sync-agents.py`, commit both.
- Runs → each agent commits its own run folder (no push); push `runs/` with your normal pushes. When more than one team uses the map, move to the separate runs repository (decision D-10) so `main` of this repo only changes when the map changes.
