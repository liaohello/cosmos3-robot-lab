#!/usr/bin/env python3
"""Apply the version-pinned RoboLab integration patches to the submodule."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys


REPO_ROOT = Path(__file__).resolve().parents[1]
BASE_COMMIT = "9db0aaf09d9fe5d4f37b168320788258c7012463"
PATCH_DIR = REPO_ROOT / "integrations" / "robolab" / "patches"


def _git(robolab_dir: Path, *args: str, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(robolab_dir), *args],
        text=True,
        capture_output=True,
        check=check,
    )


def _apply_patch(robolab_dir: Path, patch: Path) -> None:
    reverse_check = _git(robolab_dir, "apply", "--reverse", "--check", str(patch))
    if reverse_check.returncode == 0:
        print(f"Already applied: {patch.name}")
        return

    forward_check = _git(robolab_dir, "apply", "--check", str(patch))
    if forward_check.returncode != 0:
        detail = forward_check.stderr.strip() or forward_check.stdout.strip()
        raise RuntimeError(f"Patch does not apply cleanly ({patch.name}): {detail}")

    subprocess.run(["git", "-C", str(robolab_dir), "apply", str(patch)], check=True)
    print(f"Applied: {patch.name}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--trajectory-export",
        action="store_true",
        help="Also apply the LeRobot v3 DROID trajectory export patch for the later data stage.",
    )
    args = parser.parse_args(argv)

    configured = os.environ.get("ROBOLAB_DIR") or "external/RoboLab"
    robolab_dir = Path(configured).expanduser()
    if not robolab_dir.is_absolute():
        robolab_dir = REPO_ROOT / robolab_dir
    robolab_dir = robolab_dir.resolve()

    head = _git(robolab_dir, "rev-parse", "HEAD")
    if head.returncode != 0:
        print(
            "RoboLab submodule is missing. Initialize it with "
            "`git submodule update --init --recursive` first.",
            file=sys.stderr,
        )
        return 2
    actual_commit = head.stdout.strip()
    if actual_commit != BASE_COMMIT:
        print(
            f"RoboLab must be at pinned base {BASE_COMMIT}; found {actual_commit}.",
            file=sys.stderr,
        )
        return 2

    patches = [PATCH_DIR / "0001-bounded-cpu-streaming-image-recorder.patch"]
    if args.trajectory_export:
        patches.append(PATCH_DIR / "0002-Add-training-ready-Cosmos-DROID-trajectory-export.patch")

    try:
        for patch in patches:
            _apply_patch(robolab_dir, patch)
    except (OSError, subprocess.CalledProcessError, RuntimeError) as exc:
        print(f"RoboLab preparation failed: {exc}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
