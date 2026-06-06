from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml

from bountyclaw.audit import AuditEvent, AuditLogWriter
from bountyclaw.scope import ScopeGate, Target, TargetKind, load_scope_manifest


def write_manifest(
    tmp_path: Path,
    repo_path: Path,
    *,
    allowed_actions: list[str] | None = None,
    confirmed: bool = True,
    out_of_scope: list[str] | None = None,
    include_domain: bool = False,
) -> Path:
    allowed = allowed_actions if allowed_actions is not None else ["repo.read", "scan.local_static"]
    manifest = {
        "manifest_version": "1",
        "program": {
            "name": "Authorized Fixture Program",
            "policy_file": "policy.md",
            "disclosure_rules": ["manual report submission only"],
        },
        "authorization": {
            "operator": "fixture-tester",
            "basis": "own_asset",
            "confirmed": confirmed,
            "confirmation_note": "I confirm this fixture repository is authorized for testing.",
        },
        "assets": {
            "repositories": [
                {
                    "path": str(repo_path),
                    "label": "fixture",
                    "allowed_actions": allowed,
                }
            ],
            "domains": [{"pattern": "example.com", "allowed_actions": ["repo.read"]}]
            if include_domain
            else [],
            "out_of_scope": out_of_scope or [],
        },
        "controls": {
            "network_access_enabled": False,
            "require_human_approval_for_active_validation": True,
        },
    }
    path = tmp_path / "scope.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return path


def test_scope_gate_allows_explicitly_allowlisted_local_repo_action(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest_path = write_manifest(tmp_path, repo)

    loaded_scope = load_scope_manifest(manifest_path)
    decision = ScopeGate(loaded_scope).evaluate(
        "scan.local_static", Target(kind=TargetKind.LOCAL_REPO, value=str(repo))
    )

    assert decision.allowed is True
    assert decision.decision == "allow"
    assert "explicitly allowlisted" in " ".join(decision.reasons)


def test_scope_gate_denies_out_of_scope_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    excluded = repo / "private"
    excluded.mkdir()
    manifest_path = write_manifest(tmp_path, repo, out_of_scope=[str(excluded)])

    loaded_scope = load_scope_manifest(manifest_path)
    decision = ScopeGate(loaded_scope).evaluate(
        "repo.read", Target(kind=TargetKind.LOCAL_REPO, value=str(excluded))
    )

    assert decision.allowed is False
    assert decision.decision == "deny"
    assert any("out of scope" in reason for reason in decision.reasons)


def test_scope_gate_denies_unallowlisted_repo(tmp_path: Path) -> None:
    allowed_repo = tmp_path / "allowed"
    allowed_repo.mkdir()
    other_repo = tmp_path / "other"
    other_repo.mkdir()
    manifest_path = write_manifest(tmp_path, allowed_repo)

    loaded_scope = load_scope_manifest(manifest_path)
    decision = ScopeGate(loaded_scope).evaluate(
        "repo.read", Target(kind=TargetKind.LOCAL_REPO, value=str(other_repo))
    )

    assert decision.allowed is False
    assert any("not allowlisted" in reason for reason in decision.reasons)


def test_scope_gate_denies_action_not_allowlisted_for_repo(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest_path = write_manifest(tmp_path, repo, allowed_actions=["repo.read"])

    loaded_scope = load_scope_manifest(manifest_path)
    decision = ScopeGate(loaded_scope).evaluate(
        "scan.local_static", Target(kind=TargetKind.LOCAL_REPO, value=str(repo))
    )

    assert decision.allowed is False
    assert any("not allowlisted" in reason for reason in decision.reasons)


def test_scope_gate_denies_prohibited_action(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest_path = write_manifest(tmp_path, repo)

    loaded_scope = load_scope_manifest(manifest_path)
    decision = ScopeGate(loaded_scope).evaluate(
        "exploit.active", Target(kind=TargetKind.LOCAL_REPO, value=str(repo))
    )

    assert decision.allowed is False
    assert any("prohibited" in reason for reason in decision.reasons)


def test_scope_gate_denies_network_domain_targets_in_phase_one(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest_path = write_manifest(tmp_path, repo, include_domain=True)

    loaded_scope = load_scope_manifest(manifest_path)
    decision = ScopeGate(loaded_scope).evaluate(
        "repo.read", Target(kind=TargetKind.DOMAIN, value="example.com")
    )

    assert decision.allowed is False
    assert any("network/domain" in reason for reason in decision.reasons)


def test_unconfirmed_authorization_invalidates_manifest(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    manifest_path = write_manifest(tmp_path, repo, confirmed=False)

    with pytest.raises(ValueError, match="authorization.confirmed"):
        load_scope_manifest(manifest_path)


def test_audit_log_writer_appends_jsonl_event(tmp_path: Path) -> None:
    audit_path = tmp_path / "audit" / "events.jsonl"
    event = AuditEvent(
        event_type="scope.check",
        action="repo.read",
        decision="allow",
        target_kind="local_repo",
        target="repo",
        reasons=["target and action are explicitly allowlisted"],
    )

    AuditLogWriter(audit_path).append(event)

    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["event_type"] == "scope.check"
    assert payload["decision"] == "allow"
