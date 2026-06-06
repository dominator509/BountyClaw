"""Local memory, reusable skills, and workflow-learning models for Phase 8.

Phase 8 stores only human-approved, redacted, local project memory. Memory and
skill plans are advisory: they cannot expand scope, execute tools, contact
networks, invoke live providers, launch MCP/browser runtimes, validate findings,
or submit reports.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from bountyclaw.findings.models import RedactionStatus
from bountyclaw.scope import ScopeDecision

MemoryCategory = Literal[
    "operator_preference",
    "workflow_observation",
    "program_note",
    "reporting_preference",
    "skill_feedback",
]
MemorySource = Literal[
    "human_note",
    "workflow_observation",
    "policy_note",
    "reporting_preference",
    "skill_feedback",
]
MemoryRetentionPolicy = Literal["session", "project", "persistent"]


class MemoryApproval(BaseModel):
    """Explicit human approval metadata for one memory write."""

    approved_by: str = Field(min_length=1)
    approval_note: str = Field(min_length=12)
    explicit_approval: Literal[True] = True


class MemoryRecord(BaseModel):
    """Redacted local memory record.

    The content field contains the already-redacted text. Raw source excerpts,
    raw evidence, secrets, and credentials are not valid memory material.
    """

    memory_version: Literal["1"] = "1"
    memory_id: str
    repository: str
    category: MemoryCategory
    source: MemorySource
    content: str = Field(min_length=1)
    redaction_status: RedactionStatus
    redaction_count: int = Field(ge=0)
    retention_policy: MemoryRetentionPolicy = "project"
    approval: MemoryApproval
    scope_expansion_allowed: Literal[False] = False
    tool_execution_allowed: Literal[False] = False
    network_used: Literal[False] = False
    live_llm_provider_used: Literal[False] = False
    mcp_used: Literal[False] = False
    browser_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    created_at: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class MemoryWriteResult(BaseModel):
    """Result of an approved local memory write."""

    result_version: Literal["1"] = "1"
    store_path: str
    memory: MemoryRecord
    scope_decision: ScopeDecision
    notes: list[str] = Field(default_factory=list)


class MemoryDeleteResult(BaseModel):
    """Result of deleting one memory record."""

    result_version: Literal["1"] = "1"
    store_path: str
    memory_id: str
    deleted: bool
    scope_decision: ScopeDecision
    notes: list[str] = Field(default_factory=list)


class MemoryExport(BaseModel):
    """Redacted memory export bundle."""

    export_version: Literal["1"] = "1"
    store_path: str
    repository: str
    memory_records: list[MemoryRecord] = Field(default_factory=list)
    raw_secret_material_included: Literal[False] = False
    scope_expansion_allowed: Literal[False] = False
    tool_execution_allowed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class SkillTemplate(BaseModel):
    """Reusable, non-executing workflow template."""

    skill_version: Literal["1"] = "1"
    skill_id: str
    title: str
    objective: str
    required_scope_actions: list[str] = Field(default_factory=list)
    workflow_steps: list[str] = Field(default_factory=list)
    prohibited_capabilities: list[str] = Field(default_factory=list)
    output_artifacts: list[str] = Field(default_factory=list)
    executable: Literal[False] = False
    scope_expansion_allowed: Literal[False] = False
    tool_execution_allowed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class SkillProposal(BaseModel):
    """Advisory skill plan for an authorized repository.

    A proposal evaluates the requested repository scope but does not execute the
    underlying workflow steps. Each step still requires its own explicit CLI
    command and scope-gate check.
    """

    proposal_version: Literal["1"] = "1"
    proposal_id: str
    repository: str
    template: SkillTemplate
    proposal_scope_decision: ScopeDecision
    required_action_decisions: list[ScopeDecision] = Field(default_factory=list)
    all_required_actions_authorized: bool
    executable_now: Literal[False] = False
    scope_expansion_allowed: Literal[False] = False
    tool_execution_allowed: Literal[False] = False
    network_used: Literal[False] = False
    live_llm_provider_used: Literal[False] = False
    mcp_used: Literal[False] = False
    browser_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
