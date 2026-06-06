"""Local dependency-manifest risk scanner adapter.

This adapter runs entirely offline and deterministically analyzes repository
dependency declarations for known dependency-risk patterns. It intentionally does not
call advisory APIs or external vulnerability databases.
"""

from __future__ import annotations

import hashlib
import json
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from packaging.requirements import InvalidRequirement, Requirement
from packaging.version import parse as parse_version

from .models import PreliminaryFinding, ScannerContext, ScannerSpec

SCANNER_ID = "builtin.dependency.manifest"
SCANNER_VERSION = "0.1.0"


@dataclass(frozen=True)
class VulnerabilityRule:
    """Static dependency rule metadata."""

    rule_id: str
    package: str
    comparator: str
    version: str
    title: str
    description: str
    severity: str
    confidence: str
    cwe: str
    remediation_hint: str


RULES: dict[str, VulnerabilityRule] = {
    "dep.vuln-urllib3-old": VulnerabilityRule(
        rule_id="dep.vuln-urllib3-old",
        package="urllib3",
        comparator="<",
        version="1.26",
        title="Potentially vulnerable urllib3 version",
        description=(
            "urllib3 versions prior to 1.26 may include historical security issues in TLS/"
            "connection handling."
        ),
        severity="high",
        confidence="medium",
        cwe="CWE-327",
        remediation_hint="Upgrade urllib3 to a maintained branch (at least 1.26+) and pin dependencies through lockfiles.",
    ),
    "dep.vuln-requests-old": VulnerabilityRule(
        rule_id="dep.vuln-requests-old",
        package="requests",
        comparator="<",
        version="2.31",
        title="Potentially vulnerable requests version",
        description="Requests versions prior to 2.31 should be reviewed for known HTTP-related fixes.",
        severity="medium",
        confidence="medium",
        cwe="CWE-327",
        remediation_hint="Upgrade requests to a maintained release and rerun dependency risk checks.",
    ),
    "dep.vuln-jinja2-old": VulnerabilityRule(
        rule_id="dep.vuln-jinja2-old",
        package="jinja2",
        comparator="<",
        version="3.1",
        title="Potentially vulnerable Jinja2 version",
        description="Jinja2 versions prior to 3.1 have known sandbox/template escape risk classes.",
        severity="medium",
        confidence="medium",
        cwe="CWE-74",
        remediation_hint="Upgrade Jinja2 to a maintained branch and verify template rendering isolation.",
    ),
}

RULES_BY_PACKAGE: dict[str, list[VulnerabilityRule]] = {}
for _rule in RULES.values():
    RULES_BY_PACKAGE.setdefault(_rule.package, []).append(_rule)


class DependencyManifestAdapter:
    """Dependency-manifest scanner for Python and lockfile inputs."""

    @property
    def spec(self) -> ScannerSpec:
        return ScannerSpec(
            scanner_id=SCANNER_ID,
            name="Built-in dependency manifest risk scanner",
            version=SCANNER_VERSION,
            adapter_family="builtin.static.dependency",
            execution_mode="local_builtin",
        )

    def supports(self, context: ScannerContext) -> bool:
        return bool(_find_dependency_files(context.repository_root))

    def scan(self, context: ScannerContext) -> list[PreliminaryFinding]:
        findings: list[PreliminaryFinding] = []
        for manifest_path in _find_dependency_files(context.repository_root):
            if manifest_path.stat().st_size > context.max_file_bytes:
                continue
            findings.extend(_scan_manifest(context, manifest_path))
        findings = _dedupe_findings(findings)
        findings.sort(key=lambda item: (item.file_path, item.line_number or 0, item.rule_id))
        return findings


def _dedupe_findings(findings: list[PreliminaryFinding]) -> list[PreliminaryFinding]:
    seen: set[tuple[str, str, str, int | None, str]] = set()
    deduped: list[PreliminaryFinding] = []
    for finding in findings:
        key = (
            finding.scanner_id,
            finding.file_path,
            finding.rule_id,
            finding.line_number,
            finding.evidence_summary,
        )
        if key in seen:
            continue
        seen.add(key)
        deduped.append(finding)
    return deduped


