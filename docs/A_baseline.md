# 阶段 A：RoboLab + DROID 基线

## 目标

使用仓库内隔离的 Cosmos Lite 源码快照、独立量化推理环境和外部 RoboLab / Isaac Sim 运行 `BananaInBowlTask`，记录单 episode 闭环结果。模型 checkpoint、原始数据和 Python 环境仍单独管理。

## 上游与运行输入

| 组件 | 记录 |
| --- | --- |
| Cosmos Lite | [xxxxyu/cosmos-lite](https://github.com/xxxxyu/cosmos-lite)；源码位于 `sources/xxxxyu_cosmos-lite`，声明包版本 `1.2.2`、变更记录版本 `0.3.0` |
| RoboLab | [NVlabs/RoboLab](https://github.com/NVlabs/RoboLab)，固定为 `v0.3.1` / `9db0aaf` 子模块，位于 `external/RoboLab` |
| 模型 | 本地 `Cosmos3-Edge-Policy-DROID` BF16 checkpoint；不纳入 Git |
| 运行时 | Cosmos Lite 量化策略环境与 RoboLab / Isaac Sim 环境分别管理 |
| 配置 | `configs/robolab.yaml`；路径通过环境变量传入 |

Cosmos Lite 的可用快照没有 `.git` 元数据，因此当前不能确认不可变上游 revision。原始快照与本仓库脱敏副本的校验摘要见 [`source-provenance.json`](source-provenance.json)；逐文件清单分别是 [`cosmos-lite-source-manifest.sha256`](cosmos-lite-source-manifest.sha256) 和 [`cosmos-lite-project-manifest.sha256`](cosmos-lite-project-manifest.sha256)。

## 启动

在 Linux / WSL 环境安装本仓库依赖：

```bash
python -m pip install -e .
```

初始化子模块并应用阶段 A 所需的录制补丁：

```bash
GIT_LFS_SKIP_SMUDGE=1 git submodule update --init --recursive
python scripts/prepare_robolab.py
```

RoboLab 的仿真资产由 Git LFS 管理；需要运行仿真时执行 `git -C external/RoboLab lfs pull`。第二个 LeRobot 数据导出补丁属于后续数据阶段，可用 `python scripts/prepare_robolab.py --trajectory-export` 应用。

设置 Cosmos Lite 源码位置与以下外部资源路径后运行：

```bash
export COSMOS_LITE_DIR="$(pwd)/sources/xxxxyu_cosmos-lite"
export COSMOS_QUANT_PYTHON=/path/to/cosmos-runtime/bin/python
export ROBOLAB_PYTHON=/path/to/robolab/isaac_python.sh
export COSMOS_CHECKPOINT_PATH=/path/to/Cosmos3-Edge-Policy-DROID
python scripts/run_robolab.py --config configs/robolab.yaml
```

默认任务为 `BananaInBowlTask`，环境数与运行数均为 1，录像关闭，策略与仿真使用不同 GPU。RoboLab 默认使用仓库内 `external/RoboLab`；也可用 `ROBOLAB_DIR` 覆盖路径。可以用 `POLICY_GPU`、`SIM_GPU`、`TASK`、`NUM_ENVS`、`NUM_RUNS`、`VIDEO_MODE` 和 `RUN_DIR` 覆盖配置。启动器将模型加载设为离线模式，避免运行时自动下载 checkpoint。

RoboLab 启动器会检查 `OMNI_KIT_ACCEPT_EULA` 等本机许可设置；本仓库不会替使用者设置该授权变量。

## 已记录的实测结果

以下结果来自 2026-10-23 的真实仿真闭环记录，**不是本仓库新启动器的本次运行结果**：

- 任务：`BananaInBowlTask`，`NUM_ENVS=1`、`NUM_RUNS=1`、seed `0`。
- 结果：1/1 成功，score `1.0`，终止原因 `OBJECT_IN_CONTAINER_SUCCESS`。
- 仿真运行 153 步，仿真时长约 10.2 秒，墙钟总时长约 110.7 秒。
- Cosmos policy 自身报告的 CUDA reserved 峰值约 9.206 GB。测试时 GPU 处于共享负载，因此这不是可比较的性能基线。
- 另一次录像运行成功生成低画质视频，现存于 [`deployment-evidence/cosmos3-edge-banana-low.mp4`](deployment-evidence/cosmos3-edge-banana-low.mp4)。

单个固定 seed 只能说明闭环链路跑通，不代表统计成功率、鲁棒性或性能。正式基线应补齐 Cosmos Lite 的不可变 revision，再在明确的 GPU / 负载条件下重复多个 episode。

## 复现边界

- `scripts/run_robolab.py` 调用本仓库 `sources/xxxxyu_cosmos-lite/examples/robolab_quant/pipeline.sh rollout`，仿真代码来自固定版本的 RoboLab 子模块。
- 外部 checkpoint、运行数据、profile、日志和 Python 环境都由用户单独管理；仓库 `.gitignore` 会忽略常见产物，低画质示例视频作为小型证据保留。
- RoboLab、LeRobot 和 MuJoCo 仍作为外部依赖，不复制其完整源码；模型 checkpoint 不纳入 Git。
- 当前没有在此工作区重跑该实验，也没有将单次运行描述为多次评测。
