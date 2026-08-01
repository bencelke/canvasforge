"""Local evidence store (offline only)."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from canvasforge.controls.evidence import BOOTSTRAP_RECORDS
from canvasforge.controls.models import EvidenceRecord
from canvasforge.errors import Diagnostic, EvidenceError

MAX_EVIDENCE_BYTES = 512_000
MAX_EVIDENCE_NESTING = 40
ALLOWED_EXTENSIONS = frozenset({".yaml", ".yml", ".json", ".md", ".txt"})
_ABS_PATH_RE = re.compile(r"(?i)(/Users/|/home/|[A-Za-z]:\\)")
_URL_RE = re.compile(r"(?i)https?://")
_TENANT_RE = re.compile(r"(?i)tenant|environmentid|orgid")


def default_evidence_root() -> Path:
    return Path.cwd() / "evidence"


def list_evidence_records(root: Path | None = None) -> list[EvidenceRecord]:
    """List bootstrap records plus any local JSON records under evidence/records."""
    records = list(BOOTSTRAP_RECORDS)
    base = root or default_evidence_root()
    records_dir = base / "records"
    if not records_dir.is_dir():
        return records
    for path in sorted(records_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        records.append(EvidenceRecord.model_validate(data))
    return records


def import_evidence_fixture(
    source: Path,
    *,
    root: Path | None = None,
    control_type: str = "Unknown",
    property_name: str | None = None,
) -> EvidenceRecord:
    """Import a local Studio-exported text fixture with safety checks."""
    path = source.expanduser().resolve()
    if not path.is_file():
        raise EvidenceError(
            "Evidence fixture not found",
            diagnostics=[
                Diagnostic(
                    code="EVIDENCE_NOT_FOUND",
                    message=str(path.name),
                    path="$",
                )
            ],
        )
    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise EvidenceError(
            "Unexpected evidence file extension",
            diagnostics=[
                Diagnostic(
                    code="EVIDENCE_BAD_EXTENSION",
                    message=f"Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
                    path=path.name,
                )
            ],
        )
    size = path.stat().st_size
    if size > MAX_EVIDENCE_BYTES:
        raise EvidenceError(
            "Evidence file too large",
            diagnostics=[
                Diagnostic(
                    code="EVIDENCE_TOO_LARGE",
                    message=f"{size} bytes exceeds {MAX_EVIDENCE_BYTES}",
                    path=path.name,
                )
            ],
        )
    # Reject obvious binaries
    raw = path.read_bytes()
    if b"\x00" in raw[:1024]:
        raise EvidenceError(
            "Binary evidence files are not allowed",
            diagnostics=[Diagnostic(code="EVIDENCE_BINARY", message=path.name, path=path.name)],
        )
    text = raw.decode("utf-8")
    if _ABS_PATH_RE.search(text) or _URL_RE.search(text) or _TENANT_RE.search(text):
        raise EvidenceError(
            "Evidence content contains forbidden absolute paths, URLs, or tenant markers",
            diagnostics=[
                Diagnostic(
                    code="EVIDENCE_SENSITIVE_CONTENT",
                    message="Strip local paths, URLs, and tenant identifiers before import",
                    path=path.name,
                )
            ],
        )

    checksum = hashlib.sha256(raw).hexdigest()
    evidence_id = f"ev-import-{checksum[:12]}"
    record = EvidenceRecord(
        evidenceId=evidence_id,
        controlType=control_type,
        property=property_name,
        sourceType="studio-export",
        sourceReference=path.name,
        studioAccepted=None,
        studioVersion=None,
        environmentClass="unknown",
        notes="Imported locally. Studio-exported Candidate evidence. Not auto-promoted.",
        recordedOn="1970-01-01",  # caller may overwrite via record file; avoid wall-clock in tests
        checksum=checksum,
    )

    base = root or default_evidence_root()
    fixtures = base / "fixtures"
    records_dir = base / "records"
    fixtures.mkdir(parents=True, exist_ok=True)
    records_dir.mkdir(parents=True, exist_ok=True)

    dest = fixtures / path.name
    if dest.exists() and hashlib.sha256(dest.read_bytes()).hexdigest() != checksum:
        raise EvidenceError(
            "Fixture name collision with different content",
            diagnostics=[Diagnostic(code="EVIDENCE_COLLISION", message=dest.name, path=dest.name)],
        )
    dest.write_bytes(raw)
    record_path = records_dir / f"{evidence_id}.json"
    record_path.write_text(
        json.dumps(record.model_dump(by_alias=True), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return record


def records_as_dicts(records: list[EvidenceRecord]) -> list[dict[str, Any]]:
    return [record.model_dump(by_alias=True) for record in records]
