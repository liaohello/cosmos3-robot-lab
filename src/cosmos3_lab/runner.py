"""Launch the RoboLab rollout provided by an external Cosmos Lite checkout."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_REFERENCE = re.compile(r"\$\{([A-Za-z_][A-Za-z0-9_]*)\}")


class ConfigurationError(ValueError):
    """Raised when a config or required external dependency is invalid."""


def _expand_env(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _expand_env(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_expand_env(item) for item in value]
    if not isinstance(value, str):
        return value

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        resolved = os.environ.get(name)
        if not resolved:
            raise ConfigurationError(f"Required environment variable is not set: {name}")
        return resolved

    return ENV_REFERENCE.sub(replace, value)


def _load_config(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConfigurationError(f"Cannot read config file: {path}") from exc
    except yaml.YAMLError as exc:
        raise ConfigurationError(f"Invalid YAML config: {path}") from exc
    if not isinstance(loaded, dict):
        raise ConfigurationError("The config file must contain a YAML mapping")
    return _expand_env(loaded)


def _path(value: Any, label: str, *, relative_to: Path | None = None) -> Path:
    if not isinstance(value, str) or not value.strip():
        raise ConfigurationError(f"Missing path for {label}")
    candidate = Path(value).expanduser()
    if not candidate.is_absolute() and relative_to is not None:
        candidate = relative_to / candidate
    return candidate.resolve()


def _require_file(path: Path, label: str) -> None:
    if not path.is_file():
        raise ConfigurationError(f"{label} is not a file: {path}")


def _require_dir(path: Path, label: str) -> None:
    if not path.is_dir():
        raise ConfigurationError(f"{label} is not a directory: {path}")


def _positive_int(value: Any, label: str) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise ConfigurationError(f"{label} must be a positive integer") from exc
    if parsed < 1:
        raise ConfigurationError(f"{label} must be a positive integer")
    return parsed


def run(config_path: Path) -> int:
    config = _load_config(config_path)
    external = config.get("external")
    rollout = config.get("rollout")
    runtime = config.get("runtime", {})
    if not isinstance(external, dict) or not isinstance(rollout, dict):
        raise ConfigurationError("Config must define 'external' and 'rollout' mappings")
    if not isinstance(runtime, dict):
        raise ConfigurationError("Config 'runtime' must be a mapping")

    cosmos_root = _path(external.get("cosmos_lite_dir"), "external.cosmos_lite_dir")
    robolab_value = os.environ.get("ROBOLAB_DIR") or external.get("robolab_dir")
    robolab_root = _path(
        robolab_value,
        "external.robolab_dir",
        relative_to=REPO_ROOT,
    )
    cosmos_python = _path(external.get("cosmos_python"), "external.cosmos_python")
    robolab_python = _path(external.get("robolab_python"), "external.robolab_python")
    checkpoint = _path(external.get("checkpoint_path"), "external.checkpoint_path")
    pipeline = cosmos_root / "examples" / "robolab_quant" / "pipeline.sh"
    deployment_config = _path(
        external.get("deployment_config"),
        "external.deployment_config",
        relative_to=cosmos_root,
    )

    _require_dir(cosmos_root, "Cosmos Lite checkout")
    _require_dir(robolab_root, "RoboLab checkout")
    _require_file(cosmos_python, "Cosmos runtime Python")
    _require_file(robolab_python, "RoboLab Python launcher")
    _require_dir(checkpoint, "Cosmos checkpoint")
    _require_file(pipeline, "Cosmos Lite RoboLab pipeline")
    _require_file(deployment_config, "deployment config")

    policy_gpu = os.environ.get("POLICY_GPU", str(rollout.get("policy_gpu", "0")))
    sim_gpu = os.environ.get("SIM_GPU", str(rollout.get("sim_gpu", "1")))
    if not policy_gpu or not sim_gpu or policy_gpu == sim_gpu:
        raise ConfigurationError("POLICY_GPU and SIM_GPU must identify different physical GPUs")

    task = os.environ.get("TASK", str(rollout.get("task", "BananaInBowlTask")))
    if not task.strip():
        raise ConfigurationError("TASK must not be empty")
    num_envs = _positive_int(os.environ.get("NUM_ENVS", rollout.get("num_envs", 1)), "NUM_ENVS")
    num_runs = _positive_int(os.environ.get("NUM_RUNS", rollout.get("num_runs", 1)), "NUM_RUNS")
    video_mode = os.environ.get("VIDEO_MODE", str(rollout.get("video_mode", "none")))

    run_root = _path(rollout.get("run_root", "runs"), "rollout.run_root", relative_to=REPO_ROOT)
    run_dir = Path(os.environ["RUN_DIR"]).expanduser() if os.environ.get("RUN_DIR") else None
    if run_dir is None:
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        run_dir = run_root / f"robolab-{stamp}"
    run_dir = run_dir.resolve()

    bash = shutil.which("bash")
    if bash is None:
        raise ConfigurationError("bash was not found; run this on Linux or in a Linux/WSL shell")

    env = os.environ.copy()
    env.update(
        {
            "COSMOS_QUANT_PYTHON": str(cosmos_python),
            "DEPLOYMENT_CONFIG": str(deployment_config),
            "CHECKPOINT_PATH": str(checkpoint),
            "ROBOLAB_DIR": str(robolab_root),
            "ROBOLAB_PYTHON": str(robolab_python),
            "RUN_DIR": str(run_dir),
            "OUTPUT_NAME": run_dir.name,
            "POLICY_GPU": policy_gpu,
            "SIM_GPU": sim_gpu,
            "TASK": task,
            "NUM_ENVS": str(num_envs),
            "NUM_RUNS": str(num_runs),
            "VIDEO_MODE": video_mode,
            "COSMOS_TRAINING": "0",
        }
    )
    if runtime.get("offline_model_loading", True):
        env["HF_HUB_OFFLINE"] = "1"
        env["TRANSFORMERS_OFFLINE"] = "1"

    print(f"Starting RoboLab rollout for task {task}; run output: {run_dir}")
    completed = subprocess.run(
        [bash, str(pipeline), "rollout"],
        cwd=cosmos_root,
        env=env,
        check=False,
    )
    return completed.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--config",
        type=Path,
        default=REPO_ROOT / "configs" / "robolab.yaml",
        help="YAML configuration file (default: configs/robolab.yaml)",
    )
    args = parser.parse_args(argv)
    try:
        return run(args.config.resolve())
    except ConfigurationError as exc:
        print(f"configuration error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
