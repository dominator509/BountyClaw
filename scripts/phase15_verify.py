"""Phase 15 validation-runbook verification entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path

from bountyclaw.validation_runbook import verify_validation_runbook_readiness


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 15 validation-runbook readiness.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to verify.")
    parser.add_argument(
        "--journal",
        type=Path,
        default=None,
        help="Optional metadata-only execution journal file.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    result = verify_validation_runbook_readiness(args.root, args.journal)
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(
            "phase15 validation-runbook verification: "
            f"passed={result.passed_count} "
            f"failed={result.failed_count} "
            f"deferred={result.deferred_count} "
            f"ready_for_commit={result.ready_for_commit} "
            f"ready_for_codex={result.ready_for_codex} "
            f"ready_for_production={result.ready_for_production}"
        )
    return 0 if result.ready_for_commit and result.ready_for_codex else 2


if __name__ == "__main__":
    raise SystemExit(main())
