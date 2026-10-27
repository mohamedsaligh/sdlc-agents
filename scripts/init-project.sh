#!/usr/bin/env bash
# One-time initialisation for Mac/Linux/Git-Bash: replaces every __TOKEN__ with your values.
# Usage:
#   bash scripts/init-project.sh                                  # interactive for unset tokens
#   bash scripts/init-project.sh --set PLATFORM_NAME=PayCore --set DEVCTL=pctl \
#        --set AI_PLATFORM=Atlas --set CODE_ROOT=/work/paycore --set DESIGN_DOCS_ROOT=/work/design-docs
# Delegates to scripts/init-project.py (standard library only). On Windows prefer scripts/init-project.ps1.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="$(command -v python3 || command -v python || true)"
if [[ -z "$PY" ]]; then
  echo "python3 not found. On Windows use: powershell -ExecutionPolicy Bypass -File scripts\\init-project.ps1" >&2
  exit 1
fi
exec "$PY" "$HERE/init-project.py" "$@"
