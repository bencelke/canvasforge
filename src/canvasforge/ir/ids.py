"""Stable deterministic identifiers for IR nodes."""

from __future__ import annotations

import re

_SEGMENT_RE = re.compile(r"[^a-zA-Z0-9_-]+")


def _normalize_segment(value: str) -> str:
    cleaned = _SEGMENT_RE.sub("-", value.strip())
    cleaned = cleaned.strip("-_")
    return cleaned.lower() or "node"


def make_node_id(
    app_key: str,
    screen_key: str,
    *parts: str,
) -> str:
    """Build a stable slash-separated internal node ID (not a Power Apps name)."""
    segments = [_normalize_segment(app_key), _normalize_segment(screen_key)]
    segments.extend(_normalize_segment(part) for part in parts if part)
    return "/".join(segments)
