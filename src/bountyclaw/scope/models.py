"""Scope manifest and decision models.

The scope manifest is the mandatory authorization boundary for BountyClaw. Phase
18 supports local, read-only repository-oriented decisions, deterministic
scan-planning authorization, local static scanning, redaction-safe findings
persistence, mocked model triage authorization, human-reviewed report drafting,
fixture-only MCP/browser policy-ingestion controls, and local memory/skill controls.
Release, hardening, handoff, and validation-evidence commands remain local
governance checks that do not act on bounty targets. The gate rejects network and
active-validation paths until later phases add explicit human approval and
validation gates.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl, model_validator


class AuthorizationBasis(StrEnum):
    """Accepted human authorization bases."""

    OWN_ASSET = "own_asset"
    BUG_BOUNTY_PROGRAM = "bug_bounty_program"
    WRITTEN_PERMISSION = "written_permission"
    INTERNAL_SECURITY_REVIEW = "internal_security_review"


class Action(StrEnum):
    """Known non-destructive actions available to the Phase 19 gate."""

    SCOPE_VALIDATE = "scope.validate"
    REPO_READ = "repo.read"
    SCAN_LOCAL_STATIC = "scan.local_static"
    FINDINGS_WRITE = "findings.write"
    MODEL_TRIAGE = "model.triage"
    TRIAGE_REVIEW = "triage.review"
    REPORT_DRAFT = "report.draft"
    MCP_TOOL_INVOKE = "mcp.tool.invoke"
    BROWSER_POLICY_INGEST = "browser.policy_ingest"
    MEMORY_READ = "memory.read"
    MEMORY_WRITE = "memory.write"
    MEMORY_EXPORT = "memory.export"
    MEMORY_DELETE = "memory.delete"
    SKILL_PROPOSE = "skill.propose"


class TargetKind(StrEnum):
    """Supported target identifiers for authorization decisions."""

    LOCAL_REPO = "local_repo"
    DOMAIN = "domain"
    URL = "url"


PROHIBITED_ACTIONS: frozenset[str] = frozenset(
    {
        "network.scan",
        "network.probe",
        "exploit.active",
        "exploit.automated",
        "dos.test",
        "bruteforce.auth",
        "credential.harvest",
        "secret.exfiltrate",
        "persistence.install",
        "stealth.evade",
        "bounty.submit.auto",
        "browser.form_submit",
        "browser.live_target_contact",
        "browser.navigation.live",
        "browser.authenticated_session",
        "mcp.unregistered_tool",
        "mcp.external_server.invoke",
    }
)


class ProgramScope(BaseModel):
    """Bug bounty or internal review program metadata."""

    name: str = Field(min_length=1)
    policy_url: HttpUrl | None = None
    policy_file: str | None = None
    safe_harbor: str | None = None
    disclosure_rules: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_policy_reference(self) -> ProgramScope:
        if self.policy_url is None and not self.policy_file:
            raise ValueError("program must include either policy_url or policy_file")
        return self


class AuthorizationScope(BaseModel):
    """Human-supplied authorization attestation."""

    operator: str = Field(min_length=1)
    basis: AuthorizationBasis
    confirmed: bool = False
    confirmation_note: str = Field(min_length=12)

    @model_validator(mode="after")
    def require_explicit_confirmation(self) -> AuthorizationScope:
        if not self.confirmed:
            raise ValueError("authorization.confirmed must be true")
        return self


class RepositoryScope(BaseModel):
    """Allowlisted local repository path and explicitly permitted actions."""

    path: str = Field(min_length=1)
    label: str | None = None
    allowed_actions: set[Action] = Field(default_factory=set)


class DomainScope(BaseModel):
    """Declared domain scope.

    Phase 19 records domain scope for manifest completeness but does not allow
    network/domain actions.
    """

    pattern: str = Field(min_length=1)
    allowed_actions: set[Action] = Field(default_factory=set)


class AssetScope(BaseModel):
    """Assets authorized by the manifest."""

    repositories: list[RepositoryScope] = Field(default_factory=list)
    domains: list[DomainScope] = Field(default_factory=list)
    out_of_scope: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def require_some_scope(self) -> AssetScope:
        if not self.repositories and not self.domains:
            raise ValueError("assets must include at least one repository or domain")
        return self


class ControlScope(BaseModel):
    """Runtime controls for the manifest."""

    network_access_enabled: bool = False
    require_human_approval_for_active_validation: bool = True
    prohibited_actions: set[str] = Field(default_factory=lambda: set(PROHIBITED_ACTIONS))

    @model_validator(mode="after")
    def enforce_phase_eighteen_network_shutdown(self) -> ControlScope:
        if self.network_access_enabled:
            raise ValueError("network_access_enabled must remain false in Phase 19")
        return self


class ScopeManifest(BaseModel):
    """Complete Phase 19 scope manifest."""

    manifest_version: Literal["1"] = "1"
    program: ProgramScope
    authorization: AuthorizationScope
    assets: AssetScope
    controls: ControlScope = Field(default_factory=ControlScope)


class Target(BaseModel):
    """Requested target for a scope-gate decision."""

    kind: TargetKind
    value: str = Field(min_length=1)


class ScopeDecision(BaseModel):
    """Deny-by-default scope gate decision."""

    action: str
    target_kind: TargetKind | None = None
    target: str | None = None
    decision: Literal["allow", "deny", "require_human_approval"]
    reasons: list[str] = Field(default_factory=list)

    @property
    def allowed(self) -> bool:
        return self.decision == "allow"
