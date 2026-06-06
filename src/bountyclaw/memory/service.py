"""Scope-gated local memory and skill proposal services for Phase 8."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from pathlib import Path

from bountyclaw.findings import ensure_store_path_outside_repository, redact_text
from bountyclaw.scope import ScopeGate, Target, TargetKind
from bountyclaw.scope.loader import LoadedScopeManifest
from bountyclaw.scope.models import ScopeDecision

from .models import (
    MemoryApproval,
    MemoryCategory,
    MemoryDeleteResult,
    MemoryExport,
    MemoryRecord,
    MemoryRetentionPolicy,
    MemorySource,
    MemoryWriteResult,
    SkillProposal,
)
from .skills import get_skill_template
from .store import MemoryStore


class MemoryAuthorizationError(RuntimeError):
    """Raised when memory/skill actions are not scope-authorized."""

    def __init__(self, decision: ScopeDecision) -> None:
        self.decision = decision
        super().__init__("; ".join(decision.reasons))


class MemoryApprovalError(RuntimeError):
    """Raised when memory mutation lacks explicit human approval."""


class MemorySafetyError(RuntimeError):
    """Raised when memory content is not safe to persist."""


class MemoryNotFoundError(RuntimeError):
    """Raised when a requested memory record is absent."""


class SkillSelectionError(RuntimeError):
    """Raised when a requested skill template does not exist."""


SENSITIVE_MEMORY_MARKERS = (
    "raw evidence",
    "session cookie",
    "authorization header",
    "bearer ",
    "private key",
    "password=",
    "password:",
    "token=",
    "token:",
)


def remember_authorized_memory(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    store_path: Path,
    content: str,
    category: MemoryCategory,
    source: MemorySource,
    approved_by: str,
    approval_note: str,
    retention_policy: MemoryRetentionPolicy = "project",
    approve_memory_write: bool = False,
) -> MemoryWriteResult:
    """Persist a redacted memory record only after explicit approval and scope authorization."""

    decision = _require_allowed(loaded_scope, repo, action="memory.write")
    if not approve_memory_write:
        raise MemoryApprovalError(
            "memory writes require --approve-memory-write explicit human approval"
        )

    redaction = redact_text(content)
    if redaction.redaction_count > 0:
        raise MemorySafetyError(
            "memory content matched secret patterns and was rejected by default after redaction check"
        )
    if _looks_like_sensitive_memory(content):
        raise MemorySafetyError(
            "memory content appears to contain raw evidence or sensitive credential material"
        )

    resolved_store = ensure_store_path_outside_repository(store_path, repo)
    now = datetime.now(UTC).isoformat()
    repository = str(repo.expanduser().resolve(strict=False))
    memory = MemoryRecord(
        memory_id=_memory_id(repository, category, source, redaction.redacted_text, now),
        repository=repository,
        category=category,
        source=source,
        content=redaction.redacted_text,
        redaction_status=redaction.redaction_status,
        redaction_count=redaction.redaction_count,
        retention_policy=retention_policy,
        approval=MemoryApproval(
            approved_by=approved_by,
            approval_note=approval_note,
            explicit_approval=True,
        ),
        created_at=now,
        metadata={
            "phase": "8",
            "human_approved": True,
            "redaction_performed_before_persistence": True,
            "sensitive_material_retention_allowed": False,
        },
    )
    MemoryStore(resolved_store).write_memory(memory)
    return MemoryWriteResult(
        store_path=str(resolved_store),
        memory=memory,
        scope_decision=decision,
        notes=[
            "Scope-approved local memory was written after explicit human approval.",
            "Memory content was checked for secrets and persisted as redacted text only.",
            "Memory cannot expand scope, execute tools, contact networks, validate findings, or submit reports.",
        ],
    )


def list_authorized_memories(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    store_path: Path,
    category: str | None = None,
    limit: int = 100,
) -> list[MemoryRecord]:
    """List redacted local memories after scope authorization."""

    _require_allowed(loaded_scope, repo, action="memory.read")
    resolved_store = ensure_store_path_outside_repository(store_path, repo)
    repository = str(repo.expanduser().resolve(strict=False))
    return MemoryStore(resolved_store).list_memories(
        repository=repository, category=category, limit=limit
    )


def export_authorized_memories(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    store_path: Path,
) -> MemoryExport:
    """Export redacted local memories after scope authorization."""

    _require_allowed(loaded_scope, repo, action="memory.export")
    resolved_store = ensure_store_path_outside_repository(store_path, repo)
    repository = str(repo.expanduser().resolve(strict=False))
    return MemoryStore(resolved_store).export_memories(repository=repository)


def delete_authorized_memory(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    store_path: Path,
    memory_id: str,
    approve_delete: bool = False,
) -> MemoryDeleteResult:
    """Delete one local memory record after scope authorization and explicit approval."""

    decision = _require_allowed(loaded_scope, repo, action="memory.delete")
    if not approve_delete:
        raise MemoryApprovalError(
            "memory deletion requires --approve-delete explicit human approval"
        )
    resolved_store = ensure_store_path_outside_repository(store_path, repo)
    deleted = MemoryStore(resolved_store).delete_memory(memory_id)
    if not deleted:
        raise MemoryNotFoundError(f"memory record not found: {memory_id}")
    return MemoryDeleteResult(
        store_path=str(resolved_store),
        memory_id=memory_id,
        deleted=True,
        scope_decision=decision,
        notes=["Scope-approved memory deletion completed locally."],
    )


def propose_authorized_skill(
    loaded_scope: LoadedScopeManifest,
    repo: Path,
    *,
    skill_id: str,
) -> SkillProposal:
    """Create a non-executing skill proposal after scope authorization."""

    proposal_decision = _require_allowed(loaded_scope, repo, action="skill.propose")
    template = get_skill_template(skill_id)
    if template is None:
        raise SkillSelectionError(f"unknown skill template: {skill_id}")

    target = Target(kind=TargetKind.LOCAL_REPO, value=str(repo))
    gate = ScopeGate(loaded_scope)
    action_decisions = [gate.evaluate(action, target) for action in template.required_scope_actions]
    all_required_actions_authorized = all(decision.allowed for decision in action_decisions)
    repository = str(repo.expanduser().resolve(strict=False))
    proposal_id = _proposal_id(repository, skill_id, template.required_scope_actions)
    return SkillProposal(
        proposal_id=proposal_id,
        repository=repository,
        template=template,
        proposal_scope_decision=proposal_decision,
        required_action_decisions=action_decisions,
        all_required_actions_authorized=all_required_actions_authorized,
        notes=[
            "Skill proposal is advisory and non-executing.",
            "Every workflow step must be run through a separate command and pass the scope gate.",
            "The proposal cannot expand scope, execute tools, contact networks, validate findings, or submit reports.",
        ],
    )


def _require_allowed(
    loaded_scope: LoadedScopeManifest, repo: Path, *, action: str
) -> ScopeDecision:
    decision = ScopeGate(loaded_scope).evaluate(
        action=action,
        target=Target(kind=TargetKind.LOCAL_REPO, value=str(repo)),
    )
    if not decision.allowed:
        raise MemoryAuthorizationError(decision)
    return decision


def _looks_like_sensitive_memory(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in SENSITIVE_MEMORY_MARKERS)


def _memory_id(repository: str, category: str, source: str, content: str, created_at: str) -> str:
    material = "|".join([repository, category, source, content, created_at])
    return f"bcmem-sha256:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:32]}"


def _proposal_id(repository: str, skill_id: str, actions: list[str]) -> str:
    material = "|".join([repository, skill_id, *actions])
    return f"bcskill-sha256:{hashlib.sha256(material.encode('utf-8')).hexdigest()[:32]}"
