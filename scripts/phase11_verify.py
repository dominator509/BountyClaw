#!/usr/bin/env python3
"""Run deterministic Phase 11 external-validation handoff verification.

This script is local-only. It prepares future Codex/local/CI/human execution but
must not run hosted CI, install packages from the network, launch scanners,
invoke providers, start MCP/browser runtimes, contact targets, perform active
validation, or submit reports.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _ensure_src_on_path(root: Path) -> None:
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify BountyClaw Phase 11 handoff readiness.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to verify.")
    parser.add_argument("--json", action="store_true", help="Print JSON result.")
    args = parser.parse_args()

    root = args.root.expanduser().resolve(strict=False)
    _ensure_src_on_path(root)

    from bountyclaw.handoff import verify_handoff_readiness

    result = verify_handoff_readiness(root)
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(
            f"phase11 handoff verification: passed={result.passed_count} "
            f"failed={result.failed_count} deferred={result.deferred_count} "
            f"ready_for_commit={result.ready_for_commit} "
            f"ready_for_codex={result.ready_for_codex} "
            f"ready_for_production={result.ready_for_production}"
        )
        for check in result.checks:
            if check.status != "pass":
                print(f"- {check.status}: {check.check_id}: {check.summary}")
    return 0 if result.ready_for_commit and result.ready_for_codex else 2


if __name__ == "__main__":
    raise SystemExit(main())
