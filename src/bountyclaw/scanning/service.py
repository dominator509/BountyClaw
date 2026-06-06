"""Scope-gated scanner service."""

from __future__ import annotations

import hashlib
from pathlib import Path

from bountyclaw.repository import inspect_repository
from bountyclaw.scope import ScopeGate, Target, TargetKind
from bountyclaw.scope.loader import LoadedScopeManifest
from bountyclaw.scope.models import ScopeDecision

from .models import PreliminaryFinding, ScannerContext, ScannerRunResult
from .registry import DEFAULT_SCANNER_ID, ScannerRegistry, default_registry


class ScannerAuthorizationError(RuntimeError):
    """Raised when the scope gate denies scanner execution."""

    def __init__(self, decision: ScopeDecision) -> None:
        self.decision = decision
        super().__init__("; ".join(decision.reasons))


class ScannerFeatureGateError(RuntimeError):
    """Raised when a scanner execution feature gate is not explicitly enabled."""


class ScannerSelectionError(RuntimeError):
    """Raised when a requested scanner is not registered or supported."""


def scan_authorized_repository(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    scanner_ids: list[str] | None = None,
    local_scanner_enabled: bool = False,
    registry: ScannerRegistry | None = None,
    max_file_bytes: int = 1_048_576,
) -> ScannerRunResult:
    """Run scope-approved local static scanner adapters against a repository.

    This function performs only local, non-network static analysis. It reads
    source files through allowlisted adapters but does not execute target code,
    write to the repository, call LLM providers, invoke MCP/browser tools, or
    submit reports.
    """

    if not local_scanner_enabled:
        raise ScannerFeatureGateError(
            "local scanner execution requires the explicit --enable-local-scanner flag"
        )

    _require_allowed(loaded_scope, repo, action="repo.read")
    _require_allowed(loaded_scope, repo, action="scan.local_static")

    active_registry = registry or default_registry()
    selected_ids = scanner_ids or [DEFAULT_SCANNER_ID]
    adapters = []
    for scanner_id in selected_ids:
        try:
            adapters.append(active_registry.get(scanner_id))
        except KeyError as exc:
            raise ScannerSelectionError(str(exc)) from exc

    fingerprint = inspect_repository(repo)
    resolved_repo = repo.expanduser().resolve(strict=False)
    context = ScannerContext(
        repository_root=resolved_repo,
        repository_fingerprint_id=fingerprint.fingerprint_id,
        max_file_bytes=max_file_bytes,
    )

    findings: list[PreliminaryFinding] = []
    executed_specs = []
    unsupported_ids = []
    for adapter in adapters:
        if not adapter.supports(context):
            unsupported_ids.append(adapter.spec.scanner_id)
            continue
        executed_specs.append(adapter.spec)
        findings.extend(adapter.scan(context))

    findings.sort(key=lambda item: (item.file_path, item.line_number or 0, item.rule_id))
    notes = [
        "Phase 3 scanner execution is local-only and scope-gated.",
        "No network, LLM, MCP, browser, active exploitation, or report-submission actions were used.",
        "Raw source excerpts are omitted until the Phase 4 redaction and evidence-store layers exist.",
    ]
    if unsupported_ids:
        notes.append(
            "Unsupported adapters skipped for this repository: "
            + ", ".join(sorted(unsupported_ids))
        )

    return ScannerRunResult(
        scan_execution_id=_scan_execution_id(fingerprint.fingerprint_id, selected_ids, findings),
        repository=str(resolved_repo),
        repository_fingerprint_id=fingerprint.fingerprint_id,
        adapters=executed_specs,
        findings=findings,
        notes=notes,
    )


def _require_allowed(
    loaded_scope: LoadedScopeManifest, repo: Path, *, action: str
) -> ScopeDecision:
    decision = ScopeGate(loaded_scope).evaluate(
        action=action,
        target=Target(kind=TargetKind.LOCAL_REPO, value=str(repo)),
    )
    if not decision.allowed:
        raise ScannerAuthorizationError(decision)
    return decision


def _scan_execution_id(
    repository_fingerprint_id: str,
    scanner_ids: list[str],
    findings: list[PreliminaryFinding],
) -> str:
    digest = hashlib.sha256()
    digest.update(repository_fingerprint_id.encode("utf-8"))
    for scanner_id in sorted(scanner_ids):
        digest.update(scanner_id.encode("utf-8"))
    for finding in findings:
        digest.update(finding.finding_id.encode("utf-8"))
    return f"scan-sha256:{digest.hexdigest()}"
