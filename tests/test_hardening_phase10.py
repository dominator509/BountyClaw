from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.hardening import (
    build_external_validation_plan,
    build_hardening_checklist,
    run_prompt_safety_corpus,
    run_redaction_corpus,
    verify_local_hardening,
)

runner = CliRunner()


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_hardening_checklist_is_non_networked_and_production_oriented() -> None:
    result = build_hardening_checklist(repo_root())

    assert result.phase == "10"
    assert result.network_used is False
    assert result.external_validation_executed is False
    assert {item.item_id for item in result.items} >= {"HARD-001", "HARD-002", "HARD-006"}
    assert all(item.required_for_commit for item in result.items)
    assert all(item.required_for_production for item in result.items)


def test_redaction_corpus_removes_representative_raw_secret_values() -> None:
    result = run_redaction_corpus()

    assert result.phase == "10"
    assert result.passed is True
    assert result.failed_count == 0
    assert result.network_used is False
    assert {case.case_id for case in result.case_results} >= {
        "RED-AWS-001",
        "RED-GH-001",
        "RED-PRIVATE-KEY-001",
    }
    assert all(case.raw_absence_confirmed for case in result.case_results)


def test_prompt_safety_corpus_detects_injections_and_redacts_secrets() -> None:
    result = run_prompt_safety_corpus()

    assert result.phase == "10"
    assert result.passed is True
    assert result.failed_count == 0
    assert result.network_used is False
    assert result.live_llm_provider_used is False
    injection_cases = {
        case.case_id: set(case.detected_signal_ids)
        for case in result.case_results
        if case.case_id.startswith("PROMPT-INJECT")
    }
    assert "ignore-prior-instructions" in injection_cases["PROMPT-INJECT-001"]
    assert "system-prompt-extraction" in injection_cases["PROMPT-INJECT-002"]
    assert "jailbreak-language" in injection_cases["PROMPT-INJECT-003"]
    secret_case = next(case for case in result.case_results if case.case_id == "PROMPT-REDACT-001")
    assert secret_case.redaction_count >= 1


def test_external_validation_plan_is_explicitly_deferred_and_actionable() -> None:
    plan = build_external_validation_plan()

    assert plan.phase == "10"
    assert plan.network_used is False
    assert plan.task_count >= 8
    task_ids = {task.task_id for task in plan.tasks}
    assert {"P10-EXT-001", "P10-EXT-004", "P10-EXT-006"}.issubset(task_ids)
    assert all(task.exact_future_validation_required for task in plan.tasks)
    assert all(task.exact_future_tooling_environment_required for task in plan.tasks)
    assert all(task.rollback_considerations for task in plan.tasks)


def test_hardening_verification_is_commit_ready_but_not_production_ready() -> None:
    result = verify_local_hardening(repo_root())

    assert result.phase == "10"
    assert result.ready_for_commit is True
    assert result.ready_for_production is False
    assert result.failed_count == 0
    assert result.deferred_count >= 1
    assert result.external_validation_executed is False
    assert result.hosted_ci_executed is False
    assert result.clean_install_validation_executed is False
    assert result.network_used is False
    assert result.live_llm_provider_used is False
    assert result.mcp_used is False
    assert result.browser_used is False
    assert result.active_validation_used is False
    assert result.report_submission_used is False
    check_ids = {check.check_id for check in result.checks}
    assert "HARD-REDACTION-CORPUS" in check_ids
    assert "HARD-PROMPT-SAFETY-CORPUS" in check_ids
    assert "HARD-EXT-VALIDATION-PLAN-OPEN" in check_ids


def test_hardening_cli_commands_render_json() -> None:
    root = str(repo_root())

    checklist = runner.invoke(app, ["hardening", "checklist", "--root", root, "--json"])
    assert checklist.exit_code == 0, checklist.output
    checklist_payload = json.loads(checklist.output)
    assert checklist_payload["phase"] == "10"

    redaction = runner.invoke(app, ["hardening", "redaction-corpus", "--json"])
    assert redaction.exit_code == 0, redaction.output
    redaction_payload = json.loads(redaction.output)
    assert redaction_payload["passed"] is True

    prompt = runner.invoke(app, ["hardening", "prompt-corpus", "--json"])
    assert prompt.exit_code == 0, prompt.output
    prompt_payload = json.loads(prompt.output)
    assert prompt_payload["passed"] is True

    external_plan = runner.invoke(app, ["hardening", "external-plan", "--json"])
    assert external_plan.exit_code == 0, external_plan.output
    plan_payload = json.loads(external_plan.output)
    assert plan_payload["task_count"] >= 8

    verify = runner.invoke(app, ["hardening", "verify", "--root", root, "--json"])
    assert verify.exit_code == 0, verify.output
    verify_payload = json.loads(verify.output)
    assert verify_payload["ready_for_commit"] is True
    assert verify_payload["ready_for_production"] is False


def test_ci_workflow_includes_phase10_hardening_verifier() -> None:
    workflow = (repo_root() / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")

    assert "python scripts/phase9_verify.py --root ." in workflow
    assert "python scripts/phase10_verify.py --root ." in workflow
