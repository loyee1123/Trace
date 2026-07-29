---
name: trace-env-opencua
description: 项目专用 conda 环境 trace 与 OpenCUA 部署状态
metadata:
  type: project
---

2026-07-28：项目主线定为 OpenCUA（用户确认，见 [[fara-vs-opencua]]）。conda 环境 `trace` 已建于 /scratch4/kding1/envs/trace（Python 3.11 + vllm 0.26.0 + torch 2.11.0+cu130 + huggingface_hub 1.25.1 + openai，8.2G，2026-07-28 装毕验证），是本项目的专用环境。部署材料在 /scratch4/kding1/Trace/opencua/（slurm 脚本 + README + 官方仓库浅克隆 OpenCUA-ref，已 gitignore）。

之前的 UI-TARS 部署已废弃（任务取消、权重删除、记忆已删）；uitars/ 目录下脚本留作参考。

OpenCUA-7B 权重已于 2026-07-29 下载完毕（16G，28 个 safetensors 分片，位于 HF_HOME hub 缓存）。注意：`huggingface-cli` 已弃用且静默不工作（exit 0 但不下载），必须用 `hf download`。
待批准动作：提交 GPU 服务任务 sbatch serve_opencua.slurm（[[confirm-before-heavy-actions]]）。
OpenCUA 交互格式：system prompt "You are a GUI agent..."，截图+任务→输出 pyautogui 动作（绝对坐标）；官方 CLAUDE.md 在 OpenCUA-ref/ 内，含数据管线（录制→标准化→CoT）用法，研究阶段直接复用。
