from __future__ import annotations

from pathlib import Path

from bountyclaw.repository import build_scan_plan, inspect_repository


def make_fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "src").mkdir(parents=True)
    (repo / "node_modules" / "ignored").mkdir(parents=True)
    (repo / "src" / "app.py").write_text("print('fixture')\n", encoding="utf-8")
    (repo / "src" / "web.ts").write_text("export const value = 1;\n", encoding="utf-8")
    (repo / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
    (repo / "package.json").write_text('{"name":"fixture"}\n', encoding="utf-8")
    (repo / "Dockerfile").write_text("FROM python:3.12-slim\n", encoding="utf-8")
    (repo / "node_modules" / "ignored" / "ignored.js").write_text("ignored\n", encoding="utf-8")
    return repo


def test_repository_intake_detects_languages_and_manifests_deterministically(
    tmp_path: Path,
) -> None:
    repo = make_fixture_repo(tmp_path)

    first = inspect_repository(repo)
    second = inspect_repository(repo)

    assert first == second
    assert first.file_count == 5
    assert {summary.language for summary in first.language_summaries} == {
        "Dockerfile",
        "Python",
        "TypeScript",
    }
    assert {manifest.path for manifest in first.package_manifests} == {
        "Dockerfile",
        "package.json",
        "pyproject.toml",
    }
    assert first.fingerprint_id.startswith("repo-sha256:")


def test_repository_intake_is_read_only(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    before = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())

    inspect_repository(repo)

    after = sorted(path.relative_to(repo).as_posix() for path in repo.rglob("*") if path.is_file())
    assert after == before
    assert not (repo / ".bountyclaw").exists()


def test_scan_plan_is_deterministic_and_never_executes_scanners(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    fingerprint = inspect_repository(repo)

    first = build_scan_plan(fingerprint)
    second = build_scan_plan(fingerprint)

    assert first == second
    assert first.scanners_execute is False
    assert first.network_required is False
    assert first.llm_required is False
    assert first.mcp_required is False
    assert first.browser_required is False
    assert {step.execution_status for step in first.steps} == {"planned_not_executed"}
    adapter_families = {step.adapter_family for step in first.steps}
    assert "future.static.python" in adapter_families
    assert "future.static.typescript" in adapter_families
    assert "future.dependency.python" in adapter_families
    assert "future.dependency.javascript" in adapter_families
    assert "future.secret_detection.redacted" in adapter_families


def test_repository_intake_skips_symlinks(tmp_path: Path) -> None:
    repo = make_fixture_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "outside.py").write_text("print('outside')\n", encoding="utf-8")
    link = repo / "linked-outside"
    try:
        link.symlink_to(outside, target_is_directory=True)
    except OSError:
        return

    fingerprint = inspect_repository(repo)

    assert fingerprint.file_count == 5
    assert "outside.py" not in fingerprint.fingerprint_id
