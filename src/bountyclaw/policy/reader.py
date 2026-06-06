"""Redaction-first local policy document reader for Phase 7."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path

from bountyclaw.findings import redact_text
from bountyclaw.scope import LoadedScopeManifest

from .models import PolicyDocumentSummary, PolicySignal, PolicySignalKind

MAX_POLICY_BYTES = 64 * 1024
MAX_SIGNAL_LENGTH = 260

_SIGNAL_KEYWORDS: tuple[tuple[PolicySignalKind, tuple[str, ...]], ...] = (
    ("allowed_target_hint", ("in scope", "in-scope", "allowed", "target", "eligible")),
    (
        "out_of_scope_hint",
        ("out of scope", "out-of-scope", "excluded", "not allowed", "prohibited target"),
    ),
    (
        "prohibited_action_hint",
        (
            "do not",
            "prohibited",
            "forbidden",
            "denial of service",
            "brute force",
            "spam",
            "social engineering",
        ),
    ),
    ("safe_harbor_hint", ("safe harbor", "safe harbour", "authorization", "good faith")),
    (
        "disclosure_rule_hint",
        ("disclosure", "report", "submit", "triage", "duplicate", "public disclosure"),
    ),
)


class PolicyDocumentError(RuntimeError):
    """Raised when a local policy document cannot be safely read."""


def resolve_policy_file(loaded_scope: LoadedScopeManifest, policy_file: Path | None = None) -> Path:
    """Resolve a local policy file from explicit CLI input or the scope manifest."""

    candidate: Path | None
    if policy_file is not None:
        candidate = policy_file.expanduser()
    elif loaded_scope.manifest.program.policy_file:
        candidate = Path(loaded_scope.manifest.program.policy_file).expanduser()
    else:
        raise PolicyDocumentError(
            "no local policy_file is available; Phase 7 does not fetch policy URLs or live pages"
        )

    if not candidate.is_absolute():
        candidate = loaded_scope.base_dir / candidate
    return candidate.resolve(strict=False)


def read_local_policy_summary(
    loaded_scope: LoadedScopeManifest,
    policy_file: Path | None = None,
) -> PolicyDocumentSummary:
    """Read and summarize a local policy file without using a browser or network."""

    resolved = resolve_policy_file(loaded_scope, policy_file)
    if not resolved.exists():
        raise PolicyDocumentError(f"policy file does not exist: {resolved}")
    if not resolved.is_file():
        raise PolicyDocumentError(f"policy path is not a regular file: {resolved}")
    if resolved.is_symlink():
        raise PolicyDocumentError(f"policy file symlinks are denied in Phase 7: {resolved}")

    byte_count = resolved.stat().st_size
    if byte_count > MAX_POLICY_BYTES:
        raise PolicyDocumentError(
            f"policy file exceeds Phase 7 local fixture limit of {MAX_POLICY_BYTES} bytes: {resolved}"
        )

    try:
        raw_text = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise PolicyDocumentError("policy file must be UTF-8 text") from exc

    redacted = redact_text(raw_text)
    redacted_lines = redacted.redacted_text.splitlines()
    signals = _extract_signals(redacted_lines)
    notes = [
        "Policy ingestion is advisory only; it does not expand executable scope.",
        "The scope manifest remains the authorization source of truth.",
        "Phase 7 local policy ingestion used no network, no live browser, and no live MCP server.",
    ]
    if not signals:
        notes.append("No policy keywords were detected in the local fixture document.")

    return PolicyDocumentSummary(
        source_path=str(resolved),
        source_name=resolved.name,
        line_count=len(redacted_lines),
        byte_count=byte_count,
        redaction_count=len(redacted.redactions),
        signals=signals,
        notes=notes,
    )


def _extract_signals(redacted_lines: list[str]) -> list[PolicySignal]:
    seen: set[tuple[PolicySignalKind, int, str]] = set()
    signals: list[PolicySignal] = []
    for line_number, line in enumerate(redacted_lines, start=1):
        normalized = " ".join(line.strip().split())
        if not normalized:
            continue
        lowered = normalized.lower()
        for kind, keywords in _SIGNAL_KEYWORDS:
            if not any(keyword in lowered for keyword in keywords):
                continue
            truncated = normalized[:MAX_SIGNAL_LENGTH]
            key = (kind, line_number, truncated)
            if key in seen:
                continue
            seen.add(key)
            signal_hash = sha256(f"{kind}:{line_number}:{truncated}".encode()).hexdigest()[:16]
            signals.append(
                PolicySignal(
                    signal_id=f"policy-signal-{signal_hash}",
                    kind=kind,
                    line_number=line_number,
                    text=truncated,
                )
            )
            break
    return signals
