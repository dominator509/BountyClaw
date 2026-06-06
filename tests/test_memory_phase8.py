from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.memory import (
    MemoryApprovalError,
    MemoryAuthorizationError,
    MemorySafetyError,
    SkillSelectionError,
    delete_authorized_memory,
    export_authorized_memories,
    list_authorized_memories,
    list_skill_templates,
    propose_authorized_skill,
    remember_authorized_memory,
)
from bountyclaw.scope import load_scope_manifest

runner = CliRunner()


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "app.py").write_text("def handler(value):\n    return value\n", encoding="utf-8")
    return repo


def write_manifest(tmp_path: Path, repo: Path, *, allowed_actions: list[str] | None = None) -> Path:
    manifest = {
        "manifest_version": "1",
        "program": {
            "name": "Authorized Phase 8 Fixture",
            "policy_file": "policy.md",
            "disclosure_rules": ["manual report submission only"],
        },
        "authorization": {
            "operator": "phase8-tester",
            "basis": "own_asset",
            "confirmed": True,
            "confirmation_note": "I confirm this fixture repository is authorized for Phase 8 testing.",
        },
        "assets": {
            "repositories": [
                {
                    "path": str(repo),
                    "label": "fixture",
                    "allowed_actions": allowed_actions
                    or [
                        "repo.read",
                        "scan.local_static",
                        "findings.write",
                        "triage.review",
                        "report.draft",
                        "mcp.tool.invoke",
                        "browser.policy_ingest",
                        "memory.read",
                        "memory.write",
                        "memory.export",
                        "memory.delete",
                        "skill.propose",
                    ],
                }
            ],
            "domains": [],
            "out_of_scope": [],
        },
        "controls": {
            "network_access_enabled": False,
            "require_human_approval_for_active_validation": True,
        },
    }
    (tmp_path / "policy.md").write_text("Local policy fixture", encoding="utf-8")
    path = tmp_path / "scope.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return path


