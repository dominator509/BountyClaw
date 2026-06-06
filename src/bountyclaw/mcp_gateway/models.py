"""Policy-bound MCP gateway models for Phase 7.

Phase 7 implements only metadata and local fixture-style tool invocation. It does
not launch external MCP servers, execute unregistered tools, contact live
network targets, or submit reports.
"""

from __future__ import annotations

from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field

from bountyclaw.policy import PolicyDocumentSummary
from bountyclaw.scope import ScopeDecision

McpServerStatus = Literal["fixture_only", "metadata_only", "disabled"]
McpTransportKind = Literal["builtin_fixture", "stdio", "http"]
McpToolSafetyLevel = Literal["local_policy_fixture"]


class McpServerDefinition(BaseModel):
    """Registered MCP server metadata."""

    server_id: str
    display_name: str
    status: McpServerStatus
    transport: McpTransportKind
    registered_tools: list[str] = Field(default_factory=list)
    live_process_allowed: Literal[False] = False
    network_allowed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)


class McpToolDefinition(BaseModel):
    """Allowlisted MCP tool metadata."""

    tool_id: str
    server_id: str
    display_name: str
    description: str
    required_scope_action: Literal["mcp.tool.invoke"] = "mcp.tool.invoke"
    safety_level: McpToolSafetyLevel = "local_policy_fixture"
    fixture_only: Literal[True] = True
    network_required: Literal[False] = False
    live_target_contact_allowed: Literal[False] = False
    report_submission_allowed: Literal[False] = False
    browser_required: Literal[False] = False
    allowed_input_fields: list[str] = Field(default_factory=list)


class McpToolInvocationResult(BaseModel):
    """Result from an allowlisted, fixture-only MCP tool invocation."""

    result_version: Literal["1"] = "1"
    invocation_id: str = Field(default_factory=lambda: str(uuid4()))
    tool_id: str
    server_id: str
    action: Literal["mcp.tool.invoke"] = "mcp.tool.invoke"
    repository: str
    policy_summary: PolicyDocumentSummary
    scope_decision: ScopeDecision
    fixture_tool_used: Literal[True] = True
    live_mcp_server_used: Literal[False] = False
    external_process_used: Literal[False] = False
    network_used: Literal[False] = False
    live_target_contact_used: Literal[False] = False
    browser_used: Literal[False] = False
    active_validation_used: Literal[False] = False
    report_submission_used: Literal[False] = False
    submission_allowed: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
