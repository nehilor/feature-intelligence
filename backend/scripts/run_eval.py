#!/usr/bin/env python3
"""Offline evaluation entrypoint (no provider calls)."""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from evals.runners.offline import format_offline_report, run_offline_evaluation, write_optional_json_report


def main() -> int:
    result = run_offline_evaluation()
    print(format_offline_report(result))
    write_optional_json_report(result, BACKEND_ROOT / "evals" / "results" / "latest_offline.json")
    return 0 if result.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
