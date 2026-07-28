---
name: trace-env-opencua
description: 项目专用 conda 环境 trace 与 OpenCUA 部署状态
metadata:
  type: project
---

2026-07-28：项目主线定为 OpenCUA（用户确认，见 [[fara-vs-opencua]]）。conda 环境 `trace` 已建于 /scratch4/kding1/envs/trace（Python 3.11 + vllm≥0.12 + huggingface_hub + openai），是本项目的专用环境。部署材料在 /scratch4/kding1/Trace/opencua/（slurm 脚本 + README + 官方仓库浅克隆 OpenCUA-ref，已 gitignore）。

之前的 UI-TARS 部署已废弃（任务取消、权重删除、记忆已删）；uitars/ 目录下脚本留作参考。

待批准动作：下载 xlangai/OpenCUA-7B 权重（约 17GB）、提交 GPU 服务任务（[[confirm-before-heavy-actions]]）。
OpenCUA 交互格式：system prompt "You are a GUI agent..."，截图+任务→输出 pyautogui 动作（绝对坐标）；官方 CLAUDE.md 在 OpenCUA-ref/ 内，含数据管线（录制→标准化→CoT）用法，研究阶段直接复用。
