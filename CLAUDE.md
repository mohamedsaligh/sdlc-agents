# Claude Code entry point

All operating rules live in one place so that Copilot and Claude Code behave identically.

@AGENTS.md

Sub-agents for Claude Code are generated into `.claude/agents/` from the canonical
definitions in `agents/` by `python scripts/sync-agents.py`. Edit `agents/*.md`, never
the generated copies.
