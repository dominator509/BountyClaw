"""Scope-gated local static scanning."""

from .execution import (
    CommandPolicyError,
    ControlledCommandPolicy,
    ControlledCommandResult,
    ControlledSubprocessRunner,
)
from .models import PreliminaryFinding, ScannerContext, ScannerRunResult, ScannerSpec
from .registry import DEFAULT_SCANNER_ID, ScannerRegistry, default_registry
from .service import (
    ScannerAuthorizationError,
    ScannerFeatureGateError,
    ScannerSelectionError,
    scan_authorized_repository,
)

__all__ = [
    "CommandPolicyError",
    "ControlledCommandPolicy",
    "ControlledCommandResult",
    "ControlledSubprocessRunner",
    "DEFAULT_SCANNER_ID",
    "PreliminaryFinding",
    "ScannerAuthorizationError",
    "ScannerContext",
    "ScannerFeatureGateError",
    "ScannerRegistry",
    "ScannerRunResult",
    "ScannerSelectionError",
    "ScannerSpec",
    "default_registry",
    "scan_authorized_repository",
]
