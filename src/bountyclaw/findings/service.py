"""Scope-gated Phase 4 findings collection service."""

from __future__ import annotations

from pathlib import Path

from bountyclaw.scanning import DEFAULT_SCANNER_ID, scan_authorized_repository
from bountyclaw.scope import ScopeGate, Target, TargetKind
from bountyclaw.scope.loader import LoadedScopeManifest
from bountyclaw.scope.models import ScopeDecision

from .models import FindingsCollectionResult
from .normalizer import normalize_scanner_run
from .store import EvidenceStore, ensure_store_path_outside_repository


class FindingsAuthorizationError(RuntimeError):
    """Raised when findings persistence is not authorized by scope."""

    def __init__(self, decision: ScopeDecision) -> None:
        self.decision = decision
        super().__init__("; ".join(decision.reasons))


def collect_authorized_findings(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    store_path: Path,
    scanner_ids: list[str] | None = None,
    local_scanner_enabled: bool = False,
) -> FindingsCollectionResult:
    """Run authorized local scanning, normalize findings, and persist redacted evidence."""

    _require_allowed(loaded_scope, repo, action="findings.write")
    resolved_store = ensure_store_path_outside_repository(store_path, repo)
    scan_result = scan_authorized_repository(
        loaded_scope,
        repo,
        scanner_ids=scanner_ids or [DEFAULT_SCANNER_ID],
        local_scanner_enabled=local_scanner_enabled,
    )
    normalization = normalize_scanner_run(scan_result)
    EvidenceStore(resolved_store).write_scan_run(scan_result, normalization)
    return FindingsCollectionResult(
        store_path=str(resolved_store),
        scan_execution_id=scan_result.scan_execution_id,
        repository=scan_result.repository,
        repository_fingerprint_id=scan_result.repository_fingerprint_id,
        canonical_findings=normalization.canonical_findings,
        evidence_records=normalization.evidence_records,
        redaction_count=normalization.redaction_count,
        notes=[
            "Scope-approved Phase 4 findings collection completed.",
            "Only redacted evidence was persisted to the local SQLite store.",
            "No network, LLM, MCP, browser, active validation, or report submission was used.",
        ]
        + normalization.notes,
    )


def _require_allowed(
    loaded_scope: LoadedScopeManifest, repo: Path, *, action: str
) -> ScopeDecision:
    decision = ScopeGate(loaded_scope).evaluate(
        action=action,
        target=Target(kind=TargetKind.LOCAL_REPO, value=str(repo)),
    )
    if not decision.allowed:
        raise FindingsAuthorizationError(decision)
    return decision
