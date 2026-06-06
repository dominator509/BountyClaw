"""MCP registry metadata for Phase 7."""

from __future__ import annotations

from .models import McpServerDefinition, McpToolDefinition

POLICY_LOCAL_FILE_TOOL_ID = "policy.local_file_summary"
BUILTIN_POLICY_SERVER_ID = "builtin.policy_fixture"


def mcp_server_registry() -> dict[str, McpServerDefinition]:
    """Return declared MCP server metadata.

    The Phase 7 registry intentionally exposes no external process or network
    transport. The builtin fixture server is a local in-process adapter used to
    validate gateway policy and audit behavior before real MCP runtimes exist.
    """

    return {
        BUILTIN_POLICY_SERVER_ID: McpServerDefinition(
            server_id=BUILTIN_POLICY_SERVER_ID,
            display_name="Built-in Local Policy Fixture",
            status="fixture_only",
            transport="builtin_fixture",
            registered_tools=[POLICY_LOCAL_FILE_TOOL_ID],
            notes=[
                "No external MCP process is launched in Phase 7.",
                "No network transport is opened in Phase 7.",
                "Fixture output is advisory and cannot expand executable scope.",
            ],
        )
    }


def mcp_tool_registry() -> dict[str, McpToolDefinition]:
    """Return allowlisted MCP tool metadata."""

    return {
        POLICY_LOCAL_FILE_TOOL_ID: McpToolDefinition(
            tool_id=POLICY_LOCAL_FILE_TOOL_ID,
            server_id=BUILTIN_POLICY_SERVER_ID,
            display_name="Local Policy File Summary",
            description="Summarize a local policy file with redaction and keyword hints.",
            allowed_input_fields=["repo", "policy_file"],
        )
    }
