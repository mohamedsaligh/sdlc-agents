#!/usr/bin/env python3
"""Validate manifests/*.yaml against schema/manifest.schema.md rules and schema/vocabulary.yaml.

  python scripts/validate-manifests.py            # human output, exit 1 on any error
  python scripts/validate-manifests.py --json     # machine output for the maintenance agent
Requires PyYAML:  pip install pyyaml
"""
import argparse
import json
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

try:
    import yaml  # type: ignore
except ImportError:  # pragma: no cover
    print("error: PyYAML missing. Install with: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

REQUIRED = [
    "service", "manifest_version", "design_doc", "design_doc_sha256", "summary", "role",
    "consumes", "emits", "hops.upstream", "hops.downstream",
    "config.tables", "config.cache_regions", "config.lookup_keys",
    "code.repo", "code.key_packages", "code.entrypoints", "code.build",
    "tags.markets", "tags.clearings", "tags.products", "tags.directions", "tags.lifecycle_stages",
    "onboarding_recipe.required_config", "onboarding_recipe.required_code", "onboarding_recipe.substitution_rules",
    "invariants", "verification.sources", "verification.last_verified", "verification.open_gaps",
]
# lists allowed to be empty without a note
MAY_BE_EMPTY = {"onboarding_recipe.required_code", "verification.open_gaps", "external_interfaces",
                "tags.channels", "tags.priorities", "tags.clearings", "tags.markets"}
VOCAB_FIELDS = {
    "role": "roles",
    "tags.markets": "markets", "tags.clearings": "clearings", "tags.products": "products",
    "tags.directions": "directions", "tags.channels": "channels",
    "tags.lifecycle_stages": "lifecycle_stages", "tags.priorities": "priorities",
}
import re as _re
_PLACEHOLDER_RE = _re.compile(r"^(<.*>?|__[A-Z_]+__)")  # "<fill me>" or an unreplaced __TOKEN__


def get(d, dotted):
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def validate(path, vocab):
    errors, warnings = [], []
    with open(path, encoding="utf-8") as fh:
        try:
            m = yaml.safe_load(fh)
        except yaml.YAMLError as e:
            return [f"YAML parse error: {e}"], []
    if not isinstance(m, dict):
        return ["manifest is not a mapping"], []

    stem = os.path.splitext(os.path.basename(path))[0]
    if m.get("service") != stem:
        errors.append(f"service '{m.get('service')}' must equal file stem '{stem}'")
    if m.get("code", {}).get("repo") not in (None, stem):
        warnings.append(f"code.repo '{m['code']['repo']}' differs from service name; ensure folder exists under CODE_ROOT")

    for field in REQUIRED:
        v = get(m, field)
        if v is None:
            errors.append(f"missing required field: {field}")
        elif isinstance(v, (list, dict)) and len(v) == 0 and field not in MAY_BE_EMPTY:
            errors.append(f"required list is empty: {field}")
        elif isinstance(v, str) and (not v.strip() or _PLACEHOLDER_RE.match(v.strip())):
            errors.append(f"field still holds a placeholder/empty value: {field} = {v!r}")

    for field, vlist in VOCAB_FIELDS.items():
        v = get(m, field)
        allowed = set(vocab.get(vlist) or [])
        if v is None:
            continue
        values = v if isinstance(v, list) else [v]
        for item in values:
            if allowed and item not in allowed:
                errors.append(f"{field}: '{item}' not in vocabulary.{vlist}")
            elif not allowed:
                warnings.append(f"vocabulary.{vlist} is empty; cannot validate {field}")

    sha = m.get("design_doc_sha256", "")
    if not (isinstance(sha, str) and len(sha) == 64 and all(c in "0123456789abcdef" for c in sha.lower())):
        errors.append("design_doc_sha256 must be a 64-hex SHA-256")

    for rc in m.get("onboarding_recipe", {}).get("required_config", []) or []:
        for k in ("table_or_region", "key_pattern", "note"):
            if not rc.get(k):
                errors.append(f"onboarding_recipe.required_config entry missing '{k}': {rc}")

    srcs = set(get(m, "verification.sources") or [])
    if "trace" not in srcs:
        warnings.append("verification.sources lacks 'trace' — MAP lane will be penalised for this service")
    if get(m, "verification.open_gaps"):
        warnings.append(f"{len(m['verification']['open_gaps'])} open gap(s) recorded")

    size = sum(1 for _ in open(path, encoding="utf-8"))
    if size > 150:
        warnings.append(f"manifest is {size} lines; it is probably holding data or prose (target 40-120)")
    return errors, warnings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dir", default=os.path.join(REPO_ROOT, "manifests"))
    args = ap.parse_args()

    with open(os.path.join(REPO_ROOT, "schema", "vocabulary.yaml"), encoding="utf-8") as fh:
        vocab = yaml.safe_load(fh) or {}

    files = sorted(f for f in os.listdir(args.dir) if f.endswith((".yaml", ".yml")) and not f.startswith("_"))
    report = {"manifests": {}, "error_count": 0, "warning_count": 0}
    for f in files:
        errs, warns = validate(os.path.join(args.dir, f), vocab)
        report["manifests"][f] = {"errors": errs, "warnings": warns}
        report["error_count"] += len(errs)
        report["warning_count"] += len(warns)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        if not files:
            print("no manifests found in", args.dir)
        for f, r in report["manifests"].items():
            status = "OK " if not r["errors"] else "ERR"
            print(f"[{status}] {f}  errors={len(r['errors'])} warnings={len(r['warnings'])}")
            for e in r["errors"]:
                print("      E:", e)
            for w in r["warnings"]:
                print("      W:", w)
        print(f"\n{len(files)} manifest(s): {report['error_count']} error(s), {report['warning_count']} warning(s)")
    return 1 if report["error_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
