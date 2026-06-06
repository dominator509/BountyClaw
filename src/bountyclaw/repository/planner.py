"""Deterministic scan-plan generation.

Phase 2 emits recommendations only. It never executes scanners or shells out.
"""

from __future__ import annotations

import hashlib

from .models import RepositoryFingerprint, ScanPlan, ScanPlanStep

LANGUAGE_ADAPTERS: dict[str, tuple[str, str]] = {
    "C": ("future.static.c", "C source files detected"),
    "C#": ("future.static.dotnet", "C# source files detected"),
    "C++": ("future.static.cpp", "C++ source files detected"),
    "Go": ("future.static.go", "Go source files detected"),
    "Java": ("future.static.jvm", "Java source files detected"),
    "JavaScript": ("future.static.javascript", "JavaScript source files detected"),
    "Kotlin": ("future.static.jvm", "Kotlin source files detected"),
    "PHP": ("future.static.php", "PHP source files detected"),
    "Python": ("future.static.python", "Python source files detected"),
    "Ruby": ("future.static.ruby", "Ruby source files detected"),
    "Rust": ("future.static.rust", "Rust source files detected"),
    "Shell": ("future.static.shell", "Shell scripts detected"),
    "Terraform": ("future.iac.terraform", "Terraform configuration detected"),
    "TypeScript": ("future.static.typescript", "TypeScript source files detected"),
}

CONFIG_ECOSYSTEMS: frozenset[str] = frozenset({"container", "terraform"})
DEPENDENCY_KINDS: frozenset[str] = frozenset(
    {"dependency_manifest", "lockfile", "build_config", "build_script"}
)


def build_scan_plan(fingerprint: RepositoryFingerprint) -> ScanPlan:
    """Build a deterministic, non-executing scan plan from repository metadata."""

    steps: list[ScanPlanStep] = []

    for language_summary in fingerprint.language_summaries:
        adapter = LANGUAGE_ADAPTERS.get(language_summary.language)
        if adapter is None:
            continue
        adapter_family, reason = adapter
        steps.append(
            _step(
                name=f"Static review planning for {language_summary.language}",
                action="scan.local_static",
                adapter_family=adapter_family,
                reason=f"{reason}; {language_summary.file_count} file(s) observed.",
                requires_scope_action="scan.local_static",
            )
        )

    dependency_ecosystems = sorted(
        {
            manifest.ecosystem
            for manifest in fingerprint.package_manifests
            if manifest.kind in DEPENDENCY_KINDS and manifest.ecosystem not in CONFIG_ECOSYSTEMS
        }
    )
    for ecosystem in dependency_ecosystems:
        count = sum(
            1 for manifest in fingerprint.package_manifests if manifest.ecosystem == ecosystem
        )
        steps.append(
            _step(
                name=f"Dependency manifest review planning for {ecosystem}",
                action="scan.local_static",
                adapter_family=f"future.dependency.{ecosystem}",
                reason=f"{count} package/build manifest(s) detected for {ecosystem}.",
                requires_scope_action="scan.local_static",
            )
        )

    if any(manifest.ecosystem == "container" for manifest in fingerprint.package_manifests):
        steps.append(
            _step(
                name="Container configuration review planning",
                action="scan.local_static",
                adapter_family="future.config.container",
                reason="Container manifest(s) detected; plan configuration review without executing containers.",
                requires_scope_action="scan.local_static",
            )
        )

    if any(manifest.ecosystem == "terraform" for manifest in fingerprint.package_manifests):
        steps.append(
            _step(
                name="Infrastructure-as-code review planning",
                action="scan.local_static",
                adapter_family="future.iac.terraform",
                reason="Terraform manifest(s) detected; plan IaC review without cloud access.",
                requires_scope_action="scan.local_static",
            )
        )

    if fingerprint.file_count > 0:
        steps.append(
            _step(
                name="Secret-pattern review planning",
                action="scan.local_static",
                adapter_family="future.secret_detection.redacted",
                reason="Repository contains files; future secret detection must redact raw values before persistence.",
                requires_scope_action="scan.local_static",
            )
        )

    steps.sort(key=lambda item: (item.adapter_family, item.name, item.reason))

    notes = [
        "Phase 2 scan plans are recommendations only; no scanner commands are executed.",
        "No source contents are persisted by repository intake.",
        "Future scanner execution must remain scope-gated and use controlled adapters.",
    ]
    return ScanPlan(
        repository=fingerprint.root,
        repository_fingerprint_id=fingerprint.fingerprint_id,
        steps=steps,
        notes=notes,
    )


def _step(
    *,
    name: str,
    action: str,
    adapter_family: str,
    reason: str,
    requires_scope_action: str,
) -> ScanPlanStep:
    stable_source = "|".join([name, action, adapter_family, reason, requires_scope_action])
    digest = hashlib.sha256(stable_source.encode("utf-8")).hexdigest()[:12]
    return ScanPlanStep(
        step_id=f"plan-step-{digest}",
        name=name,
        action=action,
        adapter_family=adapter_family,
        reason=reason,
        requires_scope_action=requires_scope_action,
    )
