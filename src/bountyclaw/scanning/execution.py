"""Controlled subprocess execution utilities for future external scanners.

The Phase 3 CLI uses the built-in local scanner by default. This wrapper exists
so future external scanner adapters have a constrained execution path instead of
shelling out directly. It cannot provide OS-level sandboxing in ChatGPT Project
Mode; that remains tracked in the production gap ledger.
"""

from __future__ import annotations

import os
import shutil
import subprocess  # nosec B404
from dataclasses import dataclass, field
from pathlib import Path


class CommandPolicyError(RuntimeError):
    """Raised when a scanner command violates the execution policy."""


@dataclass(frozen=True)
class ControlledCommandPolicy:
    """Allowlist and safety constraints for scanner subprocesses."""

    allowed_executables: frozenset[str]
    allowed_cwd_parent: Path
    max_timeout_seconds: int = 30
    environment_allowlist: frozenset[str] = field(
        default_factory=lambda: frozenset({"LANG", "LC_ALL", "PATH"})
    )
    shell_allowed: bool = False
    network_arguments_denied: bool = True


@dataclass(frozen=True)
class ControlledCommandResult:
    """Captured subprocess output."""

    command: tuple[str, ...]
    cwd: str
    return_code: int
    stdout: str
    stderr: str
    timeout_seconds: int


class ControlledSubprocessRunner:
    """Validate and execute scanner commands without using a shell."""

    def __init__(self, policy: ControlledCommandPolicy) -> None:
        self.policy = policy

    def run(
        self, command: list[str], *, cwd: Path, timeout_seconds: int | None = None
    ) -> ControlledCommandResult:
        resolved_cwd = cwd.expanduser().resolve(strict=False)
        timeout = timeout_seconds or self.policy.max_timeout_seconds
        self._validate(command, resolved_cwd, timeout)
        completed = subprocess.run(  # nosec B603
            command,
            cwd=resolved_cwd,
            env=self._safe_environment(),
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
        return ControlledCommandResult(
            command=tuple(command),
            cwd=str(resolved_cwd),
            return_code=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
            timeout_seconds=timeout,
        )

    def _validate(self, command: list[str], cwd: Path, timeout_seconds: int) -> None:
        if not command:
            raise CommandPolicyError("scanner command is empty")
        if timeout_seconds < 1 or timeout_seconds > self.policy.max_timeout_seconds:
            raise CommandPolicyError("scanner command timeout exceeds policy")
        if self.policy.shell_allowed:
            raise CommandPolicyError("scanner subprocess policy must keep shell execution disabled")
        if not _path_is_relative_to(
            cwd, self.policy.allowed_cwd_parent.expanduser().resolve(strict=False)
        ):
            raise CommandPolicyError("scanner cwd is outside the allowed repository boundary")

        executable = Path(command[0]).name
        resolved = shutil.which(command[0]) if os.sep not in command[0] else command[0]
        resolved_name = Path(resolved).name if resolved else executable
        if (
            executable not in self.policy.allowed_executables
            and resolved_name not in self.policy.allowed_executables
        ):
            raise CommandPolicyError(f"scanner executable is not allowlisted: {executable}")

        if self.policy.network_arguments_denied:
            for argument in command[1:]:
                lowered = argument.lower()
                if "://" in lowered or lowered.startswith(("--proxy", "--url", "--host")):
                    raise CommandPolicyError("scanner command contains network-oriented argument")

    def _safe_environment(self) -> dict[str, str]:
        return {
            key: os.environ[key]
            for key in sorted(self.policy.environment_allowlist)
            if key in os.environ
        }


def _path_is_relative_to(path: Path, expected_parent: Path) -> bool:
    try:
        path.relative_to(expected_parent)
        return True
    except ValueError:
        return False
