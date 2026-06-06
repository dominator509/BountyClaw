"""Local release-control service for Phase 9."""

import shutil
import subprocess
import tomllib
from pathlib import Path

from .models import (
    ReleaseCheck,
    ReleaseChecklistItem,
    ReleaseChecklistResult,
    ReleaseRollbackPlan,
    ReleaseVerificationResult,
)

MANDATORY_GOVERNANCE_FILES: tuple[str, ...] = (
    "ARCHITECTURE.md",
    "AGENTS.md",
    "ROADMAP.md",
    "PHASE_9_SUBROADMAP.md",
    "PRODUCTION_GAP_TRACKER.md",
)

PHASE_9_RELEASE_DOCS: tuple[str, ...] = (
    "RELEASE.md",
    "ROLLBACK.md",
    "SECURITY_VALIDATION.md",
)

REQUIRED_WORKFLOW_SNIPPETS: tuple[str, ...] = (
    "permissions:",
    "contents: read",
    "actions/checkout@v6",
    "actions/setup-python@v6",
    "persist-credentials: false",
    "python -m compileall -q src tests",
    "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q",
    "ruff check src tests",
    "mypy src",
    "bandit -q -r src",
    "pip-audit",
    "python scripts/phase9_verify.py --root .",
)

REQUIRED_DEV_DEPENDENCIES: tuple[str, ...] = (
    "pytest",
    "ruff",
    "mypy",
    "bandit",
    "pip-audit",
    "build",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _pass_fail(
    *,
    check_id: str,
    category: str,
    passed: bool,
    summary: str,
    evidence: list[str],
    required_for_commit: bool = True,
    required_for_external_release: bool = True,
) -> ReleaseCheck:
    return ReleaseCheck(
        check_id=check_id,
        category=category,  # type: ignore[arg-type]
        status="pass" if passed else "fail",
        summary=summary,
        required_for_commit=required_for_commit,
        required_for_external_release=required_for_external_release,
        evidence=evidence,
    )


def _deferred(
    *,
    check_id: str,
    category: str,
    summary: str,
    deferred_reason: str,
    future_validation_required: str,
    future_environment_required: str,
    required_for_commit: bool = False,
    required_for_external_release: bool = True,
) -> ReleaseCheck:
    return ReleaseCheck(
        check_id=check_id,
        category=category,  # type: ignore[arg-type]
        status="deferred",
        summary=summary,
        required_for_commit=required_for_commit,
        required_for_external_release=required_for_external_release,
        evidence=[],
        deferred_reason=deferred_reason,
        future_validation_required=future_validation_required,
        future_environment_required=future_environment_required,
    )


def _tool_check(
    *,
    check_id: str,
    category: str,
    tool: str,
) -> ReleaseCheck:
    """Validate optional local quality/security tool availability.

    The check does not run full gates, but verifies the executable exists and can
    at least report its own version in this environment.
    """

    path = shutil.which(tool)
    if path is None:
        return _deferred(
            check_id=check_id,
            category=category,
            summary=f"Local optional static/security tool availability: {tool}",
            deferred_reason=(f"The local environment does not currently expose `{tool}` on PATH."),
            future_validation_required=(
                f"Install dev extras and verify {tool} is available before release attempts."
            ),
            future_environment_required=(
                "Codex/local/CI environment with package installation and network access to package indexes where permitted."
            ),
        )

    try:
        result = subprocess.run(
            [tool, "--version"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as exc:
        return _deferred(
            check_id=check_id,
            category=category,
            summary=f"Local optional static/security tool availability: {tool}",
            deferred_reason=f"{tool} was found in PATH but could not be executed: {exc}",
            future_validation_required=(
                f"Repair runtime health for {tool} and rerun release verification."
            ),
            future_environment_required=(
                "Codex/local/CI environment with package installation and network access to package indexes where permitted."
            ),
        )

    if result.returncode != 0:
        return _deferred(
            check_id=check_id,
            category=category,
            summary=f"Local optional static/security tool availability: {tool}",
            deferred_reason=(
                f"{tool} execution failed (`{tool} --version` returned {result.returncode})."
            ),
            future_validation_required=(
                f"Repair runtime health for {tool} and rerun release verification."
            ),
            future_environment_required=(
                "Codex/local/CI environment with package installation and package-index access where permitted."
            ),
        )

    version = (result.stdout or result.stderr).strip().splitlines()[0]
    return _pass_fail(
        check_id=check_id,
        category=category,
        passed=True,
        summary=f"Local optional static/security tool available: {tool}",
        evidence=[f"{tool}: {version}", f"path={path}"],
        required_for_commit=False,
        required_for_external_release=True,
    )


def build_release_checklist(root: Path) -> ReleaseChecklistResult:
    """Build the deterministic Phase 9 release checklist without executing tools."""

    resolved_root = root.expanduser().resolve(strict=False)
    items = [
        ReleaseChecklistItem(
            item_id="REL-001",
            category="governance",
            title="Governance files are current",
            description="Mandatory governance files must exist and identify Phase 9 as complete before commit.",
            owner_agent="Repository governance controller",
            completion_criteria=[
                "ARCHITECTURE.md records Phase 9 completion.",
                "ROADMAP.md marks Phase 9 completed and Phase 10 next.",
                "PRODUCTION_GAP_TRACKER.md records unresolved release gaps.",
            ],
        ),
        ReleaseChecklistItem(
            item_id="REL-002",
            category="ci_cd",
            title="CI workflow is defined",
            description="GitHub Actions workflow must define test, static quality/security, and package validation jobs.",
            owner_agent="DevSecOps orchestrator",
            completion_criteria=[
                ".github/workflows/ci.yml exists.",
                "Workflow uses read-only repository permissions.",
                "Workflow runs tests, compile checks, static gates, and package validation.",
            ],
        ),
        ReleaseChecklistItem(
            item_id="REL-003",
            category="quality",
            title="Local deterministic validation passes",
            description="The local environment must pass pytest and compileall before commit.",
            owner_agent="Release engineering authority",
            completion_criteria=[
                "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q passes.",
                "PYTHONPATH=src python -m compileall -q src tests passes.",
            ],
        ),
        ReleaseChecklistItem(
            item_id="REL-004",
            category="security",
            title="Static security gates are defined",
            description="ruff, mypy, bandit, and pip-audit gates must be declared even if external execution is deferred.",
            owner_agent="AppSec lead",
            completion_criteria=[
                "dev extras include security/quality tools.",
                "CI workflow declares static and dependency security scans.",
                "Gap tracker records unexecuted local/CI scans when tools are unavailable.",
            ],
        ),
        ReleaseChecklistItem(
            item_id="REL-005",
            category="packaging",
            title="Packaging controls are defined",
            description="Build metadata and release checklist must support future clean install and artifact validation.",
            owner_agent="Release engineering authority",
            completion_criteria=[
                "pyproject.toml has build-system and console script metadata.",
                "CI package job builds wheel/sdist and performs a clean smoke import.",
                "External package publishing remains disabled until human approval.",
            ],
        ),
        ReleaseChecklistItem(
            item_id="REL-006",
            category="rollback",
            title="Rollback plan is explicit",
            description="Release changes must be revertible to Phase 8 without touching runtime state.",
            owner_agent="Deterministic SDLC controller",
            completion_criteria=[
                "ROLLBACK.md exists.",
                "release rollback-plan command returns deterministic steps.",
                "No cloud, external accounts, credentials, or production state were introduced.",
            ],
        ),
    ]
    return ReleaseChecklistResult(
        items=items,
        notes=[
            f"Checklist generated for repository root: {resolved_root}",
            "Checklist construction does not execute CI, package publishing, live providers, MCP, browser, active validation, or report submission.",
        ],
    )


def verify_release_controls(root: Path) -> ReleaseVerificationResult:
    """Verify Phase 9 release-control definitions in a local, non-networked way."""

    resolved_root = root.expanduser().resolve(strict=False)
    checks: list[ReleaseCheck] = []

    for filename in MANDATORY_GOVERNANCE_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"REL-GOV-{filename}",
                category="governance",
                passed=path.exists(),
                summary=f"Mandatory governance file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )

    roadmap = _read_text(resolved_root / "ROADMAP.md")
    checks.append(
        _pass_fail(
            check_id="REL-GOV-ROADMAP-PHASE9",
            category="governance",
            passed="Phase 9" in roadmap and "Completed" in roadmap and "Phase 10" in roadmap,
            summary="ROADMAP.md records Phase 9 completion and Phase 10 continuation.",
            evidence=["ROADMAP.md includes Phase 9/Phase 10 markers"],
        )
    )

    gap_tracker = _read_text(resolved_root / "PRODUCTION_GAP_TRACKER.md")
    checks.append(
        _pass_fail(
            check_id="REL-GOV-GAP-TRACKER",
            category="governance",
            passed=(
                "PGT-083" in gap_tracker and "PGT-084" in gap_tracker and "PGT-085" in gap_tracker
            ),
            summary="PRODUCTION_GAP_TRACKER.md records Phase 9 environment-limited release gaps.",
            evidence=["Expected Phase 9 gap IDs found"] if gap_tracker else [],
        )
    )

    workflow_path = resolved_root / ".github" / "workflows" / "ci.yml"
    workflow_text = _read_text(workflow_path)
    checks.append(
        _pass_fail(
            check_id="REL-CI-WORKFLOW-EXISTS",
            category="ci_cd",
            passed=workflow_path.exists(),
            summary="GitHub Actions CI workflow file exists.",
            evidence=[str(workflow_path)] if workflow_path.exists() else [],
        )
    )
    for index, snippet in enumerate(REQUIRED_WORKFLOW_SNIPPETS, start=1):
        checks.append(
            _pass_fail(
                check_id=f"REL-CI-SNIPPET-{index:02d}",
                category="ci_cd",
                passed=snippet in workflow_text,
                summary=f"CI workflow includes required release-control snippet: {snippet}",
                evidence=[snippet] if snippet in workflow_text else [],
            )
        )

    pyproject_path = resolved_root / "pyproject.toml"
    pyproject_text = _read_text(pyproject_path)
    pyproject_data: dict[str, object] = {}
    if pyproject_text:
        pyproject_data = tomllib.loads(pyproject_text)
    project = pyproject_data.get("project", {}) if pyproject_data else {}
    scripts = project.get("scripts", {}) if isinstance(project, dict) else {}
    build_system = pyproject_data.get("build-system", {}) if pyproject_data else {}
    optional_deps = project.get("optional-dependencies", {}) if isinstance(project, dict) else {}
    dev_deps = optional_deps.get("dev", []) if isinstance(optional_deps, dict) else []
    dev_deps_text = "\n".join(str(item) for item in dev_deps)

    checks.append(
        _pass_fail(
            check_id="REL-PKG-BUILD-SYSTEM",
            category="packaging",
            passed=bool(build_system),
            summary="pyproject.toml declares build-system metadata.",
            evidence=[str(build_system)] if build_system else [],
        )
    )
    checks.append(
        _pass_fail(
            check_id="REL-PKG-CONSOLE-SCRIPT",
            category="packaging",
            passed=isinstance(scripts, dict) and scripts.get("bountyclaw") == "bountyclaw.cli:app",
            summary="pyproject.toml declares bountyclaw console script entry point.",
            evidence=["bountyclaw = bountyclaw.cli:app"] if isinstance(scripts, dict) else [],
        )
    )
    for dependency in REQUIRED_DEV_DEPENDENCIES:
        checks.append(
            _pass_fail(
                check_id=f"REL-PKG-DEV-{dependency}",
                category="packaging",
                passed=dependency in dev_deps_text,
                summary=f"dev extras include {dependency} for future local/CI validation.",
                evidence=[dependency] if dependency in dev_deps_text else [],
            )
        )

    for filename in PHASE_9_RELEASE_DOCS:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"REL-DOC-{filename}",
                category="rollback" if filename == "ROLLBACK.md" else "packaging",
                passed=path.exists() and len(_read_text(path).strip()) > 200,
                summary=f"Release documentation exists and is substantive: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )

    verify_script = resolved_root / "scripts" / "phase9_verify.py"
    checks.append(
        _pass_fail(
            check_id="REL-CI-LOCAL-VERIFY-SCRIPT",
            category="ci_cd",
            passed=verify_script.exists(),
            summary="Local deterministic Phase 9 verification script exists.",
            evidence=[str(verify_script)] if verify_script.exists() else [],
        )
    )

    for tool in ("ruff", "mypy", "bandit", "pip-audit", "python"):
        found = shutil.which(tool) is not None
        if tool == "python":
            checks.append(
                _pass_fail(
                    check_id="REL-LOCAL-PYTHON-AVAILABLE",
                    category="quality",
                    passed=found,
                    summary="Local Python executable is available for validation.",
                    evidence=[shutil.which(tool) or ""],
                )
            )
        else:
            checks.append(
                _tool_check(
                    check_id=f"REL-LOCAL-TOOL-{tool}",
                    category="environment_limited",
                    tool=tool,
                )
            )

    checks.extend(
        [
            _deferred(
                check_id="REL-EXT-GITHUB-ACTIONS-RUN",
                category="environment_limited",
                summary="GitHub Actions workflow execution is not performed in ChatGPT Project Mode.",
                deferred_reason="Requires a real GitHub repository and hosted or self-hosted Actions runner.",
                future_validation_required="Push branch/PR, verify CI matrix jobs, artifact build job, security gates, and failure behavior.",
                future_environment_required="GitHub repository with Actions enabled and least-privilege workflow permissions.",
            ),
            _deferred(
                check_id="REL-EXT-CLEAN-INSTALL",
                category="environment_limited",
                summary="Clean virtualenv package install validation is deferred.",
                deferred_reason="Requires dependency installation from package indexes and isolated clean environment setup.",
                future_validation_required="Create fresh virtualenv, install wheel/sdist, run bountyclaw doctor and smoke commands without PYTHONPATH.",
                future_environment_required="Codex/local/CI environment with package installation access.",
            ),
            _deferred(
                check_id="REL-EXT-PUBLISH",
                category="environment_limited",
                summary="Package publishing/release artifact upload is intentionally not performed.",
                deferred_reason="Requires registry credentials, release approval, version policy, signing policy, and human release manager authorization.",
                future_validation_required="Perform TestPyPI/internal registry dry run, verify provenance/signing policy, then publish only after human approval.",
                future_environment_required="Approved package registry, credentials manager, artifact signing/provenance tooling, human release authority.",
            ),
        ]
    )

    passed_count = sum(1 for check in checks if check.status == "pass")
    failed_count = sum(1 for check in checks if check.status == "fail")
    deferred_count = sum(1 for check in checks if check.status == "deferred")
    required_commit_failures = sum(
        1 for check in checks if check.required_for_commit and check.status == "fail"
    )
    required_external_release_deferred = sum(
        1
        for check in checks
        if check.required_for_external_release and check.status in {"fail", "deferred"}
    )
    return ReleaseVerificationResult(
        repository_root=str(resolved_root),
        checks=checks,
        passed_count=passed_count,
        failed_count=failed_count,
        deferred_count=deferred_count,
        required_commit_failures=required_commit_failures,
        required_external_release_deferred=required_external_release_deferred,
        ready_for_commit=required_commit_failures == 0,
        ready_for_external_release=required_external_release_deferred == 0,
        clean_install_validation_executed=False,
        notes=[
            "Phase 9 verification is local and non-networked.",
            "External CI execution, clean install validation, package publishing, signing/provenance, and rollback drills remain deferred until an appropriate environment exists.",
        ],
    )


def build_release_rollback_plan() -> ReleaseRollbackPlan:
    """Return deterministic rollback steps for Phase 9."""

    return ReleaseRollbackPlan(
        steps=[
            "Remove PHASE_9_SUBROADMAP.md.",
            "Remove .github/workflows/ci.yml and .github/dependabot.yml.",
            "Remove RELEASE.md, ROLLBACK.md, SECURITY_VALIDATION.md, and scripts/phase9_verify.py.",
            "Remove src/bountyclaw/release/ and tests/test_release_phase9.py.",
            "Revert release CLI additions in src/bountyclaw/cli.py.",
            "Revert Phase 9 version/config/pyproject changes.",
            "Revert Phase 9 governance and gap-tracker updates.",
        ],
        preserved_fallbacks=[
            "Phase 8 memory/skills behavior remains the rollback-safe baseline.",
            "Phase 7 MCP/browser fixtures remain disabled unless explicitly invoked.",
            "Phase 6 non-submitting report drafts remain local-only.",
        ],
        validation_after_rollback=[
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 PYTHONPATH=src pytest -q",
            "PYTHONPATH=src python -m compileall -q src tests",
            "PYTHONPATH=src python -m bountyclaw doctor",
        ],
        notes=[
            "No cloud infrastructure, registry credentials, external CI state, live providers, MCP servers, browser runtimes, or bounty submissions are introduced by Phase 9.",
            "Rollback does not require deleting any production data because Phase 9 adds release-control definitions only.",
        ],
    )
