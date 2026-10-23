#!/usr/bin/env python3
"""Run the external Cosmos Lite RoboLab baseline from this lab checkout."""

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from cosmos3_lab.runner import main


if __name__ == "__main__":
    raise SystemExit(main())
