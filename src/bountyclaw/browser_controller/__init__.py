"""Policy-bound headless browser controller foundation."""

from .models import BrowserPolicyIngestionResult, BrowserWorkflowPlan
from .service import (
    BrowserAuthorizationError,
    BrowserControllerError,
    BrowserFeatureGateError,
    build_policy_ingestion_plan,
    ingest_authorized_policy,
)

__all__ = [
    "BrowserAuthorizationError",
    "BrowserControllerError",
    "BrowserFeatureGateError",
    "BrowserPolicyIngestionResult",
    "BrowserWorkflowPlan",
    "build_policy_ingestion_plan",
    "ingest_authorized_policy",
]
