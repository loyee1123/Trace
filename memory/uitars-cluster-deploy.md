---
name: uitars-cluster-deploy
description: UI-TARS-1.5-7B 在集群上的 vLLM 部署方案：脚本位置、环境、连接方式
metadata:
  type: project
---

2026-07-28 搭建：UI-TARS-1.5-7B 部署在集群 a100 分区（13+ 台 4×A100 节点）。关键事实：
- 现成环境 `/scratch4/kding1/envs/Aria_conda` 已带 vLLM 0.11.2 + torch 2.9，无需新建
- 权重下载到共享缓存 `HF_HOME=/scratch4/kding1/huggingface/hf-home`（约 17GB，不入 git）
- 启动：`sbatch /scratch4/kding1/Trace/uitars/serve_uitars.slurm`（1×A100，8h 时限，端口 8000，served-model-name `ui-tars-1.5-7b`）
- 用户笔记本经 SSH 隧道 `-L 8000:<GPU节点>:8000` 连 UI-TARS Desktop（配置见 uitars/README.md）
- 集群登录节点无 docker/KVM（见 [[osworld-run-options]]），故模型服务上集群、GUI 客户端在用户本机

**Why:** 用户选择先直接试 UI-TARS（而非 Anthropic quickstart）；集群 GPU 托管省 API 费且贴合后续科研路线（[[gui-agent-survey-2026-07]]）。
**How to apply:** 后续要起服务直接 sbatch 该脚本；vLLM 报 --limit-mm-per-prompt JSON 格式错误时改旧语法 image=10。
