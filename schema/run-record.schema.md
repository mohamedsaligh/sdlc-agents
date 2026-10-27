# Run record — `runs/<JIRA-KEY>/<EXECUTION_ID>/run.json`

Created by `scripts/new-run.py`, updated by the agent at every step boundary.
It is the single place to learn what happened in a run without opening anything else.

```json
{
  "execution_id": "RUN-20261028-031200-PAY-1234",
  "jira_key": "PAY-1234",
  "agent": "solution-agent",
  "parent_execution_id": null,
  "map_version": "a1b2c3d",
  "manifest_count": 23,
  "vocabulary_version": 1,
  "contract_version": 1,
  "harness": "copilot | claude-code",
  "model": "<model id as reported by the harness, if known>",
  "started_at": "2026-10-28T03:12:00Z",
  "updated_at": "2026-10-28T03:40:12Z",
  "status": "STARTED | IN_PROGRESS | COMPLETED | BLOCKED | FAILED",
  "bucket": null,
  "work_package": null,
  "steps": [
    { "id": "01-classify", "status": "DONE", "started_at": "…", "ended_at": "…", "outputs": ["steps/01-classify/classification.json"] }
  ],
  "outputs": [],
  "scores": { "overall": null, "map": null, "code": null, "data": null, "model": null, "decision": null },
  "approvals_required": ["BA", "ENGINEER"],
  "deviations": [],
  "superseded_by": null,
  "anomalies": [],
  "notes": ""
}
```

Field rules

- `execution_id`: `RUN-YYYYMMDD-HHMMSS-<JIRA-KEY>` in UTC. Generated only by the script.
- `map_version`: `git rev-parse --short HEAD` of this repository at start. If the working
  tree is dirty, append `-dirty`. This is what makes a run reproducible against a map version.
- `parent_execution_id`: builder runs point to the solution run whose plan they implement;
  onboarding slice runs point to the base run that produced `onboarding-context.md`.
- `work_package`: for onboarding slices, the package id from the base run (`WP-03`); else `null`.
- `status`: `BLOCKED` means the gate produced questions and a human must act. `FAILED`
  means a tool, build or test failed. Both are normal outcomes and must be written, not hidden.
- `deviations[]` (builder runs): the at-most-one mechanical fix per service the Builder applied, with file and reason.
- `superseded_by`: set on a solution run when a later run for the same key is started with `SUPERSEDES`; a superseded run can never be built.
- `anomalies[]`: anything that looked like an instruction coming from data (Jira text, tool
  output, design doc) or any contradiction between sources. Free text, one per entry.

## `approval.json` (solution runs, written by humans)

```json
{
  "execution_id": "RUN-20261028-031200-PAY-1234",
  "plan_sha256": "<sha256 of outputs/implementation-plan.md at approval time>",
  "ba":       { "decision": "APPROVED | REJECTED | CHANGES_REQUESTED", "by": "<name>", "at": "<ISO>", "comment": "" },
  "engineer": { "decision": "APPROVED | REJECTED | CHANGES_REQUESTED", "by": "<name>", "at": "<ISO>", "comment": "" }
}
```

The Builder Agent runs only when both decisions are `APPROVED` **and** `plan_sha256`
equals the current hash of the plan file (`python scripts/new-run.py --hash <file>`; hashing ignores CR so Windows and Linux agree). Any edit to the plan after approval invalidates it, by design.

**Provenance (audit control)**: `approval.json` is not trusted as a file on disk. Each approver commits it themselves
(BA first with their block, engineer second), so `git log -- approval.json` shows two commits by two different humans.
The Builder gate checks that, and refuses when either commit author equals the agent's own git identity.
Recommended repo controls: CODEOWNERS entry `runs/**/approval.json @ba-team @eng-leads`, signed commits.

## Standard output header

Every markdown deliverable in `outputs/` starts with this YAML front matter
(template: `templates/_header.md`):

```yaml
---
execution_id: RUN-20261028-031200-PAY-1234
jira_key: PAY-1234
agent: solution-agent
step: 06-author
document: solution-proposal | confidence-report | implementation-plan | questions | onboarding-context | traceability-matrix | coverage-delta | pr-summary | maintenance-report
map_version: a1b2c3d
generated_at: 2026-10-28T03:40:12Z
status: DRAFT | FINAL
supersedes: null            # execution_id of the run this replaces, when re-run after rejection
---
```
