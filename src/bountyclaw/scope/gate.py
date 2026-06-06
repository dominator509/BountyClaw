"""Deny-by-default scope and policy gate."""

from __future__ import annotations

from pathlib import Path

from .loader import LoadedScopeManifest
from .models import PROHIBITED_ACTIONS, Action, ScopeDecision, Target, TargetKind


class ScopeGate:
    """Evaluate whether a requested action is inside the active scope manifest."""

    def __init__(self, loaded_scope: LoadedScopeManifest) -> None:
        self.loaded_scope = loaded_scope

    def evaluate(self, action: str, target: Target | None = None) -> ScopeDecision:
        """Return an allow/deny decision for the requested action.

        This method intentionally fails closed for anything ambiguous. It never
        initiates scans, network calls, browser actions, LLM calls, or MCP tools.
        """

        reasons: list[str] = []
        normalized_action = action.strip()

        if not normalized_action:
            return self._deny(normalized_action, target, "missing action")

        configured_prohibited = self.loaded_scope.manifest.controls.prohibited_actions
        if normalized_action in PROHIBITED_ACTIONS or normalized_action in configured_prohibited:
            return self._deny(
                normalized_action,
                target,
                f"action is prohibited by policy: {normalized_action}",
            )

        if normalized_action not in {item.value for item in Action}:
            return self._deny(
                normalized_action,
                target,
                f"unknown action is denied by default: {normalized_action}",
            )

        if normalized_action == Action.SCOPE_VALIDATE.value:
            return ScopeDecision(
                action=normalized_action,
                target_kind=target.kind if target else None,
                target=target.value if target else None,
                decision="allow",
                reasons=["scope manifest is syntactically valid"],
            )

        if target is None:
            return self._deny(normalized_action, None, "missing target")

        if target.kind in {TargetKind.DOMAIN, TargetKind.URL}:
            return self._deny(
                normalized_action,
                target,
                "network/domain targets are disabled in Phase 19",
            )

        if target.kind != TargetKind.LOCAL_REPO:
            return self._deny(
                normalized_action,
                target,
                f"unsupported target kind: {target.kind}",
            )

        target_path = self._resolve_user_path(target.value)
        if not target_path.exists():
            reasons.append(f"target path does not exist: {target_path}")
        elif not target_path.is_dir():
            reasons.append(f"target path is not a directory: {target_path}")

        if self._is_out_of_scope(target_path):
            reasons.append(f"target is explicitly out of scope: {target_path}")

        matched_authorized_repo = False
        matched_repo_action_allowed = False
        for repository in self.loaded_scope.manifest.assets.repositories:
            allowed_repo_path = self._resolve_manifest_path(repository.path)
            if not self._path_is_relative_to(target_path, allowed_repo_path):
                continue
            matched_authorized_repo = True
            if normalized_action in {item.value for item in repository.allowed_actions}:
                matched_repo_action_allowed = True
                break
            reasons.append(
                f"action {normalized_action} is not allowlisted for repository {repository.path}"
            )

        if not matched_authorized_repo:
            reasons.append("target repository is not allowlisted in scope manifest")

        if reasons:
            return self._deny(normalized_action, target, *reasons)

        if matched_repo_action_allowed:
            return ScopeDecision(
                action=normalized_action,
                target_kind=target.kind,
                target=target.value,
                decision="allow",
                reasons=["target and action are explicitly allowlisted"],
            )

        return self._deny(
            normalized_action,
            target,
            "action is denied by default because no allowlist rule matched",
        )

    def _resolve_user_path(self, value: str) -> Path:
        return Path(value).expanduser().resolve(strict=False)

    def _resolve_manifest_path(self, value: str) -> Path:
        candidate = Path(value).expanduser()
        if not candidate.is_absolute():
            candidate = self.loaded_scope.base_dir / candidate
        return candidate.resolve(strict=False)

    def _is_out_of_scope(self, target_path: Path) -> bool:
        for entry in self.loaded_scope.manifest.assets.out_of_scope:
            out_path = self._resolve_manifest_path(entry)
            if self._path_is_relative_to(target_path, out_path):
                return True
        return False

    @staticmethod
    def _path_is_relative_to(path: Path, expected_parent: Path) -> bool:
        try:
            path.relative_to(expected_parent)
            return True
        except ValueError:
            return False

    @staticmethod
    def _deny(action: str, target: Target | None, *reasons: str) -> ScopeDecision:
        return ScopeDecision(
            action=action,
            target_kind=target.kind if target else None,
            target=target.value if target else None,
            decision="deny",
            reasons=list(reasons) or ["denied by default"],
        )
