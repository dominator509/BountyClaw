"""Phase 18 readiness dashboard and external executor index models.

The readiness dashboard is local-only governance tooling. It consolidates
existing release, hardening, handoff, evidence, review, gap tracker, runbook,
baseline, and closure-gate metadata into one operator-facing status report. It
never executes external validation, inspects raw evidence contents, closes gaps,
changes production readiness, contacts targets, or submits bounty reports.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

DashboardCheckStatus = Literal["pass", "fail", "deferred"]
DashboardSubsystemKind = Literal[
    "release",
    "hardening",
    "handoff",
    "validation_evidence",
    "evidence_review",
    "gap_tracker",
    "validation_runbook",
    "validation_baseline",
    "closure_gate",
]


class DashboardSubsystemStatus(BaseModel):
    """One consolidated governance subsystem status."""

    subsystem_id: str
    kind: DashboardSubsystemKind
    source_phase: str
    title: str
    verify_command: str
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_production: Literal[False] = False
    passed_count: int
    failed_count: int
    deferred_count: int
    production_open_items: int
    notes: list[str] = Field(default_factory=list)


class ExternalExecutorCommand(BaseModel):
    """One future external-executor command sequence item."""

    command_id: str
    order: int
    title: str
    command: str
    purpose: str
    output_path: str | None = None
    related_phases: list[str] = Field(default_factory=list)
    related_gap_ids: list[str] = Field(default_factory=list)
    required_environment: str
    expected_artifact_kind: str
    raw_evidence_contents_included: Literal[False] = False
    closes_gaps: Literal[False] = False
    changes_production_readiness: Literal[False] = False


class ReadinessDashboard(BaseModel):
    """Aggregate local readiness dashboard for future Codex/local/CI handoff."""

    result_version: Literal["1"] = "1"
    phase: Literal["18"] = "18"
    source_phase: Literal["17"] = "17"
    repository_root: str
    roadmap_position: str
    production_readiness_percent: int
    completed_phase_count: int
    incomplete_phase_count: int
    gap_entry_count: int
    high_risk_gap_count: int
    medium_risk_gap_count: int
    low_risk_gap_count: int
    unknown_risk_gap_count: int
    subsystem_statuses: list[DashboardSubsystemStatus] = Field(default_factory=list)
    external_executor_commands: list[ExternalExecutorCommand] = Field(default_factory=list)
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_external_executor: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    hosted_ci_executed: Literal[False] = False
    clean_install_validation_executed: Literal[False] = False
    live_provider_validation_executed: Literal[False] = False
    mcp_browser_runtime_validation_executed: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ExternalExecutorIndex(BaseModel):
    """Standalone ordered index for future external validation execution."""

    result_version: Literal["1"] = "1"
    phase: Literal["18"] = "18"
    source_phase: Literal["17"] = "17"
    repository_root: str
    command_count: int
    commands: list[ExternalExecutorCommand] = Field(default_factory=list)
    ready_for_external_executor: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ReadinessDashboardExportResult(BaseModel):
    """Result from exporting the Phase 18 dashboard package."""

    result_version: Literal["1"] = "1"
    phase: Literal["18"] = "18"
    source_phase: Literal["17"] = "17"
    output_directory: str
    written_files: list[str] = Field(default_factory=list)
    baseline_id: str
    production_readiness_percent: int
    subsystem_count: int
    command_count: int
    gap_entry_count: int
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_external_executor: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ReadinessDashboardCheck(BaseModel):
    """One local Phase 18 readiness-dashboard check."""

    check_id: str
    status: DashboardCheckStatus
    summary: str
    required_for_commit: bool = True
    required_for_codex: bool = True
    required_for_production: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class ReadinessDashboardVerificationResult(BaseModel):
    """Aggregated local Phase 18 readiness-dashboard verification result."""

    result_version: Literal["1"] = "1"
    phase: Literal["18"] = "18"
    source_phase: Literal["17"] = "17"
    repository_root: str
    baseline_id: str
    checks: list[ReadinessDashboardCheck] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    deferred_count: int
    required_commit_failures: int
    required_codex_failures: int
    required_production_open_items: int
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_external_executor: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    hosted_ci_executed: Literal[False] = False
    clean_install_validation_executed: Literal[False] = False
    live_provider_validation_executed: Literal[False] = False
    mcp_browser_runtime_validation_executed: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
