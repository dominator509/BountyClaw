"""Read-only local repository intake.

This module deliberately reads repository metadata only. It does not open source
files for content analysis, execute scanners, create output files inside the
repository, call network services, or persist evidence.
"""

from __future__ import annotations

import hashlib
from collections import defaultdict
from collections.abc import Iterator
from pathlib import Path

from .models import LanguageSummary, PackageManifest, RepositoryFingerprint

IGNORED_DIRECTORIES: tuple[str, ...] = (
    ".bountyclaw",
    ".git",
    ".hg",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".svn",
    ".tox",
    ".venv",
    "__pycache__",
    "build",
    "coverage",
    "dist",
    "node_modules",
    "target",
    "venv",
)

EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".c": "C",
    ".cc": "C++",
    ".cpp": "C++",
    ".cs": "C#",
    ".css": "CSS",
    ".go": "Go",
    ".h": "C/C++ Header",
    ".hpp": "C++ Header",
    ".html": "HTML",
    ".java": "Java",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".kt": "Kotlin",
    ".php": "PHP",
    ".py": "Python",
    ".rb": "Ruby",
    ".rs": "Rust",
    ".scala": "Scala",
    ".sh": "Shell",
    ".swift": "Swift",
    ".tf": "Terraform",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".vue": "Vue",
    ".yaml": "YAML",
    ".yml": "YAML",
}

MANIFEST_NAME_MAP: dict[str, tuple[str, str]] = {
    "Pipfile": ("python", "dependency_manifest"),
    "poetry.lock": ("python", "lockfile"),
    "pyproject.toml": ("python", "dependency_manifest"),
    "requirements.txt": ("python", "dependency_manifest"),
    "setup.cfg": ("python", "build_config"),
    "setup.py": ("python", "build_script"),
    "uv.lock": ("python", "lockfile"),
    "package.json": ("javascript", "dependency_manifest"),
    "package-lock.json": ("javascript", "lockfile"),
    "pnpm-lock.yaml": ("javascript", "lockfile"),
    "yarn.lock": ("javascript", "lockfile"),
    "go.mod": ("go", "dependency_manifest"),
    "go.sum": ("go", "lockfile"),
    "Cargo.toml": ("rust", "dependency_manifest"),
    "Cargo.lock": ("rust", "lockfile"),
    "pom.xml": ("java", "dependency_manifest"),
    "build.gradle": ("java", "build_config"),
    "build.gradle.kts": ("kotlin", "build_config"),
    "composer.json": ("php", "dependency_manifest"),
    "composer.lock": ("php", "lockfile"),
    "Gemfile": ("ruby", "dependency_manifest"),
    "Gemfile.lock": ("ruby", "lockfile"),
    "Dockerfile": ("container", "container_config"),
    "docker-compose.yml": ("container", "container_config"),
    "docker-compose.yaml": ("container", "container_config"),
    "terraform.tf": ("terraform", "iac_config"),
}


def inspect_repository(root: Path) -> RepositoryFingerprint:
    """Return a deterministic metadata-only fingerprint for a local repository."""

    resolved_root = root.expanduser().resolve(strict=False)
    if not resolved_root.exists():
        raise FileNotFoundError(f"Repository path does not exist: {resolved_root}")
    if not resolved_root.is_dir():
        raise NotADirectoryError(f"Repository path is not a directory: {resolved_root}")

    language_counts: dict[str, int] = defaultdict(int)
    language_bytes: dict[str, int] = defaultdict(int)
    package_manifests: list[PackageManifest] = []
    file_count = 0
    total_bytes = 0
    fingerprint_parts: list[str] = []

    for path in _iter_repository_files(resolved_root):
        relative_path = path.relative_to(resolved_root).as_posix()
        stat = path.stat()
        size = stat.st_size
        file_count += 1
        total_bytes += size
        fingerprint_parts.append(f"{relative_path}\0{size}")

        language = _detect_language(path)
        if language is not None:
            language_counts[language] += 1
            language_bytes[language] += size

        manifest = _detect_manifest(relative_path, path.name)
        if manifest is not None:
            package_manifests.append(manifest)

    language_summaries = [
        LanguageSummary(
            language=language,
            file_count=language_counts[language],
            total_bytes=language_bytes[language],
        )
        for language in sorted(language_counts)
    ]
    package_manifests.sort(key=lambda item: (item.ecosystem, item.kind, item.path))

    fingerprint_id = _compute_fingerprint_id(fingerprint_parts)
    return RepositoryFingerprint(
        fingerprint_id=fingerprint_id,
        root=str(resolved_root),
        root_name=resolved_root.name,
        file_count=file_count,
        total_bytes=total_bytes,
        language_summaries=language_summaries,
        package_manifests=package_manifests,
        ignored_directories=sorted(IGNORED_DIRECTORIES),
    )


def _iter_repository_files(root: Path) -> Iterator[Path]:
    """Yield repository files in deterministic order while skipping ignored dirs."""

    stack = [root]
    while stack:
        directory = stack.pop()
        entries = sorted(directory.iterdir(), key=lambda item: item.name.lower())
        child_dirs: list[Path] = []
        for entry in entries:
            if entry.is_symlink():
                continue
            if entry.is_dir():
                if entry.name in IGNORED_DIRECTORIES:
                    continue
                child_dirs.append(entry)
            elif entry.is_file():
                yield entry
        stack.extend(reversed(child_dirs))


def _detect_language(path: Path) -> str | None:
    if path.name == "Dockerfile":
        return "Dockerfile"
    return EXTENSION_LANGUAGE_MAP.get(path.suffix.lower())


def _detect_manifest(relative_path: str, name: str) -> PackageManifest | None:
    if name in MANIFEST_NAME_MAP:
        ecosystem, kind = MANIFEST_NAME_MAP[name]
        return PackageManifest(path=relative_path, ecosystem=ecosystem, kind=kind)
    if name.endswith(".tf"):
        return PackageManifest(path=relative_path, ecosystem="terraform", kind="iac_config")
    return None


def _compute_fingerprint_id(parts: list[str]) -> str:
    digest = hashlib.sha256()
    for part in sorted(parts):
        digest.update(part.encode("utf-8", errors="surrogateescape"))
        digest.update(b"\n")
    return f"repo-sha256:{digest.hexdigest()}"
