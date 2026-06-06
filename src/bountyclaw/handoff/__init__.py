"""Phase 11 external-validation handoff package."""

from .models import (
    CodexHandoffPlan,
    EvidenceArtifactTemplate,
    EvidenceTemplate,
    HandoffCheck,
    HandoffExportResult,
    HandoffTask,
    HandoffVerificationResult,
)
from .service import (
    build_codex_handoff_plan,
    build_evidence_template,
    export_handoff_package,
    verify_handoff_readiness,
)

__all__ = [
    "CodexHandoffPlan",
    "EvidenceArtifactTemplate",
    "EvidenceTemplate",
    "HandoffCheck",
    "HandoffExportResult",
    "HandoffTask",
    "HandoffVerificationResult",
    "build_codex_handoff_plan",
    "build_evidence_template",
    "export_handoff_package",
    "verify_handoff_readiness",
]
