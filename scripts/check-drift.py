#!/usr/bin/env python3
"""Drift check between design docs, manifests and code folders.

Reports:
  - design docs without a manifest, manifests without a design doc
  - service folders under CODE_ROOT without a manifest, manifests without a folder
  - manifests whose design_doc_sha256 no longer matches the design doc — a file or a folder (doc changed, manifest not re-verified)

  python scripts/check-drift.py            # human output; exit 1 if any HIGH finding
  python scripts/check-drift.py --json     # for the maintenance agent
Reads CODE_ROOT and DESIGN_DOCS_ROOT from config/platform.env (after init-project has run).
Standard library only (manifest sha field is read with a regex, no YAML dependency).
"""
import argparse
import hashlib
import json
import os
import re
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


def sha256_path(path):
    """SHA-256 of a file (CR bytes removed) or of a FOLDER: every file under it, sorted by relative
    path, hashed as '<relpath>\n<content-hash>\n'. Identical on Windows and Linux."""
    h = hashlib.sha256()
    if os.path.isdir(path):
        for dirpath, dirnames, filenames in os.walk(path):
            dirnames[:] = sorted(d for d in dirnames if not d.startswith("."))
            for name in sorted(filenames):
                fp = os.path.join(dirpath, name)
                rel = os.path.relpath(fp, path).replace(os.sep, "/")
                h.update(f"{rel}\n{_sha256_file(fp)}\n".encode())
        return h.hexdigest()
    return _sha256_file(path)


def _sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(65536), b""):
            h.update(chunk.replace(b"\r", b""))
    return h.hexdigest()


def manifest_fields(path):
    text = open(path, encoding="utf-8").read()
    doc = re.search(r"^design_doc:\s*(\S+)", text, re.M)
    sha = re.search(r"^design_doc_sha256:\s*([0-9a-fA-F]{64})", text, re.M)
    return (doc.group(1) if doc else None), (sha.group(1).lower() if sha else None)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default=None, help="write the report to this file (UTF-8) instead of stdout; avoids PowerShell UTF-16 redirection")
    args = ap.parse_args()

    env = load_env()
    code_root = env.get("CODE_ROOT", "")
    docs_root = env.get("DESIGN_DOCS_ROOT", "")
    findings = []

    if code_root.startswith("__") or docs_root.startswith("__"):
        findings.append({"severity": "HIGH", "kind": "NOT_INITIALIZED", "detail": "config/platform.env still has placeholders; run scripts/init-project"})

    mdir = os.path.join(REPO_ROOT, "manifests")
    manifests = {os.path.splitext(f)[0]: os.path.join(mdir, f) for f in os.listdir(mdir) if f.endswith((".yaml", ".yml")) and not f.startswith("_")} if os.path.isdir(mdir) else {}

    docs = {}
    if os.path.isdir(docs_root):
        # a design doc is either <stem>.md or a folder <stem>/ (any layout inside)
        docs = {}
        for f in os.listdir(docs_root):
            fp = os.path.join(docs_root, f)
            if f.startswith((".", "_", "README")):
                continue
            if os.path.isdir(fp) or f.endswith(".md"):
                docs[os.path.splitext(f)[0] if not os.path.isdir(fp) else f] = fp
    else:
        findings.append({"severity": "HIGH", "kind": "DESIGN_DOCS_ROOT_MISSING", "detail": docs_root})

    folders = {}
    if os.path.isdir(code_root):
        folders = {d: os.path.join(code_root, d) for d in os.listdir(code_root) if os.path.isdir(os.path.join(code_root, d)) and not d.startswith(".")}
    else:
        findings.append({"severity": "HIGH", "kind": "CODE_ROOT_MISSING", "detail": code_root})

    # join docs <-> manifests through the manifest's design_doc field (folder names need not equal service names)
    referenced = {}
    for s, mpath in manifests.items():
        doc_rel, _ = manifest_fields(mpath)
        if doc_rel:
            referenced[doc_rel.strip("/").split("/")[0]] = s
    for d in sorted(set(docs) - set(referenced)):
        findings.append({"severity": "HIGH", "kind": "DOC_WITHOUT_MANIFEST", "service": d, "detail": "no manifest's design_doc points here"})
    for s, mpath in sorted(manifests.items()):
        doc_rel, _ = manifest_fields(mpath)
        if not doc_rel or not os.path.exists(os.path.join(docs_root, doc_rel)):
            findings.append({"severity": "MED", "kind": "MANIFEST_WITHOUT_DOC", "service": s, "detail": f"design_doc '{doc_rel}' not found under DESIGN_DOCS_ROOT"})
    if folders:
        for s in sorted(set(folders) - set(manifests)):
            findings.append({"severity": "MED", "kind": "FOLDER_WITHOUT_MANIFEST", "service": s, "detail": "ignore if the folder is not a service"})
        for s in sorted(set(manifests) - set(folders)):
            findings.append({"severity": "HIGH", "kind": "MANIFEST_WITHOUT_FOLDER", "service": s})

    for s, mpath in sorted(manifests.items()):
        doc_rel, sha = manifest_fields(mpath)
        if not doc_rel or not sha:
            findings.append({"severity": "HIGH", "kind": "MANIFEST_MISSING_SHA", "service": s})
            continue
        dpath = os.path.join(docs_root, doc_rel) if docs_root else None
        if dpath and os.path.exists(dpath):
            actual = sha256_path(dpath)
            if actual != sha:
                findings.append({"severity": "HIGH", "kind": "DESIGN_DOC_CHANGED", "service": s, "detail": f"manifest sha {sha[:12]} != doc sha {actual[:12]}; re-verify manifest"})

    summary = {"manifests": len(manifests), "design_docs": len(docs), "service_folders": len(folders), "findings": findings,
               "high": sum(1 for f in findings if f["severity"] == "HIGH")}
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(summary, fh, indent=2)
        print(f"wrote {args.out}: {len(findings)} finding(s), {summary['high']} HIGH")
    elif args.json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"manifests={summary['manifests']} design_docs={summary['design_docs']} service_folders={summary['service_folders']}")
        for f in findings:
            print(f"[{f['severity']}] {f['kind']}", f.get("service", ""), f.get("detail", ""))
        print(f"{len(findings)} finding(s), {summary['high']} HIGH")
    return 1 if summary["high"] else 0


if __name__ == "__main__":
    sys.exit(main())
