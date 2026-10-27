<!-- templates/onboarding-context.md — produced ONCE per onboarding by the BASE pass of the
     Solution Agent. Every slice run (per work package) and every engineer picking up a slice
     reads this instead of redoing discovery. Audience: engineers, BA, PM.
     Lives at runs/<JIRA-KEY>/<BASE_EXECUTION_ID>/outputs/onboarding-context.md
     and is published to __AI_PLATFORM__ in phase 4. -->

<!-- paste templates/_header.md here with document: onboarding-context -->

# Onboarding Context — <JIRA-KEY>: <initiative title>

## 1. Target

| Market | Clearing(s) | Product(s) | Direction(s) | Epics in scope |
|---|---|---|---|---|

## 2. Baseline chosen
Baseline: **<market × clearing × product>** — chosen by matching clearing first, then product, then direction.
Alternatives considered: <list with one-line reason each>.
Evidence: `steps/02-route/radius.json`, `steps/03-load/normalized/trace-1.json`.

## 3. Platform footprint of the baseline (full scaffolding list)
<!-- From every manifest's onboarding_recipe, confirmed by describe against the baseline market. -->

| Service | Table / Region | Key pattern | Baseline rows | Target rows | Substitution rule | Status |
|---|---|---|---|---|---|---|
| | | | n | 0 | | TO_CREATE / EXISTS / SHARED |

Per-market code elements (from `onboarding_recipe.required_code`):

| Service | Element | Kind | Baseline implementation | Action |
|---|---|---|---|---|

## 4. Work packages
<!-- Epics grouped by lifecycle stage, then by service; max N epics each (config/thresholds.yaml onboarding). -->

| WP | Lifecycle stage | Services | Epics | Depends on | Suggested owner |
|---|---|---|---|---|---|
| WP-01 | SCAFFOLDING | all | — | — | |
| WP-02 | INGESTION | | | WP-01 | |

## 5. Invariants every work package must respect
- …

## 6. Shared decisions (append as slices progress)
| Date | Decision | By | Affects WPs |
|---|---|---|---|

## 7. How to pick up a slice
1. Create a slice run: `python scripts/new-run.py --jira <JIRA-KEY> --agent solution --parent <BASE_EXECUTION_ID> --work-package WP-nn`
2. Run `prompts/10-run-solution-agent.md` with the work package id; the agent loads this file first and skips steps already decided here.
