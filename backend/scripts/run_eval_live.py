#!/usr/bin/env python3
"""Optional live provider evaluation (explicit opt-in, not part of verify)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("AI_ENABLED", "true")

from app.core.config import get_settings
from evals.runners.live import format_live_report, run_live_evaluation, write_live_report


def main() -> int:
    get_settings.cache_clear()
    max_cases_raw = os.environ.get("EVAL_MAX_CASES")
    max_cases = int(max_cases_raw) if max_cases_raw else None
    try:
        result = run_live_evaluation(max_cases=max_cases)
    except RuntimeError as exc:
        print(f"Live evaluation skipped: {exc}")
        return 2
    print(format_live_report(result))
    path = write_live_report(result)
    print(f"\nWrote report: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
