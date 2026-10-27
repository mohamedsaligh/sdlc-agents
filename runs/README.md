# runs/ — the audit trail

Every agent execution lives here: `runs/<JIRA-KEY>/<EXECUTION_ID>/`.
Created only by `python scripts/new-run.py`. Layout and `run.json` fields: `schema/run-record.schema.md`.

```
runs/PAY-1234/
  RUN-20261028-031200-PAY-1234/      # solution run
    run.json
    steps/00-input … 06-author/
    outputs/solution-proposal.md, confidence-report.md, implementation-plan.md | questions.md
    approval.json                     # written by BA + engineer
  RUN-20261029-091500-PAY-1234/      # builder run (parent_execution_id = the run above)
    run.json
    steps/00-gate … 09-close/
    outputs/coverage-delta.md, traceability-matrix.md, pr-summary.md, data-scripts/
runs/MAINT/RUN-…-MAINT/               # maintenance and triangulation runs
```

Commit run folders: they are the evidence. Raw tool responses (`steps/**/raw/`) are git-ignored by
default because they may hold more than the masked, normalized copies; keep them locally.
