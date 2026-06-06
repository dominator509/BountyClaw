"""Phase 18 readiness-dashboard verification entrypoint."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from bountyclaw.readiness_dashboard import verify_readiness_dashboard


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify Phase 18 readiness-dashboard governance.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to verify.")
    parser.add_argument("--json", action="store_true", help="Emit JSON result.")
    args = parser.parse_args()

    result = verify_readiness_dashboard(args.root)
    if args.json:
        print(result.model_dump_json(indent=2))
    else:
        print(json.dumps(result.model_dump(mode="json"), indent=2))
    return 0 if result.ready_for_commit and result.ready_for_codex else 2


if __name__ == "__main__":
    raise SystemExit(main())
