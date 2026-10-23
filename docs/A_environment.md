# Cosmos3-Edge 环境记录（脱敏摘要）

该摘要整理自 2026-10-23 的一次环境核查与仿真实测。原始报告含服务器目录、账号和连接信息，因此没有复制进此仓库。

## 锁定运行环境

| 组件 | 记录版本 / 状态 |
| --- | --- |
| Python | `3.13.15` |
| PyTorch | `2.10.0+cu128` |
| NumPy | `2.2.6` |
| Diffusers | `0.39.0` |
| Transformers | `>=4.57.1,<5.0.0` |
| FlashAttention | `2.7.4.post1+cu128.torch210` |
| NATTEN | `0.21.6.dev6+cu128.torch210` |
| vLLM | `0.19.1` |
| OpenPI | server `0.1.0`，client `0.1.2` |
| GPU | RTX 4090 / Ada；策略和仿真分配到不同 GPU |

锁文件检查曾报告 `uv sync --frozen --no-dev --check` 无需改动；CUDA、FlashAttention、NATTEN、vLLM Marlin ops、OpenPI 与 ZMQ 导入核查通过。运行使用本地 Edge BF16 checkpoint 和离线模型加载。

## 实测边界

- `BananaInBowlTask` 单 episode 成功，具体结果见 [`A_baseline.md`](A_baseline.md)。
- policy CUDA reserved 峰值约 `9.206 GB`；首次策略请求约 `4.085 s`，后续请求约 `1.22–1.25 s`。
- 测试期间 GPU 为共享负载，因此延迟数据只作运行记录，不作为性能比较基准。
- 一次运行及一次录像运行都完成闭环；这不代表多 seed 成功率或实机安全性验证。
- 本摘要不包含权重、VAE 文件、Python 环境、数据集、日志或服务器路径。
