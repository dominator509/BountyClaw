from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.gap_tracker import (
    audit_gap_tracker,
    build_codex_gap_backlog,
    export_gap_tracker_package,
    verify_gap_tracker_governance,
)

runner = CliRunner()


def test_gap_tracker_audit_parses_current_gap_ledger() -> None:
    result = audit_gap_tracker(Path("."))

    assert result.phase == "14"
    assert result.entry_count >= 60
    assert not result.duplicate_gap_ids
    assert not result.malformed_entry_ids
    assert result.missing_required_field_count == 0
    assert result.ready_for_codex_backlog is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.raw_evidence_contents_included is False


def test_codex_gap_backlog_covers_all_entries_without_auto_closure() -> None:
    audit = audit_gap_tracker(Path("."))
    backlog = build_codex_gap_backlog(Path("."))

    assert backlog.item_count == audit.entry_count
    assert backlog.ready_for_codex is True
    assert backlog.ready_for_gap_closure is False
    assert backlog.ready_for_production is False
    assert all(item.task_id == f"CODEX-{item.gap_id}" for item in backlog.items)
    assert all(item.human_review_required for item in backlog.items)
    assert all(not item.auto_gap_closure_allowed for item in backlog.items)
    assert all(not item.production_readiness_increase_allowed for item in backlog.items)
    assert backlog.items == sorted(backlog.items, key=lambda item: item.priority_rank)


def test_gap_tracker_export_writes_metadata_only_package(tmp_path: Path) -> None:
    output = tmp_path / "gap_tracker_package"
    result = export_gap_tracker_package(Path("."), output)

    assert result.ready_for_codex is True
    assert result.ready_for_production is False
    written_names = {Path(path).name for path in result.written_files}
    assert {
        "GAP_TRACKER_AUDIT.json",
        "GAP_TRACKER_AUDIT.md",
        "CODEX_GAP_BACKLOG.json",
        "CODEX_GAP_BACKLOG.md",
        "GAP_TRACKER_COMMANDS.md",
    }.issubset(written_names)
    backlog = json.loads((output / "CODEX_GAP_BACKLOG.json").read_text(encoding="utf-8"))
    assert backlog["ready_for_production"] is False
    assert (
        "raw_evidence" not in (output / "CODEX_GAP_BACKLOG.md").read_text(encoding="utf-8").lower()
    )


def test_gap_tracker_verifier_is_commit_ready_but_not_production_ready() -> None:
    result = verify_gap_tracker_governance(Path("."))

    assert result.phase == "14"
    assert result.ready_for_commit is True
    assert result.ready_for_codex is True
    assert result.ready_for_gap_closure is False
    assert result.ready_for_production is False
    assert result.failed_count == 0
    assert result.deferred_count >= 1
    assert result.raw_evidence_contents_included is False


def test_gap_tracker_cli_json_smoke(tmp_path: Path) -> None:
    commands = [
        ["gap-tracker", "audit", "--root", ".", "--json"],
        ["gap-tracker", "backlog", "--root", ".", "--json"],
        ["gap-tracker", "export", "--root", ".", "--output", str(tmp_path / "export"), "--json"],
        ["gap-tracker", "verify", "--root", ".", "--json"],
    ]
    for command in commands:
        result = runner.invoke(app, command)
        assert result.exit_code == 0, result.output
        payload = json.loads(result.output)
        assert payload["phase"] == "14"
        assert payload["ready_for_production"] is False


def test_gap_tracker_audit_detects_missing_required_fields(tmp_path: Path) -> None:
    tracker = tmp_path / "PRODUCTION_GAP_TRACKER.md"
    tracker.write_text(
        "# Deferred Production Tasks\n\n"
        "### PGT-999\n\n"
        "- Unique ID: PGT-999\n"
        "- Phase association: Test Phase\n"
        "- Subsystem association: Test\n"
        "- Description: Missing most fields.\n",
        encoding="utf-8",
    )
    result = audit_gap_tracker(tmp_path)

    assert result.entry_count == 1
    assert result.ready_for_codex_backlog is False
    assert result.entries[0].gap_id == "PGT-999"
    assert "Why incomplete" in result.entries[0].missing_required_fields


def test_phase11_handoff_export_contains_phase14_gap_tracker_commands(tmp_path: Path) -> None:
    from bountyclaw.handoff import export_handoff_package

    output = tmp_path / "handoff"
    result = export_handoff_package(Path("."), output)

    assert "GAP_TRACKER_COMMANDS.md" in {Path(path).name for path in result.written_files}
    command_text = (output / "GAP_TRACKER_COMMANDS.md").read_text(encoding="utf-8")
    assert "gap-tracker audit" in command_text
    assert "do not inspect raw evidence" in command_text
