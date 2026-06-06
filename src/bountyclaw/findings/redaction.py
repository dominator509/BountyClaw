"""Redaction engine for evidence-safe persistence.

The redactor is deliberately conservative and deterministic. It is not a full
DLP product, but it blocks common credential shapes before text reaches the
Phase 4 SQLite evidence store or any future model prompt builder.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from re import Pattern

from .models import RedactionMatch, RedactionResult


@dataclass(frozen=True)
class _RedactionPattern:
    secret_type: str
    regex: Pattern[str]
    preserve_prefix: bool = False


_PATTERNS: tuple[_RedactionPattern, ...] = (
    _RedactionPattern(
        "PRIVATE_KEY_BLOCK",
        re.compile(
            r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY-----.*?-----END [A-Z0-9 ]*PRIVATE KEY-----",
            re.DOTALL,
        ),
    ),
    _RedactionPattern("AWS_ACCESS_KEY_ID", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    _RedactionPattern(
        "GITHUB_TOKEN",
        re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9_]{30,}|github_pat_[A-Za-z0-9_]{30,})\b"),
    ),
    _RedactionPattern("OPENAI_API_KEY", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    _RedactionPattern("SLACK_TOKEN", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b")),
    _RedactionPattern(
        "JWT",
        re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b"),
    ),
    _RedactionPattern(
        "BEARER_TOKEN",
        re.compile(r"(?i)\bBearer\s+[A-Za-z0-9._~+/=-]{20,}"),
    ),
    _RedactionPattern(
        "GENERIC_SECRET_ASSIGNMENT",
        re.compile(
            r"(?i)\b((?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|secret|token|password|passwd|pwd|private[_-]?key)\s*[:=]\s*)[\"']?[^\s,;\"']{8,}[\"']?"
        ),
        preserve_prefix=True,
    ),
)


def redact_text(value: str) -> RedactionResult:
    """Return a redacted version of *value* without storing raw match data."""

    redacted = value
    redactions: list[RedactionMatch] = []

    for pattern in _PATTERNS:
        redacted = pattern.regex.sub(_replacement_factory(pattern, redactions), redacted)

    return RedactionResult(
        original_text_was_modified=redacted != value,
        redacted_text=redacted,
        redaction_status="redacted" if redactions else "no_sensitive_patterns_detected",
        redactions=redactions,
    )


def _replacement_factory(
    pattern: _RedactionPattern,
    redactions: list[RedactionMatch],
) -> Callable[[re.Match[str]], str]:
    def replace(match: re.Match[str]) -> str:
        placeholder = f"[REDACTED:{pattern.secret_type}:{len(redactions) + 1}]"
        redactions.append(RedactionMatch(secret_type=pattern.secret_type, placeholder=placeholder))
        if pattern.preserve_prefix:
            return f"{match.group(1)}{placeholder}"
        return placeholder

    return replace
