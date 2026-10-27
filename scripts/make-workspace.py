#!/usr/bin/env python3
"""Generate the multi-root VS Code workspace the agents need, and print the Claude Code equivalent.

Copilot and Claude Code can only read folders that are open. The agents need three roots:
this repo, CODE_ROOT (all service repos) and DESIGN_DOCS_ROOT (design markdowns).

  python scripts/make-workspace.py            # writes sdlc-agents.code-workspace next to this repo's root
  python scripts/make-workspace.py --print    # only print the claude command
Reads config/platform.env (after init-project). Standard library only.
"""
import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_env():
    env = {}
    with open(os.path.join(REPO_ROOT, "config", "platform.env"), encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--print", action="store_true", help="print commands only, do not write the workspace file")
    args = ap.parse_args()

    env = load_env()
    code_root, docs_root = env.get("CODE_ROOT", ""), env.get("DESIGN_DOCS_ROOT", "")
    if code_root.startswith("__") or docs_root.startswith("__"):
        print("config/platform.env still has placeholders; run scripts/init-project first", file=sys.stderr)
        return 1
    for label, p in (("CODE_ROOT", code_root), ("DESIGN_DOCS_ROOT", docs_root)):
        if not os.path.isdir(p):
            print(f"warning: {label} does not exist: {p}", file=sys.stderr)

    ws = {
        "folders": [
            {"name": "sdlc-agents (map + agents)", "path": "."},
            {"name": "services (CODE_ROOT)", "path": code_root},
            {"name": "design-docs (DESIGN_DOCS_ROOT)", "path": docs_root},
        ],
        "settings": {
            "files.exclude": {"**/__pycache__": True},
            "search.exclude": {"**/runs/**/raw/**": True},
        },
    }
    out = os.path.join(REPO_ROOT, "sdlc-agents.code-workspace")
    if not args.print:
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(ws, fh, indent=2)
        print(f"wrote {out}\n  VS Code: File > Open Workspace from File... > {os.path.basename(out)}")
    q = '"' if os.name == "nt" else "'"
    print("  Claude Code: run from this repo root:")
    print(f"    claude --add-dir {q}{code_root}{q} --add-dir {q}{docs_root}{q}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
