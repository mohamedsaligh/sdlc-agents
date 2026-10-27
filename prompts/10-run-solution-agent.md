# Prompt 10 — Run the Solution Agent on a Jira

**How to run**
- VS Code Copilot: select the custom agent **solution-agent** (from `.github/agents/`), paste the block below.
- Claude Code: `claude` in the repo root, then type `use the solution-agent sub-agent` followed by the block below (or paste the block; `CLAUDE.md` routes it).

Fill the parameters. Leave optional ones blank. One Jira per run.

---

Run the **solution-agent** exactly as defined in `agents/solution-agent.md` and `AGENTS.md`.

```
JIRA_KEY:              <e.g. PAY-1234>
ENVIRONMENT_DESCRIBE:  <UAT>
ENVIRONMENT_TRACE:     <PROD (read-only) | UAT>
WORK_PACKAGE:          <blank | WP-nn for an onboarding slice>
PARENT_EXECUTION_ID:   <blank | base run id, required when WORK_PACKAGE is set>
SUPERSEDES:            <blank | previous execution id when re-running after questions>
GUIDANCE:              <blank | answers / constraints from BA or engineer, free text>
```

Operating instructions for this run:
1. Start with Step 00 (create the run folder with `scripts/new-run.py`; fetch the Jira and children; save inputs). Print the `EXECUTION_ID` immediately.
2. Execute stages 01 → 06 strictly in order. After each stage print one line: `STEP nn DONE — <output files>` or `STEP nn BLOCKED — <reason>`.
3. Keep every claim tied to evidence files inside the run folder. Do not paste raw tool output into documents.
4. If the gate fails, write `questions.md` and stop. Do not write an implementation plan "anyway".
5. Finish by printing: execution id · bucket · radius · scores (overall + four lanes) · decision · output paths · next action for humans (approval or answering questions).

Do not modify Jira, code under `__CODE_ROOT__`, design docs, manifests or any file outside the run folder (the final commit of the run folder is the one allowed git action; no push).

Note for Claude Code: a sub-agent's progress lines are not streamed; only its final message is shown. The per-stage status is always in `run.json.steps[]`, so open that file if you want to follow along.
