"""Static model provider catalog for Phase 5 routing."""

from __future__ import annotations

from .models import ModelTaskType, ProviderSpec

MOCK_PROVIDER_ID = "mock.local"


def provider_catalog() -> dict[str, ProviderSpec]:
    """Return supported provider metadata.

    Only ``mock.local`` is executable in Phase 5. Other providers are registered
    as metadata-only options for deterministic future routing and Codex/local
    handoff without enabling network calls or credentials in this environment.
    """

    all_tasks: set[ModelTaskType] = {
        "finding_triage",
        "false_positive_review",
        "remediation_guidance",
        "report_outline",
    }
    return {
        MOCK_PROVIDER_ID: ProviderSpec(
            provider_id=MOCK_PROVIDER_ID,
            display_name="Local deterministic mock provider",
            default_model="mock-bountyclaw-triage-v1",
            status="mock_available",
            supports_local_execution=True,
            supports_live_api=False,
            supported_task_types=all_tasks,
            notes=["Executable in Phase 5; no network, credential, or live model call is used."],
        ),
        "openai": ProviderSpec(
            provider_id="openai",
            display_name="OpenAI",
            default_model="configured-by-user",
            status="metadata_only_live_disabled",
            supports_live_api=True,
            supported_task_types=all_tasks,
            notes=["Cataloged only; live API calls are disabled in Phase 5."],
        ),
        "anthropic": ProviderSpec(
            provider_id="anthropic",
            display_name="Anthropic",
            default_model="configured-by-user",
            status="metadata_only_live_disabled",
            supports_live_api=True,
            supported_task_types=all_tasks,
            notes=["Cataloged only; live API calls are disabled in Phase 5."],
        ),
        "google": ProviderSpec(
            provider_id="google",
            display_name="Google Gemini",
            default_model="configured-by-user",
            status="metadata_only_live_disabled",
            supports_live_api=True,
            supported_task_types=all_tasks,
            notes=["Cataloged only; live API calls are disabled in Phase 5."],
        ),
        "mistral": ProviderSpec(
            provider_id="mistral",
            display_name="Mistral AI",
            default_model="configured-by-user",
            status="metadata_only_live_disabled",
            supports_live_api=True,
            supported_task_types=all_tasks,
            notes=["Cataloged only; live API calls are disabled in Phase 5."],
        ),
        "cohere": ProviderSpec(
            provider_id="cohere",
            display_name="Cohere",
            default_model="configured-by-user",
            status="metadata_only_live_disabled",
            supports_live_api=True,
            supported_task_types=all_tasks,
            notes=["Cataloged only; live API calls are disabled in Phase 5."],
        ),
        "groq": ProviderSpec(
            provider_id="groq",
            display_name="Groq",
            default_model="configured-by-user",
            status="metadata_only_live_disabled",
            supports_live_api=True,
            supported_task_types=all_tasks,
            notes=["Cataloged only; live API calls are disabled in Phase 5."],
        ),
        "ollama": ProviderSpec(
            provider_id="ollama",
            display_name="Ollama/local model server",
            default_model="configured-by-user",
            status="metadata_only_live_disabled",
            supports_local_execution=True,
            supports_live_api=True,
            supported_task_types=all_tasks,
            notes=[
                "Cataloged only; even local server calls are disabled until a later governed phase."
            ],
        ),
    }
