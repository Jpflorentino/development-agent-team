#!/usr/bin/env python3
"""Run directly from a checkout; does not install a Python package globally."""
import sys
from pathlib import Path

if sys.version_info < (3, 11):
    raise SystemExit("Development Agent Team requires Python 3.11+ (uses standard-library tomllib).")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from dat.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
