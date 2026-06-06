"""Scope-gated repository intake service."""

from __future__ import annotations

from pathlib import Path

from bountyclaw.scope import ScopeGate, Target, TargetKind
from bountyclaw.scope.loader import LoadedScopeManifest
from bountyclaw.scope.models import ScopeDecision

from .intake import inspect_repository
from .models import RepositoryFingerprint, ScanPlan
from .planner import build_scan_plan


class RepositoryAuthorizationError(RuntimeError):
    """Raised when the scope gate denies a repository action."""

    def __init__(self, decision: ScopeDecision) -> None:
        self.decision = decision
        super().__init__("; ".join(decision.reasons))


def inspect_authorized_repository(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
) -> RepositoryFingerprint:
    """Inspect a repository only after `repo.read` is scope-approved."""

    _require_allowed(loaded_scope, repo, action="repo.read")
    return inspect_repository(repo)


def plan_authorized_repository_scan(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
) -> ScanPlan:
    """Build a scan plan only after read and scan-planning actions are approved."""

    _require_allowed(loaded_scope, repo, action="repo.read")
    _require_allowed(loaded_scope, repo, action="scan.local_static")
    fingerprint = inspect_repository(repo)
    return build_scan_plan(fingerprint)


def _require_allowed(
    loaded_scope: LoadedScopeManifest, repo: Path, *, action: str
) -> ScopeDecision:
    decision = ScopeGate(loaded_scope).evaluate(
        action=action,
        target=Target(kind=TargetKind.LOCAL_REPO, value=str(repo)),
    )
    if not decision.allowed:
        raise RepositoryAuthorizationError(decision)
    return decision
