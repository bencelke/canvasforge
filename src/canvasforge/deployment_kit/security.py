"""Forbidden-content scanner for Deployment Kit members."""

from __future__ import annotations

import re
from collections.abc import Mapping

from canvasforge.deployment_kit.constants import FORBIDDEN_SUFFIXES, TEXT_SUFFIXES
from canvasforge.deployment_kit.models import ForbiddenContentReport, ForbiddenFinding

# Blocking patterns — never bypass.
_BLOCKING: list[tuple[str, re.Pattern[str], str]] = [
    (
        "PRIVATE_KEY",
        re.compile(r"-----BEGIN ([A-Z0-9 ]+)?PRIVATE KEY-----"),
        "Private key marker detected",
    ),
    (
        "CERTIFICATE_BUNDLE",
        re.compile(r"-----BEGIN CERTIFICATE-----"),
        "Certificate PEM marker detected",
    ),
    (
        "BEARER_TOKEN",
        re.compile(r"(?i)\bbearer\s+[a-z0-9\-._~+/]+=*"),
        "Bearer token-like value detected",
    ),
    (
        "ACCESS_TOKEN_ASSIGNMENT",
        re.compile(
            r"(?i)[\"']?(access[_-]?token|api[_-]?key|client[_-]?secret)[\"']?\s*[:=]\s*[\"']?[^\s\"']+"
        ),
        "Credential assignment detected",
    ),
    (
        "CAC_MATERIAL",
        re.compile(r"(?i)\b(cac\s*pin|piv\s*pin|smart\s*card\s*pin)\b"),
        "CAC/PIV secret material reference detected",
    ),
]

# Warnings — recorded, usually non-blocking.
_WARNINGS: list[tuple[str, re.Pattern[str], str]] = [
    (
        "EMAIL_ADDRESS",
        re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
        "Email address-like text detected",
    ),
    (
        "URL",
        re.compile(r"https?://[^\s\"'<>]+", re.I),
        "URL detected",
    ),
    (
        "GUID",
        re.compile(
            r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b",
            re.I,
        ),
        "GUID-like identifier detected",
    ),
    (
        "TENANT_TERM",
        re.compile(r"(?i)\b(tenantId|environmentId|organizationId|orgId)\b"),
        "Tenant/environment identifier term detected",
    ),
    (
        "WINDOWS_ABS_PATH",
        re.compile(r"(?i)\b[A-Z]:\\(?:Users|Windows|Program Files)\\[^\s\"']+"),
        "Windows absolute personal/system path detected",
    ),
    (
        "UNIX_HOME_PATH",
        re.compile(r"(?i)/(?:Users|home)/[A-Za-z0-9._-]+/"),
        "Unix absolute personal path detected",
    ),
    (
        "MILITARY_EMAIL_DOMAIN",
        re.compile(r"(?i)@[A-Za-z0-9.-]*\.(mil|army|navy|af|usmc)\b"),
        "Military email domain pattern detected",
    ),
    (
        "EDIPI_LABEL",
        re.compile(r"(?i)\bEDIPI\b"),
        "EDIPI label detected",
    ),
    (
        "UIC_LABEL",
        re.compile(r"(?i)\bUIC\b"),
        "UIC label detected",
    ),
    (
        "SSN_LABEL",
        re.compile(r"(?i)\b(SSN|social security number)\b"),
        "SSN label detected",
    ),
    (
        "PRODUCTION_DATA_MARKER",
        re.compile(r"(?i)\b(production data|live tenant|real personnel)\b"),
        "Production-data marker detected",
    ),
]

# Paths where generic security vocabulary is expected (checklists, READMEs).
_DOC_ALLOW_PATH_PREFIXES = (
    "deployment/",
    "formulas/README.md",
    "mock-schema/README.md",
    "reports/",
)

_DOC_ALLOWED_WARNING_CODES = frozenset(
    {
        "TENANT_TERM",
        "EDIPI_LABEL",
        "UIC_LABEL",
        "SSN_LABEL",
        "PRODUCTION_DATA_MARKER",
        "URL",
    }
)

