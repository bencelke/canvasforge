"""Deterministic YAML serializer for Candidate Code View output."""

from __future__ import annotations

from typing import Any

from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO


def dumps_code_view_yaml(data: dict[str, Any]) -> str:
    """Serialize mapping to UTF-8 YAML without anchors/aliases.

    Uses the round-trip dumper so insertion order is preserved (safe dumper
    may reorder keys alphabetically, which hurts readability of Candidate trees).
    """
    yaml = YAML(typ="rt")
    yaml.default_flow_style = False
    yaml.allow_unicode = True
    yaml.explicit_start = False
    yaml.explicit_end = False
    yaml.width = 120
    yaml.indent(mapping=2, sequence=4, offset=2)
    stream = StringIO()
    yaml.dump(data, stream)
    text = stream.getvalue()
    if not text.endswith("\n"):
        text += "\n"
    return text
