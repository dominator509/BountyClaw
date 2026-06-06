"""Validation baseline snapshot models for Phase 16.

Phase 16 is local-only governance tooling. It creates a metadata-only source
snapshot so future Codex/local/CI/human validation evidence can be tied to an
exact source baseline. It hashes source-controlled files but never reads or
exports private validation evidence contents, closes gaps, raises production
readiness, contacts targets, calls live providers, launches MCP/browser runtimes,
or submits bounty reports.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

BaselineCategory = Literal[
    "governance_markdown",
    "phase_subroadmap",
    "markdown_review",
    "documentation",
    "python_source",
    "python_test",
    "script",
    "ci_config",
    "package_config",
    "configuration",
    "other",
]
BaselineCheckStatus = Literal["pass", "fail", "deferred"]


class BaselineFileRecord(BaseModel):
    """Hash-only record for one file in the validation baseline."""

    path: str
    sha256: str
    size_bytes: int
    category: BaselineCategory
    raw_contents_included: Literal[False] = False


class ValidationBaselineManifest(BaseModel):
    """Deterministic source snapshot for future external validation evidence."""

    manifest_version: Literal["1"] = "1"
    phase: Literal["16"] = "16"
    source_phase: Literal["15"] = "15"
    title: str = "BountyClaw Validation Baseline Manifest"
    repository_root: str
    baseline_id: str
    files: list[BaselineFileRecord] = Field(default_factory=list)
    file_count: int
    markdown_file_count: int
    python_file_count: int
    governance_file_count: int
    excluded_path_count: int
    excluded_path_samples: list[str] = Field(default_factory=list)
    ready_for_external_validation_reference: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ValidationBaselineExportResult(BaseModel):
    """Result from exporting the baseline manifest package."""

    result_version: Literal["1"] = "1"
    phase: Literal["16"] = "16"
    output_directory: str
    baseline_id: str
    written_files: list[str] = Field(default_factory=list)
    file_count: int
    ready_for_external_validation_reference: bool
    ready_for_gap_closure: Literal[False] = False
    ready_for_production: Literal[False] = False
    network_used: Literal[False] = False
    external_actions_executed: Literal[False] = False
    raw_evidence_contents_included: Literal[False] = False
    raw_source_contents_included: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ValidationBaselineCheck(BaseModel):
    """One local Phase 16 baseline-readiness check."""

    check_id: str
    status: BaselineCheckStatus
    summary: str
    required_for_commit: bool = True
    required_for_codex: bool = True
    required_for_production: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class ValidationBaselineVerificationResult(BaseModel):
    """Aggregated local Phase 16 baseline verification result."""

    result_version: Literal["1"] = "1"
    phase: Literal["16"] = "16"
    source_phase: Literal["15"] = "15"
    repository_root: str
    baseline_id: str
    checks: list[ValidationBaselineCheck] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    deferred_count: int
    required_commit_failures: int
    required_codex_failures: int
    required_production_open_items: int
    ready_for_commit: bool
    ready_for_codex: bool
    ready_for_external_validation_reference: bool
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
