"""Phase 16 validation-baseline verification entrypoint."""

from __future__ import annotations

import argparse
from pathlib import Path

from bountyclaw.validation_baseline import verify_validation_baseline_readiness


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 16 validation-baseline readiness.")
    parser.add_argument("--root", default=".", help="Repository root to verify.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    result = verify_validation_baseline_readiness(root=Path(args.root))
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
