from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.release import (
    build_release_checklist,
    build_release_rollback_plan,
    verify_release_controls,
)

runner = CliRunner()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_release_checklist_is_non_networked_and_commit_oriented() -> None:
    result = build_release_checklist(repo_root())

    assert result.phase == "9"
    assert result.external_ci_executed is False
    assert result.network_used is False
    assert {item.item_id for item in result.items} >= {"REL-001", "REL-002", "REL-006"}
    assert all(item.required_for_commit for item in result.items)


def test_release_verification_passes_commit_gates_and_discloses_external_deferrals() -> None:
    result = verify_release_controls(repo_root())

    assert result.phase == "9"
    assert result.ready_for_commit is True
    assert result.ready_for_external_release is False
    assert result.external_ci_executed is False
    assert result.package_publish_executed is False
    assert result.network_used is False
    assert result.failed_count == 0
    assert result.deferred_count >= 3
    deferred = {check.check_id for check in result.checks if check.status == "deferred"}
    assert "REL-EXT-GITHUB-ACTIONS-RUN" in deferred
    assert "REL-EXT-CLEAN-INSTALL" in deferred
    assert "REL-EXT-PUBLISH" in deferred


def test_ci_workflow_defines_least_privilege_quality_security_and_package_gates() -> None:
    workflow = (repo_root() / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "permissions:" in workflow
    assert "contents: read" in workflow
    assert "actions/checkout@v6" in workflow
    assert "persist-credentials: false" in workflow
    assert "actions/setup-python@v6" in workflow
    assert "ruff check src tests" in workflow
    assert "mypy src" in workflow
    assert "bandit -q -r src" in workflow
    assert "pip-audit" in workflow
    assert "python -m compileall -q src tests" in workflow
    assert "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q" in workflow
    assert "python -m build" in workflow
    assert "workflow_dispatch" in workflow


def test_release_rollback_plan_is_reversible_without_external_resources() -> None:
    plan = build_release_rollback_plan()

    assert plan.phase == "9"
    assert plan.rollback_ready is True
    assert plan.external_resources_created is False
    assert any("PHASE_9_SUBROADMAP.md" in step for step in plan.steps)
    assert any("Phase 8" in fallback for fallback in plan.preserved_fallbacks)


def test_release_cli_commands_render_json() -> None:
    root = str(repo_root())

    checklist = runner.invoke(app, ["release", "checklist", "--root", root, "--json"])
    assert checklist.exit_code == 0, checklist.output
    checklist_payload = json.loads(checklist.output)
    assert checklist_payload["phase"] == "9"

    verify = runner.invoke(app, ["release", "verify", "--root", root, "--json"])
    assert verify.exit_code == 0, verify.output
    verify_payload = json.loads(verify.output)
    assert verify_payload["ready_for_commit"] is True
    assert verify_payload["ready_for_external_release"] is False

    rollback = runner.invoke(app, ["release", "rollback-plan", "--json"])
    assert rollback.exit_code == 0, rollback.output
    rollback_payload = json.loads(rollback.output)
    assert rollback_payload["rollback_ready"] is True
