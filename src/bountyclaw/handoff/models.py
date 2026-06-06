"""External-validation handoff models for Phase 11.

Phase 11 is a local-only bridge from ChatGPT Project Mode to Codex/local/CI/
human execution. It does not execute external validation. It creates deterministic
plans and evidence templates that make the remaining production work auditable.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

HandoffRiskLevel = Literal["low", "medium", "high", "critical"]
HandoffTaskCategory = Literal[
    "governance",
    "ci_cd",
    "packaging",
    "security_tools",
    "scanner_sandbox",
    "ai_safety",
    "mcp_browser",
    "report_quality",
    "operations",
    "release_governance",
]
HandoffCheckStatus = Literal["pass", "fail", "deferred"]


class HandoffTask(BaseModel):
    """A deterministic external-validation task for a future executor."""

    task_id: str
    category: HandoffTaskCategory
    title: str
    purpose: str
    related_gap_ids: list[str] = Field(default_factory=list)
    prerequisite_files: list[str] = Field(default_factory=list)
    environment_required: str
    recommended_future_agent_type: str
    risk_level: HandoffRiskLevel
    exact_commands_or_steps: list[str] = Field(default_factory=list)
    expected_evidence_artifacts: list[str] = Field(default_factory=list)
    completion_criteria: list[str] = Field(default_factory=list)
    blocked_in_chatgpt_reason: str
    prohibited_claims_until_complete: list[str] = Field(default_factory=list)
    rollback_considerations: str


class CodexHandoffPlan(BaseModel):
    """Codex/local/CI/human handoff plan for post-Phase-10 validation."""

    plan_version: Literal["1"] = "1"
    phase: Literal["11"] = "11"
    source_phase: Literal["10"] = "10"
    title: str = "BountyClaw Phase 11 External Validation Handoff Plan"
    repository_root: str
    tasks: list[HandoffTask] = Field(default_factory=list)
    task_count: int
    ready_for_codex: bool
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class EvidenceArtifactTemplate(BaseModel):
    """Expected artifact that a future environment must produce."""

    artifact_id: str
    filename: str
    producer_task_id: str
    validates_gap_ids: list[str] = Field(default_factory=list)
    required_for_production: bool = True
    sensitive_handling: str
    acceptance_criteria: list[str] = Field(default_factory=list)


class EvidenceTemplate(BaseModel):
    """Deterministic template for future production-validation evidence."""

    template_version: Literal["1"] = "1"
    phase: Literal["11"] = "11"
    title: str = "BountyClaw External Validation Evidence Template"
    artifacts: list[EvidenceArtifactTemplate] = Field(default_factory=list)
    artifact_count: int
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class HandoffExportResult(BaseModel):
    """Result from writing a local handoff package."""

    result_version: Literal["1"] = "1"
    phase: Literal["11"] = "11"
    output_directory: str
    written_files: list[str] = Field(default_factory=list)
    task_count: int
    artifact_count: int
    ready_for_codex: bool
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class HandoffCheck(BaseModel):
    """One local handoff-readiness check."""

    check_id: str
    category: HandoffTaskCategory
    status: HandoffCheckStatus
    summary: str
    required_for_commit: bool = True
    required_for_codex: bool = True
    required_for_production: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class HandoffVerificationResult(BaseModel):
    """Aggregated local handoff-readiness verification."""

    result_version: Literal["1"] = "1"
    phase: Literal["11"] = "11"
    repository_root: str
    checks: list[HandoffCheck] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    deferred_count: int
    required_commit_failures: int
    required_codex_failures: int
    required_production_open_items: int
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    hosted_ci_executed: Literal[False] = False
    clean_install_validation_executed: Literal[False] = False
    live_provider_validation_executed: Literal[False] = False
    mcp_browser_runtime_validation_executed: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
