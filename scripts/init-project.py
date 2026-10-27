#!/usr/bin/env python3
"""Cross-platform core of the one-time initialisation (used by init-project.cmd and init-project.sh).

Replaces every __TOKEN__ in file CONTENTS (text files) and in file/folder NAMES (path values are
sanitised to a safe name segment). Skips .git/, runs/, and the init scripts themselves.

  python scripts/init-project.py                       # interactive for any token still unset in config/platform.env
  python scripts/init-project.py --set PLATFORM_NAME=PayCore --set DEVCTL=pctl ... [--force] [--dry-run]
  python scripts/init-project.py --verify              # after init: exit 1 if any __TOKEN__ pattern remains
Standard library only.
"""
import argparse
import datetime as dt
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_FILE = os.path.join(REPO_ROOT, "config", "platform.env")
MARKER = os.path.join(REPO_ROOT, "config", ".initialized")
TOKENS = ["PLATFORM_NAME", "DEVCTL", "AI_PLATFORM", "CODE_ROOT", "DESIGN_DOCS_ROOT"]
TEXT_EXT = {".md", ".yaml", ".yml", ".json", ".env", ".txt", ".html", ".py", ".sh", ".cmd", ".sql", ".yml", ".gitignore", ".gitattributes"}
SKIP_DIRS = {".git", "runs", "node_modules", "__pycache__"}
SKIP_FILES = {"init-project.cmd", "init-project.sh", "init-project.py"}


def iter_text_files():
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            ext = os.path.splitext(name)[1].lower()
            if name in SKIP_FILES or (ext not in TEXT_EXT and name != ".gitignore"):
                continue
            yield os.path.join(dirpath, name)


def iter_named_paths():
    """Every file and folder path (deepest first) outside the skip dirs — for renaming."""
    for dirpath, dirnames, filenames in os.walk(REPO_ROOT, topdown=False):
        rel_top = os.path.relpath(dirpath, REPO_ROOT).split(os.sep)[0]
        if rel_top in SKIP_DIRS:
            continue
        for name in filenames:
            if name not in SKIP_FILES:
                yield os.path.join(dirpath, name)
        for name in dirnames:
            if name not in SKIP_DIRS:
                yield os.path.join(dirpath, name)


def rename_paths(values):
    """Rename files/folders whose NAME contains a token. Path separators in values are not allowed in names."""
    renamed = 0
    for path in list(iter_named_paths()):
        base = os.path.basename(path)
        new_base = base
        for t in TOKENS:
            if f"__{t}__" in new_base:
                safe = re.sub(r"[\\/:*?\"<>|]+", "-", values[t])  # a path value cannot become a file name verbatim
                new_base = new_base.replace(f"__{t}__", safe)
        if new_base != base:
            target = os.path.join(os.path.dirname(path), new_base)
            if os.path.exists(target):
                print(f"  SKIP rename (target exists): {os.path.relpath(path, REPO_ROOT)} -> {new_base}")
                continue
            os.rename(path, target)
            renamed += 1
            print(f"  renamed {os.path.relpath(path, REPO_ROOT)} -> {new_base}")
    return renamed


def verify():
    """This script is excluded from replacement, so it can safely search for the exact tokens."""
    pattern = re.compile("|".join(f"__{t}__" for t in TOKENS))
    offenders = []
    for path in iter_text_files():
        try:
            text = open(path, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        hits = sorted(set(pattern.findall(text)))
        if hits:
            offenders.append((os.path.relpath(path, REPO_ROOT), hits))
    named = [os.path.relpath(p, REPO_ROOT) for p in iter_named_paths() if pattern.search(os.path.basename(p))]
    if offenders or named:
        if offenders:
            print("Unreplaced placeholders found in file contents:")
            for rel, hits in offenders:
                print(f"  {rel}: {', '.join(hits)}")
        if named:
            print("Unreplaced placeholders found in file/folder NAMES:")
            for rel in named:
                print(f"  {rel}")
        return 1
    print("OK: no unreplaced placeholders in contents or names.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--set", action="append", default=[], help="TOKEN=value")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true", help="report files that still contain an unreplaced __TOKEN__ and exit 1 if any")
    args = ap.parse_args()

    if args.verify:
        return verify()

    if os.path.exists(MARKER) and not args.force:
        print(f"Already initialised ({os.path.relpath(MARKER, REPO_ROOT)}). Use --force to re-run.")
        return 0

    values = {}
    with open(ENV_FILE, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                values[k.strip()] = v.strip()
    for item in args.set:
        k, _, v = item.partition("=")
        values[k.strip()] = v.strip()
    for t in TOKENS:
        while not values.get(t) or values[t] == f"__{t}__":
            values[t] = input(f"Value for {t}: ").strip()
    for p in ("CODE_ROOT", "DESIGN_DOCS_ROOT"):
        if not os.path.isdir(values[p]):
            print(f"warning: {p} path does not exist yet: {values[p]} (continuing)")

    print("Values:")
    for t in TOKENS:
        print(f"  {t:<18} = {values[t]}")
    if args.dry_run:
        print("--dry-run: no files changed.")
        return 0

    changed = 0
    for path in iter_text_files():
        try:
            text = open(path, encoding="utf-8").read()
        except UnicodeDecodeError:
            continue
        new = text
        for t in TOKENS:
            new = new.replace(f"__{t}__", values[t])
        if new != text:
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(new)
            changed += 1
            print("  updated", os.path.relpath(path, REPO_ROOT))

    renamed = rename_paths(values)

    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(MARKER, "w", encoding="utf-8") as fh:
        fh.write(f"initialized_at={stamp}\n")
        for t in TOKENS:
            fh.write(f"{t}={values[t]}\n")
    print(f"Done. {changed} file(s) updated, {renamed} file/folder name(s) renamed. Marker written: config/.initialized")
    print("Next: python scripts/sync-agents.py  then open prompts/00-discover.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
