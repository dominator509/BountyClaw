"""Production-hardening validation models for Phase 10."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

HardeningCheckStatus = Literal["pass", "fail", "deferred"]
HardeningCategory = Literal[
    "governance",
    "release",
    "safety",
    "redaction",
    "prompt_safety",
    "scope",
    "packaging",
    "environment_limited",
]


class HardeningChecklistItem(BaseModel):
    """A Phase 10 hardening gate that must be reviewed before production claims."""

    item_id: str
    category: HardeningCategory
    title: str
    description: str
    required_for_commit: bool = True
    required_for_production: bool = True
    owner_agent: str
    environment_required: str = "local ChatGPT/Codex workspace"
    completion_criteria: list[str] = Field(default_factory=list)


class HardeningChecklistResult(BaseModel):
    """Deterministic Phase 10 hardening checklist."""

    checklist_version: Literal["1"] = "1"
    phase: Literal["10"] = "10"
    title: str = "BountyClaw Phase 10 Production-Hardening Checklist"
    items: list[HardeningChecklistItem] = Field(default_factory=list)
    network_used: Literal[False] = False
    external_validation_executed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class HardeningCheck(BaseModel):
    """One hardening verification result."""

    check_id: str
    category: HardeningCategory
    status: HardeningCheckStatus
    summary: str
    required_for_commit: bool = True
    required_for_production: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class RedactionCorpusCase(BaseModel):
    """One deterministic redaction-corpus fixture."""

    case_id: str
    description: str
    input_text: str
    expected_secret_types: list[str]
    expected_raw_absent: list[str]


class RedactionCorpusCaseResult(BaseModel):
    """Result for one redaction-corpus fixture."""

    case_id: str
    passed: bool
    redaction_count: int
    redaction_status: str
    detected_secret_types: list[str]
    raw_absence_confirmed: bool
    evidence: list[str] = Field(default_factory=list)


class RedactionCorpusResult(BaseModel):
    """Aggregated deterministic redaction-corpus result."""

    result_version: Literal["1"] = "1"
    phase: Literal["10"] = "10"
    case_results: list[RedactionCorpusCaseResult] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    passed: bool
    network_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class PromptSafetyCorpusCase(BaseModel):
    """One deterministic prompt-safety fixture."""

    case_id: str
    label: str
    input_text: str
    expected_min_signal_count: int
    expected_signal_ids: list[str] = Field(default_factory=list)
    expected_redaction_count_min: int = 0


class PromptSafetyCorpusCaseResult(BaseModel):
    """Result for one prompt-safety fixture."""

    case_id: str
    passed: bool
    signal_count: int
    redaction_count: int
    detected_signal_ids: list[str]
    delimiter: str
    evidence: list[str] = Field(default_factory=list)


class PromptSafetyCorpusResult(BaseModel):
    """Aggregated deterministic prompt-safety corpus result."""

    result_version: Literal["1"] = "1"
    phase: Literal["10"] = "10"
    case_results: list[PromptSafetyCorpusCaseResult] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    passed: bool
    network_used: Literal[False] = False
    live_llm_provider_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ExternalValidationTask(BaseModel):
    """A production validation task that cannot be completed inside ChatGPT Project Mode."""

    task_id: str
    category: str
    title: str
    description: str
    why_blocked_in_chatgpt: str
    risk_level: Literal["low", "medium", "high", "critical"]
    dependency_requirements: list[str] = Field(default_factory=list)
    exact_future_validation_required: str
    exact_future_tooling_environment_required: str
    recommended_future_agent_type: str
    completion_criteria: list[str] = Field(default_factory=list)
    rollback_considerations: str


class ExternalValidationPlan(BaseModel):
    """Deferred external-validation plan for Phase 10 handoff."""

    plan_version: Literal["1"] = "1"
    phase: Literal["10"] = "10"
    tasks: list[ExternalValidationTask] = Field(default_factory=list)
    task_count: int
    network_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class HardeningVerificationResult(BaseModel):
    """Aggregated Phase 10 local hardening-verification result."""

    result_version: Literal["1"] = "1"
    phase: Literal["10"] = "10"
    repository_root: str
    checks: list[HardeningCheck] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    deferred_count: int
    required_commit_failures: int
    required_production_open_items: int
    ready_for_commit: bool
    ready_for_production: bool
    external_validation_executed: Literal[False] = False
    hosted_ci_executed: Literal[False] = False
    clean_install_validation_executed: Literal[False] = False
    package_publish_executed: Literal[False] = False
    network_used: Literal[False] = False
    live_llm_provider_used: Literal[False] = False
    mcp_used: Literal[False] = False
    browser_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
