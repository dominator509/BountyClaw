"""Scope-gated browser policy-ingestion foundation for Phase 7."""

from __future__ import annotations

from pathlib import Path

from bountyclaw.policy import read_local_policy_summary
from bountyclaw.scope import (
    Action,
    LoadedScopeManifest,
    ScopeDecision,
    ScopeGate,
    Target,
    TargetKind,
)

from .models import BrowserPolicyIngestionResult, BrowserWorkflowPlan


class BrowserControllerError(RuntimeError):
    """Base browser controller error."""


class BrowserFeatureGateError(BrowserControllerError):
    """Raised when fixture browser ingestion is not explicitly enabled."""


class BrowserAuthorizationError(BrowserControllerError):
    """Raised when scope denies browser policy ingestion."""

    def __init__(self, decision: ScopeDecision) -> None:
        super().__init__("browser policy ingestion is not authorized")
        self.decision = decision


def build_policy_ingestion_plan() -> BrowserWorkflowPlan:
    """Return the Phase 7 no-network browser workflow plan."""

    return BrowserWorkflowPlan(
        notes=[
            "Phase 7 does not launch a live browser runtime.",
            "Only local policy files may be parsed in fixture mode.",
            "Policy output is advisory and cannot expand executable scope.",
        ]
    )


def ingest_authorized_policy(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    policy_file: Path | None = None,
    fixture_browser_enabled: bool = False,
) -> BrowserPolicyIngestionResult:
    """Ingest a local policy file behind the browser controller safety boundary."""

    if not fixture_browser_enabled:
        raise BrowserFeatureGateError(
            "Phase 7 browser policy ingestion requires --enable-browser-fixture; live browser automation remains disabled"
        )

    decision = ScopeGate(loaded_scope).evaluate(
        Action.BROWSER_POLICY_INGEST.value,
        Target(kind=TargetKind.LOCAL_REPO, value=str(repo)),
    )
    if not decision.allowed:
        raise BrowserAuthorizationError(decision)

    summary = read_local_policy_summary(loaded_scope, policy_file=policy_file)
    return BrowserPolicyIngestionResult(
        repository=str(repo.expanduser().resolve(strict=False)),
        workflow_plan=build_policy_ingestion_plan(),
        policy_summary=summary,
        scope_decision=decision,
        notes=[
            "Headless-browser controller path used only a local fixture parser.",
            "No live browser, network request, live target contact, form submission, active validation, or report submission was used.",
            "Parsed policy hints remain advisory and must be reconciled by a human before scope changes.",
        ],
    )
