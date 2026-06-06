"""Deterministic model-routing policy for Phase 5."""

from __future__ import annotations

from .catalog import MOCK_PROVIDER_ID, provider_catalog
from .models import ModelRoutingDecision, ModelRoutingRequest, RoutingPolicy


class ModelRoutingError(RuntimeError):
    """Raised when routing would violate Phase 5 policy."""


def route_model_request(
    request: ModelRoutingRequest,
    *,
    policy: RoutingPolicy | None = None,
) -> ModelRoutingDecision:
    """Select a model provider without enabling live API calls."""

    active_policy = policy or RoutingPolicy()
    catalog = provider_catalog()
    requested_provider_id = request.requested_provider_id or MOCK_PROVIDER_ID
    provider = catalog.get(requested_provider_id)
    if provider is None:
        raise ModelRoutingError(f"unknown model provider: {requested_provider_id}")

    if request.task_type not in provider.supported_task_types:
        raise ModelRoutingError(
            f"provider {provider.provider_id} does not support task {request.task_type}"
        )

    if active_policy.require_mock_provider and provider.provider_id != MOCK_PROVIDER_ID:
        raise ModelRoutingError(
            "Phase 5 permits mocked provider execution only; "
            f"requested provider is metadata-only: {provider.provider_id}"
        )

    if provider.supports_live_api and not active_policy.allow_live_provider_calls:
        raise ModelRoutingError(
            f"live provider calls are disabled in Phase 5: {provider.provider_id}"
        )

    if request.max_prompt_characters > active_policy.max_prompt_characters:
        raise ModelRoutingError("requested prompt budget exceeds Phase 5 routing policy")

    reasons = [
        "Phase 5 routing is provider-neutral but live calls are disabled by policy.",
        "Selected the deterministic local mock provider for offline validation.",
        "Prompt payloads must be redacted and isolate untrusted content before provider invocation.",
    ]
    if request.privacy_sensitivity in {"high", "maximum"}:
        reasons.append("High privacy sensitivity requires offline/mock routing in Phase 5.")

    return ModelRoutingDecision(
        task_type=request.task_type,
        provider_id=provider.provider_id,
        model_id=provider.default_model,
        provider_status=provider.status,
        reasons=reasons,
    )
