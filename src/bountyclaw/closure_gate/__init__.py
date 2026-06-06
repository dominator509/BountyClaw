"""Phase 17 closure-gate and readiness-attestation subsystem."""

from .models import (
    ClosureGateAttestationStatus,
    ClosureGateCheck,
    ClosureGateExportResult,
    ClosureGateStatusResult,
    ClosureGateVerificationResult,
    ReadinessAttestationFile,
    ReadinessAttestationRecord,
    ReadinessAttestationTemplateResult,
)
from .service import (
    assess_closure_gate_status,
    build_readiness_attestation_template,
    export_closure_gate_package,
    verify_closure_gate_readiness,
)

__all__ = [
    "ClosureGateAttestationStatus",
    "ClosureGateCheck",
    "ClosureGateExportResult",
    "ClosureGateStatusResult",
    "ClosureGateVerificationResult",
    "ReadinessAttestationFile",
    "ReadinessAttestationRecord",
    "ReadinessAttestationTemplateResult",
    "assess_closure_gate_status",
    "build_readiness_attestation_template",
    "export_closure_gate_package",
    "verify_closure_gate_readiness",
]
