<!-- templates/confidence-report.md — EVIDENCE document. Audience: engineering lead, BA.
     Rules: every number has evidence; no evidence => null + reason. Rubric: config/thresholds.yaml.
     Keep every heading. -->

<!-- paste templates/_header.md here with document: confidence-report -->

# Confidence Report — <JIRA-KEY>

## 1. Decision

| Overall | MAP | CODE | DATA | MODEL | Gate | Decision |
|---|---|---|---|---|---|---|
| <n> | <n> | <n> | <n> | <n> | ≥70 overall and ≥50 every lane | **PROCEED** / **QUESTIONS** |

Weights: MAP 0.30 · CODE 0.30 · DATA 0.25 · MODEL 0.15 (`config/thresholds.yaml` v<thresholds_version>)

## 2. Lane detail

### 2.1 MAP — do the map, the design docs and reality agree on the radius?
Start 100.

| Deduction | Rule (thresholds.yaml) | Evidence |
|---|---|---|
| −<n> | <rule text> | `<file>:<field or line>` |

**Score: <n>**
Radius considered: <service list> (`steps/02-route/radius.json`). Trace used: `steps/03-load/normalized/trace-<n>.json`.

### 2.2 CODE — was everything named actually found?
Start 100.

| Deduction | Rule | Evidence |
|---|---|---|

**Score: <n>**
Located elements: <k> of <m> (`steps/03-load/normalized/locate-*.json`). Unlocated: <list or None>.

### 2.3 DATA — did `describe` prove the baseline and show the gap?
Start 100.

| Deduction | Rule | Evidence |
|---|---|---|

**Score: <n>**
Baseline market: <X>, environment <E> (`steps/03-load/normalized/describe-<n>.json`). Target market run: <yes/no>.

### 2.4 MODEL — how clear is the requirement and how close is the pattern?
Start 100.

| Deduction | Rule | Evidence |
|---|---|---|

**Score: <n>**

## 3. Per-epic / per-work-package scores
<!-- One row per epic (or per work package for onboarding). Same four lanes. Mark anything below 50. -->

| Epic / WP | Title | MAP | CODE | DATA | MODEL | Overall | Note |
|---|---|---|---|---|---|---|---|

## 4. Contradictions found
<!-- Jira vs design doc vs code vs data. If none, write "None". -->
| # | Source A says | Source B says | Resolution (or: unresolved → question) |
|---|---|---|---|

## 5. Manifest health in the radius
| Service | verification.sources | open_gaps | last_verified |
|---|---|---|---|

## 6. What would raise the score
<!-- Concrete, actionable. E.g. "run describe for target market in UAT", "BA to confirm cut-off rule". -->
- …
