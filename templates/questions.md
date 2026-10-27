<!-- templates/questions.md — written INSTEAD of the Implementation Plan when the gate fails,
     or at step 01 when required Jira fields are missing. Audience: BA and engineering lead.
     Rules: each question names exactly what is needed, who answers it, and what it unblocks.
     After answers are added to the Jira (or injected via prompts/10 "guidance"), re-run with supersedes set. -->

<!-- paste templates/_header.md here with document: questions -->

# Questions before an Implementation Plan can be written — <JIRA-KEY>

## Why the run stopped
<!-- One of: REQUIRED_FIELDS_MISSING | GATE_FAILED | CONTRADICTION_UNRESOLVED | TOOL_UNAVAILABLE -->
Reason: **<code>** — <one sentence>.
Scores at stop (if scored): Overall <n> · MAP <n> · CODE <n> · DATA <n> · MODEL <n> (`outputs/confidence-report.md`)

## Questions

| # | Question | Exact information needed | For | Unblocks | Evidence of the gap |
|---|---|---|---|---|---|
| Q1 | | e.g. "the cut-off time rule for CLR_HV_A in MKT_C" | BA / Engineer / Ops | DATA lane, §3.2 of plan | `steps/03-load/normalized/describe-2.json#missing` |

## What the agent could establish with confidence
<!-- So reviewers do not re-check what is already solid. -->
- …

## Proposed answers (agent's best guess — NOT to be used without confirmation)
| # | Proposed answer | Basis | Confidence |
|---|---|---|---|

## How to resume
1. Add the answers to the Jira (fields, acceptance criteria, or a comment titled `agent-guidance`).
2. Re-run `prompts/10-run-solution-agent.md` with the same key. The new run's header will set `supersedes: <this execution_id>`.
