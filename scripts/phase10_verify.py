#!/usr/bin/env python3
"""Run deterministic Phase 10 hardening verification.

This script is intentionally local-only. It must not run hosted CI, publish
packages, invoke live providers, launch real MCP/browser runtimes, contact
external targets, perform active validation, or submit reports.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bountyclaw.hardening import verify_local_hardening


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify BountyClaw Phase 10 hardening controls.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to verify.")
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args()

    result = verify_local_hardening(args.root)
    payload = result.model_dump(mode="json")
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(
            "Phase 10 hardening verification: "
            f"passed={result.passed_count} failed={result.failed_count} "
            f"deferred={result.deferred_count} ready_for_commit={result.ready_for_commit} "
            f"ready_for_production={result.ready_for_production}"
        )
    return 0 if result.ready_for_commit else 2


if __name__ == "__main__":
    raise SystemExit(main())
