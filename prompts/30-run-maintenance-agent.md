# Prompt 30 — Run the Maintenance Agent (keep the map true)

**When**: a design doc changed · a service's code changed materially · after every 5–10 builder runs ·
on a schedule (weekly is a good start) · when a solution run's radius proved wrong.

**How to run**: select the **maintenance-agent** custom agent (Copilot) or ask Claude Code to use it, then paste the block.

---

Run the **maintenance-agent** exactly as defined in `agents/maintenance-agent.md` and `AGENTS.md`.

```
SCOPE:          <all | service-a,service-b | since:<git-ref or date>>
TRIGGER:        <DESIGN_DOC_CHANGED | CODE_CHANGED | SCHEDULED | RUN_FEEDBACK | MANUAL>
APPLY_PATCHES:  <blank = propose only | service-a.patch,service-c.patch from a previous run's outputs/manifest-diffs/>
```

Operating instructions for this run:
1. Start with `scripts/check-drift.py --json --out <run folder>/steps/00-start/drift.json` and `scripts/validate-manifests.py --json --out <run folder>/steps/00-start/validate.json`.
2. Work through steps 01 → 05. Print `STEP nn DONE — <detail>` after each.
3. Every proposed manifest change is a patch file under `outputs/manifest-diffs/`; show me the list with severity and one line of reason each.
4. If `APPLY_PATCHES` is set, apply exactly those patch files, then re-run the validator and show the result. Proposing and applying are always two separate invocations so a human reviews in between.
5. Never edit design docs or code; put those suggestions in the report as diffs.
6. Finish by printing: execution id · HIGH/MED/LOW counts · patches proposed/applied · radius accuracy summary (if runs were reviewed) · actions for humans.
