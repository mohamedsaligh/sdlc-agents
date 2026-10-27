# Prompt 03 — Validate the repository is complete and ready for a real run

**Purpose**: an independent completeness audit of everything prompts 00–02 produced, plus a
dry run of the Solution Agent on a synthetic Jira, before the first real Jira is used.
Run this in a **fresh** chat session so the auditor has not seen the build-up.

**How to run**: paste below the line. Takes one session. Output: `docs/readiness-report.md`.

---

You are auditing this repository for readiness. Read `AGENTS.md` first. Be strict and specific:
every finding must name a file and what exactly is wrong. Do not fix anything; report.

Produce `docs/readiness-report.md` with the sections below, each item marked PASS / FAIL / N/A with evidence.

## 1. Initialisation
- `config/.initialized` exists; no `__PLATFORM_NAME__`, `__DEVCTL__`, `__AI_PLATFORM__`, `__CODE_ROOT__`, `__DESIGN_DOCS_ROOT__` token remains anywhere outside `scripts/init-project.*` and `runs/` (search the whole repo).
- `CODE_ROOT` and `DESIGN_DOCS_ROOT` paths exist and contain what `AGENTS.md §1` says.
- `python scripts/sync-agents.py --check` passes (generated agents are current).
- `.github/agents/*.agent.md` and `.claude/agents/*.md` exist for solution, builder, maintenance.

## 2. Discovery
- `config/tools.md` has no `NOT YET DISCOVERED` line; every row of the capability table is filled or explicitly `none` with a workaround.
- `schema/devctl-contracts.md` sections B.1–B.3 are filled; example files exist under `docs/discovery/`.
- `schema/vocabulary.yaml`: `markets`, `clearings`, `products`, `channels` non-empty; no `TO CONFIRM` items left.
- `docs/discovery/design-doc-map.md` exists and covers every manifest field.

## 3. Map
- `python scripts/validate-manifests.py` → 0 errors. Paste the summary line.
- `python scripts/check-drift.py` → 0 HIGH findings. Paste the summary line.
- Count: design docs = manifests = service folders (explain any difference).
- Every manifest `verification.sources` includes `trace` for at least the services on the traced paths; list services never traced.
- Open the three largest manifests: confirm shape-only (no rows, hostnames, secrets); confirm `onboarding_recipe` is actionable (a junior could follow the substitution rules).

## 4. Templates and agents
- Every template in `templates/` has the standard header block and keeps its headings.
- `agents/solution-agent.md`: the six sub-agents each state Inputs, Work, Outputs, Checks; outputs reference existing templates; thresholds reference `config/thresholds.yaml` keys that exist.
- `agents/builder-agent.md`: hard rules present; gate requires `approval.json` with both approvals and `plan_sha256`.
- `agents/maintenance-agent.md`: never edits design docs or code.

## 5. Dry run (synthetic Jira)
1. Create `runs/_dryrun/SYNTHETIC-1/steps/00-input/jira.md` by hand with: a plausible ENHANCEMENT for an existing market × clearing × product (pick values present in manifests), two acceptance criteria, the four routing fields filled.
2. Execute the Solution Agent steps 01–02 **manually** following `agents/solution-agent.md` using only files (skip tool calls; where a tool would be called, write what you would call and with which arguments).
3. Check: did the tag intersection produce a sensible radius? Is the baseline choice explainable? Would the Load step fetch only radius docs? Record the radius and your verdict.
4. Delete nothing; leave `runs/_dryrun/` for review.

## 6. Verdict
`READY FOR FIRST REAL RUN` only if every item in sections 1–4 is PASS and the dry run radius is sensible.
Otherwise list the blocking items in priority order with the prompt or script that fixes each.
Print the verdict and the blocking list in the chat.