_ALLOWED_URL_HOST_FRAGMENTS = (
    "example.com",
    "example.org",
    "localhost",
    "powerapps.microsoft.com",
    "learn.microsoft.com",
    "github.com/bencelke/canvasforge",
)


def _redact(value: str, *, limit: int = 24) -> str:
    cleaned = re.sub(r"\s+", " ", value).strip()
    if len(cleaned) <= limit:
        return cleaned[: max(0, limit // 2)] + "…"
    return cleaned[:12] + "…" + cleaned[-6:]


def _is_allowed_url(match: str) -> bool:
    lower = match.lower()
    return any(fragment in lower for fragment in _ALLOWED_URL_HOST_FRAGMENTS)


def scan_members(members: Mapping[str, bytes]) -> ForbiddenContentReport:
    findings: list[ForbiddenFinding] = []

    for path, payload in sorted(members.items()):
        suffix = ""
        if "." in path.rsplit("/", 1)[-1]:
            suffix = "." + path.rsplit(".", 1)[-1].lower()

        if suffix in FORBIDDEN_SUFFIXES:
            findings.append(
                ForbiddenFinding(
                    code="FORBIDDEN_BINARY",
                    severity="error",
                    path=path,
                    message=f"Unsupported or sensitive file type '{suffix}'",
                    redacted_excerpt="",
                )
            )
            continue

        if (
            suffix
            and suffix not in TEXT_SUFFIXES
            and not path.endswith("checksums.sha256")
            and suffix not in {".sha256"}
        ):
            findings.append(
                ForbiddenFinding(
                    code="UNSUPPORTED_BINARY",
                    severity="error",
                    path=path,
                    message="Non-text archive member is not allowed in Phase 3B kits",
                    redacted_excerpt="",
                )
            )
            continue

        try:
            text = payload.decode("utf-8")
        except UnicodeDecodeError:
            findings.append(
                ForbiddenFinding(
                    code="NON_UTF8",
                    severity="error",
                    path=path,
                    message="Member is not valid UTF-8 text",
                    redacted_excerpt="",
                )
            )
            continue

        for code, pattern, message in _BLOCKING:
            for match in pattern.finditer(text):
                findings.append(
                    ForbiddenFinding(
                        code=code,
                        severity="error",
                        path=path,
                        message=message,
                        redacted_excerpt=_redact(match.group(0)),
                    )
                )

        doc_path = any(path.startswith(prefix) for prefix in _DOC_ALLOW_PATH_PREFIXES)
        for code, pattern, message in _WARNINGS:
            if doc_path and code in _DOC_ALLOWED_WARNING_CODES:
                continue
            for match in pattern.finditer(text):
                if code == "URL" and _is_allowed_url(match.group(0)):
                    continue
                # Ignore fictional example.com emails in fixtures intentionally? still warn
                # unless in deployment docs.
                findings.append(
                    ForbiddenFinding(
                        code=code,
                        severity="warning",
                        path=path,
                        message=message,
                        redacted_excerpt=_redact(match.group(0)),
                    )
                )

    blocking_count = sum(1 for f in findings if f.severity == "error")
    warning_count = sum(1 for f in findings if f.severity == "warning")
    if blocking_count:
        status: str = "fail"
    elif warning_count:
        status = "pass-with-warnings"
    else:
        status = "pass"

    return ForbiddenContentReport(
        status=status,  # type: ignore[arg-type]
        findingCount=blocking_count + warning_count,
        blockingCount=blocking_count,
        warningCount=warning_count,
        findings=findings,
    )


def has_non_bypassable_blockers(report: ForbiddenContentReport) -> bool:
    """Credential/private-key class findings are never bypassable."""
    non_bypass = {
        "PRIVATE_KEY",
        "CERTIFICATE_BUNDLE",
        "BEARER_TOKEN",
        "ACCESS_TOKEN_ASSIGNMENT",
        "CAC_MATERIAL",
        "FORBIDDEN_BINARY",
    }
    return any(f.severity == "error" and f.code in non_bypass for f in report.findings)
