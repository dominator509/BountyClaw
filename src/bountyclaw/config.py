"""Configuration loading for BountyClaw.

Phase 19 configuration is intentionally small and local-first. Potentially risky
capabilities remain disabled until later governed phases explicitly implement
and validate them. Fixture MCP/browser, memory/skill workflows, and release verification are enabled only by per-command flags or local-only commands.
"""

from __future__ import annotations

import json
import os
import tomllib
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError, model_validator


class BountyClawConfig(BaseModel):
    """Local configuration with safe defaults.

    The feature flags are deliberately hard-failed if enabled during Phase 19.
    Mock model routing remains available through explicit CLI flags, but live provider calls remain disabled. Fixture MCP/browser commands also require explicit CLI flags.
    """

    scope_manifest: Path | None = None
    audit_log: Path = Field(default=Path(".bountyclaw/audit.jsonl"))
    network_enabled: bool = False
    llm_enabled: bool = False
    mcp_enabled: bool = False
    browser_enabled: bool = False

    @model_validator(mode="after")
    def enforce_phase_eighteen_safety_defaults(self) -> BountyClawConfig:
        enabled = [
            name
            for name, enabled_flag in (
                ("network_enabled", self.network_enabled),
                ("llm_enabled", self.llm_enabled),
                ("mcp_enabled", self.mcp_enabled),
                ("browser_enabled", self.browser_enabled),
            )
            if enabled_flag
        ]
        if enabled:
            joined = ", ".join(enabled)
            raise ValueError(
                f"Phase 19 requires live/external risky capabilities to remain disabled: {joined}"
            )
        return self


def _read_structured_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    elif suffix == ".json":
        loaded = json.loads(path.read_text(encoding="utf-8"))
    elif suffix == ".toml":
        loaded = tomllib.loads(path.read_text(encoding="utf-8"))
    else:
        raise ValueError("Config file must be YAML, JSON, or TOML")

    if not isinstance(loaded, dict):
        raise ValueError("Config file must contain a mapping/object at the top level")
    return loaded


def load_config(path: Path | None = None) -> BountyClawConfig:
    """Load configuration from an explicit path or environment variable.

    With no file configured, return safe defaults.
    """

    env_path = os.environ.get("BOUNTYCLAW_CONFIG")
    resolved_path = path or (Path(env_path) if env_path else None)
    if resolved_path is None:
        return BountyClawConfig()

    data = _read_structured_file(resolved_path)
    try:
        return BountyClawConfig.model_validate(data)
    except ValidationError as exc:
        raise ValueError(f"Invalid BountyClaw config: {exc}") from exc
