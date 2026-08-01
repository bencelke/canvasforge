"""Constants and size limits for Deployment Kits."""

from __future__ import annotations

PACKAGE_FORMAT = "CanvasForgeDeploymentKit"
PACKAGE_SCHEMA_VERSION = "0.1"
SUPPORTED_PACKAGE_SCHEMA_VERSIONS = frozenset({"0.1"})
COMPATIBILITY_PROFILE_ID = "documented-bootstrap"
COMPATIBILITY_PROFILE_VERSION = "0.1"
DEFAULT_TARGET = "code-view"

PROJECT_DESCRIPTOR_NAME = "canvasforge-project.json"
CHECKSUMS_NAME = "checksums.sha256"
ENTRY_MANIFEST_NAME = "app.manifest.yaml"

# Defense limits (bytes)
MAX_ARCHIVE_BYTES = 50 * 1024 * 1024
MAX_MEMBER_BYTES = 5 * 1024 * 1024
MAX_UNCOMPRESSED_BYTES = 80 * 1024 * 1024
MAX_COMPRESSION_RATIO = 100.0
MAX_MEMBER_COUNT = 500

# Deterministic ZIP metadata
ZIP_EPOCH = (1980, 1, 1, 0, 0, 0)
ZIP_EXTERNAL_ATTR = 0o644 << 16

TEXT_SUFFIXES = frozenset(
    {
        ".json",
        ".yaml",
        ".yml",
        ".md",
        ".txt",
        ".powerfx",
        ".sha256",
        ".csv",
        ".gitkeep",
    }
)

FORBIDDEN_SUFFIXES = frozenset(
    {
        ".msapp",
        ".p12",
        ".pfx",
        ".pem",
        ".key",
        ".cer",
        ".crt",
        ".exe",
        ".dll",
        ".so",
        ".dylib",
    }
)

REQUIRED_MEMBERS = frozenset(
    {
        PROJECT_DESCRIPTOR_NAME,
        ENTRY_MANIFEST_NAME,
        CHECKSUMS_NAME,
        "deployment/install-order.md",
        "deployment/power-apps-checklist.md",
        "deployment/data-connection-checklist.md",
        "deployment/validation-record-template.json",
        "deployment/known-limitations.md",
        "compatibility/profile.json",
        "compatibility/evidence-summary.json",
        "reports/build-report.json",
        "reports/validation-report.json",
        "reports/forbidden-content-report.json",
        "reports/package-manifest.json",
        "generated/control-tree.json",
        "generated/generation-plan.json",
        "mock-schema/README.md",
        "formulas/README.md",
        "theme/theme.json",
    }
)
