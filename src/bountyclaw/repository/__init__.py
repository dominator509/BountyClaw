"""Read-only local repository intake and scan planning."""

from .intake import inspect_repository
from .models import LanguageSummary, PackageManifest, RepositoryFingerprint, ScanPlan, ScanPlanStep
from .planner import build_scan_plan
from .service import (
    RepositoryAuthorizationError,
    inspect_authorized_repository,
    plan_authorized_repository_scan,
)

__all__ = [
    "LanguageSummary",
    "PackageManifest",
    "RepositoryAuthorizationError",
    "RepositoryFingerprint",
    "ScanPlan",
    "ScanPlanStep",
    "build_scan_plan",
    "inspect_authorized_repository",
    "inspect_repository",
    "plan_authorized_repository_scan",
]
