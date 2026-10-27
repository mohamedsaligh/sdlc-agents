<!-- templates/implementation-plan.md — TECHNICAL document. Audience: engineers, Builder Agent.
     Rules: the Builder executes this literally. Every file path relative to __CODE_ROOT__.
     Every diff anchored to located lines. Every data statement paired with rollback.
     Keep every heading. This file's SHA-256 is recorded at approval; do not edit after approval. -->

<!-- paste templates/_header.md here with document: implementation-plan -->

# Implementation Plan — <JIRA-KEY>: <Jira summary>

## 0. Builder contract
- Bucket: <bucket> · Work package: <WP-id or n/a> · Baseline: <market × clearing × product>
- Services in radius (in build order): `service-a`, `service-b`, …
- Branch name: `feature/<JIRA-KEY>-<short-slug>` (same name in every touched repo)
- Build per service: `<code.build from manifest>`
- Expected new/changed tests: <n> (listed in §4)
- Acceptance criteria covered: AC-1, AC-2 … (traceability in §7)

## 1. Change radius

| Service | Why in radius (manifest tag match / trace hop / dependency) | Change type | Files touched |
|---|---|---|---|
| | | CODE / CONFIG / DATA / TEST | <n> |

Services considered and excluded, with reason: …

## 2. Code changes
<!-- One subsection per file. Diff must apply with `git apply`. Keep hunks small. -->

### 2.1 `<service>/<path/to/File.java>`
Purpose: <one line>. Anchored at lines <a>–<b> (`steps/03-load/normalized/locate-<n>.json`).
Pattern copied from: `<baseline file>:<lines>` (if reused).

```diff
--- a/<service>/<path/to/File.java>
+++ b/<service>/<path/to/File.java>
@@ -41,6 +41,9 @@
 context lines
+added lines
```

## 3. Configuration and static data changes
<!-- Every statement has a rollback directly below. Values derived from describe output. Environment-agnostic;
     environment-specific values are parameters in ${...}. -->

### 3.1 `<TABLE_OR_REGION>` — <ADD | CHANGE | REMOVE> for <market>
Derived from baseline rows: `steps/03-load/normalized/describe-<n>.json#sources[ROUTING_RULE]`
Substitution rule applied: <from manifest onboarding_recipe.substitution_rules>

```sql
-- apply
INSERT INTO ROUTING_RULE (...) VALUES (...);
-- rollback
DELETE FROM ROUTING_RULE WHERE ...;
```

Cache invalidation required: <region name or None>. Ordering constraints: <e.g. CLEARING_CALENDAR before ROUTING_RULE>.

## 4. Tests
| Service | Test class / method | Type | Covers AC | New or Modified |
|---|---|---|---|---|

Minimum expectation: every new branch of logic has a unit test; every new static data row has at least one test or an assertion in an existing flow test.

## 5. Execution order for the Builder
1. `service-a`: apply §2.x, run build, must pass.
2. `service-b`: …
3. Data scripts §3 in order …
4. Re-run flow test (if any) …

## 6. Risks and rollback
| Risk | Likelihood | Mitigation | Rollback |
|---|---|---|---|

## 7. Traceability (requirement → plan section)
| AC / Epic | Plan sections | Services |
|---|---|---|
| AC-1 | §2.1, §3.1, §4 row 1 | service-a |

## 8. Out of scope / follow-ups
- …

## 9. Sources
- `steps/02-route/radius.json`, `steps/03-load/normalized/*.json`, `steps/04-analyse/analysis.md`
- Design docs: …
- Baseline files: …
