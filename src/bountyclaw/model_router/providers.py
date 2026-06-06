"""Mock provider client for Phase 5 model-routing validation."""

from __future__ import annotations

from typing import Protocol

from .catalog import MOCK_PROVIDER_ID
from .models import MockModelResponse, ModelRequest, PromptEnvelope
from .prompt_safety import render_prompt_for_provider


class ModelProviderClient(Protocol):
    """Protocol for future provider adapters."""

    def generate(self, request: ModelRequest) -> MockModelResponse:
        """Generate a response from a routed model request."""


class MockModelProviderClient:
    """Deterministic offline provider used for Phase 5 tests and CLI smoke checks."""

    def generate(self, request: ModelRequest) -> MockModelResponse:
        envelope = request.prompt_envelope
        rendered = render_prompt_for_provider(envelope)
        content = _deterministic_triage_content(envelope)
        content["rendered_prompt_sha256_material_length"] = len(rendered)
        return MockModelResponse(
            provider_id=MOCK_PROVIDER_ID,
            model_id=request.routing_decision.model_id,
            content=content,
            notes=[
                "Mock provider returned deterministic offline triage content.",
                "No live model provider, network, MCP, browser, active validation, or report submission was used.",
                "Untrusted prompt sections were not treated as instructions.",
            ],
        )


def _deterministic_triage_content(envelope: PromptEnvelope) -> dict[str, object]:
    by_label = {
        component.label: component.redacted_text for component in envelope.untrusted_components
    }
    injection_labels = [
        component.label
        for component in envelope.untrusted_components
        if component.injection_signals
    ]
    return {
        "triage_status": "needs_human_review",
        "finding_id": by_label.get("finding.id", "unknown"),
        "summary": by_label.get("finding.title", "Untitled finding"),
        "severity_input": by_label.get("finding.severity", "unknown"),
        "confidence_input": by_label.get("finding.confidence", "unknown"),
        "recommended_next_steps": [
            "Review the redacted evidence manually.",
            "Confirm affected code and exploitability without destructive testing.",
            "Collect additional non-sensitive evidence before report drafting if needed.",
        ],
        "limitations": [
            "This is mocked offline assistance, not a live LLM judgment.",
            "No active validation or target interaction was performed.",
            "Do not submit a bounty report without human review.",
        ],
        "prompt_safety": {
            "redaction_count": envelope.total_redaction_count,
            "injection_signal_count": envelope.injection_signal_count,
            "injection_signal_component_labels": injection_labels,
            "untrusted_content_isolated": envelope.untrusted_content_isolated,
        },
    }


def provider_client_for(provider_id: str) -> ModelProviderClient:
    """Return a provider client if executable in Phase 5."""

    if provider_id == MOCK_PROVIDER_ID:
        return MockModelProviderClient()
    raise ValueError(f"provider is not executable in Phase 5: {provider_id}")
