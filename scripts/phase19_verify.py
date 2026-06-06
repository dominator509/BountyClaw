#!/usr/bin/env python
"""Phase 19 local quality/security gate verification entrypoint."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from bountyclaw.quality_gates import verify_quality_gate_readiness


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 19 quality gate readiness.")
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = verify_quality_gate_readiness(args.root)
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
    sys.exit(main())
