<!-- templates/traceability-matrix.md — produced by the Builder Agent. Audience: BA, QA, audit.
     Shows the unbroken chain: acceptance criterion → plan section → file + lines changed → test → PR.
     Every row must be complete or marked GAP with a reason. -->

<!-- paste templates/_header.md here with document: traceability-matrix -->

# Traceability Matrix — <JIRA-KEY>

Solution run: `<SOLUTION_EXECUTION_ID>` · Plan hash: `<plan_sha256>` · Builder run: `<EXECUTION_ID>`

## 1. Requirement → implementation

| AC / Epic | Requirement (short) | Plan section(s) | Service | Files changed (path:lines) | Data scripts | Tests | PR | Status |
|---|---|---|---|---|---|---|---|---|
| AC-1 | | §2.1, §3.1 | service-a | `src/.../File.java:41-58` | §3.1 | `FileTest#newCase` | #123 | DONE / GAP |

## 2. Implementation → requirement (reverse check)
<!-- Every changed file must map back to at least one AC. Unmapped changes are a finding. -->

| File changed | Mapped to AC | Note |
|---|---|---|

## 3. Gaps and deviations from the approved plan
<!-- The Builder may not improvise. Every difference from the plan is listed here. Allowed: at most one mechanical fix per service (builder-agent hard rule 2), recorded in run.json.deviations[]. Anything beyond that means the run is FAILED. -->

| # | Plan said | What happened | Why | Action needed |
|---|---|---|---|---|

## 4. Summary
- Acceptance criteria: <k> of <m> fully traced.
- Files changed: <n> · Data scripts: <n> · Tests added/modified: <n>.
- Unmapped changes: <n> (must be 0).
