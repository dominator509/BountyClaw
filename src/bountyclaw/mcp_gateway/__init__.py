"""Policy-bound MCP gateway foundation."""

from .models import McpServerDefinition, McpToolDefinition, McpToolInvocationResult
from .registry import (
    BUILTIN_POLICY_SERVER_ID,
    POLICY_LOCAL_FILE_TOOL_ID,
    mcp_server_registry,
    mcp_tool_registry,
)
from .service import (
    McpAuthorizationError,
    McpFeatureGateError,
    McpGatewayError,
    McpToolSelectionError,
    invoke_authorized_mcp_tool,
    list_mcp_servers,
    list_mcp_tools,
)

__all__ = [
    "BUILTIN_POLICY_SERVER_ID",
    "POLICY_LOCAL_FILE_TOOL_ID",
    "McpAuthorizationError",
    "McpFeatureGateError",
    "McpGatewayError",
    "McpServerDefinition",
    "McpToolDefinition",
    "McpToolInvocationResult",
    "McpToolSelectionError",
    "invoke_authorized_mcp_tool",
    "list_mcp_servers",
    "list_mcp_tools",
    "mcp_server_registry",
    "mcp_tool_registry",
]
