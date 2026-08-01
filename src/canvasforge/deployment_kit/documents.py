"""Deployment document and auxiliary artifact generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from canvasforge.deployment_kit.models import ValidationRecordTemplate, dump_canonical_json
from canvasforge.generate.reports import dump_json
from canvasforge.manifest.models import AppManifest


def theme_json(manifest: AppManifest) -> str:
    if manifest.theme is None:
        payload: dict[str, object] = {
            "key": None,
            "mode": None,
            "tokens": {},
            "notes": "No theme block in source manifest.",
        }
    else:
        payload = {
            "key": manifest.theme.key,
            "mode": manifest.theme.mode,
            "tokens": dict(sorted(manifest.theme.tokens.items())),
            "notes": "Recreate these tokens manually in Power Apps Studio theme settings.",
        }
    return dump_canonical_json(payload)


def formulas_readme() -> str:
    return """# Formulas

Phase 3B packages only Power Fx that already exists or can be stated as an
explicit requirement. No invented production Patch logic is included.

| Artifact | Status |
|----------|--------|
| `app-onstart.powerfx` | Placeholder — not generated in this phase |
| `screen-formulas/` | Empty — no screen formulas emitted yet |

All formula maturity remains **Candidate / Studio-unvalidated**.
"""


def app_onstart_placeholder() -> str:
    return """// CanvasForge Phase 3B placeholder
// STATUS: not-generated — do not treat as production Power Fx
// App.OnStart was not emitted because no evidenced OnStart template exists yet.
// Replace in Power Apps Studio after maker review.
"""


def mock_schema_readme(*, include_mock_data: bool) -> str:
    records = (
        "Fictional mock **records** are included because `--include-mock-data` was set."
        if include_mock_data
        else "Mock **records** are excluded by default. Pass `--include-mock-data` to include fictional records only."
    )
    return f"""# Mock schema

This folder describes fictional offline data shapes for maker wiring guidance.

{records}

Never connect production SharePoint Lists from these files automatically.
Lists are created and permissioned by authorized makers in the work environment.
"""


def build_data_contract(manifest: AppManifest, *, actions_path: Path | None) -> dict[str, Any]:
    sources: list[dict[str, Any]] = []
    for source in manifest.data_sources:
        sources.append(
            {
                "key": source.key,
                "kind": source.kind,
                "mode": source.mode,
                "localCollectionName": source.collection,
                "description": source.description,
                "fields": [],
                "requiredFields": [],
                "optionalFields": [],
                "choiceLike": [],
                "personLike": [],
                "lookupLike": [],
                "sharePointMappingNotes": (
                    "Deferred — connect Lists manually in Studio after kit review."
                ),
            }
        )

    if not sources and actions_path is not None and actions_path.is_file():
        records = json.loads(actions_path.read_text(encoding="utf-8"))
        fields: list[str] = []
        if isinstance(records, list) and records and isinstance(records[0], dict):
            fields = sorted(str(key) for key in records[0])
        sources.append(
            {
                "key": "actionsMock",
                "kind": "mock",
                "mode": "offline-mock",
                "localCollectionName": "colActions",
                "description": "Fictional O-Room actions shape derived from example mock-data.",
                "fields": [
                    {"name": name, "type": "string", "required": name in {"id", "title", "status"}}
                    for name in fields
                ],
                "requiredFields": [n for n in fields if n in {"id", "title", "status"}],
                "optionalFields": [n for n in fields if n not in {"id", "title", "status"}],
                "choiceLike": [{"field": "status", "values": _unique_status(records)}],
                "personLike": [{"field": "requestorAlias", "notes": "Fictional alias only"}],
                "lookupLike": [],
                "sharePointMappingNotes": (
                    "Map to a SharePoint List later; do not embed tenant URLs in kits."
                ),
            }
        )

    if not sources:
        sources.append(
            {
                "key": "none",
                "kind": "mock",
                "mode": "offline-mock",
                "localCollectionName": None,
                "description": "No data sources declared in the source manifest.",
                "fields": [],
                "requiredFields": [],
                "optionalFields": [],
                "choiceLike": [],
                "personLike": [],
                "lookupLike": [],
                "sharePointMappingNotes": "Not applicable for this kit.",
            }
        )

    return {
        "schemaVersion": "0.1",
        "classification": "fictional-development",
        "dataSources": sources,
    }


def _unique_status(records: Any) -> list[str]:
    values: set[str] = set()
    if isinstance(records, list):
        for row in records:
            if isinstance(row, dict) and "status" in row:
                values.add(str(row["status"]))
    return sorted(values)


def collections_json(manifest: AppManifest) -> dict[str, Any]:
    collections = []
    for source in manifest.data_sources:
        if source.collection:
            collections.append(
                {
                    "name": source.collection,
                    "dataSourceKey": source.key,
                    "mode": source.mode,
                }
            )
    return {"schemaVersion": "0.1", "collections": collections}


def install_order_md(*, screens: list[str], target: str) -> str:
    screen_list = "\n".join(f"   - `{key}`" for key in screens) or "   - (none)"
    return f"""# Install order (Candidate Code View)

