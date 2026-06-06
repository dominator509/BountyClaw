"""Release-control models for Phase 9.

Phase 9 defines deterministic CI/CD, packaging, and release governance checks
that can run locally without contacting external services. External CI execution,
clean-room package installs, hosted artifact publication, and production rollback
drills remain explicitly deferred until a real repository/runner environment is
available.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

ReleaseCheckStatus = Literal["pass", "fail", "deferred"]
ReleaseGateCategory = Literal[
    "governance",
    "ci_cd",
    "quality",
    "security",
    "packaging",
    "rollback",
    "environment_limited",
]


class ReleaseChecklistItem(BaseModel):
    """A release gate that should be reviewed before a commit or release."""

    item_id: str
    category: ReleaseGateCategory
    title: str
    description: str
    required_for_commit: bool = True
    required_for_external_release: bool = True
    owner_agent: str
    environment_required: str = "local ChatGPT/Codex workspace"
    completion_criteria: list[str] = Field(default_factory=list)


class ReleaseChecklistResult(BaseModel):
    """Phase 9 release checklist output."""

    checklist_version: Literal["1"] = "1"
    phase: Literal["9"] = "9"
    title: str = "BountyClaw Phase 9 Release Control Checklist"
    items: list[ReleaseChecklistItem] = Field(default_factory=list)
    external_ci_executed: Literal[False] = False
    network_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ReleaseCheck(BaseModel):
    """Result for one deterministic release-control verification."""

    check_id: str
    category: ReleaseGateCategory
    status: ReleaseCheckStatus
    summary: str
    required_for_commit: bool = True
    required_for_external_release: bool = True
    evidence: list[str] = Field(default_factory=list)
    deferred_reason: str | None = None
    future_validation_required: str | None = None
    future_environment_required: str | None = None


class ReleaseVerificationResult(BaseModel):
    """Aggregated release-readiness result.

    A result may be commit-ready while still not externally release-ready when
    environment-limited checks are deferred.
    """

    result_version: Literal["1"] = "1"
    phase: Literal["9"] = "9"
    repository_root: str
    checks: list[ReleaseCheck] = Field(default_factory=list)
    passed_count: int
    failed_count: int
    deferred_count: int
    required_commit_failures: int
    required_external_release_deferred: int
    ready_for_commit: bool
    ready_for_external_release: bool
    external_ci_executed: Literal[False] = False
    package_publish_executed: Literal[False] = False
    clean_install_validation_executed: bool = False
    network_used: Literal[False] = False
    live_llm_provider_used: Literal[False] = False
    mcp_used: Literal[False] = False
    browser_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class ReleaseRollbackPlan(BaseModel):
    """Rollback plan for Phase 9 release-control artifacts."""

    plan_version: Literal["1"] = "1"
    phase: Literal["9"] = "9"
    rollback_target: str = "Phase 8 memory/skills baseline"
    rollback_ready: Literal[True] = True
    external_resources_created: Literal[False] = False
    steps: list[str] = Field(default_factory=list)
    preserved_fallbacks: list[str] = Field(default_factory=list)
    validation_after_rollback: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)
