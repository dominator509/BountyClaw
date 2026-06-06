"""Phase 17 closure-gate verification entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bountyclaw.closure_gate import verify_closure_gate_readiness


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 17 closure-gate readiness.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to verify.")
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path("validation_evidence"),
        help="Future validation evidence directory to assess metadata for.",
    )
    parser.add_argument(
        "--attestation-file",
        type=Path,
        default=Path("validation_evidence/readiness_attestations.json"),
        help="Metadata-only readiness attestation file.",
    )
    parser.add_argument(
        "--journal",
        type=Path,
        default=Path("validation_runs/execution_journal.json"),
        help="Metadata-only validation execution journal file.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    result = verify_closure_gate_readiness(
        args.root, args.evidence_dir, args.attestation_file, args.journal
    )
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(json.dumps(result.model_dump(mode="json"), indent=2))
    return 0 if result.ready_for_commit and result.ready_for_codex else 2


if __name__ == "__main__":
    raise SystemExit(main())
