<!-- templates/coverage-delta.md — produced by the Builder Agent from the build's coverage report
     (JaCoCo or equivalent). Audience: engineers, reviewers. Numbers come from report files; cite them. -->

<!-- paste templates/_header.md here with document: coverage-delta -->

# Coverage Delta — <JIRA-KEY>

Builder run: `<EXECUTION_ID>` · Branch: `feature/<JIRA-KEY>-<slug>`

## 1. Per service

| Service | Build | Tests run | Passed | Failed | Line cov. before | Line cov. after | Δ | Report |
|---|---|---|---|---|---|---|---|---|
| service-a | PASS | | | 0 | | | | `steps/07-artefacts/service-a.coverage.json` |

"Before" = baseline run performed by the Builder in step 03 on the base commit; "after" = step 06 on the feature branch. Numbers produced by `scripts/coverage-delta.py` from the two `coverage.xml` files.

## 2. Coverage of the changed lines only
<!-- This is the number that matters for the review: of the lines this change added or modified, how many are executed by tests? -->

| Service | Changed lines | Covered | % | Uncovered (path:lines) |
|---|---|---|---|---|

## 3. New and modified tests
| Service | Test | Covers AC | New / Modified |
|---|---|---|---|

## 4. Notes
- Flaky or skipped tests: <list or None>
- Tests the plan asked for but the Builder could not implement as specified: <list with reason or None>