def _scan_manifest(
    context: ScannerContext,
    manifest_path: Path,
) -> list[PreliminaryFinding]:
    if manifest_path.name == "requirements.txt" or manifest_path.name == "requirements-dev.txt":
        return _scan_requirements_txt(context, manifest_path)
    if manifest_path.name == "pyproject.toml":
        return _scan_pyproject(context, manifest_path)
    if manifest_path.name == "Pipfile.lock":
        return _scan_pipfile_lock(context, manifest_path)
    return []


def _find_dependency_files(root: Path) -> list[Path]:
    candidates = [
        "requirements.txt",
        "requirements-dev.txt",
        "pyproject.toml",
        "Pipfile.lock",
    ]
    return [root / name for name in candidates if (root / name).exists()]


def _scan_requirements_txt(
    context: ScannerContext,
    path: Path,
) -> list[PreliminaryFinding]:
    relative_path = path.relative_to(context.repository_root).as_posix()
    findings: list[PreliminaryFinding] = []
    for index, raw_line in enumerate(
        path.read_text(encoding="utf-8", errors="replace").splitlines(),
        start=1,
    ):
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("-r") or line.startswith("--"):
            continue
        parsed = _parse_requirement_text(line)
        if parsed is None:
            continue
        package, specifiers = parsed
        for rule, requested_version in _matching_rules(package, specifiers):
            findings.append(
                _finding_for_rule(
                    rule=rule,
                    context=context,
                    relative_path=relative_path,
                    line_number=index,
                    version_request=requested_version,
                )
            )
    return findings


def _scan_pyproject(context: ScannerContext, path: Path) -> list[PreliminaryFinding]:
    relative_path = path.relative_to(context.repository_root).as_posix()
    try:
        payload = tomllib.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, tomllib.TOMLDecodeError):
        return []

    findings: list[PreliminaryFinding] = []
    findings.extend(_scan_python_project_table(context, relative_path, payload.get("project", {})))
    findings.extend(
        _scan_poetry_dependencies(
            context,
            relative_path,
            payload.get("tool", {}).get("poetry", {}).get("dependencies", {}),
        )
    )
    return findings


def _scan_python_project_table(
    context: ScannerContext,
    relative_path: str,
    project: dict[str, Any],
) -> list[PreliminaryFinding]:
    requirements: list[str] = []
    deps = project.get("dependencies", [])
    if isinstance(deps, list):
        requirements.extend(item for item in deps if isinstance(item, str))

    optional = project.get("optional-dependencies", {})
    if isinstance(optional, dict):
        for _group, values in optional.items():
            if isinstance(values, list):
                requirements.extend(item for item in values if isinstance(item, str))

    findings: list[PreliminaryFinding] = []
    for requirement_text in requirements:
        parsed = _parse_requirement_text(requirement_text)
        if parsed is None:
            continue
        package, specifiers = parsed
        for rule, requested_version in _matching_rules(package, specifiers):
            findings.append(
                _finding_for_rule(
                    rule=rule,
                    context=context,
                    relative_path=relative_path,
                    line_number=None,
                    version_request=requested_version,
                )
            )
    return findings


def _scan_poetry_dependencies(
    context: ScannerContext,
    relative_path: str,
    dependencies: dict[str, Any],
) -> list[PreliminaryFinding]:
    if not isinstance(dependencies, dict):
        return []
    findings: list[PreliminaryFinding] = []
    for package_name, spec in dependencies.items():
        if package_name.lower() == "python":
            continue
        if isinstance(spec, str):
            parsed = _parse_requirement_text(f"{package_name}{spec}")
        elif isinstance(spec, dict):
            marker = spec.get("version")
            if not isinstance(marker, str):
                continue
            parsed = _parse_requirement_text(f"{package_name}{marker}")
        else:
            continue
        if parsed is None:
            continue
        package, specifiers = parsed
        for rule, requested_version in _matching_rules(package, specifiers):
            findings.append(
                _finding_for_rule(
                    rule=rule,
                    context=context,
                    relative_path=relative_path,
                    line_number=None,
                    version_request=requested_version,
                )
            )
    return findings


