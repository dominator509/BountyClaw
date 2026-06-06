"""Validation baseline snapshot services for Phase 16.

The validation-baseline subsystem emits hash-only source snapshot metadata for
future Codex/local/CI/human validation. It never exports raw source contents,
reads raw validation evidence, closes production gaps, raises readiness, or runs
external validation.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from bountyclaw.gap_tracker import audit_gap_tracker, build_codex_gap_backlog
from bountyclaw.handoff import verify_handoff_readiness
from bountyclaw.hardening import verify_local_hardening
from bountyclaw.release import verify_release_controls
from bountyclaw.validation_runbook import verify_validation_runbook_readiness

from .models import (
    BaselineCategory,
    BaselineFileRecord,
    ValidationBaselineCheck,
    ValidationBaselineExportResult,
    ValidationBaselineManifest,
    ValidationBaselineVerificationResult,
)

EXCLUDED_DIRECTORY_NAMES: frozenset[str] = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        ".tox",
        ".venv",
        "venv",
        "env",
        "dist",
        "build",
        ".bountyclaw",
        "validation_evidence",
        "validation_runs",
        "validation_handoff",
        "validation_runbook",
        "validation_evidence_ledger",
        "validation_evidence_review",
        "gap_tracker_package",
    }
)

EXCLUDED_FILE_SUFFIXES: tuple[str, ...] = (
    ".pyc",
    ".pyo",
    ".sqlite",
    ".db",
    ".zip",
    ".tar",
    ".gz",
    ".whl",
)

MANDATORY_PHASE_16_GOVERNANCE_FILES: tuple[str, ...] = (
    "ARCHITECTURE.md",
    "AGENTS.md",
    "ROADMAP.md",
    "PHASE_15_SUBROADMAP.md",
    "PHASE_16_SUBROADMAP.md",
    "PRODUCTION_GAP_TRACKER.md",
    "MARKDOWN_REVIEW_PHASE16.md",
)

MANDATORY_PHASE_16_SUPPORT_FILES: tuple[str, ...] = (
    "README.md",
    "RELEASE.md",
    "ROLLBACK.md",
    "SECURITY_VALIDATION.md",
    "scripts/phase9_verify.py",
    "scripts/phase10_verify.py",
    "scripts/phase11_verify.py",
    "scripts/phase12_verify.py",
    "scripts/phase13_verify.py",
    "scripts/phase14_verify.py",
    "scripts/phase15_verify.py",
    "scripts/phase16_verify.py",
)

EXPECTED_PHASE_16_GAP_IDS: tuple[str, ...] = ("PGT-112", "PGT-113", "PGT-114")


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _manifest_digest(records: list[BaselineFileRecord]) -> str:
    payload = [
        {
            "path": record.path,
            "sha256": record.sha256,
            "size_bytes": record.size_bytes,
            "category": record.category,
        }
        for record in records
    ]
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _should_exclude(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    parts = set(relative.parts)
    if parts & EXCLUDED_DIRECTORY_NAMES:
        return True
    if path.name.startswith(".") and path.name not in {".github"}:
        return True
    return path.suffix in EXCLUDED_FILE_SUFFIXES


def _categorize(relative_path: str) -> BaselineCategory:
    if relative_path in {"ARCHITECTURE.md", "AGENTS.md", "ROADMAP.md", "PRODUCTION_GAP_TRACKER.md"}:
        return "governance_markdown"
    if relative_path.startswith("PHASE_") and relative_path.endswith("_SUBROADMAP.md"):
        return "phase_subroadmap"
    if relative_path.startswith("MARKDOWN_REVIEW_PHASE") and relative_path.endswith(".md"):
        return "markdown_review"
    if relative_path in {"README.md", "RELEASE.md", "ROLLBACK.md", "SECURITY_VALIDATION.md"}:
        return "documentation"
    if relative_path.startswith("src/") and relative_path.endswith(".py"):
        return "python_source"
    if relative_path.startswith("tests/") and relative_path.endswith(".py"):
        return "python_test"
    if relative_path.startswith("scripts/") and relative_path.endswith(".py"):
        return "script"
    if relative_path.startswith(".github/"):
        return "ci_config"
    if relative_path == "pyproject.toml":
        return "package_config"
    if relative_path.endswith((".toml", ".yaml", ".yml", ".json")):
        return "configuration"
    if relative_path.endswith(".md"):
        return "documentation"
    return "other"


def _pass_fail(
    *,
    check_id: str,
    passed: bool,
    summary: str,
    evidence: list[str] | None = None,
    required_for_commit: bool = True,
    required_for_codex: bool = True,
    required_for_production: bool = True,
) -> ValidationBaselineCheck:
    return ValidationBaselineCheck(
        check_id=check_id,
        status="pass" if passed else "fail",
        summary=summary,
        required_for_commit=required_for_commit,
        required_for_codex=required_for_codex,
        required_for_production=required_for_production,
        evidence=evidence or [],
    )


def _deferred(
    *,
    check_id: str,
    summary: str,
    deferred_reason: str,
    future_validation_required: str,
    future_environment_required: str,
    required_for_commit: bool = False,
    required_for_codex: bool = False,
    required_for_production: bool = True,
) -> ValidationBaselineCheck:
    return ValidationBaselineCheck(
        check_id=check_id,
        status="deferred",
        summary=summary,
        required_for_commit=required_for_commit,
        required_for_codex=required_for_codex,
        required_for_production=required_for_production,
        deferred_reason=deferred_reason,
        future_validation_required=future_validation_required,
        future_environment_required=future_environment_required,
    )


def build_validation_baseline_manifest(root: Path) -> ValidationBaselineManifest:
    """Build a hash-only source baseline manifest for future evidence binding."""

    resolved_root = root.expanduser().resolve(strict=False)
    records: list[BaselineFileRecord] = []
    excluded: list[str] = []
    for path in sorted(resolved_root.rglob("*")):
        if not path.is_file():
            continue
        if _should_exclude(path, resolved_root):
            try:
                excluded.append(path.relative_to(resolved_root).as_posix())
            except ValueError:
                excluded.append(str(path))
            continue
        try:
            relative = path.relative_to(resolved_root).as_posix()
        except ValueError:
            continue
        records.append(
            BaselineFileRecord(
                path=relative,
                sha256=_file_sha256(path),
                size_bytes=path.stat().st_size,
                category=_categorize(relative),
            )
        )
    baseline_id = _manifest_digest(records)
    markdown_count = sum(1 for record in records if record.path.endswith(".md"))
    python_count = sum(1 for record in records if record.path.endswith(".py"))
    governance_count = sum(
        1
        for record in records
        if record.category in {"governance_markdown", "phase_subroadmap", "markdown_review"}
    )
    mandatory_present = all(
        (resolved_root / filename).exists() for filename in MANDATORY_PHASE_16_GOVERNANCE_FILES
    )
    return ValidationBaselineManifest(
        repository_root=str(resolved_root),
        baseline_id=baseline_id,
        files=records,
        file_count=len(records),
        markdown_file_count=markdown_count,
        python_file_count=python_count,
        governance_file_count=governance_count,
        excluded_path_count=len(excluded),
        excluded_path_samples=excluded[:25],
        ready_for_external_validation_reference=bool(records) and mandatory_present,
        notes=[
            "Phase 16 baseline manifest is hash-only and local-only.",
            "The manifest can bind future external validation evidence to a source snapshot.",
            "The manifest does not include raw source contents, raw evidence contents, gap closures, or production-readiness claims.",
        ],
    )


def _manifest_markdown(manifest: ValidationBaselineManifest) -> str:
    category_counts: dict[str, int] = {}
    for record in manifest.files:
        category_counts[record.category] = category_counts.get(record.category, 0) + 1
    lines = [
        "# Phase 16 Validation Baseline Manifest",
        "",
        f"- Baseline ID: `{manifest.baseline_id}`",
        f"- File count: {manifest.file_count}",
        f"- Markdown files: {manifest.markdown_file_count}",
        f"- Python files: {manifest.python_file_count}",
        f"- Governance files: {manifest.governance_file_count}",
        f"- Ready for external validation reference: {str(manifest.ready_for_external_validation_reference).lower()}",
        "- Ready for gap closure: false",
        "- Ready for production: false",
        "",
        "## Category Counts",
        "",
    ]
    for category in sorted(category_counts):
        lines.append(f"- {category}: {category_counts[category]}")
    lines.extend(
        [
            "",
            "## Safety Notes",
            "",
            "This manifest contains file paths, sizes, categories, and SHA-256 hashes only.",
            "It must not be treated as external validation evidence by itself.",
            "Future evidence must reference this baseline ID and still pass Phase 12/13/14/15 governance.",
        ]
    )
    return "\n".join(lines)


def _commands_markdown() -> str:
    return "\n".join(
        [
            "# Phase 16 Validation Baseline Commands",
            "",
            "Run these commands before and after future external validation to bind evidence to an exact source snapshot.",
            "",
            "- `python -m bountyclaw validation-baseline manifest --root . --json`",
            "- `python -m bountyclaw validation-baseline export --root . --output validation_baseline --json`",
            "- `python -m bountyclaw validation-baseline verify --root . --json`",
            "- `python scripts/phase16_verify.py --root . --json`",
            "",
            "These commands create hash-only source baseline metadata. They do not execute external validation, inspect raw evidence, close gaps, or prove production readiness.",
        ]
    )


def export_validation_baseline_package(
    root: Path, output_dir: Path
) -> ValidationBaselineExportResult:
    """Export the Phase 16 source baseline package."""

    resolved_output = output_dir.expanduser().resolve(strict=False)
    resolved_output.mkdir(parents=True, exist_ok=True)
    manifest = build_validation_baseline_manifest(root)
    files = {
        "validation_baseline_manifest.json": manifest.model_dump_json(indent=2),
        "VALIDATION_BASELINE.md": _manifest_markdown(manifest),
        "VALIDATION_BASELINE_COMMANDS.md": _commands_markdown(),
    }
    written_files: list[str] = []
    for filename, content in files.items():
        path = resolved_output / filename
        path.write_text(content + ("\n" if not content.endswith("\n") else ""), encoding="utf-8")
        written_files.append(str(path))
    index_payload = {
        "phase": "16",
        "baseline_id": manifest.baseline_id,
        "file_count": manifest.file_count,
        "ready_for_external_validation_reference": manifest.ready_for_external_validation_reference,
        "ready_for_gap_closure": False,
        "ready_for_production": False,
        "network_used": False,
        "external_actions_executed": False,
        "raw_evidence_contents_included": False,
        "raw_source_contents_included": False,
        "written_files": written_files,
    }
    index_path = resolved_output / "validation_baseline_index.json"
    index_path.write_text(
        json.dumps(index_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    written_files.append(str(index_path))
    return ValidationBaselineExportResult(
        output_directory=str(resolved_output),
        baseline_id=manifest.baseline_id,
        written_files=written_files,
        file_count=manifest.file_count,
        ready_for_external_validation_reference=manifest.ready_for_external_validation_reference,
        notes=[
            "Baseline export is local-only and hash-only.",
            "Future evidence may reference the baseline ID, but human review remains required before gap closure.",
        ],
    )


def verify_validation_baseline_readiness(root: Path) -> ValidationBaselineVerificationResult:
    """Verify Phase 16 validation-baseline readiness without external execution."""

    resolved_root = root.expanduser().resolve(strict=False)
    manifest = build_validation_baseline_manifest(resolved_root)
    checks: list[ValidationBaselineCheck] = []

    for filename in MANDATORY_PHASE_16_GOVERNANCE_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"BASELINE-GOV-{filename}",
                passed=path.exists(),
                summary=f"Mandatory Phase 16 governance file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )
    for filename in MANDATORY_PHASE_16_SUPPORT_FILES:
        path = resolved_root / filename
        checks.append(
            _pass_fail(
                check_id=f"BASELINE-SUPPORT-{filename}",
                passed=path.exists(),
                summary=f"Mandatory Phase 16 support file exists: {filename}",
                evidence=[str(path)] if path.exists() else [],
            )
        )

    architecture = _read_text(resolved_root / "ARCHITECTURE.md")
    roadmap = _read_text(resolved_root / "ROADMAP.md")
    gap_tracker = _read_text(resolved_root / "PRODUCTION_GAP_TRACKER.md")
    workflow = _read_text(resolved_root / ".github" / "workflows" / "ci.yml")
    pyproject = _read_text(resolved_root / "pyproject.toml")

    checks.extend(
        [
            _pass_fail(
                check_id="BASELINE-GOV-ARCH-PHASE16",
                passed="Phase 16" in architecture and "Validation Baseline" in architecture,
                summary="ARCHITECTURE.md records Phase 16 validation-baseline subsystem.",
                evidence=["Phase 16 validation baseline architecture marker found"]
                if "Phase 16" in architecture
                else [],
            ),
            _pass_fail(
                check_id="BASELINE-GOV-ROADMAP-PHASE16",
                passed="Phase 16" in roadmap
                and "Validation Baseline" in roadmap
                and "Completed" in roadmap,
                summary="ROADMAP.md records Phase 16 completion and remaining external validation.",
                evidence=["Phase 16 roadmap marker found"] if "Phase 16" in roadmap else [],
            ),
            _pass_fail(
                check_id="BASELINE-GOV-GAPS-PHASE16",
                passed=all(gap_id in gap_tracker for gap_id in EXPECTED_PHASE_16_GAP_IDS),
                summary="PRODUCTION_GAP_TRACKER.md records Phase 16 baseline gaps.",
                evidence=list(EXPECTED_PHASE_16_GAP_IDS) if gap_tracker else [],
            ),
            _pass_fail(
                check_id="BASELINE-CI-PHASE16-VERIFY-DEFINED",
                passed="python scripts/phase16_verify.py --root ." in workflow,
                summary="CI definition includes Phase 16 validation-baseline verification script.",
                evidence=["python scripts/phase16_verify.py --root ."]
                if "phase16_verify.py" in workflow
                else [],
            ),
            _pass_fail(
                check_id="BASELINE-PKG-VERSION-CURRENT",
                passed=(
                    ('version = "0.17.0"' in pyproject and 'phase = "17"' in pyproject)
                    or ('version = "0.18.0"' in pyproject and 'phase = "18"' in pyproject)
                    or ('version = "0.19.0"' in pyproject and 'phase = "19"' in pyproject)
                ),
                summary="pyproject.toml records current Phase 18 or compatible Phase 17 non-production version and phase metadata while preserving Phase 16 baseline tooling.",
                evidence=["version/phase metadata compatible with Phase 16 baseline tooling"]
                if ("0.17.0" in pyproject or "0.18.0" in pyproject or "0.19.0" in pyproject)
                else [],
            ),
            _pass_fail(
                check_id="BASELINE-MANIFEST-HAS-FILES",
                passed=manifest.file_count > 0
                and manifest.markdown_file_count > 0
                and manifest.python_file_count > 0,
                summary="Validation baseline includes Markdown and Python source/test files.",
                evidence=[
                    f"file_count={manifest.file_count}",
                    f"baseline_id={manifest.baseline_id}",
                ],
            ),
            _pass_fail(
                check_id="BASELINE-MANIFEST-HASH-ONLY",
                passed=not manifest.raw_evidence_contents_included
                and not manifest.raw_source_contents_included,
                summary="Validation baseline manifest is hash-only and does not include raw source/evidence contents.",
                evidence=[
                    "raw_evidence_contents_included=false",
                    "raw_source_contents_included=false",
                ],
            ),
        ]
    )

    release_result = verify_release_controls(resolved_root)
    hardening_result = verify_local_hardening(resolved_root)
    handoff_result = verify_handoff_readiness(resolved_root)
    runbook_result = verify_validation_runbook_readiness(resolved_root)
    gap_audit = audit_gap_tracker(resolved_root)
    gap_backlog = build_codex_gap_backlog(resolved_root)

    checks.extend(
        [
            _pass_fail(
                check_id="BASELINE-REGRESSION-RELEASE",
                passed=release_result.ready_for_commit,
                summary="Phase 9 release verifier remains commit-ready.",
                evidence=[
                    f"passed={release_result.passed_count}",
                    f"failed={release_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="BASELINE-REGRESSION-HARDENING",
                passed=hardening_result.ready_for_commit,
                summary="Phase 10 hardening verifier remains commit-ready.",
                evidence=[
                    f"passed={hardening_result.passed_count}",
                    f"failed={hardening_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="BASELINE-REGRESSION-HANDOFF",
                passed=handoff_result.ready_for_commit and handoff_result.ready_for_codex,
                summary="Phase 11 handoff verifier remains commit-ready and Codex-ready.",
                evidence=[
                    f"passed={handoff_result.passed_count}",
                    f"failed={handoff_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="BASELINE-REGRESSION-RUNBOOK",
                passed=runbook_result.ready_for_commit and runbook_result.ready_for_codex,
                summary="Phase 15 validation-runbook verifier remains commit-ready and Codex-ready.",
                evidence=[
                    f"passed={runbook_result.passed_count}",
                    f"failed={runbook_result.failed_count}",
                ],
            ),
            _pass_fail(
                check_id="BASELINE-GAP-AUDIT-CLEAN",
                passed=gap_audit.ready_for_codex_backlog and gap_backlog.ready_for_codex,
                summary="Gap tracker audit/backlog remain structurally ready for Codex execution.",
                evidence=[
                    f"gap_count={gap_audit.entry_count}",
                    f"backlog_count={gap_backlog.item_count}",
                ],
            ),
        ]
    )

    checks.append(
        _deferred(
            check_id="BASELINE-EXTERNAL-VALIDATION-STILL-OPEN",
            summary="Phase 16 baseline is ready for future evidence binding but external validation still has not run.",
            deferred_reason="ChatGPT Project Mode cannot run hosted CI, clean package installs, external scanner sandboxes, live providers, real MCP/browser runtimes, human report review, operational drills, branch protection, signing, provenance, publishing, or evidence review.",
            future_validation_required="Execute the Phase 15 runbook externally, store evidence artifacts, reference this baseline ID in journal/evidence metadata, and complete Phase 12/13/14 governance before closing gaps.",
            future_environment_required="Codex/local/CI/human validation environment with approved repository checkout, runners, scanners, sandboxing, model-provider policies, private evidence storage, and release/AppSec review authority.",
        )
    )

    passed_count = sum(1 for check in checks if check.status == "pass")
    failed_count = sum(1 for check in checks if check.status == "fail")
    deferred_count = sum(1 for check in checks if check.status == "deferred")
    required_commit_failures = sum(
        1 for check in checks if check.status == "fail" and check.required_for_commit
    )
    required_codex_failures = sum(
        1 for check in checks if check.status == "fail" and check.required_for_codex
    )
    required_production_open_items = sum(
        1
        for check in checks
        if check.required_for_production and check.status in {"fail", "deferred"}
    )
    ready_for_commit = required_commit_failures == 0
    ready_for_codex = (
        ready_for_commit
        and required_codex_failures == 0
        and manifest.ready_for_external_validation_reference
    )
    return ValidationBaselineVerificationResult(
        repository_root=str(resolved_root),
        baseline_id=manifest.baseline_id,
        checks=checks,
        passed_count=passed_count,
        failed_count=failed_count,
        deferred_count=deferred_count,
        required_commit_failures=required_commit_failures,
        required_codex_failures=required_codex_failures,
        required_production_open_items=required_production_open_items,
        ready_for_commit=ready_for_commit,
        ready_for_codex=ready_for_codex,
        ready_for_external_validation_reference=manifest.ready_for_external_validation_reference,
        notes=[
            "Phase 16 verification is local-only and metadata-only.",
            "A passing baseline verifier means future validation evidence can reference a stable source snapshot.",
            "It does not mean external validation, evidence review, gap closure, or production readiness is complete.",
        ],
    )
