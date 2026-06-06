"""Gap tracker governance and Codex backlog models for Phase 14.

Phase 14 is local-only governance tooling. It parses and audits
PRODUCTION_GAP_TRACKER.md, then exports a deterministic Codex/local/CI/human
backlog. It does not close gaps, edit production readiness, inspect external
evidence contents, execute external validation, or submit reports.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

GapRiskLevel = Literal["critical", "high", "medium", "low", "unknown"]
GapTrackerCheckStatus = Literal["pass", "fail", "deferred"]


class GapTrackerEntry(BaseModel):
    """One parsed unresolved production gap entry."""

    gap_id: str
    source_section: str
    line_start: int
    line_end: int
    unique_id: str | None = None
    phase_association: str | None = None
    subsystem_association: str | None = None
    description: str | None = None
    why_incomplete: str | None = None
    why_blocked_in_chatgpt_project_mode: str | None = None
    risk_level: GapRiskLevel = "unknown"
    dependency_requirements: str | None = None
    exact_future_validation_required: str | None = None
    exact_future_tooling_environment_required: str | None = None
    recommended_future_agent_type: str | None = None
    estimated_production_impact: str | None = None
    completion_criteria: str | None = None
    rollback_considerations: str | None = None
    missing_required_fields: list[str] = Field(default_factory=list)
    raw_field_count: int = 0


class GapTrackerAuditResult(BaseModel):
    """Parsed gap tracker audit result."""

    result_version: Literal["1"] = "1"
    phase: Literal["14"] = "14"
    repository_root: str
    gap_tracker_path: str
    entries: list[GapTrackerEntry] = Field(default_factory=list)
    entry_count: int
    duplicate_gap_ids: list[str] = Field(default_factory=list)
    missing_required_field_count: int
    entries_with_missing_required_fields: list[str] = Field(default_factory=list)
    malformed_entry_ids: list[str] = Field(default_factory=list)
    ready_for_codex_backlog: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class CodexBacklogItem(BaseModel):
    """One future-executor task derived from an unresolved gap."""

    task_id: str
    gap_id: str
    priority_rank: int
    risk_level: GapRiskLevel
    phase_association: str
    subsystem_association: str
    description: str
    blocked_in_chatgpt_project_mode: str
    recommended_future_agent_type: str
    dependency_requirements: str
    exact_future_validation_required: str
    exact_future_tooling_environment_required: str
    estimated_production_impact: str
    completion_criteria: str
    rollback_considerations: str
    codex_ready: bool
    human_review_required: Literal[True] = True
    auto_gap_closure_allowed: Literal[False] = False
    production_readiness_increase_allowed: Literal[False] = False


class CodexBacklogResult(BaseModel):
    """Deterministic Codex/local/CI/human backlog export."""

    result_version: Literal["1"] = "1"
    phase: Literal["14"] = "14"
    repository_root: str
    gap_tracker_path: str
    items: list[CodexBacklogItem] = Field(default_factory=list)
    item_count: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    unknown_risk_count: int
    ready_for_codex: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class GapTrackerExportResult(BaseModel):
    """Result from exporting gap tracker governance artifacts."""

    result_version: Literal["1"] = "1"
    phase: Literal["14"] = "14"
    output_directory: str
    written_files: list[str] = Field(default_factory=list)
    gap_entry_count: int
    backlog_item_count: int
    ready_for_codex: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class GapTrackerCheck(BaseModel):
    """One Phase 14 gap tracker governance readiness check."""

    check_id: str
    status: GapTrackerCheckStatus
    summary: str
    required_for_commit: bool = True
    required_for_codex: bool = True
    required_for_production: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class GapTrackerVerificationResult(BaseModel):
    """Aggregated Phase 14 gap tracker governance verification result."""

    result_version: Literal["1"] = "1"
    phase: Literal["14"] = "14"
    source_phase: Literal["13"] = "13"
    repository_root: str
    checks: list[GapTrackerCheck] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    deferred_count: int
    required_commit_failures: int
    required_codex_failures: int
    required_production_open_items: int
    ready_for_commit: bool
    ready_for_codex: bool
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
    notes: list[str] = Field(default_factory=list)
