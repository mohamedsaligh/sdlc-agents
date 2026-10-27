#!/usr/bin/env python3
"""Compute coverage before/after and changed-line coverage from two JaCoCo XML reports and git diff.

  python scripts/coverage-delta.py --service payment-router --repo /path/CODE_ROOT/payment-router \
      --before runs/.../steps/03-baseline/payment-router/coverage.xml \
      --after  runs/.../steps/06-test/payment-router/coverage.xml \
      --base <base commit sha> [--out runs/.../steps/07-artefacts/payment-router.coverage.json]

Output JSON:
{
  "service": "...", "before": {"lines_total", "lines_covered", "line_pct"}, "after": {...}, "delta_pct": 1.2,
  "changed": {"lines": 57, "covered": 51, "pct": 89.5, "uncovered": ["src/main/java/.../File.java:44", ...]},
  "files_changed": [...], "notes": [...]
}
Standard library only. JaCoCo XML must be generated with source file info (default for jacoco-maven-plugin report goal).
"""
import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET


def parse_jacoco(path):
    """Return ({'<package>/<sourcefilename>': {line_nr: covered_bool}}, totals)."""
    tree = ET.parse(path)
    root = tree.getroot()
    files = {}
    total = covered = 0
    for pkg in root.iter("package"):
        pname = pkg.get("name", "")
        for sf in pkg.findall("sourcefile"):
            key = f"{pname}/{sf.get('name')}" if pname else sf.get("name")
            lines = {}
            for ln in sf.findall("line"):
                nr = int(ln.get("nr"))
                ci = int(ln.get("ci", "0"))
                lines[nr] = ci > 0
            files[key] = lines
    for counter in root.findall("counter"):
        if counter.get("type") == "LINE":
            covered = int(counter.get("covered", "0"))
            total = covered + int(counter.get("missed", "0"))
    if total == 0:  # fall back to summing source files
        for lines in files.values():
            total += len(lines)
            covered += sum(1 for v in lines.values() if v)
    pct = round(100.0 * covered / total, 2) if total else 0.0
    return files, {"lines_total": total, "lines_covered": covered, "line_pct": pct}


def changed_lines(repo, base):
    """{repo-relative path: set(added/modified line numbers in the new version)} from git diff -U0."""
    out = subprocess.check_output(["git", "diff", "-U0", base, "--", "."], cwd=repo).decode("utf-8", "replace")
    result, current = {}, None
    for line in out.splitlines():
        if line.startswith("+++ b/"):
            current = line[6:]
            result.setdefault(current, set())
        elif line.startswith("@@") and current:
            m = re.search(r"\+(\d+)(?:,(\d+))?", line)
            if m:
                start = int(m.group(1))
                count = int(m.group(2)) if m.group(2) is not None else 1
                result[current].update(range(start, start + count))
    return {k: v for k, v in result.items() if v}


def match_source(path, jacoco_files):
    """Map a repo path like src/main/java/com/x/Foo.java to the jacoco key com/x/Foo.java."""
    for key in jacoco_files:
        if path.endswith(key):
            return key
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--service", required=True)
    ap.add_argument("--repo", required=True, help="path to the service repository")
    ap.add_argument("--before", required=True, help="baseline jacoco.xml")
    ap.add_argument("--after", required=True, help="feature-branch jacoco.xml")
    ap.add_argument("--base", required=True, help="base commit the feature branch was cut from")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    notes = []
    _, before_tot = parse_jacoco(args.before)
    after_files, after_tot = parse_jacoco(args.after)
    diff = changed_lines(args.repo, args.base)

    ch_total = ch_cov = 0
    uncovered = []
    for path, nrs in sorted(diff.items()):
        if not path.endswith(".java") or "/src/test/" in path or path.startswith("src/test/"):
            continue  # only production code counts toward changed-line coverage
        key = match_source(path, after_files)
        if key is None:
            notes.append(f"{path}: not present in coverage report (no executable lines, or report lacks source info)")
            continue
        lines = after_files[key]
        for nr in sorted(nrs):
            if nr in lines:  # only lines JaCoCo considers executable
                ch_total += 1
                if lines[nr]:
                    ch_cov += 1
                else:
                    uncovered.append(f"{path}:{nr}")
    ch_pct = round(100.0 * ch_cov / ch_total, 2) if ch_total else None
    if ch_total == 0:
        notes.append("no executable changed production lines found; check --base and that the report has source info")

    result = {
        "service": args.service,
        "base_commit": args.base,
        "before": before_tot,
        "after": after_tot,
        "delta_pct": round(after_tot["line_pct"] - before_tot["line_pct"], 2),
        "changed": {"lines": ch_total, "covered": ch_cov, "pct": ch_pct, "uncovered": uncovered},
        "files_changed": sorted(diff.keys()),
        "notes": notes,
    }
    text = json.dumps(result, indent=2)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"wrote {args.out}: changed-line coverage {ch_pct}% ({ch_cov}/{ch_total}), total {before_tot['line_pct']}% -> {after_tot['line_pct']}%")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