def test_memory_write_requires_explicit_approval(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    loaded_scope = load_scope_manifest(write_manifest(tmp_path, repo))

    with pytest.raises(MemoryApprovalError):
        remember_authorized_memory(
            loaded_scope,
            repo,
            store_path=tmp_path / "memory.sqlite",
            content="Prefer concise remediation guidance.",
            category="reporting_preference",
            source="human_note",
            approved_by="tester",
            approval_note="Approving this local memory write for the fixture project.",
            approve_memory_write=False,
        )


def test_memory_write_requires_scope_action(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    loaded_scope = load_scope_manifest(
        write_manifest(tmp_path, repo, allowed_actions=["memory.read"])
    )

    with pytest.raises(MemoryAuthorizationError) as exc:
        remember_authorized_memory(
            loaded_scope,
            repo,
            store_path=tmp_path / "memory.sqlite",
            content="Prefer concise remediation guidance.",
            category="reporting_preference",
            source="human_note",
            approved_by="tester",
            approval_note="Approving this local memory write for the fixture project.",
            approve_memory_write=True,
        )

    assert exc.value.decision.action == "memory.write"
    assert exc.value.decision.allowed is False


def test_memory_write_list_export_and_delete_are_scope_gated_and_local(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest = write_manifest(tmp_path, repo)
    loaded_scope = load_scope_manifest(manifest)
    store = tmp_path / "state" / "memory.sqlite"

    result = remember_authorized_memory(
        loaded_scope,
        repo,
        store_path=store,
        content="Prefer evidence summaries that preserve uncertainty and static-only validation status.",
        category="reporting_preference",
        source="human_note",
        approved_by="tester",
        approval_note="Approving this local memory write for future report drafting consistency.",
        approve_memory_write=True,
    )

    assert result.memory.scope_expansion_allowed is False
    assert result.memory.tool_execution_allowed is False
    assert result.memory.network_used is False
    assert result.memory.report_submission_used is False
    assert result.memory.redaction_count == 0

    memories = list_authorized_memories(loaded_scope, repo, store_path=store)
    assert [memory.memory_id for memory in memories] == [result.memory.memory_id]

    export = export_authorized_memories(loaded_scope, repo, store_path=store)
    assert export.raw_secret_material_included is False
    assert export.tool_execution_allowed is False
    assert len(export.memory_records) == 1

    deleted = delete_authorized_memory(
        loaded_scope,
        repo,
        store_path=store,
        memory_id=result.memory.memory_id,
        approve_delete=True,
    )
    assert deleted.deleted is True
    assert list_authorized_memories(loaded_scope, repo, store_path=store) == []


def test_memory_rejects_secret_like_content_before_persistence(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    loaded_scope = load_scope_manifest(write_manifest(tmp_path, repo))
    store = tmp_path / "memory.sqlite"

    with pytest.raises(MemorySafetyError):
        remember_authorized_memory(
            loaded_scope,
            repo,
            store_path=store,
            content="api_key = sk-this-secret-should-not-be-retained-in-memory",
            category="workflow_observation",
            source="human_note",
            approved_by="tester",
            approval_note="Approving fixture memory but the content should be rejected.",
            approve_memory_write=True,
        )

    assert not store.exists()


def test_memory_store_inside_target_repository_is_rejected(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    loaded_scope = load_scope_manifest(write_manifest(tmp_path, repo))

    with pytest.raises(Exception, match="inside the target repository"):
        remember_authorized_memory(
            loaded_scope,
            repo,
            store_path=repo / ".bountyclaw" / "memory.sqlite",
            content="Do not store state inside the target repository.",
            category="workflow_observation",
            source="human_note",
            approved_by="tester",
            approval_note="Approving fixture memory path rejection test.",
            approve_memory_write=True,
        )


def test_skill_templates_are_non_executing() -> None:
    templates = list_skill_templates()

    assert templates
    assert all(template.executable is False for template in templates)
    assert all(template.scope_expansion_allowed is False for template in templates)
    assert all(template.tool_execution_allowed is False for template in templates)
    assert "local-static-triage-draft" in {template.skill_id for template in templates}


def test_skill_proposal_requires_scope_and_does_not_execute_tools(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest = write_manifest(
        tmp_path,
        repo,
        allowed_actions=["skill.propose", "repo.read", "scan.local_static"],
    )
    loaded_scope = load_scope_manifest(manifest)

    proposal = propose_authorized_skill(
        loaded_scope,
        repo,
        skill_id="local-static-triage-draft",
    )

    assert proposal.executable_now is False
    assert proposal.tool_execution_allowed is False
    assert proposal.scope_expansion_allowed is False
    assert proposal.network_used is False
    assert proposal.report_submission_used is False
    assert proposal.proposal_scope_decision.allowed is True
    assert proposal.all_required_actions_authorized is False
    denied_actions = {
        decision.action for decision in proposal.required_action_decisions if not decision.allowed
    }
    assert {"findings.write", "triage.review", "report.draft"}.issubset(denied_actions)


def test_skill_proposal_denies_unknown_template_after_scope(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    loaded_scope = load_scope_manifest(write_manifest(tmp_path, repo))

    with pytest.raises(SkillSelectionError):
        propose_authorized_skill(loaded_scope, repo, skill_id="unknown-template")


def test_memory_and_skill_cli_smoke(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest = write_manifest(tmp_path, repo)
    store = tmp_path / "state" / "memory.sqlite"

    remember = runner.invoke(
        app,
        [
            "memory",
            "remember",
            "--manifest",
            str(manifest),
            "--repo",
            str(repo),
            "--store",
            str(store),
            "--content",
            "Prefer static-only wording unless active validation is manually confirmed.",
            "--category",
            "reporting_preference",
            "--source",
            "human_note",
            "--approved-by",
            "tester",
            "--approval-note",
            "Approving this local memory write for CLI smoke validation.",
            "--approve-memory-write",
            "--json",
        ],
    )
    assert remember.exit_code == 0, remember.output
    payload = json.loads(remember.output)
    memory_id = payload["memory"]["memory_id"]
    assert payload["memory"]["tool_execution_allowed"] is False

    listed = runner.invoke(
        app,
        [
            "memory",
            "list",
            "--manifest",
            str(manifest),
            "--repo",
            str(repo),
            "--store",
            str(store),
            "--json",
        ],
    )
    assert listed.exit_code == 0, listed.output
    assert json.loads(listed.output)[0]["memory_id"] == memory_id

    exported = runner.invoke(
        app,
        [
            "memory",
            "export",
            "--manifest",
            str(manifest),
            "--repo",
            str(repo),
            "--store",
            str(store),
            "--json",
        ],
    )
    assert exported.exit_code == 0, exported.output
    assert json.loads(exported.output)["raw_secret_material_included"] is False

    skills = runner.invoke(app, ["skills", "list", "--json"])
    assert skills.exit_code == 0, skills.output
    assert any(
        item["skill_id"] == "local-static-triage-draft" for item in json.loads(skills.output)
    )

    proposal = runner.invoke(
        app,
        [
            "skills",
            "propose",
            "--manifest",
            str(manifest),
            "--repo",
            str(repo),
            "--skill-id",
            "memory-hygiene-review",
            "--json",
        ],
    )
    assert proposal.exit_code == 0, proposal.output
    proposal_payload = json.loads(proposal.output)
    assert proposal_payload["executable_now"] is False
    assert proposal_payload["template"]["tool_execution_allowed"] is False

    deleted = runner.invoke(
        app,
        [
            "memory",
            "delete",
            "--manifest",
            str(manifest),
            "--repo",
            str(repo),
            "--store",
            str(store),
            "--memory-id",
            memory_id,
            "--approve-delete",
            "--json",
        ],
    )
    assert deleted.exit_code == 0, deleted.output
    assert json.loads(deleted.output)["deleted"] is True
