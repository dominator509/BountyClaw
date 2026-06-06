"""Headless browser controller foundation models for Phase 7.

Phase 7 does not launch Playwright, navigate live pages, submit forms, or contact
third-party targets. It provides a safe local policy-ingestion seam that future
browser automation must preserve.
"""

from __future__ import annotations

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from bountyclaw.policy import PolicyDocumentSummary
from bountyclaw.scope import ScopeDecision

BrowserWorkflow = Literal["policy_ingestion"]


def _default_allowed_source_kinds() -> list[Literal["local_file"]]:
    return ["local_file"]


class BrowserWorkflowPlan(BaseModel):
    """Declared browser workflow constraints for a Phase 7 action."""

    plan_version: Literal["1"] = "1"
    workflow: BrowserWorkflow = "policy_ingestion"
    requires_scope_action: Literal["browser.policy_ingest"] = "browser.policy_ingest"
    live_browser_allowed: Literal[False] = False
    network_allowed: Literal[False] = False
    live_target_contact_allowed: Literal[False] = False
    form_submission_allowed: Literal[False] = False
    report_submission_allowed: Literal[False] = False
    scope_expansion_allowed: Literal[False] = False
    allowed_source_kinds: list[Literal["local_file"]] = Field(
        default_factory=_default_allowed_source_kinds
    )
    notes: list[str] = Field(default_factory=list)


class BrowserPolicyIngestionResult(BaseModel):
    """Result from fixture-only browser policy ingestion."""

    result_version: Literal["1"] = "1"
    ingestion_id: str = Field(default_factory=lambda: str(uuid4()))
    repository: str
    workflow_plan: BrowserWorkflowPlan
    policy_summary: PolicyDocumentSummary
    scope_decision: ScopeDecision
    fixture_parser_used: Literal[True] = True
    live_browser_used: Literal[False] = False
    network_used: Literal[False] = False
    live_target_contact_used: Literal[False] = False
    form_submission_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    submission_allowed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
