"""Scanner adapter registry."""

from __future__ import annotations

from .builtin_python import BuiltInPythonStaticAdapter
from .models import ScannerAdapter

DEFAULT_SCANNER_ID = "builtin.python.static"


class ScannerRegistry:
    """Deterministic scanner adapter registry."""

    def __init__(self, adapters: list[ScannerAdapter] | None = None) -> None:
        self._adapters: dict[str, ScannerAdapter] = {}
        for adapter in adapters or []:
            self.register(adapter)

    def register(self, adapter: ScannerAdapter) -> None:
        scanner_id = adapter.spec.scanner_id
        if scanner_id in self._adapters:
            raise ValueError(f"duplicate scanner adapter registered: {scanner_id}")
        self._adapters[scanner_id] = adapter

    def get(self, scanner_id: str) -> ScannerAdapter:
        try:
            return self._adapters[scanner_id]
        except KeyError as exc:
            raise KeyError(
                f"scanner adapter is not registered or allowlisted: {scanner_id}"
            ) from exc

    def list_ids(self) -> list[str]:
        return sorted(self._adapters)


def default_registry() -> ScannerRegistry:
    """Return the Phase 3 allowlisted scanner registry."""

    return ScannerRegistry([BuiltInPythonStaticAdapter()])
