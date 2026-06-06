"""Provider-neutral model-routing and prompt-safety models for Phase 5.

Phase 5 introduces deterministic, offline-safe model abstractions. It does not
perform live provider calls. All prompt payload construction must happen after
redaction and untrusted-content isolation.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ModelTaskType = Literal[
    "finding_triage",
    "false_positive_review",
    "remediation_guidance",
    "report_outline",
]
PrivacySensitivity = Literal["low", "medium", "high", "maximum"]
ProviderStatus = Literal["mock_available", "metadata_only_live_disabled"]
InjectionSignalSeverity = Literal["low", "medium", "high"]


class ProviderSpec(BaseModel):
    """Static metadata for a model provider option.

    Non-mock providers are cataloged for future routing policy, but Phase 5 keeps
    live calls disabled and uses mocked providers for validation.
    """

    provider_id: str
    display_name: str
    default_model: str
    status: ProviderStatus
    supports_json: bool = True
    supports_local_execution: bool = False
    supports_live_api: bool = False
    supported_task_types: set[ModelTaskType] = Field(default_factory=set)
    notes: list[str] = Field(default_factory=list)


class RoutingPolicy(BaseModel):
    """Fail-closed model-routing policy."""

    allow_live_provider_calls: Literal[False] = False
    require_mock_provider: Literal[True] = True
    require_redacted_payload: Literal[True] = True
    require_untrusted_content_isolation: Literal[True] = True
    max_prompt_characters: int = Field(default=20_000, ge=1)


class ModelRoutingRequest(BaseModel):
    """Inputs used to select a provider/model."""

    task_type: ModelTaskType
    privacy_sensitivity: PrivacySensitivity = "high"
    requested_provider_id: str | None = None
    require_json: bool = True
    max_prompt_characters: int = Field(default=20_000, ge=1)


class ModelRoutingDecision(BaseModel):
    """Deterministic provider/model selection decision."""

    decision_version: Literal["1"] = "1"
    task_type: ModelTaskType
    provider_id: str
    model_id: str
    provider_status: ProviderStatus
    live_provider_call_allowed: Literal[False] = False
    live_provider_call_used: Literal[False] = False
    prompt_redaction_required: Literal[True] = True
    untrusted_content_isolation_required: Literal[True] = True
    reasons: list[str] = Field(default_factory=list)


class PromptInjectionSignal(BaseModel):
    """Non-sensitive metadata for suspicious untrusted prompt content."""

    signal_id: str
    severity: InjectionSignalSeverity
    description: str


class SanitizedPromptComponent(BaseModel):
    """One redacted, explicitly untrusted prompt component."""

    label: str
    redacted_text: str
    untrusted: Literal[True] = True
    delimiter: str
    redaction_count: int = Field(default=0, ge=0)
    injection_signals: list[PromptInjectionSignal] = Field(default_factory=list)


class PromptEnvelope(BaseModel):
    """Policy-bound prompt payload passed to provider clients."""

    envelope_version: Literal["1"] = "1"
    task_type: ModelTaskType
    system_policy: str
    safety_policy: str
    untrusted_components: list[SanitizedPromptComponent] = Field(default_factory=list)
    total_redaction_count: int = Field(default=0, ge=0)
    injection_signal_count: int = Field(default=0, ge=0)
    prompt_character_count: int = Field(default=0, ge=0)
    payload_redacted: Literal[True] = True
    untrusted_content_isolated: Literal[True] = True
    network_required: Literal[False] = False
    llm_live_call_allowed: Literal[False] = False
    mcp_required: Literal[False] = False
    browser_required: Literal[False] = False
    active_validation_allowed: Literal[False] = False
    report_submission_allowed: Literal[False] = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class ModelRequest(BaseModel):
    """A routed, sanitized model request."""

    request_version: Literal["1"] = "1"
    request_id: str
    routing_decision: ModelRoutingDecision
    prompt_envelope: PromptEnvelope


class MockModelResponse(BaseModel):
    """Deterministic offline response from the Phase 5 mock provider."""

    response_version: Literal["1"] = "1"
    provider_id: str
    model_id: str
    live_provider_call_used: Literal[False] = False
    response_format: Literal["json"] = "json"
    content: dict[str, Any] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)


class ModelTriageResult(BaseModel):
    """Scope-gated, mocked model triage result for a stored canonical finding."""

    triage_version: Literal["1"] = "1"
    request_id: str
    canonical_finding_id: str
    repository: str
    store_path: str
    routing_decision: ModelRoutingDecision
    prompt_safety: PromptEnvelope
    response: MockModelResponse
    network_used: Literal[False] = False
    live_llm_provider_used: Literal[False] = False
    mcp_used: Literal[False] = False
    browser_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
