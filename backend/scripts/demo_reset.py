#!/usr/bin/env python3
"""Destructive local demo database reset."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))


def _load_seed():
    seed_path = BACKEND_ROOT / "scripts" / "seed.py"
    spec = importlib.util.spec_from_file_location("demo_seed", seed_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def main() -> None:
    print("WARNING: Resetting local demo database...")
    print("This removes local SQLite feature-intelligence data and reloads baseline demo requests.")
    seed_module = _load_seed()
    seed_module.seed()
    print("Demo reset complete.")


if __name__ == "__main__":
    main()
