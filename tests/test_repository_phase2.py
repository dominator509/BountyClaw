from __future__ import annotations

import json
from pathlib import Path

import yaml
from typer.testing import CliRunner

from bountyclaw.cli import app
from bountyclaw.repository import (
    RepositoryAuthorizationError,
    build_scan_plan,
    inspect_authorized_repository,
    inspect_repository,
    plan_authorized_repository_scan,
)
from bountyclaw.scope import load_scope_manifest

runner = CliRunner()


def make_fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "fixture_repo"
    repo.mkdir()
    (repo / "pyproject.toml").write_text("[project]\nname = 'fixture'\n", encoding="utf-8")
    (repo / "package.json").write_text('{"name":"fixture"}\n', encoding="utf-8")
    (repo / "Dockerfile").write_text("FROM scratch\n", encoding="utf-8")
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('authorized fixture')\n", encoding="utf-8")
    (repo / "src" / "web.ts").write_text("export const ok = true;\n", encoding="utf-8")
    (repo / ".git").mkdir()
    (repo / ".git" / "ignored.py").write_text("print('ignored')\n", encoding="utf-8")
    return repo


def write_scope(tmp_path: Path, repo: Path, *, actions: list[str] | None = None) -> Path:
    manifest = {
        "manifest_version": "1",
        "program": {
            "name": "Authorized Phase 2 Fixture",
            "policy_file": "policy.md",
            "disclosure_rules": ["manual report submission only"],
        },
        "authorization": {
            "operator": "fixture-tester",
            "basis": "own_asset",
            "confirmed": True,
            "confirmation_note": "I confirm this fixture repository is authorized for testing.",
        },
        "assets": {
            "repositories": [
                {
                    "path": str(repo),
                    "label": "fixture",
                    "allowed_actions": actions or ["repo.read", "scan.local_static"],
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
    path = tmp_path / "scope.yaml"
    path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
    return path


def test_repository_intake_detects_languages_and_manifests(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)

    fingerprint = inspect_repository(repo)

    languages = {item.language: item.file_count for item in fingerprint.language_summaries}
    manifests = {(item.path, item.ecosystem, item.kind) for item in fingerprint.package_manifests}

    assert languages["Python"] == 1
    assert languages["TypeScript"] == 1
    assert languages["Dockerfile"] == 1
    assert ".git/ignored.py" not in fingerprint.model_dump_json()
    assert ("pyproject.toml", "python", "dependency_manifest") in manifests
    assert ("package.json", "javascript", "dependency_manifest") in manifests
    assert ("Dockerfile", "container", "container_config") in manifests


def test_repository_intake_is_deterministic(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)

    first = inspect_repository(repo)
    second = inspect_repository(repo)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")


def test_scan_plan_is_deterministic_and_non_executing(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    fingerprint = inspect_repository(repo)

    first = build_scan_plan(fingerprint)
    second = build_scan_plan(fingerprint)

    assert first.model_dump(mode="json") == second.model_dump(mode="json")
    assert first.scanners_execute is False
    assert first.network_required is False
    assert all(step.execution_status == "planned_not_executed" for step in first.steps)
    assert any(step.adapter_family == "future.static.python" for step in first.steps)
    assert any(step.adapter_family == "future.dependency.python" for step in first.steps)
    assert any(step.adapter_family == "future.secret_detection.redacted" for step in first.steps)


def test_authorized_inspect_requires_scope_gate_approval(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    manifest_path = write_scope(tmp_path, repo, actions=["scan.local_static"])
    loaded_scope = load_scope_manifest(manifest_path)

    try:
        inspect_authorized_repository(loaded_scope, repo)
    except RepositoryAuthorizationError as exc:
        assert exc.decision.allowed is False
        assert any("not allowlisted" in reason for reason in exc.decision.reasons)
    else:  # pragma: no cover - test must fail if gate is bypassed.
        raise AssertionError("repository intake bypassed scope gate")


def test_authorized_scan_plan_requires_scan_action_approval(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    manifest_path = write_scope(tmp_path, repo, actions=["repo.read"])
    loaded_scope = load_scope_manifest(manifest_path)

    try:
        plan_authorized_repository_scan(loaded_scope, repo)
    except RepositoryAuthorizationError as exc:
        assert exc.decision.action == "scan.local_static"
        assert exc.decision.allowed is False
    else:  # pragma: no cover - test must fail if gate is bypassed.
        raise AssertionError("scan planning bypassed scan.local_static scope gate")


def test_repository_intake_does_not_write_to_repo(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())

    inspect_repository(repo)
    plan = build_scan_plan(inspect_repository(repo))

    after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
    assert before == after
    assert plan.scanners_execute is False


def test_cli_repo_inspect_outputs_json_for_authorized_repo(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    manifest_path = write_scope(tmp_path, repo)

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
    assert payload["root_name"] == "fixture_repo"
    assert payload["fingerprint_id"].startswith("repo-sha256:")


def test_cli_repo_plan_outputs_non_executing_plan(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    manifest_path = write_scope(tmp_path, repo)

    result = runner.invoke(
        app,
        [
            "repo",
            "plan",
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
    assert payload["scanners_execute"] is False
    assert payload["network_required"] is False
    assert payload["steps"]


def test_cli_repo_plan_denies_out_of_scope_repo_before_plan(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    other = tmp_path / "other_repo"
    other.mkdir()
    manifest_path = write_scope(tmp_path, repo)

    result = runner.invoke(
        app,
        [
            "repo",
            "plan",
            "--manifest",
            str(manifest_path),
            "--repo",
            str(other),
        ],
    )

    assert result.exit_code == 2
    assert "DENY: repo.read" in result.output
    assert "not allowlisted" in result.output