Target adapter: `{target}`

1. Verify this kit with `canvasforge package verify`.
2. Review `reports/build-report.json` and `reports/validation-report.json`.
3. Create a **blank** Canvas app in Power Apps Studio (sandbox).
4. Create required screens matching generated keys:
{screen_list}
5. Paste app-level formulas from `formulas/` only when they are not placeholders.
6. Paste Code View blocks from `generated/code-view/` **in screen-key order**.
7. Run App.OnStart where applicable (skip if placeholder).
8. Confirm controls appear; do not expect pixel-perfect parity with local tools.
9. Record Studio validation using `deployment/validation-record-template.json`.
10. Create/connect production Lists later (not in this kit).
11. Replace mock adapters with maker-approved connections.
12. Test permissions with authorized accounts.
13. Publish only after explicit approval.

Power Apps Studio remains the final validation authority.
"""


def power_apps_checklist_md() -> str:
    return """# Power Apps maker checklist

## Required maker permissions

- [ ] Environment Maker (or equivalent) in the target environment
- [ ] Rights to create/edit Canvas apps
- [ ] Rights to create or use intended SharePoint Lists (later)

## Local kit review

- [ ] `canvasforge package verify` passed
- [ ] Forbidden-content report reviewed
- [ ] Build maturity understood (Candidate / Studio-unvalidated)

## Studio import / paste

- [ ] Blank or sandbox app created
- [ ] Code View blocks pasted in install order
- [ ] No production app overwritten accidentally

## Formula validation

- [ ] Placeholder formulas skipped or replaced intentionally
- [ ] App.OnStart reviewed before enabling

## Data connection

- [ ] Lists not auto-created by CanvasForge
- [ ] Connections configured only by authorized makers

## Security

- [ ] No credentials copied from this kit (none should exist)
- [ ] No tenant IDs present in kit files

## Testing

- [ ] Navigation smoke test
- [ ] Permission smoke test

## Publishing

- [ ] Explicit approval recorded
- [ ] Publish performed by authorized maker only
"""


def data_connection_checklist_md() -> str:
    return """# Data connection checklist

CanvasForge Deployment Kits do **not** create SharePoint Lists, Dataverse tables,
or Power Automate flows.

1. Review `mock-schema/data-contract.json` for fictional field shapes.
2. Design or select Lists in the work tenant using approved processes.
3. Connect Lists in Power Apps Studio under maker credentials.
4. Replace any offline collections with connected data sources.
5. Configure item permissions separately — not via this kit.
6. Never paste production connection strings into the public repository.
"""


def known_limitations_md() -> str:
    return """# Known limitations (Phase 3B)

- Output is **Candidate Code View**, Studio-unvalidated.
- Local preview is not included in this kit.
- OnSelect and most Power Fx templates are not generated yet.
- `.msapp` packaging is experimental and deferred.
- No Microsoft authentication or API calls are performed by CanvasForge.
- Galleries, forms, and connectors remain limited by the control allowlist.
- O-Room full application generation is out of scope for this kit type.
"""


def validation_record_template_json(*, build_id: str) -> str:
    template = ValidationRecordTemplate(packageBuildId=build_id, packageChecksum="")
    return dump_canonical_json(template.model_dump(mode="json", by_alias=True))


def compatibility_profile_json() -> str:
    payload = {
        "id": "documented-bootstrap",
        "version": "0.1",
        "policy": "documented|studio-exported|studio-validated allowed; inferred blocked",
        "notes": "Bootstrap profile until Studio Compatibility Laboratory fixtures exist.",
    }
    return dump_canonical_json(payload)


def evidence_summary_json(generation_report: dict[str, Any]) -> str:
    payload = {
        "studioValidationState": generation_report.get("studioValidationState", "unvalidated"),
        "outputStatus": "Candidate",
        "evidenceSummary": generation_report.get("evidenceSummary", {}),
        "controlsGenerated": generation_report.get("controlsGenerated"),
        "propertiesGenerated": generation_report.get("propertiesGenerated"),
    }
    return dump_canonical_json(payload)


def validation_report_json(
    *,
    manifest_checksum: str,
    diagnostics: list[dict[str, Any]],
    valid: bool,
) -> str:
    payload = {
        "valid": valid,
        "sourceManifestChecksum": manifest_checksum,
        "diagnosticCount": len(diagnostics),
        "diagnostics": diagnostics,
    }
    return dump_json(payload)
