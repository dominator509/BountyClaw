"""Scope-gated mocked model triage service for Phase 5."""

from __future__ import annotations

import hashlib
from pathlib import Path

from bountyclaw.findings import EvidenceStore, ensure_store_path_outside_repository
from bountyclaw.scope import ScopeGate, Target, TargetKind
from bountyclaw.scope.loader import LoadedScopeManifest
from bountyclaw.scope.models import ScopeDecision

from .models import ModelRequest, ModelRoutingRequest, ModelTriageResult
from .prompt_safety import build_finding_triage_prompt
from .providers import provider_client_for
from .router import route_model_request


class ModelAuthorizationError(RuntimeError):
    """Raised when model triage is not scope-authorized."""

    def __init__(self, decision: ScopeDecision) -> None:
        self.decision = decision
        super().__init__("; ".join(decision.reasons))


class ModelFeatureGateError(RuntimeError):
    """Raised when model invocation is not explicitly enabled."""


class ModelFindingNotFoundError(RuntimeError):
    """Raised when a requested finding is absent from the evidence store."""


def triage_authorized_finding(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    store_path: Path,
    finding_id: str,
    provider_id: str | None = None,
    mock_model_enabled: bool = False,
) -> ModelTriageResult:
    """Build a redacted prompt and invoke the Phase 5 mock provider.

    This service never performs live model provider calls. It exists to prove
    routing, scope-gating, redaction, prompt isolation, and mocked output shape.
    """

    if not mock_model_enabled:
        raise ModelFeatureGateError(
            "model triage requires the explicit --enable-mock-model flag in Phase 5"
        )

    _require_allowed(loaded_scope, repo, action="model.triage")
    resolved_store = ensure_store_path_outside_repository(store_path, repo)
    bundle = EvidenceStore(resolved_store).get_finding_bundle(finding_id)
    if bundle is None:
        raise ModelFindingNotFoundError(f"finding not found in evidence store: {finding_id}")

    envelope = build_finding_triage_prompt(
        finding=bundle.finding,
        evidence_records=bundle.evidence_records,
        program_name=loaded_scope.manifest.program.name,
    )
    routing_decision = route_model_request(
        ModelRoutingRequest(
            task_type="finding_triage",
            privacy_sensitivity="high",
            requested_provider_id=provider_id,
            max_prompt_characters=20_000,
        )
    )
    request = ModelRequest(
        request_id=_request_id(
            bundle.finding.canonical_finding_id, envelope.prompt_character_count
        ),
        routing_decision=routing_decision,
        prompt_envelope=envelope,
    )
    response = provider_client_for(routing_decision.provider_id).generate(request)
    return ModelTriageResult(
        request_id=request.request_id,
        canonical_finding_id=bundle.finding.canonical_finding_id,
        repository=str(repo.expanduser().resolve(strict=False)),
        store_path=str(resolved_store),
        routing_decision=routing_decision,
        prompt_safety=envelope,
        response=response,
        notes=[
            "Scope-approved Phase 5 mocked model triage completed.",
            "Prompt payload was redacted and isolated before provider invocation.",
            "Only the deterministic mock provider was used; live model calls remain disabled.",
        ],
    )


def _require_allowed(
    loaded_scope: LoadedScopeManifest, repo: Path, *, action: str
) -> ScopeDecision:
    decision = ScopeGate(loaded_scope).evaluate(
        action=action,
        target=Target(kind=TargetKind.LOCAL_REPO, value=str(repo)),
    )
    if not decision.allowed:
        raise ModelAuthorizationError(decision)
    return decision


def _request_id(finding_id: str, prompt_character_count: int) -> str:
    material = f"{finding_id}|{prompt_character_count}|phase5.mock.triage"
    return f"bcmodelreq-sha256:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:32]}"
