<!-- templates/maintenance-report.md — produced by the Maintenance Agent. Audience: engineering lead. -->

<!-- paste templates/_header.md here with document: maintenance-report -->

# Maintenance Report — <scope>

Trigger: <DESIGN_DOC_CHANGED | CODE_CHANGED | SCHEDULED | RUN_FEEDBACK | MANUAL>

## 1. Drift found

| Service | Source A | Source B | Disagreement | Severity |
|---|---|---|---|---|
| | design doc | manifest | `consumes[]` lists X, design doc no longer mentions X | HIGH / MED / LOW |

## 2. Manifest updates proposed
<!-- Diffs against manifests/<service>.yaml. Applied only when the operator confirms (prompt 30). -->

```diff
```

## 3. Design doc updates proposed
<!-- Never applied by the agent. Diff + reason. -->

```diff
```

## 4. Radius accuracy from completed runs
<!-- For each builder run since the last report: services the solution run predicted vs services actually changed. -->

| Jira | Predicted radius | Actual files' services | Missed | Extra | Lesson |
|---|---|---|---|---|---|

## 5. Vocabulary changes needed
- …

## 6. Actions
| # | Action | Owner | Status |
|---|---|---|---|
