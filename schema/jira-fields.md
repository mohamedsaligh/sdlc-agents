# Jira fields the agents expect

The Jira issue is the only input a business analyst writes. Everything else is derived.
To make routing a **lookup instead of a guess**, four small fields are required on the
top-level issue (Epic or Initiative). Values must come from `schema/vocabulary.yaml`.

## Required custom fields (dropdowns, single or multi select)

| Field    | Vocabulary list | Multi-select | Example |
|----------|-----------------|--------------|---------|
| Market   | `markets`       | yes          | `MKT_A` |
| Clearing | `clearings`     | yes          | `CLR_HV_A` |
| Product  | `products`      | yes          | `HVP` |
| Direction| `directions`    | yes          | `OUTWARD` |

Optional but helpful:

| Field            | Vocabulary list    | Note |
|------------------|--------------------|------|
| Channel          | `channels`         | when the entry channel is known |
| Lifecycle Stage  | `lifecycle_stages` | when the BA knows where the change sits |
| Baseline Market  | `markets`          | for onboarding, the market to copy from (agent proposes one if empty) |

## Standard fields the agent also reads

- Summary, Description, Acceptance Criteria (field or a clearly headed section in Description)
- Issue type and hierarchy: Initiative → Epic → Story. The agent fetches **all children** of the key it is given.
- Labels and Components are read but never trusted over the four required fields.

## Readiness rule

If any of the four required fields is empty on the top-level issue and cannot be
inferred unambiguously from the title or acceptance criteria, the Solution Agent stops
at step 01 and writes `questions.md` addressed to the BA. This is intentional: a
requirement that cannot name its market, clearing, product and direction is not ready
for engineering.

## Fallback when custom fields do not exist yet

Until the Jira admin creates the fields, the BA can put a fenced block at the top of the
Description. The agent parses this block with the same strictness:

```
agent-fields:
  market: [MKT_A]
  clearing: [CLR_HV_A]
  product: [HVP]
  direction: [OUTWARD]
  baseline_market: [MKT_B]
```
