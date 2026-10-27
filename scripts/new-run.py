#!/usr/bin/env python3
"""Create a run folder and run.json for an agent execution.

Usage:
  python scripts/new-run.py --jira PAY-1234 --agent solution
  python scripts/new-run.py --jira PAY-1234 --agent builder --parent RUN-20261028-031200-PAY-1234
  python scripts/new-run.py --jira PAY-1234 --agent solution --parent <BASE_ID> --work-package WP-03
  python scripts/new-run.py --hash runs/PAY-1234/<id>/outputs/implementation-plan.md

Prints EXECUTION_ID and RUN_DIR on separate lines (machine-readable), nothing else.
Standard library only, so it runs on any engineer's machine.
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import subprocess
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS = {"solution": "solution-agent", "builder": "builder-agent", "maintenance": "maintenance-agent"}
STEP_PLAN = {
    "solution": ["00-input", "01-classify", "02-route", "03-load", "04-analyse", "05-score", "06-author"],
    "builder": ["00-gate", "01-parse", "02-prepare", "03-baseline", "04-apply", "05-data", "06-test", "07-artefacts", "08-pr", "09-close"],
    "maintenance": ["00-start", "01-design", "02-code", "03-reality", "04-learn", "05-report"],
}


def git_short_sha():
    try:
        sha = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL).decode().strip()
        dirty = subprocess.check_output(["git", "status", "--porcelain"], cwd=REPO_ROOT, stderr=subprocess.DEVNULL).decode().strip()
        return sha + ("-dirty" if dirty else "")
    except Exception:
        return "unknown"


def count_manifests():
    d = os.path.join(REPO_ROOT, "manifests")
    if not os.path.isdir(d):
        return 0
    return len([f for f in os.listdir(d) if f.endswith((".yaml", ".yml")) and not f.startswith("_")])


def read_version(path, key):
    try:
        with open(os.path.join(REPO_ROOT, path), encoding="utf-8") as fh:
            for line in fh:
                m = re.match(rf"^{key}:\s*(\d+)", line)
                if m:
                    return int(m.group(1))
    except FileNotFoundError:
        pass
    return None


def sha256_file(path):
    """SHA-256 of the file with CR bytes removed, so Windows (CRLF) and Linux (LF) checkouts agree."""
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk.replace(b"\r", b""))
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jira", help="Jira key, e.g. PAY-1234 (use MAINT for maintenance runs)")
    ap.add_argument("--agent", choices=sorted(AGENTS), help="solution | builder | maintenance")
    ap.add_argument("--parent", default=None, help="parent EXECUTION_ID (builder -> solution run; slice -> base run)")
    ap.add_argument("--work-package", default=None, help="onboarding work package id, e.g. WP-03")
    ap.add_argument("--harness", default=os.environ.get("AGENT_HARNESS", "unknown"), help="copilot | claude-code")
    ap.add_argument("--hash", default=None, help="print SHA-256 of a file and exit")
    args = ap.parse_args()

    if args.hash:
        print(sha256_file(args.hash))
        return 0

    if not args.jira or not args.agent:
        ap.error("--jira and --agent are required (or use --hash FILE)")

    jira = args.jira.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9_]+-\d+|MAINT", jira):
        print(f"error: '{jira}' is not a Jira key like PAY-1234 (or MAINT)", file=sys.stderr)
        return 2

    for _attempt in range(3):  # two runs started in the same second get distinct ids
        now = dt.datetime.now(dt.timezone.utc)
        exec_id = f"RUN-{now.strftime('%Y%m%d-%H%M%S')}-{jira}"
        run_dir = os.path.join(REPO_ROOT, "runs", jira, exec_id)
        if not os.path.exists(run_dir):
            break
        time.sleep(1)
    else:
        print("error: run folder already exists, retry in a moment", file=sys.stderr)
        return 3

    os.makedirs(os.path.join(run_dir, "outputs"))
    for step in STEP_PLAN[args.agent]:
        os.makedirs(os.path.join(run_dir, "steps", step))

    record = {
        "execution_id": exec_id,
        "jira_key": jira,
        "agent": AGENTS[args.agent],
        "parent_execution_id": args.parent,
        "map_version": git_short_sha(),
        "manifest_count": count_manifests(),
        "vocabulary_version": read_version("schema/vocabulary.yaml", "vocabulary_version"),
        "contract_version": 1,
        "thresholds_version": read_version("config/thresholds.yaml", "thresholds_version"),
        "harness": args.harness,
        "model": None,
        "started_at": now.isoformat().replace("+00:00", "Z"),
        "updated_at": now.isoformat().replace("+00:00", "Z"),
        "status": "STARTED",
        "bucket": None,
        "work_package": args.work_package,
        "steps": [{"id": s, "status": "PENDING", "started_at": None, "ended_at": None, "outputs": []} for s in STEP_PLAN[args.agent]],
        "outputs": [],
        "scores": {"overall": None, "map": None, "code": None, "data": None, "model": None, "decision": None},
        "approvals_required": ["BA", "ENGINEER"] if args.agent == "solution" else [],
        "deviations": [] if args.agent == "builder" else None,
        "anomalies": [],
        "notes": "",
    }
    with open(os.path.join(run_dir, "run.json"), "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=2)

    print(exec_id)
    print(os.path.relpath(run_dir, REPO_ROOT).replace(os.sep, "/"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
