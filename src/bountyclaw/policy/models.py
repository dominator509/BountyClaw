"""Local policy document ingestion models for Phase 7.

Policy documents are untrusted input. Phase 7 supports local fixture-style policy
summaries only; it does not fetch policy URLs, launch browsers, submit forms, or
expand scope from parsed policy text.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

PolicySourceKind = Literal["local_file"]
PolicySignalKind = Literal[
    "allowed_target_hint",
    "out_of_scope_hint",
    "prohibited_action_hint",
    "safe_harbor_hint",
    "disclosure_rule_hint",
]


class PolicySignal(BaseModel):
    """One redacted, non-authoritative policy hint extracted from a local file."""

    signal_id: str
    kind: PolicySignalKind
    line_number: int = Field(ge=1)
    text: str = Field(max_length=280)


class PolicyDocumentSummary(BaseModel):
    """Redacted summary of a local policy document.

    The summary is intentionally not an authorization source. It is advisory data
    for humans and future program-fit logic. The scope manifest remains the only
    executable authorization boundary.
    """

    summary_version: Literal["1"] = "1"
    source_kind: PolicySourceKind = "local_file"
    source_path: str
    source_name: str
    line_count: int = Field(ge=0)
    byte_count: int = Field(ge=0)
    redaction_count: int = Field(ge=0)
    signals: list[PolicySignal] = Field(default_factory=list)
    scope_expansion_allowed: Literal[False] = False
    network_used: Literal[False] = False
    live_browser_used: Literal[False] = False
    live_mcp_server_used: Literal[False] = False
    notes: list[str] = Field(default_factory=list)
