---
name: trace-env-opencua
description: 项目专用 conda 环境 trace 与 OpenCUA 部署状态
metadata:
  type: project
---

2026-07-28：项目主线定为 OpenCUA（用户确认，见 [[fara-vs-opencua]]）。conda 环境 `trace` 建于 /scratch4/kding1/envs/trace，是本项目的专用环境。部署材料在 /scratch4/kding1/Trace/opencua/（slurm 脚本 + demo_client.py + README + 官方仓库浅克隆 OpenCUA-ref，已 gitignore）。

2026-07-29 环境重构：最初 pip 装的 vllm 0.26.0 + torch 2.11+cu130 因集群驱动/glibc 约束全部不可用（见 [[cluster-gpu-cuda-constraint]]），已卸载，改装 conda-forge `vllm=0.19.1=cuda129_py311*`（transformers 回到 4.x）。slurm 脚本已加 module purge + LD_LIBRARY_PATH 修复，时限按用户要求设为 1 小时。曾给 HF 缓存里的 tokenization_opencua.py 和 vllm 0.26 的 opencua.py 打过 transformers-5.x 兼容补丁；降级到 transformers 4.x 后不再需要（HF 缓存补丁无害保留）。

之前的 UI-TARS 部署已废弃（任务取消、权重删除、记忆已删）；uitars/ 目录下脚本留作参考。

OpenCUA-7B 权重已于 2026-07-29 下载完毕（16G，28 个 safetensors 分片，位于 HF_HOME hub 缓存）。注意：`huggingface-cli` 已弃用且静默不工作（exit 0 但不下载），必须用 `hf download`。
待批准动作：conda 环境装好验证后，提交 GPU 服务任务 sbatch serve_opencua.slurm——用户 2026-07-29 明确说"装好后先暂时不提交"（[[confirm-before-heavy-actions]]）。
OpenCUA 交互格式：system prompt "You are a GUI agent..."，截图+任务→输出 pyautogui 动作（绝对坐标）；官方 CLAUDE.md 在 OpenCUA-ref/ 内，含数据管线（录制→标准化→CoT）用法，研究阶段直接复用。
