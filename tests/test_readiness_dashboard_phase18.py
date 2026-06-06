from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.handoff import export_handoff_package
from bountyclaw.readiness_dashboard import (
    build_external_executor_index,
    build_readiness_dashboard,
    export_readiness_dashboard_package,
    verify_readiness_dashboard,
)

runner = CliRunner()


def test_readiness_dashboard_is_metadata_only_and_non_production() -> None:
    dashboard = build_readiness_dashboard(Path("."))

    assert dashboard.phase == "18"
    assert dashboard.source_phase == "17"
    assert dashboard.production_readiness_percent >= 90
    assert dashboard.gap_entry_count >= 70
    assert dashboard.ready_for_commit is True
    assert dashboard.ready_for_codex is True
    assert dashboard.ready_for_external_executor is True
    assert dashboard.ready_for_gap_closure is False
    assert dashboard.ready_for_production is False
    assert dashboard.network_used is False
    assert dashboard.external_actions_executed is False
    assert dashboard.raw_evidence_contents_included is False
    assert dashboard.raw_source_contents_included is False
    assert {status.subsystem_id for status in dashboard.subsystem_statuses} >= {
        "release-controls",
        "hardening-controls",
        "external-handoff",
        "validation-evidence-ledger",
        "evidence-review-workflow",
        "gap-tracker-governance",
        "validation-runbook",
        "validation-baseline",
        "closure-gate",
    }


def test_external_executor_index_is_ordered_and_non_closing() -> None:
    index = build_external_executor_index(Path("."))

    assert index.phase == "18"
    assert index.command_count >= 8
    assert [command.order for command in index.commands] == sorted(
        command.order for command in index.commands
    )
    assert all(command.closes_gaps is False for command in index.commands)
    assert all(command.changes_production_readiness is False for command in index.commands)
    assert all(command.raw_evidence_contents_included is False for command in index.commands)
    assert any("validation-baseline export" in command.command for command in index.commands)
    assert any("closure-gate export" in command.command for command in index.commands)
    assert any("readiness-dashboard export" in command.command for command in index.commands)


def test_dashboard_export_and_handoff_include_commands(tmp_path: Path) -> None:
    output = tmp_path / "dashboard"
    result = export_readiness_dashboard_package(Path("."), output)

    assert result.phase == "18"
    assert result.ready_for_commit is True
    assert result.ready_for_codex is True
    assert result.ready_for_external_executor is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    names = {Path(path).name for path in result.written_files}
    assert {
        "readiness_dashboard.json",
        "external_executor_index.json",
        "READINESS_DASHBOARD.md",
        "EXTERNAL_EXECUTOR_INDEX.md",
        "READINESS_DASHBOARD_COMMANDS.md",
        "readiness_dashboard_index.json",
    }.issubset(names)
    assert (
        "raw evidence"
        in (output / "READINESS_DASHBOARD_COMMANDS.md").read_text(encoding="utf-8").lower()
    )

    handoff_output = tmp_path / "handoff"
    handoff = export_handoff_package(Path("."), handoff_output)
    assert "READINESS_DASHBOARD_COMMANDS.md" in {Path(path).name for path in handoff.written_files}
    assert "phase18_verify.py" in (handoff_output / "READINESS_DASHBOARD_COMMANDS.md").read_text(
        encoding="utf-8"
    )


def test_readiness_dashboard_verifier_is_codex_ready_not_production_ready() -> None:
    result = verify_readiness_dashboard(Path("."))

    assert result.phase == "18"
    assert result.source_phase == "17"
    assert result.ready_for_commit is True
    assert result.ready_for_codex is True
    assert result.ready_for_external_executor is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.failed_count == 0
    assert result.deferred_count >= 1
    assert result.raw_evidence_contents_included is False
    assert result.raw_source_contents_included is False


def test_readiness_dashboard_cli_json_smoke() -> None:
    # Keep the unit-level CLI smoke focused and fast; full build/export/verify
    # commands are exercised through direct CLI validation in the phase workflow.
    result = runner.invoke(app, ["readiness-dashboard", "handoff-index", "--root", ".", "--json"])
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["phase"] == "18"
    assert payload["ready_for_production"] is False
    assert payload["command_count"] >= 8
