"""Scope-gated, fixture-only MCP gateway service for Phase 7."""

from __future__ import annotations

from pathlib import Path

from bountyclaw.policy import PolicyDocumentError, read_local_policy_summary
from bountyclaw.scope import (
    Action,
    LoadedScopeManifest,
    ScopeDecision,
    ScopeGate,
    Target,
    TargetKind,
)

from .models import McpServerDefinition, McpToolDefinition, McpToolInvocationResult
from .registry import mcp_server_registry, mcp_tool_registry


class McpGatewayError(RuntimeError):
    """Base MCP gateway error."""


class McpFeatureGateError(McpGatewayError):
    """Raised when a fixture MCP invocation is not explicitly enabled."""


class McpToolSelectionError(McpGatewayError):
    """Raised when an MCP tool or server is not registered and allowlisted."""


class McpAuthorizationError(McpGatewayError):
    """Raised when the scope gate denies MCP tool invocation."""

    def __init__(self, decision: ScopeDecision) -> None:
        super().__init__("MCP tool invocation is not authorized")
        self.decision = decision


def list_mcp_servers() -> list[McpServerDefinition]:
    """List registered MCP server metadata."""

    return sorted(mcp_server_registry().values(), key=lambda item: item.server_id)


def list_mcp_tools() -> list[McpToolDefinition]:
    """List allowlisted MCP tool metadata."""

    return sorted(mcp_tool_registry().values(), key=lambda item: item.tool_id)


def invoke_authorized_mcp_tool(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    tool_id: str,
    policy_file: Path | None = None,
    fixture_tool_enabled: bool = False,
) -> McpToolInvocationResult:
    """Invoke an allowlisted, local fixture MCP tool after scope approval."""

    if not fixture_tool_enabled:
        raise McpFeatureGateError(
            "Phase 7 MCP fixture invocation requires --enable-mcp-fixture; live MCP servers remain disabled"
        )

    tools = mcp_tool_registry()
    if tool_id not in tools:
        raise McpToolSelectionError(f"unregistered MCP tool is denied: {tool_id}")
    tool = tools[tool_id]

    servers = mcp_server_registry()
    if tool.server_id not in servers:
        raise McpToolSelectionError(f"tool references unregistered MCP server: {tool.server_id}")
    server = servers[tool.server_id]
    if (
        server.transport != "builtin_fixture"
        or server.network_allowed
        or server.live_process_allowed
    ):
        raise McpToolSelectionError("Phase 7 only permits builtin fixture MCP tools")

    decision = ScopeGate(loaded_scope).evaluate(
        Action.MCP_TOOL_INVOKE.value,
        Target(kind=TargetKind.LOCAL_REPO, value=str(repo)),
    )
    if not decision.allowed:
        raise McpAuthorizationError(decision)

    try:
        policy_summary = read_local_policy_summary(loaded_scope, policy_file=policy_file)
    except PolicyDocumentError:
        raise

    return McpToolInvocationResult(
        tool_id=tool.tool_id,
        server_id=server.server_id,
        repository=str(repo.expanduser().resolve(strict=False)),
        policy_summary=policy_summary,
        scope_decision=decision,
        notes=[
            "MCP gateway used only an in-process fixture adapter.",
            "No external MCP server, network transport, browser automation, active validation, or report submission was used.",
            "Parsed policy hints are advisory and cannot expand the scope manifest.",
        ],
    )