def _scan_pipfile_lock(context: ScannerContext, path: Path) -> list[PreliminaryFinding]:
    relative_path = path.relative_to(context.repository_root).as_posix()
    try:
        lock_payload = json.loads(path.read_text(encoding="utf-8", errors="replace"))
    except (OSError, json.JSONDecodeError):
        return []

    findings: list[PreliminaryFinding] = []
    for section_name in ("default", "develop"):
        section = lock_payload.get(section_name)
        if not isinstance(section, dict):
            continue
        for name, spec in section.items():
            if not isinstance(spec, dict):
                continue
            version_text = spec.get("version")
            if not isinstance(version_text, str):
                continue
            cleaned = version_text.lstrip("=vV")
            parsed = _parse_requirement_text(f"{name}=={cleaned}")
            if parsed is None:
                continue
            package, specifiers = parsed
            for rule, requested_version in _matching_rules(package, specifiers):
                findings.append(
                    _finding_for_rule(
                        rule=rule,
                        context=context,
                        relative_path=relative_path,
                        line_number=None,
                        version_request=requested_version,
                    )
                )
    return findings


def _matching_rules(
    package: str,
    specifiers: list[str],
) -> list[tuple[VulnerabilityRule, str]]:
    matches: list[tuple[VulnerabilityRule, str]] = []
    for rule in RULES_BY_PACKAGE.get(package, []):
        for specifier in specifiers:
            if _specifier_matches(rule, specifier):
                matches.append((rule, specifier))
                break
    return matches


def _specifier_matches(rule: VulnerabilityRule, specifier: str) -> bool:
    try:
        operator, version = _split_specifier(specifier)
        if operator is None or version is None:
            return False
        request_version = parse_version(version)
        rule_version = parse_version(rule.version)
        if operator == "==":
            if rule.comparator == "<":
                return request_version < rule_version
            if rule.comparator == "<=":
                return request_version <= rule_version
            return False
        if operator in {"<", "<="}:
            if rule.comparator == "<":
                return True
            return bool(rule.comparator == "<=" and operator == "<=")
        return False
    except (TypeError, ValueError):
        return False


def _split_specifier(specifier: str) -> tuple[str | None, str | None]:
    match = re.match(r"^(<=|>=|==|!=|<|>|~=)\s*([^\s,]+)$", specifier.strip())
    if not match:
        return None, None
    operator = match.group(1)
    version_text = match.group(2).lstrip("vV")
    return operator, version_text


def _parse_requirement_text(requirement_text: str) -> tuple[str, list[str]] | None:
    try:
        cleaned = _strip_inline_comment(requirement_text)
        req = Requirement(cleaned)
    except InvalidRequirement:
        return None

    specifiers = [str(spec) for spec in req.specifier]
    if not specifiers:
        return None
    package = req.name.lower()
    if not package:
        return None
    return package, specifiers


def _strip_inline_comment(line: str) -> str:
    if "#" not in line:
        return line
    return line.split("#", 1)[0].strip()


def _finding_for_rule(
    rule: VulnerabilityRule,
    context: ScannerContext,
    relative_path: str,
    line_number: int | None,
    version_request: str,
) -> PreliminaryFinding:
    stable_source = "|".join(
        [
            context.repository_fingerprint_id,
            SCANNER_ID,
            rule.rule_id,
            relative_path,
            str(line_number or 0),
            version_request,
        ]
    )
    digest = hashlib.sha256(stable_source.encode("utf-8")).hexdigest()[:16]
    return PreliminaryFinding(
        finding_id=f"finding-{digest}",
        scanner_id=SCANNER_ID,
        scanner_version=SCANNER_VERSION,
        rule_id=rule.rule_id,
        title=rule.title,
        description=rule.description,
        severity=rule.severity,  # type: ignore[arg-type]
        confidence=rule.confidence,  # type: ignore[arg-type]
        target=str(context.repository_root),
        file_path=relative_path,
        line_number=line_number,
        evidence_summary=(
            f"Dependency risk rule {rule.rule_id} matched in {relative_path}"
            + (f":{line_number}" if line_number else "")
            + f" with requested spec {version_request}."
        ),
        cwe=rule.cwe,
        remediation_hint=rule.remediation_hint,
        metadata={
            "phase": "3",
            "source_excerpt_policy": "omitted_until_redaction_layer_exists",
            "dependency_rule": rule.rule_id,
        },
    )
