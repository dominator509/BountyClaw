"""Scope manifest loading."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .models import ScopeManifest


@dataclass(frozen=True)
class LoadedScopeManifest:
    """Scope manifest plus source path for relative asset resolution."""

    manifest: ScopeManifest
    source_path: Path

    @property
    def base_dir(self) -> Path:
        return self.source_path.parent


def _read_manifest_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Scope manifest not found: {path}")

    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    elif suffix == ".json":
        loaded = json.loads(path.read_text(encoding="utf-8"))
    else:
        raise ValueError("Scope manifest must be YAML or JSON")

    if not isinstance(loaded, dict):
        raise ValueError("Scope manifest must contain a mapping/object at the top level")
    return loaded


def load_scope_manifest(path: Path) -> LoadedScopeManifest:
    """Load and validate a scope manifest from disk."""

    resolved_path = path.expanduser().resolve(strict=False)
    data = _read_manifest_file(resolved_path)
    try:
        manifest = ScopeManifest.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"Invalid scope manifest: {exc}") from exc
    return LoadedScopeManifest(manifest=manifest, source_path=resolved_path)
