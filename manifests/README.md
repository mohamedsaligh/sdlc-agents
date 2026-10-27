# manifests/

One YAML file per service: `manifests/<service>.yaml`, where `<service>` equals the folder name under
`__CODE_ROOT__` and the stem of the design doc `__DESIGN_DOCS_ROOT__/<service>.md`.

- Schema and completeness rules: `schema/manifest.schema.md`
- Template: `schema/manifest.template.yaml` · Example: `schema/manifest.example.yaml`
- Built by `prompts/01-build-manifests.md`, proven by `prompts/02-triangulate.md`, kept true by the maintenance agent.
- Validate: `python scripts/validate-manifests.py` · Drift: `python scripts/check-drift.py`

Files starting with `_` are ignored by the scripts and the agents.
