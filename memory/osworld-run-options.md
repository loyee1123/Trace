---
name: osworld-run-options
description: 用 Claude Fable 5 跑 OSWorld 基准的可行路径；集群无 Docker/KVM 跑不了本地 VM 模式
metadata:
  type: reference
---

2026-07-28 核实：集群（login 节点）无 docker/podman/apptainer 二进制、无 /dev/kvm（CPU 有 vmx 但未启用），OSWorld 本地虚拟化模式在集群上不可行。可行路径：

1. 尝鲜：Anthropic computer-use quickstart（个人电脑 Docker，容器内虚拟桌面）— https://github.com/anthropics/anthropic-quickstarts/tree/main/computer-use-demo
2. 正式子集：OSWorld harness（https://github.com/xlang-ai/OSWorld），`--provider_name modal/daytona` 云沙箱模式不需本地 KVM，集群登录节点也能发起；`--model claude-fable-5`，先 `--domain chrome` 小规模跑（几美元），全量 369 任务需几十上百美元 API 费。
3. 复现榜单：AWS provider 并行（约 1h）；注意榜单 85% 是 OSWorld-Verified 配置（修订任务集 + 官方 harness 设定），普通配置分数有出入；上榜需联系维护者，部分任务要 Google OAuth。

参见 [[gui-agent-survey-2026-07]]。
