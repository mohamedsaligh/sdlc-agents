# Prompt 20 — Run the Builder Agent on an approved plan

**Before you run**: both reviewers must have written `approval.json` into the solution run folder.
Create it like this (edit the values), then compute the plan hash:

```
python scripts/new-run.py --hash runs/<JIRA-KEY>/<SOLUTION_EXECUTION_ID>/outputs/implementation-plan.md
```

```json
{
  "execution_id": "<SOLUTION_EXECUTION_ID>",
  "plan_sha256": "<paste hash>",
  "ba":       { "decision": "APPROVED", "by": "<name>", "at": "<ISO date-time>", "comment": "" },
  "engineer": { "decision": "APPROVED", "by": "<name>", "at": "<ISO date-time>", "comment": "" }
}
```

**How to run**: select the **builder-agent** custom agent (Copilot) or ask Claude Code to use the
builder-agent sub-agent, then paste the block below. Service repos under `__CODE_ROOT__` must be clean
working trees on their default branch.

---

Run the **builder-agent** exactly as defined in `agents/builder-agent.md` and `AGENTS.md`.

```
JIRA_KEY:               <e.g. PAY-1234>
SOLUTION_EXECUTION_ID:  <RUN-...-PAY-1234>
DRY_RUN:                <false | true>
```

Operating instructions for this run:
1. Step 00 gate first. If approvals or the plan hash do not check out, stop and tell me exactly what is missing.
2. Execute steps 01 → 09 in order; print `STEP nn DONE/FAILED/BLOCKED — <detail>` after each.
3. Apply the plan literally. If something in the plan cannot be applied as written, stop with the section number and the exact problem. Do not improvise a fix beyond the one mechanical correction the agent definition allows, and record any such correction in `deviations[]`.
4. Write data scripts; never execute them.
5. Finish by printing: execution id · status · per-service build/test result · changed-line coverage · ACs traced · PR links (or the manual commands if the PR tool is unavailable) · deviations.
