# Cosmos3 Robot Lab

用于组织 Cosmos3 机器人实验的代码、配置、评测记录和研究文档。仓库按阶段推进，当前入口聚焦 RoboLab + DROID 基线（阶段 A）。

## 仓库边界

本仓库保存实验适配层和可复现材料。Cosmos Lite、RoboLab、LeRobot、MuJoCo 等上游项目通过独立 checkout 或环境安装使用，不把它们的完整源码复制进来。模型权重、原始数据、视频、运行日志和 Python 环境也不进入 Git。

本机 Cosmos Lite 快照的来源摘要见 [`docs/source-provenance.json`](docs/source-provenance.json)，逐文件清单见 [`docs/cosmos-lite-source-manifest.sha256`](docs/cosmos-lite-source-manifest.sha256)。清单只用于校验外部源码快照，不代表本仓库包含上游源码。运行时通过环境变量传入外部源码、RoboLab checkout、解释器和 checkpoint 位置。

## 阶段

| 阶段 | 内容 | 当前状态 |
| --- | --- | --- |
| A | RoboLab + DROID 基线复现 | 已有单 episode 闭环记录；新仓库中的启动器尚未在此工作区重跑 |
| B | MuJoCo + SO101 仿真适配 | 后续阶段 |
| C | LeRobot 数据转换与 Cosmos 微调 | 后续阶段 |
| D | 仿真 / 真机闭环评测 | 后续阶段 |

这些阶段共用同一个实验仓库；通用仿真、遥操作和真机控制仍由现有机器人平台负责。

## 目录

```text
configs/robolab.yaml          阶段 A 的无主机路径配置
integrations/robolab/         对 RoboLab 的版本化集成补丁
scripts/run_robolab.py        阶段 A 启动入口
src/cosmos3_lab/              实验仓库的轻量适配代码
docs/A_baseline.md            基线条件、结果与复现限制
docs/source-provenance.json   外部 Cosmos Lite 快照的来源摘要
```

## 阶段 A：RoboLab + DROID

运行环境需要 Linux（或配置好 Linux 路径的 WSL）、RoboLab / Isaac Sim 环境、Cosmos Lite 的量化推理环境、可读的本地 Cosmos3-Edge checkpoint，以及两个可用且不同的 GPU。安装本仓库的轻量依赖：

```bash
python -m pip install -e .
```

从干净的 RoboLab `v0.3.1` checkout 开始时，先按 [`integrations/robolab/README.md`](integrations/robolab/README.md) 应用第一个录制补丁；阶段 A 不需要应用 DROID 数据导出补丁。

设置外部资源路径后启动单次基线：

```bash
export COSMOS_LITE_DIR=/path/to/cosmos-lite
export ROBOLAB_DIR=/path/to/RoboLab
export COSMOS_QUANT_PYTHON=/path/to/cosmos-runtime/bin/python
export ROBOLAB_PYTHON=/path/to/robolab/isaac_python.sh
export COSMOS_CHECKPOINT_PATH=/path/to/Cosmos3-Edge-Policy-DROID
python scripts/run_robolab.py --config configs/robolab.yaml
```

如需同意 Isaac Sim 的许可条款，请先在本地确认并按 RoboLab / Isaac Sim 的要求完成授权；启动器不会替使用者自动接受条款。运行输出默认进入 Git 忽略的 `runs/` 和 RoboLab 自己的输出目录。

更详细的来源、运行约束和已记录结果见 [`docs/A_baseline.md`](docs/A_baseline.md)。阶段 A 的历史结果是单 episode 功能验证，不是成功率或性能基准。
