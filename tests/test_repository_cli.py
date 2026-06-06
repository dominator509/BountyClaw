from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from bountyclaw.cli import app

runner = CliRunner()


def make_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "src" / "app.py").write_text("print('authorized')\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='authorized'\n", encoding="utf-8")
    return repo


def write_manifest(
    tmp_path: Path,
    repo_path: Path,
    *,
    allowed_actions: list[str] | None = None,
) -> Path:
    manifest = {
        "manifest_version": "1",
        "program": {"name": "Repo CLI Fixture Program", "policy_file": "policy.md"},
        "authorization": {
            "operator": "repo-cli-tester",
            "basis": "own_asset",
            "confirmed": True,
            "confirmation_note": "I confirm this fixture repository is authorized for repo CLI testing.",
        },
        "assets": {
            "repositories": [
                {
                    "path": str(repo_path),
                    "allowed_actions": allowed_actions or ["repo.read", "scan.local_static"],
                }
            ],
            "domains": [],
            "out_of_scope": [],
        },
        "controls": {"network_access_enabled": False},
    }
    path = tmp_path / "scope.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return path


def test_repo_inspect_outputs_json_for_allowlisted_repo(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)

    result = runner.invoke(
        app,
        [
            "repo",
            "inspect",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(repo),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["root"] == str(repo.resolve())
    assert payload["file_count"] == 2
    assert {summary["language"] for summary in payload["language_summaries"]} == {"Python"}
    assert payload["package_manifests"][0]["path"] == "pyproject.toml"


def test_repo_plan_outputs_non_executing_json_plan(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)

    result = runner.invoke(
        app,
        ["repo", "plan", "--manifest", str(manifest_path), "--repo", str(repo), "--format", "json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["scanners_execute"] is False
    assert payload["network_required"] is False
    assert payload["llm_required"] is False
    assert payload["mcp_required"] is False
    assert payload["browser_required"] is False
    assert {step["execution_status"] for step in payload["steps"]} == {"planned_not_executed"}


def test_repo_plan_requires_scan_local_static_before_reading_repo(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo, allowed_actions=["repo.read"])

    result = runner.invoke(
        app,
        ["repo", "plan", "--manifest", str(manifest_path), "--repo", str(repo), "--format", "json"],
    )

    assert result.exit_code == 2
    assert "DENY: scan.local_static" in result.output


def test_repo_inspect_denies_unallowlisted_repo(tmp_path: Path) -> None:
    allowed_repo = make_repo(tmp_path)
    other_repo = tmp_path / "other"
    other_repo.mkdir()
    manifest_path = write_manifest(tmp_path, allowed_repo)

    result = runner.invoke(
        app,
        [
            "repo",
            "inspect",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(other_repo),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 2
    assert "DENY: repo.read" in result.output
    assert "not allowlisted" in result.output


def test_repo_plan_writes_audit_log(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)
    audit_path = tmp_path / "audit" / "events.jsonl"

    result = runner.invoke(
        app,
        [
            "repo",
            "plan",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(repo),
            "--audit-log",
            str(audit_path),
        ],
    )

    assert result.exit_code == 0
    lines = audit_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    payload = json.loads(lines[0])
    assert payload["event_type"] == "repo.plan"
    assert payload["decision"] == "allow"


def test_repo_inspect_accepts_json_shortcut(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)

    result = runner.invoke(
        app,
        ["repo", "inspect", "--manifest", str(manifest_path), "--repo", str(repo), "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["root"] == str(repo.resolve())
    assert payload["file_count"] == 2


def test_repo_plan_accepts_json_shortcut(tmp_path: Path) -> None:
    repo = make_repo(tmp_path)
    manifest_path = write_manifest(tmp_path, repo)

    result = runner.invoke(
        app,
        ["repo", "plan", "--manifest", str(manifest_path), "--repo", str(repo), "--json"],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["scanners_execute"] is False
    assert payload["network_required"] is False


def test_repo_command_help_advertises_json_shortcut() -> None:
    inspect_result = runner.invoke(app, ["repo", "inspect", "--help"])
    plan_result = runner.invoke(app, ["repo", "plan", "--help"])

    assert inspect_result.exit_code == 0
    assert plan_result.exit_code == 0
    assert "--json" in inspect_result.output
    assert "--json" in plan_result.output
