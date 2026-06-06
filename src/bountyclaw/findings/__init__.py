"""Canonical findings, redaction, and evidence persistence."""

from .models import (
    CanonicalFinding,
    EvidenceRecord,
    FindingsCollectionResult,
    NormalizationResult,
    RedactionMatch,
    RedactionResult,
    StoredFindingBundle,
    StoredFindingSummary,
)
from .normalizer import normalize_scanner_run
from .redaction import redact_text
from .service import FindingsAuthorizationError, collect_authorized_findings
from .store import EvidenceStore, EvidenceStorePathError, ensure_store_path_outside_repository

__all__ = [
    "CanonicalFinding",
    "EvidenceRecord",
    "EvidenceStore",
    "EvidenceStorePathError",
    "FindingsAuthorizationError",
    "FindingsCollectionResult",
    "NormalizationResult",
    "RedactionMatch",
    "RedactionResult",
    "StoredFindingBundle",
    "StoredFindingSummary",
    "collect_authorized_findings",
    "ensure_store_path_outside_repository",
    "normalize_scanner_run",
    "redact_text",
]
