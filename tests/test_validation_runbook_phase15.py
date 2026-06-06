from __future__ import annotations

import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.handoff import export_handoff_package
from bountyclaw.validation_runbook import (
    ValidationRunJournalEntry,
    ValidationRunJournalFile,
    assess_run_journal_status,
    build_external_validation_runbook,
    build_run_journal_template,
    export_validation_runbook_package,
    verify_validation_runbook_readiness,
)

runner = CliRunner()


def test_validation_runbook_derives_steps_from_gap_backlog_without_execution() -> None:
    runbook = build_external_validation_runbook(Path("."))

    assert runbook.phase == "15"
    assert runbook.source_phase == "14"
    assert runbook.step_count >= 60
    assert runbook.ready_for_codex_execution is True
    assert runbook.ready_for_gap_closure is False
    assert runbook.ready_for_production is False
    assert runbook.network_used is False
    assert runbook.external_actions_executed is False
    assert runbook.raw_evidence_contents_included is False
    assert all(step.source_backlog_task_id == f"CODEX-{step.gap_id}" for step in runbook.steps)
    assert all(not step.auto_gap_closure_allowed for step in runbook.steps)
    assert all(not step.production_readiness_increase_allowed for step in runbook.steps)
    assert all(not step.raw_evidence_content_allowed for step in runbook.steps)


def test_execution_journal_template_is_metadata_only_and_non_closing() -> None:
    runbook = build_external_validation_runbook(Path("."))
    template = build_run_journal_template(Path("."))

    assert template.phase == "15"
    assert len(template.entries) == runbook.step_count
    assert template.raw_evidence_contents_included is False
    assert template.ready_for_gap_closure is False
    assert template.ready_for_production is False
    assert all(entry.status == "planned" for entry in template.entries)
    assert all(entry.production_gap_closed is False for entry in template.entries)
    assert all(entry.production_readiness_changed is False for entry in template.entries)


def test_journal_status_blocks_missing_journal_and_never_closes_gaps(tmp_path: Path) -> None:
    result = assess_run_journal_status(Path("."), tmp_path / "missing.json")

    assert result.phase == "15"
    assert result.step_count >= 60
    assert result.missing_journal_count == result.step_count
    assert result.ready_for_evidence_ledger is False
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.raw_evidence_contents_included is False
    assert all(not status.accepted_for_evidence_ledger for status in result.step_statuses)


def test_passed_journal_metadata_can_feed_evidence_ledger_without_closing_gap(
    tmp_path: Path,
) -> None:
    runbook = build_external_validation_runbook(Path("."))
    step = runbook.steps[0]
    journal = ValidationRunJournalFile(
        entries=[
            ValidationRunJournalEntry(
                run_id="RUN-001",
                step_id=step.step_id,
                source_backlog_task_id=step.source_backlog_task_id,
                gap_id=step.gap_id,
                status="passed",
                executor="codex-smoke",
                executor_agent_type=step.recommended_future_agent_type,
                environment="external local smoke fixture",
                completed_at_utc="2026-06-01T00:00:00Z",
                command_summary="metadata-only smoke fixture; no raw output",
                evidence_artifact_ids=["ARTIFACT-SMOKE-001"],
                evidence_sha256={"ARTIFACT-SMOKE-001": "a" * 64},
            )
        ]
    )
    path = tmp_path / "execution_journal.json"
    path.write_text(journal.model_dump_json(indent=2), encoding="utf-8")

    result = assess_run_journal_status(Path("."), path)

    assert result.ready_for_evidence_ledger is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    accepted = [status for status in result.step_statuses if status.accepted_for_evidence_ledger]
    assert len(accepted) == 1
    assert accepted[0].gap_id == step.gap_id
    assert accepted[0].evidence_sha256 == {"ARTIFACT-SMOKE-001": "a" * 64}


def test_journal_schema_rejects_raw_evidence_and_auto_closure_claims() -> None:
    with pytest.raises(ValidationError):
        ValidationRunJournalEntry(
            run_id="RUN-BAD",
            step_id="P15-RUNBOOK-001",
            source_backlog_task_id="CODEX-PGT-001",
            gap_id="PGT-001",
            raw_evidence_contents_included=True,  # type: ignore[arg-type]
        )
    with pytest.raises(ValidationError):
        ValidationRunJournalEntry(
            run_id="RUN-BAD",
            step_id="P15-RUNBOOK-001",
            source_backlog_task_id="CODEX-PGT-001",
            gap_id="PGT-001",
            production_gap_closed=True,  # type: ignore[arg-type]
        )


def test_validation_runbook_export_and_handoff_include_commands(tmp_path: Path) -> None:
    output = tmp_path / "runbook"
    result = export_validation_runbook_package(Path("."), output)

    assert result.ready_for_codex_execution is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    written = {Path(path).name for path in result.written_files}
    assert {
        "VALIDATION_RUNBOOK.json",
        "VALIDATION_RUNBOOK.md",
        "EXECUTION_JOURNAL_TEMPLATE.json",
        "EXECUTION_JOURNAL_INSTRUCTIONS.md",
        "EXECUTION_JOURNAL_STATUS.json",
        "VALIDATION_RUNBOOK_COMMANDS.md",
        "validation_runbook_manifest.json",
    }.issubset(written)
    commands = (output / "VALIDATION_RUNBOOK_COMMANDS.md").read_text(encoding="utf-8")
    assert "validation-runbook build" in commands
    assert "do not execute external validation" in commands.lower()

    handoff_output = tmp_path / "handoff"
    handoff = export_handoff_package(Path("."), handoff_output)
    assert "VALIDATION_RUNBOOK_COMMANDS.md" in {Path(path).name for path in handoff.written_files}
    handoff_commands = (handoff_output / "VALIDATION_RUNBOOK_COMMANDS.md").read_text(
        encoding="utf-8"
    )
    assert "validation-runbook verify" in handoff_commands


def test_validation_runbook_verifier_is_codex_ready_but_not_production_ready() -> None:
    result = verify_validation_runbook_readiness(Path("."))

    assert result.phase == "15"
    assert result.ready_for_commit is True
    assert result.ready_for_codex is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.failed_count == 0
    assert result.deferred_count >= 1
    assert result.raw_evidence_contents_included is False


def test_validation_runbook_cli_commands_render_json(tmp_path: Path) -> None:
    commands = [
        ["validation-runbook", "build", "--root", ".", "--json"],
        ["validation-runbook", "journal-template", "--root", ".", "--json"],
        [
            "validation-runbook",
            "journal-status",
            "--root",
            ".",
            "--journal",
            str(tmp_path / "missing.json"),
            "--json",
        ],
        [
            "validation-runbook",
            "export",
            "--root",
            ".",
            "--output",
            str(tmp_path / "export"),
            "--json",
        ],
        ["validation-runbook", "verify", "--root", ".", "--json"],
    ]
    for command in commands:
        result = runner.invoke(app, command)
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["phase"] == "15"
        assert payload["ready_for_production"] is False


def test_ci_workflow_includes_phase15_runbook_verifier() -> None:
    workflow = Path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "python scripts/phase15_verify.py --root ." in workflow
