from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.handoff import (
    build_codex_handoff_plan,
    build_evidence_template,
    export_handoff_package,
    verify_handoff_readiness,
)

runner = CliRunner()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_codex_handoff_plan_is_non_networked_and_covers_external_gaps() -> None:
    plan = build_codex_handoff_plan(repo_root())

    assert plan.phase == "11"
    assert plan.source_phase == "10"
    assert plan.ready_for_codex is True
    assert plan.ready_for_production is False
    assert plan.network_used is False
    assert plan.external_actions_executed is False
    assert plan.task_count == 10
    task_ids = {task.task_id for task in plan.tasks}
    assert {"P11-HANDOFF-002", "P11-HANDOFF-005", "P11-HANDOFF-010"}.issubset(task_ids)
    related_gaps = {gap_id for task in plan.tasks for gap_id in task.related_gap_ids}
    assert {"PGT-088", "PGT-091", "PGT-096", "PGT-097", "PGT-099"}.issubset(related_gaps)
    assert all(task.expected_evidence_artifacts for task in plan.tasks)
    assert all(task.blocked_in_chatgpt_reason for task in plan.tasks)
    assert all(task.prohibited_claims_until_complete for task in plan.tasks)


def test_evidence_template_requires_future_external_artifacts() -> None:
    template = build_evidence_template(repo_root())

    assert template.phase == "11"
    assert template.network_used is False
    assert template.external_actions_executed is False
    assert template.artifact_count >= 20
    filenames = {artifact.filename for artifact in template.artifacts}
    assert "validation_evidence/hosted_ci_run.json" in filenames
    assert "validation_evidence/live_provider_no_secret_payloads.json" in filenames
    assert "validation_evidence/signing_provenance_attestation.txt" in filenames
    assert all(
        "ChatGPT Project Mode" in " ".join(artifact.acceptance_criteria)
        for artifact in template.artifacts
    )
    assert all(artifact.sensitive_handling for artifact in template.artifacts)


def test_handoff_export_writes_deterministic_local_package(tmp_path: Path) -> None:
    output_dir = tmp_path / "handoff"
    result = export_handoff_package(repo_root(), output_dir)

    assert result.phase == "11"
    assert result.ready_for_codex is True
    assert result.ready_for_production is False
    assert result.network_used is False
    assert result.external_actions_executed is False
    written_names = {Path(path).name for path in result.written_files}
    assert {
        "CODEX_HANDOFF.md",
        "VALIDATION_COMMANDS.md",
        "GAP_CLOSURE_CHECKLIST.md",
        "codex_handoff_plan.json",
        "evidence_template.json",
        "handoff_manifest.json",
    }.issubset(written_names)
    manifest = json.loads((output_dir / "handoff_manifest.json").read_text(encoding="utf-8"))
    assert manifest["ready_for_codex"] is True
    assert manifest["ready_for_production"] is False


def test_handoff_verification_is_codex_ready_but_not_production_ready() -> None:
    result = verify_handoff_readiness(repo_root())

    assert result.phase == "11"
    assert result.ready_for_commit is True
    assert result.ready_for_codex is True
    assert result.ready_for_production is False
    assert result.failed_count == 0
    assert result.deferred_count >= 1
    assert result.network_used is False
    assert result.external_actions_executed is False
    assert result.hosted_ci_executed is False
    assert result.clean_install_validation_executed is False
    assert result.live_provider_validation_executed is False
    assert result.mcp_browser_runtime_validation_executed is False
    assert result.active_validation_used is False
    assert result.report_submission_used is False
    check_ids = {check.check_id for check in result.checks}
    assert "HANDOFF-PLAN-TASK-COVERAGE" in check_ids
    assert "HANDOFF-EVIDENCE-TEMPLATE-COVERAGE" in check_ids
    assert "HANDOFF-EXTERNAL-VALIDATION-STILL-OPEN" in check_ids


def test_handoff_cli_commands_render_json(tmp_path: Path) -> None:
    root = str(repo_root())

    plan = runner.invoke(app, ["handoff", "plan", "--root", root, "--json"])
    assert plan.exit_code == 0, plan.output
    plan_payload = json.loads(plan.output)
    assert plan_payload["phase"] == "11"
    assert plan_payload["ready_for_codex"] is True

    template = runner.invoke(app, ["handoff", "evidence-template", "--root", root, "--json"])
    assert template.exit_code == 0, template.output
    template_payload = json.loads(template.output)
    assert template_payload["artifact_count"] >= 20

    export = runner.invoke(
        app,
        [
            "handoff",
            "export",
            "--root",
            root,
            "--output",
            str(tmp_path / "handoff"),
            "--json",
        ],
    )
    assert export.exit_code == 0, export.output
    export_payload = json.loads(export.output)
    assert export_payload["ready_for_codex"] is True
    assert export_payload["ready_for_production"] is False

    verify = runner.invoke(app, ["handoff", "verify", "--root", root, "--json"])
    assert verify.exit_code == 0, verify.output
    verify_payload = json.loads(verify.output)
    assert verify_payload["ready_for_commit"] is True
    assert verify_payload["ready_for_codex"] is True
    assert verify_payload["ready_for_production"] is False


def test_ci_workflow_includes_phase11_handoff_verifier() -> None:
    workflow = (repo_root() / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "python scripts/phase9_verify.py --root ." in workflow
    assert "python scripts/phase10_verify.py --root ." in workflow
    assert "python scripts/phase11_verify.py --root ." in workflow
