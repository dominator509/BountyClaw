"""Provider-neutral model router and prompt-safety foundation."""

from .catalog import MOCK_PROVIDER_ID, provider_catalog
from .models import (
    MockModelResponse,
    ModelRequest,
    ModelRoutingDecision,
    ModelRoutingRequest,
    ModelTriageResult,
    PromptEnvelope,
    PromptInjectionSignal,
    ProviderSpec,
    RoutingPolicy,
    SanitizedPromptComponent,
)
from .prompt_safety import (
    build_finding_triage_prompt,
    detect_prompt_injection_signals,
    render_prompt_for_provider,
    sanitize_prompt_component,
)
from .router import ModelRoutingError, route_model_request
from .service import (
    ModelAuthorizationError,
    ModelFeatureGateError,
    ModelFindingNotFoundError,
    triage_authorized_finding,
)

__all__ = [
    "MOCK_PROVIDER_ID",
    "MockModelResponse",
    "ModelAuthorizationError",
    "ModelFeatureGateError",
    "ModelFindingNotFoundError",
    "ModelRequest",
    "ModelRoutingDecision",
    "ModelRoutingError",
    "ModelRoutingRequest",
    "ModelTriageResult",
    "PromptEnvelope",
    "PromptInjectionSignal",
    "ProviderSpec",
    "RoutingPolicy",
    "SanitizedPromptComponent",
    "build_finding_triage_prompt",
    "detect_prompt_injection_signals",
    "provider_catalog",
    "render_prompt_for_provider",
    "route_model_request",
    "sanitize_prompt_component",
    "triage_authorized_finding",
]
