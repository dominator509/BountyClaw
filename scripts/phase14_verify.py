#!/usr/bin/env python3
"""Phase 14 verification entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bountyclaw.gap_tracker import verify_gap_tracker_governance


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify Phase 14 gap tracker governance readiness."
    )
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to verify.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    result = verify_gap_tracker_governance(args.root)
    if args.json:
        print(json.dumps(result.model_dump(mode="json"), indent=2, sort_keys=True))
    else:
        print(
            "Phase 14 gap tracker governance verification: "
            f"passed={result.passed_count} failed={result.failed_count} "
            f"deferred={result.deferred_count} ready_for_commit={result.ready_for_commit} "
            f"ready_for_codex={result.ready_for_codex} ready_for_production={result.ready_for_production}"
        )
    return 0 if result.ready_for_commit and result.ready_for_codex else 2


if __name__ == "__main__":
    raise SystemExit(main())
