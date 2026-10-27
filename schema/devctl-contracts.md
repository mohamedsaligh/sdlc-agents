# `__DEVCTL__` contracts — raw in, normalized out

`__DEVCTL__` is reached through MCP and returns JSON whose exact shape is specific to your
environment. Agents never reason over the raw shape. Step 03 (load) converts every response
into the **normalized** shapes below and saves both files:

```
steps/03-load/raw/<capability>-<n>.json          # untouched tool response
steps/03-load/normalized/<capability>-<n>.json   # shape defined here
```

All later steps read only `normalized/`. This is what makes the agents portable when the
tool changes, and what lets a reviewer check a result without knowing the tool.

`prompts/00-discover.md` fills in **Section B (raw → normalized mapping)** once, from real
responses. Until Section B is filled, agents must stop and ask for discovery to be run.

---

## A. Normalized shapes (fixed — do not change without bumping `contract_version`)

### A.1 `describe` — static data a service reads for a market

Question it answers: *"What configuration does service S actually have for market M
(optionally clearing C, product P) in environment E?"*

```json
{
  "contract_version": 1,
  "capability": "describe",
  "query": { "service": "payment-router", "market": "MKT_A", "clearing": "CLR_HV_A", "product": "HVP", "environment": "UAT" },
  "executed_at": "2026-10-28T03:12:44Z",
  "sources": [
    {
      "kind": "table | cache_region",
      "name": "ROUTING_RULE",
      "key_pattern": "market+clearing+product+direction",
      "row_count": 3,
      "rows": [ { "<column>": "<value>" } ],
      "truncated": false
    }
  ],
  "missing": [ "PRIORITY_LANE" ],
  "notes": "free text from the tool, if any"
}
```

Rules: `sources[]` must contain one entry for every `config.tables[]` and
`config.cache_regions[]` named in the service's manifest — with `row_count: 0` and
`rows: []` when nothing exists for that market. Names the tool did not return at all go
to `missing[]`. `rows[]` is **projected and masked per section C** before saving: `row_count` is always the full count, but a row carries only the lookup-key columns plus behaviour columns, never customer, account or credential data. In lean mode (onboarding base pass) `rows` may be omitted entirely.

### A.2 `locate` — find code elements

Question it answers: *"Where in the code is X?"* where X is a class, mapper, processor,
table name, event name, property key, or free-text symbol.

```json
{
  "contract_version": 1,
  "capability": "locate",
  "query": { "symbol": "RouteDecisionProcessor", "kind": "class | mapper | table | event | property | text", "services": ["payment-router"] },
  "executed_at": "2026-10-28T03:13:01Z",
  "matches": [
    {
      "service": "payment-router",
      "path": "payment-router/src/main/java/com/example/router/rules/RouteDecisionProcessor.java",
      "line_start": 41,
      "line_end": 118,
      "kind": "class",
      "snippet": "public class RouteDecisionProcessor { ... }"
    }
  ],
  "match_count": 1,
  "truncated": false
}
```

Rules: `path` is relative to `__CODE_ROOT__`. If `__DEVCTL__` has no locate capability,
step 03 produces this same shape from a repository text search and sets
`"query.kind": "text"` with `"tool": "grep"` added under `query`.

### A.3 `trace` — walk one real payment

Question it answers: *"Which services, in which order, touched payment X (or the most
recent payment matching product P, market M, clearing C)?"*

```json
{
  "contract_version": 1,
  "capability": "trace",
  "query": { "payment_ref": null, "market": "MKT_A", "clearing": "CLR_HV_A", "product": "HVP", "direction": "OUTWARD", "environment": "PROD", "lookback": "7d" },
  "executed_at": "2026-10-28T03:14:20Z",
  "payment_ref": "<masked or hashed reference>",
  "hops": [
    { "seq": 1, "service": "channel-adapter",   "event_in": null,                "event_out": "payment.received",  "at": "…", "status": "OK" },
    { "seq": 2, "service": "payment-validator", "event_in": "payment.received", "event_out": "payment.validated", "at": "…", "status": "OK" },
    { "seq": 3, "service": "payment-router",    "event_in": "payment.validated","event_out": "payment.routed",    "at": "…", "status": "OK" }
  ],
  "parallel_groups": [ [4, 5] ],
  "end_state": "SETTLED",
  "duration_ms": 1830,
  "source": "splunk | event-store | other"
}
```

Rules: `hops[].service` values must be manifest `service` identifiers (map log component
names to service names in Section B). Payment references and customer data are masked.

---

## B. Raw → normalized mapping  (FILLED BY `prompts/00-discover.md`)

> Status: **NOT YET DISCOVERED**. Run prompt 00. Agents must refuse to proceed past
> step 03 while this status line is present. **Prompt 00 Task 7 deletes this status line** once B.1–B.3 are filled.

For each capability, discovery records:

1. **MCP tool name(s)** actually exposed, and the argument names (also copied to `config/tools.md`).
2. **One real raw response** (masked) saved at `docs/discovery/<capability>.raw.example.json`.
3. **Field mapping table** raw path → normalized path, including any value translations
   (log component name → service name; environment aliases; date formats).
4. **Limits**: page size, truncation flag, rate limits, environments allowed.
5. **Gaps**: anything in the normalized shape the tool cannot supply, and the agreed workaround.

### B.1 describe
_(empty)_

### B.2 locate
_(empty)_

### B.3 trace
_(empty)_

---

## C. Masking and projection rules (deterministic — not left to judgement)

Normalized files are committed to git; raw files are not. Before writing any normalized file:

1. **Project rows** to: every column named in the manifest's `config.lookup_keys[]` patterns, plus columns whose names indicate behaviour (`*_FLAG`, `*_CODE`, `*_TYPE`, `*_RULE`, `*_LIMIT`, `*_PRIORITY`, `*_CUTOFF`, `*_CALENDAR`, `STATUS`, `ENABLED`, `ACTIVE`). Every other column is dropped from the row (not masked — dropped) and its name listed once in `sources[].dropped_columns[]`.
2. **Mask** any kept value whose column name matches, case-insensitively, `.*(PASS|PWD|SECRET|TOKEN|KEY_MATERIAL|CERT|PRIVATE|IBAN|ACCOUNT_NO|ACCT|BIC_OWNER|NAME|ADDRESS|PHONE|EMAIL|TAX_ID|NATIONAL_ID).*` → `"***"`. Host names, URLs and ports are masked to their last path segment or `"***"`.
3. **Trace**: `payment_ref` is replaced by its first 4 characters + `…` + SHA-256 first 8 hex; amounts are rounded to 2 significant figures; counterparties are dropped.
4. **Locate**: snippets are at most 20 lines and must not include string literals longer than 40 characters (replace with `"…"`).
5. **Jira**: `jira.md` keeps summary, description, acceptance criteria, routing fields; attachments and people fields (reporter, assignee, watchers) are reduced to display names only.
6. If a column cannot be classified, drop it and record it in `dropped_columns[]`; dropping is always the safe default.

Discovery (prompt 00) may **extend** the regex in rule 2 with firm-specific column names; it may never shorten it.
