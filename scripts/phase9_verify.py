#!/usr/bin/env python3
"""Deterministic Phase 9 release-control verification script."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _ensure_src_on_path(root: Path) -> None:
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify BountyClaw Phase 9 release controls.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to verify.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    root = args.root.expanduser().resolve(strict=False)
    _ensure_src_on_path(root)

    from bountyclaw.release import verify_release_controls

    result = verify_release_controls(root)
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(
            f"phase9 release controls: passed={result.passed_count} "
            f"failed={result.failed_count} deferred={result.deferred_count} "
            f"ready_for_commit={result.ready_for_commit} "
            f"ready_for_external_release={result.ready_for_external_release}"
        )
        for check in result.checks:
            if check.status != "pass":
                print(f"- {check.status}: {check.check_id}: {check.summary}")
    return 0 if result.ready_for_commit else 2


if __name__ == "__main__":
    raise SystemExit(main())
