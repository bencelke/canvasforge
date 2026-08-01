"""Evidence status helpers and bootstrap documentation records."""

from __future__ import annotations

from canvasforge.controls.models import EvidenceRecord

BOOTSTRAP_RECORDS: list[EvidenceRecord] = [
    EvidenceRecord(
        evidenceId="ev-screen-documented",
        controlType="Screen",
        property=None,
        sourceType="official-documentation",
        sourceReference="Microsoft Canvas app Screen control concepts",
        studioAccepted=None,
        studioVersion=None,
        environmentClass="unknown",
        notes="Bootstrap documented entry. No Studio-exported fixture in-repo yet.",
        recordedOn="2026-08-01",
        checksum="bootstrap-no-fixture",
    ),
    EvidenceRecord(
        evidenceId="ev-groupcontainer-documented",
        controlType="VerticalContainer",
        property="LayoutDirection",
        sourceType="official-documentation",
        sourceReference="Microsoft Canvas container layout properties",
        studioAccepted=None,
        studioVersion=None,
        environmentClass="unknown",
        notes="Logical VerticalContainer maps to GroupContainer candidate identifier.",
        recordedOn="2026-08-01",
        checksum="bootstrap-no-fixture",
    ),
    EvidenceRecord(
        evidenceId="ev-label-documented",
        controlType="Text",
        property="Text",
        sourceType="official-documentation",
        sourceReference="Microsoft Canvas Label/Text control Text property",
        studioAccepted=None,
        studioVersion=None,
        environmentClass="unknown",
        notes="Code View identifier Candidate: Label.",
        recordedOn="2026-08-01",
        checksum="bootstrap-no-fixture",
    ),
    EvidenceRecord(
        evidenceId="ev-button-documented",
        controlType="Button",
        property="Text",
        sourceType="official-documentation",
        sourceReference="Microsoft Canvas Button control Text property",
        studioAccepted=None,
        studioVersion=None,
        environmentClass="unknown",
        notes="OnSelect intentionally omitted until Studio-exported evidence exists.",
        recordedOn="2026-08-01",
        checksum="bootstrap-no-fixture",
    ),
]


def evidence_summary() -> dict[str, int]:
    """Count bootstrap evidence by source type."""
    counts: dict[str, int] = {}
    for record in BOOTSTRAP_RECORDS:
        counts[record.source_type] = counts.get(record.source_type, 0) + 1
    return counts
