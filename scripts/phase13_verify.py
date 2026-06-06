"""Phase 13 deterministic verification entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path

from bountyclaw.evidence_review import verify_evidence_review_readiness


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 13 evidence-review readiness.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to verify.")
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=Path("validation_evidence"),
        help="Evidence artifact directory.",
    )
    parser.add_argument(
        "--review-file", type=Path, default=None, help="Optional evidence review decision file."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()
    result = verify_evidence_review_readiness(args.root, args.evidence_dir, args.review_file)
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(
            f"phase={result.phase} passed={result.passed_count} failed={result.failed_count} "
            f"deferred={result.deferred_count} ready_for_commit={result.ready_for_commit} "
            f"ready_for_codex={result.ready_for_codex} ready_for_production={result.ready_for_production}"
        )
    return 0 if result.ready_for_commit and result.ready_for_codex else 2


if __name__ == "__main__":
    raise SystemExit(main())
