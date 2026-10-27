# Prompt 00 — Discover the environment (run once, before anything else)

**How to run**: open this repository in VS Code (Copilot agent mode) or Claude Code with the
Jira and `__DEVCTL__` MCP servers connected. Paste everything below the line into the chat.
Expected duration: one session. Output: five files updated, one report written.

**Pre-conditions**: `scripts/init-project` has been run (`python scripts/init-project.py --verify` is clean);
`python scripts/sync-agents.py` has been run; the chat is open in the multi-root workspace from
`python scripts/make-workspace.py` (or Claude Code was started with the `--add-dir` flags it prints), so
`__CODE_ROOT__` and `__DESIGN_DOCS_ROOT__` are readable.

---

You are setting up the agent harness in this repository. Read `AGENTS.md` first and follow it.
Your job is discovery only: learn what the tools return and what the design docs look like, then
record it precisely so later agents never have to guess. Do not analyse any Jira, do not build manifests.

Work through the numbered tasks in order. After each task, write the output file named, then print
one line: `TASK n DONE — <file>`. If a task cannot be completed, print `TASK n BLOCKED — <reason>` and
continue with the next task; never silently skip.

## Task 1 — Inventory the MCP tools

1. List every MCP tool available in this session with its exact name, server, and argument schema.
2. Map tools to the capabilities in `config/tools.md` (`jira.get_issue`, `jira.get_children`, `jira.add_attachment`, `jira.add_comment`, `devctl.describe`, `devctl.locate`, `devctl.trace`, `scm.create_pr`). A capability may map to no tool (write `none`) or to one tool with a specific argument pattern (write the pattern).
3. Fill the "Capability → tool" and "Environment names" tables in `config/tools.md`. Remove the `NOT YET DISCOVERED` status line **only if** `jira.get_issue`, `devctl.describe` and `devctl.trace` all have a tool. Otherwise keep the line and write exactly what is missing below it.

## Task 2 — Probe `__DEVCTL__` describe

1. Pick one service that certainly has configuration (ask me if unsure; otherwise choose the one whose design doc mentions the most tables) and one live market.
2. Call the describe tool for that service and market in the lowest non-production environment allowed. Save the raw response, with any secret-looking values masked as `***`, to `docs/discovery/describe.raw.example.json`.
3. Write the raw → normalized field mapping for contract A.1 into `schema/devctl-contracts.md` section B.1: for each normalized field, the raw JSON path that supplies it, or `DERIVED: <how>` or `UNAVAILABLE: <workaround>`. Note page size / truncation behaviour.
4. Produce one normalized example at `docs/discovery/describe.normalized.example.json` following A.1 exactly, **with section C projection and masking applied**, and check it against the shape field by field. If the describe output has columns the section C regex does not catch but that hold personal or credential data, extend the regex in section C (never shorten it) and say so in the report.

## Task 3 — Probe `__DEVCTL__` trace

1. Call the trace tool for the most common product in the same market (read-only, production allowed if the tool is read-only, else UAT). Save the masked raw response to `docs/discovery/trace.raw.example.json`.
2. Build the **component-name → service-name** translation table: every component/log source name in the raw trace mapped to a service identifier equal to a folder name under `__CODE_ROOT__`. Put it in section B.3 of `schema/devctl-contracts.md`. Unknown components go in a "to confirm" list — ask me.
3. Write `docs/discovery/trace.normalized.example.json` following A.3. Confirm hop order and parallel groups are represented.

## Task 4 — Probe `__DEVCTL__` locate (or establish the fallback)

1. If a locate capability exists, call it for one known class name and one table name; save raw and normalized examples as above; fill B.2.
2. If it does not exist, write in B.2 the exact fallback the agents will use: a recursive text search under `__CODE_ROOT__/<service>` (state the command for this OS) producing contract A.2 with `query.kind = text`. Test the command once and paste the (trimmed) result as the example.

## Task 5 — Sample the design docs

1. List `__DESIGN_DOCS_ROOT__`: count files, confirm each is `<service>.md` and that `<service>` matches a folder under `__CODE_ROOT__`. Write mismatches to `docs/discovery/naming-mismatches.md` (empty file if none).
2. Open two design docs (the largest and a median one). For each manifest field in `schema/manifest.schema.md`, note under which heading(s) of the design doc the information is found. Write `docs/discovery/design-doc-map.md` as a table: manifest field → typical heading → example value → reliability (ALWAYS / USUALLY / SOMETIMES / NEVER present). This table is what prompt 01 uses to extract manifests consistently.
3. Record anything that differs between the two docs in structure.

## Task 6 — Populate the firm-specific vocabulary

1. From the two design docs, the describe output, the trace output, and `__CODE_ROOT__` (enum classes or constants for markets, clearings, products, channels, priorities), collect candidate values for `markets`, `clearings`, `products`, `channels`, `priorities`.
2. Write them into `schema/vocabulary.yaml`. Keep the identifiers exactly as the code spells them. Where you are unsure whether two spellings are the same thing, list both under a `# TO CONFIRM` comment and ask me.
3. Bump nothing; `vocabulary_version` stays 1 until I approve.

## Task 7 — Discovery report

If sections B.1, B.2 and B.3 are all filled (`UNAVAILABLE` with a workaround counts as filled), **delete the `> Status: NOT YET DISCOVERED` line in section B** of `schema/devctl-contracts.md`; otherwise leave it and list what is missing under it.

Write `docs/discovery/discovery-report.md` with: tools found and missing; one paragraph per capability on reliability and limits; naming mismatches; design-doc consistency; vocabulary gaps; and a **Readiness** section listing exactly what must be fixed before prompt 01 can run. Finish by printing the readiness section in the chat.

## Rules
- Never call a tool in write mode. Never change production. Mask secrets and personal data before saving.
- Do not invent a mapping. `UNAVAILABLE` with a workaround is a correct answer; a guessed path is not.
- Keep raw examples under 200 lines each (truncate arrays and say so).
