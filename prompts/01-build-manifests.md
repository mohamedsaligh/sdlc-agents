# Prompt 01 — Build the service manifests (run in batches of 4–6 services)

**How to run**: paste below the line into Copilot / Claude Code with this repo open. Replace
`<SERVICES>` with 4–6 service names per session (context stays small and review stays easy).
Repeat until every design doc has a manifest. Then run prompt 02.

**Pre-conditions**: prompt 00 completed; `docs/discovery/design-doc-map.md` exists;
`schema/vocabulary.yaml` populated; `docs/discovery/discovery-report.md` Readiness section clear.

---

Read `AGENTS.md`, `schema/manifest.schema.md`, `schema/manifest.template.yaml`,
`schema/manifest.example.yaml`, `schema/vocabulary.yaml`, and `docs/discovery/design-doc-map.md`.

Build one manifest for each of these services, one at a time, in this order: `<SERVICES>`.

For **each** service do all seven steps before moving to the next:

1. **Read the design doc** `__DESIGN_DOCS_ROOT__/<service>.md` fully. Using `design-doc-map.md`, extract a first draft of every manifest field. Keep the service's own identifiers verbatim (event names, table names, class names). Business tags must be vocabulary values; if the doc uses a synonym, map it and note the mapping in a comment.
2. **Verify against code.** For every value in `consumes[].event`, `emits[].event`, `config.tables[]`, `config.cache_regions[]`, `code.entrypoints[]`: search `__CODE_ROOT__/<service>` for the literal string. Keep values that are found. Values not found go to `verification.open_gaps[]` as `"<field>: '<value>' in design doc, not found in code"`. Also scan the key packages for listener/topic/table identifiers present in code but absent in the doc; add them to the manifest with a comment `# from code` and list them in `open_gaps[]` as `"<value> in code, not in design doc"` so the doc can be updated later.
3. **Build command.** Find how the repo builds and runs unit tests (pom.xml / build.gradle / Makefile / README). Write the exact command into `code.build`. If coverage needs a flag or profile, include it.
4. **Onboarding recipe.** From the doc and the code, list what must exist for a market to be live in this service: config rows (table/region + key pattern + what they control) and per-market code elements. Write substitution rules as instructions a junior engineer could follow. If the service is market-agnostic, say so in `required_config[0].note` and keep `required_code: []`.
5. **Invariants.** Capture the rules that must hold across all markets (idempotency, ordering, SLA, limits, cut-offs). Prefer the doc's wording.
6. **Hashes and verification.** Compute SHA-256 of the design doc file (`python scripts/new-run.py --hash "<path>"`) into `design_doc_sha256`. Set `verification.sources` to `[design, code]`, `last_verified` to today, and `open_gaps` as collected. Do not claim `trace` or `describe` yet — prompt 02 adds those.
7. **Validate.** Save as `manifests/<service>.yaml`, run `python scripts/validate-manifests.py`, and fix every error. Warnings are acceptable only if explained in a comment in the manifest.

After the batch, print a table: service · lines · open_gaps count · validator status · anything you need me to confirm.

Rules
- Shape only. Never copy rows, hostnames, credentials or environment values into a manifest.
- Never fill a field from imagination to pass validation; use `open_gaps[]`.
- If a design doc is missing or clearly out of date, stop that service, write `docs/discovery/doc-issues.md` with what is wrong, and continue with the next service.
