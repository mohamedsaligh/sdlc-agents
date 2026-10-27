# Prompt 02 — Triangulate the map against reality (run once per product, then as needed)

**Purpose**: prove the manifests are complete by walking real payments. This is the phase-1 exit test.
A manifest set that passes this is good enough to route Jiras.

**How to run**: paste below the line. Replace `<MARKET>` with a live baseline market and
`<PRODUCTS>` with the products to prove (start with the most common one; add RTP and a batch product
later). Allowed environments per `config/tools.md`.

**Pre-conditions**: every design doc has a manifest; `python scripts/validate-manifests.py` passes;
`python scripts/check-drift.py` has no HIGH finding except unverified hashes.

---

Read `AGENTS.md`, `schema/devctl-contracts.md` and all `manifests/*.yaml`.

Create a run folder: `python scripts/new-run.py --jira MAINT --agent maintenance` and work inside it.

For each product in `<PRODUCTS>`, for market `<MARKET>`:

### A. Trace one real payment
1. Call `__DEVCTL__` trace (read-only) for market `<MARKET>`, the product, direction OUTWARD (then INWARD if the product has it). Save raw to `steps/03-reality/raw/trace-<product>-<direction>.json` and normalized (contract A.3) to `steps/03-reality/normalized/`.
2. Translate component names to service identifiers with the table in `schema/devctl-contracts.md` B.3. Any component without a translation: stop and ask me; do not guess.

### B. Compare hops to manifests
For every consecutive pair of hops (S1 → S2):
- `S1` manifest `hops.downstream` must contain `S2`, and `S2` manifest `hops.upstream` must contain `S1`.
- The event between them (if the trace shows it) must appear in `S1.emits[]` and `S2.consumes[]`.
- Parallel groups must be reflected as multiple downstream entries of the fan-out service.
Record each check as PASS/FAIL with the evidence in `steps/03-reality/hop-check-<product>.md`.

### C. Describe the baseline for each traced service
For each service on the path: call describe for `<MARKET>` (lowest allowed environment). For each `onboarding_recipe.required_config[]` entry, confirm rows exist. Record PASS (rows found), EMPTY (zero rows — either optional or wrong), MISSING (table/region not returned at all). Save normalized files.

### D. Fix the manifests
For every FAIL / EMPTY / MISSING: decide with evidence whether the manifest or the design doc is wrong.
- Manifest wrong → fix the manifest field directly.
- Design doc wrong or incomplete → fix the manifest, and add a line to `docs/discovery/doc-issues.md` for the doc owner.
- Cannot decide → add to `verification.open_gaps[]` with both observations.
Then update `verification.sources` (add `trace`, and `describe` where it ran), `last_verified`, and re-run `python scripts/validate-manifests.py`.

### E. Report
Write `outputs/maintenance-report.md` (template `templates/maintenance-report.md`) with trigger `MANUAL`,
listing: traced paths (as a simple `A → B → C` line per product/direction), checks passed/failed,
manifests changed, open gaps remaining. Finish with a one-line verdict per product:
`READY` (all hop checks pass, no MISSING) or `NOT READY` with the blocking items.

Rules: read-only tools only; mask payment references; never "fix" a manifest to make a check pass
without evidence — a recorded gap is more valuable than a false pass.
