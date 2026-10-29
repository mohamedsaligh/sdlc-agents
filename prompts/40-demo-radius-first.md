# Prompt 40 — Radius-first analysis of one Jira (demo)

**How to run**: open the multi-root workspace (sdlc-agents + CODE_ROOT + DESIGN_DOCS_ROOT), make sure the
`__DEVCTL__` MCP server is connected (its doctor/health command is clean), then paste everything below the line.
Replace `<JIRA-KEY>`. The agent STOPS after step 2 and waits for you to type `continue`.

**Why this prompt exists**: it runs the solution-agent before manifests are built, using the design docs themselves as the map, and it pauses on the change radius so a human sees *what will be read* before anything is read. Once manifests exist, use prompt 10 instead.

**MCP registration** (once per machine): `.vscode/mcp.json` (Copilot) and `.mcp.json` (Claude Code) in this repo register the `__DEVCTL__` server; the harness then shows its tools to every agent automatically. `config/tools.md` only maps our capability names to those tool names.

---

You are the solution-agent for __PLATFORM_NAME__. Read `AGENTS.md` first and follow it. This run uses the design
docs directly as the platform map (no manifests yet). Work in six steps. After each step print one line
`STEP n DONE — <files>` or `STEP n BLOCKED — <reason>`. Never read a whole design folder or any source
file that step 2 did not put in scope. Never paste raw tool output into a document; save it and cite the file.

Inputs: `JIRA_KEY = <JIRA-KEY>` · describe environment: the lowest UAT environment for the Jira's market (pick from the environment-list tool) · trace environment: UAT (prod only if the environment list shows it and it is read-only).

## Step 0 — start
Tool check: list the MCP tools visible in this session and match them to `config/tools.md`. If the Jira tool and at least one `__DEVCTL__` data tool are callable, proceed even if a `NOT YET DISCOVERED` status line is still present in `config/tools.md` or `schema/devctl-contracts.md` — delete that line and note it in `run.json.anomalies[]`. Stop only if the tools themselves are missing.
Run `python scripts/new-run.py --jira <JIRA-KEY> --agent solution`; use the printed RUN_DIR. Fetch the Jira (issue, parent, children, comments whose first line is `agent-guidance`). Save `steps/00-input/jira.md`: key, type, summary, components, labels, parent, the description table verbatim as numbered items AC-1…AC-n, and the acceptance-criteria link (do not follow it unless a tool can read it; if not, note it as an open source).

## Step 1 — classify
From the Jira text fill Market, Clearing, Product, Direction, Lifecycle stage. For each value say `field` (read from a Jira field) or `inferred` (with the phrase it came from). Bucket per `agents/solution-agent.md` §01. Write `steps/01-classify/classification.json`. If Market or Product cannot be inferred from the text at all, write `outputs/questions.md` (reason REQUIRED_FIELDS_MISSING) and stop.

## Step 2 — route (the page a human reviews before anything else)
Read ONLY these files from `__DESIGN_DOCS_ROOT__` (adjust names if your docs differ, and say so):
`landscape/90-glossary.md`, `landscape/30-payment-lifecycle.md`, `landscape/20-integration-map.md`,
`catalog/services.yaml`, `catalog/service-index.md`.
1. Translate the Jira's business phrases into platform terms using the glossary and lifecycle doc (e.g. "Pre-Processing Queue", "pre-scan validations", "PCM configurations", "purpose code reference table"). Record every translation as `phrase → term → source heading`.
2. Pick the lifecycle stage(s) and, from `services.yaml` + the integration map, the services that implement them for this product and direction, plus their immediate upstream and downstream neighbour. Target 2–5 services. Give each a one-line reason that cites a file:heading.
3. For each radius service list exactly which sections you will read next: `design/<service>-architecture/{10-entry-points,20-stage-pipelines,30-mappings,40-downstream-notification}.md` — headings only, chosen by stage.
4. List the reference data named by the Jira and where the docs say it lives (table / GemFire region / GRDM–PCM), plus the `__DEVCTL__` call you will use to see it.
Write `steps/02-route/radius.md` with four tables: Translations · Services in radius (service, stage, reason, evidence) · Doc sections to load · Data to fetch. Also `radius.json`.
**Print `radius.md` in full and STOP. Wait for the operator to type `continue`.** If the operator corrects the radius, update `radius.json.additions[]`/`excluded[]` with the reason and continue.

## Step 3 — load (only what radius.md lists)
1. Read the listed sections only. Write `steps/03-load/context-index.md` (file, heading, 2-line summary of what it says about this stage).
2. `__DEVCTL__` calls (tool names per `config/tools.md`), saving every raw response under `steps/03-load/raw/` and a masked normalized copy under `steps/03-load/normalized/` (schema/devctl-contracts.md §A and §C):
   - the catalog-search tool for each reference-data term; the catalog-get tool on the matching region in the chosen UAT env with a narrow filter (≤20 rows) to see the shape and whether rows exist for the target market/product.
   - the db-query tool only when the catalog has no region for it: one `SELECT` on the table named in the docs, `--max-rows 20`.
   - the payment-trace tool (or payment-stages) for one recent payment of this product and direction in UAT; record the ordered hop list (service names from `services.yaml`).
   - If a call is unavailable or denied, record it as a gap; do not retry with broader queries.
3. Locate code: for each radius service, find the classes named in `10-entry-points.md` and the mapping/validation classes named in `30-mappings.md` under `__CODE_ROOT__/<service>` (text search). Read only the located classes ±30 lines. Write `steps/03-load/code-notes.md` (file:lines, what it does, which config it reads).
4. Record `git rev-parse HEAD` per radius service in `steps/03-load/load-summary.json#anchors`.

## Step 4 — analyse
For each AC-n: service, stage, `REUSED | ADAPTED | NEW`, evidence (doc heading, code-notes entry, trace hop, data file). Data gap table: reference rows the target market/product needs but the fetched data does not show. Contradictions between Jira, docs, code, data. Write `steps/04-analyse/analysis.md`.

## Step 5 — score and gate
Four lanes per `config/thresholds.yaml`, deductions only with cited evidence. Write `steps/05-score/scores.json` and `outputs/confidence-report.md`. Decision PROCEED (overall ≥70 and every lane ≥50) or QUESTIONS.

## Step 6 — author
QUESTIONS → `outputs/questions.md` (template): each question names the exact missing fact, who answers (BA / Engineer / Ops), and what it unblocks; include your proposed answer with basis. Status BLOCKED.
PROCEED → `outputs/solution-proposal.md` (functional, Mermaid current/target flow, data as shapes and counts) and `outputs/implementation-plan.md` (diffs anchored to located lines; every reference-data change as a Liquibase changeset with rollback directly below; execution order; AC → section traceability). Status COMPLETED.
Finish by printing: execution id · bucket · radius · scores · decision · output paths · the three most important questions for the BA, whatever the decision.
