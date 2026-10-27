# GitHub Copilot entry point

All operating rules live in `AGENTS.md` at the repository root. Read it fully before
acting in this repository; it applies to every chat, agent and sub-agent.

Custom agents for VS Code are generated into `.github/agents/*.agent.md` from the
canonical definitions in `agents/` by `python scripts/sync-agents.py`. Edit `agents/*.md`,
never the generated copies.
