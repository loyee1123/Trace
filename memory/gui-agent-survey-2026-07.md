---
name: gui-agent-survey-2026-07
description: 2026-07-28 完成的 GUI agent 选型调研结论与报告链接（学习用户习惯的桌面 agent）
metadata: 
  node_type: memory
  type: project
  originSessionId: 2ea9e7a0-b0ac-4b96-acd7-b8701fa5c08c
  modified: 2026-07-28T16:08:07.922Z
---

2026-07-28 应用户要求调研「能学习使用习惯的现成 GUI agent」，报告已发布为 Artifact：https://claude.ai/code/artifact/26e52d47-7802-4c4a-9f9a-7d61b5a8d70b

核心结论（当时核实）：无单一产品能闭环「长期观察 → 学习习惯 → 主动执行」，按三层架构拼装：
- 观察/记忆层：Screenpipe（24/7 本地录屏记忆库 + Pipes 触发自动化 + MCP server，20.6k★）
- 学习层：OpenAdapt（演示→编译确定性重放脚本）、ProactiveAgent（清华，ActivityWatch 监测 + 主动提议，ICLR 2025）
- 执行层：UI-TARS Desktop（字节，38.3k★，即装即用）、Agent S3（`pip install gui-agents`，episodic memory，OSWorld 72.6% 超人类，科研基座首选）、UFO²（仅 Windows）

推荐：即用走 Screenpipe + UI-TARS Desktop；科研走 Agent S3 为基座、把观察层习惯记忆注入执行层规划（当前研究空白）。

**Why:** 用户明确表示两条路线都要，后续大概率会继续推进部署或研究选题。
**How to apply:** 后续讨论 GUI agent 时以此结论为起点，不必重新调研；注意执行层工具需图形桌面（用户 HPC 节点跑不了，但集群 GPU 可托管 UI-TARS-1.5-7B 供远程调用）。参见 [[user-profile]]。
