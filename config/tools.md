# MCP tool registry

Agents call tools by **capability**, then look up the concrete tool here. This file is
filled by `prompts/00-discover.md` from the tools actually visible in your Copilot /
Claude Code session. Keep it short and exact: tool name, required arguments, one example.

> Status: **NOT YET DISCOVERED** — run `prompts/00-discover.md`.
> While this line is present, agents must stop at the first tool call and ask for discovery.

## Capability → tool

| Capability | MCP server | Tool name | Required args | Read-only | Notes |
|---|---|---|---|---|---|
| `jira.get_issue`        | | | key | yes | returns issue + fields |
| `jira.get_children`     | | | key | yes | epics/stories under an initiative/epic; may be the same tool with a JQL arg |
| `jira.add_attachment`   | | | key, file | **no** | Builder step 08 only |
| `jira.add_comment`      | | | key, body | **no** | Builder step 08 only |
| `devctl.describe`       | | | service, market, environment | yes | see schema/devctl-contracts.md A.1 |
| `devctl.locate`         | | | symbol, kind | yes | A.2 — may fall back to repo search |
| `devctl.trace`          | | | market, clearing, product, direction, environment | yes | A.3 |
| `scm.create_pr`         | | | repo, branch, title, body | **no** | Builder step 08; if absent, print the PR body and stop |

## Environment names

| Alias used in prompts | Real environment name | Allowed for describe | Allowed for trace |
|---|---|---|---|
| DEV  | | | |
| UAT  | | | |
| PROD | | read-only | read-only |

## Example calls (copied from a real session, arguments masked where needed)

_(empty)_
