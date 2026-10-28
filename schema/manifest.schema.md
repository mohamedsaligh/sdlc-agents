# Service Manifest — schema and completeness rules

One manifest per service, at `manifests/<service>.yaml`. `<service>` must equal the service's folder
name under `__CODE_ROOT__`. The design doc is referenced by `design_doc`, a path relative to
`__DESIGN_DOCS_ROOT__` that is **either a single file** (`<service>.md`) **or a folder** (e.g.
`<id>-architecture/`, holding `service.yaml` and other files). When the design docs are folders whose names
do not equal the service name, the manifest's `design_doc` field is the join — keep it exact. That naming rule is what lets agents join the three
sources without a lookup table.

A manifest holds **shape, not data**. It answers "what does this service touch and serve"
so an agent can decide whether the service is inside a change radius and what to fetch.
It never contains configuration rows, secrets, hostnames or environment-specific values.

Target size: 40–120 lines. If a manifest grows past ~150 lines, it is holding data or prose
that belongs in the design doc.

---

## Fields

| Field | Type | Required | Meaning | Primary source |
|---|---|---|---|---|
| `service` | string | yes | Identifier, see naming rule above | folder name |
| `manifest_version` | int | yes | Schema version, currently `1` | fixed |
| `design_doc` | string | yes | Path relative to `__DESIGN_DOCS_ROOT__`: a file or a folder | — |
| `design_doc_sha256` | string | yes | `python scripts/new-run.py --hash <path>` of the design doc when last verified. For a folder it is the hash of every file inside, sorted, so any change in the folder is drift. `scripts/check-drift.py` compares it. | computed |
| `summary` | string | yes | One sentence, business language | design doc |
| `role` | enum | yes | One of `schema/vocabulary.yaml: roles` | design doc |
| `consumes[]` | list | yes | `{event, from[], channel}` — events/messages this service listens to | design doc, verified in code |
| `emits[]` | list | yes | `{event, to[], channel}` — events/messages it produces | design doc, verified in code |
| `hops.upstream[]` | list | yes | Services that typically precede it in a payment lifecycle | design doc, verified by `trace` |
| `hops.downstream[]` | list | yes | Services that typically follow it | design doc, verified by `trace` |
| `external_interfaces[]` | list | no | `{name, direction, protocol}` — upstream systems, clearing systems, cross-impact systems | design doc |
| `config.tables[]` | list | yes | Database tables read for behaviour (routing, mapping, limits, calendars…) | design doc, verified in code |
| `config.cache_regions[]` | list | yes | Cache regions read (write-through cache) | design doc, verified in code |
| `config.lookup_keys[]` | list | yes | Key patterns used to select rows, e.g. `market+clearing+product+direction` | design doc / `describe` |
| `code.repo` | string | yes | Folder name under `__CODE_ROOT__` (normally equals `service`) | folder |
| `code.key_packages[]` | list | yes | Packages where behaviour lives | code |
| `code.entrypoints[]` | list | yes | Listener / processor / handler class names that start work | code |
| `code.build` | string | yes | Build + test command from repo root, e.g. `mvn -q -DskipITs verify` | repo |
| `tags.markets[]` | list | yes | Markets live, vocabulary values only | `describe` / design doc |
| `tags.clearings[]` | list | yes | Clearing systems handled, vocabulary values only | design doc |
| `tags.products[]` | list | yes | Payment products handled, vocabulary values only | design doc |
| `tags.directions[]` | list | yes | `INWARD`, `OUTWARD`, or both | design doc |
| `tags.channels[]` | list | no | Inbound channels handled | design doc |
| `tags.lifecycle_stages[]` | list | yes | Stages this service implements, vocabulary values only | design doc |
| `tags.priorities[]` | list | no | Processing priorities / SLA classes handled | design doc |
| `onboarding_recipe.required_config[]` | list | yes | `{table_or_region, key_pattern, note}` — what must exist for a market to be live in this service | design doc + `describe` of a live market |
| `onboarding_recipe.required_code[]` | list | yes | `{element, kind, note}` — per-market code elements (mappers, validators, profiles) if any; `[]` if the service is fully config-driven | design doc + code |
| `onboarding_recipe.substitution_rules[]` | list | yes | How to derive new-market values from a baseline, e.g. `replace market code in key; recalculate cut-off calendar` | design doc |
| `invariants[]` | list | yes | Things that must stay true across markets (idempotency keys, ordering, SLA, amount limits) | design doc |
| `verification.sources[]` | list | yes | Which of `design`, `code`, `trace`, `describe` confirmed this manifest | prompts 01/02 |
| `verification.last_verified` | date | yes | ISO date | prompts 01/02 |
| `verification.open_gaps[]` | list | yes | Known disagreements not yet resolved; `[]` when clean | prompts 01/02 |

Vocabulary-controlled fields (`role`, `tags.*`) accept **only** values present in
`schema/vocabulary.yaml`. `scripts/validate-manifests.py` enforces this, and also checks that every
service named in `hops.*`, `consumes[].from` and `emits[].to` has a manifest (dangling names break routing).

Empty lists are allowed, with a reason in a comment, for: `tags.markets` (service not yet live anywhere),
`tags.clearings` and `tags.channels` (clearing/channel-agnostic service), `tags.priorities`,
`external_interfaces`, `onboarding_recipe.required_code`, `verification.open_gaps`.

---

## Completeness rules (what "done" means for a manifest)

A manifest is complete when all of the following hold. Prompt 01 produces it; prompt 02 proves it.

1. **Every required field present** and non-empty (lists may be `[]` only where the table above allows it, with a one-line `note` explaining why).
2. **Code agreement**: every `consumes[].event`, `emits[].event`, `config.tables[]`, `config.cache_regions[]` and `code.entrypoints[]` value appears in the service's source under `__CODE_ROOT__/<service>` (string search is sufficient). Anything named in the design doc but absent in code goes to `verification.open_gaps[]`, not into the field.
3. **Trace agreement**: for at least one real payment per product the service handles, the service appears in the `trace` hop list exactly where `hops.upstream/downstream` say it should. Mismatches go to `open_gaps[]`.
4. **Data agreement**: for at least one live market, `describe` returns rows for every `onboarding_recipe.required_config[]` entry. Entries that return nothing are either wrong or optional — decide, and record the decision.
5. **Join integrity**: `service` == folder name under `__CODE_ROOT__`; `design_doc` resolves to an existing file or folder under `__DESIGN_DOCS_ROOT__`.
6. **Validator passes**: `python scripts/validate-manifests.py` reports zero errors.

A manifest with `open_gaps[]` non-empty is still usable; the Solution Agent lowers the MAP lane
for any radius that includes it and lists the gaps in the Confidence Report.

---

## How agents use it

| Agent step | Fields read |
|---|---|
| Solution 01 classify | `tags.markets`, `tags.clearings`, `tags.products` (to detect "new combination") |
| Solution 02 route | all `tags.*`, `hops.*`, `consumes/emits` |
| Solution 03 load | `design_doc`, `config.*`, `code.*`, `onboarding_recipe.*` |
| Solution 05 score | `verification.*`, `hops.*` |
| Builder 02 prepare | `code.repo`, `code.build` |
| Maintenance | everything, plus `design_doc_sha256` |
