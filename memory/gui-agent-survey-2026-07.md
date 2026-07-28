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

2026-07-28 补充核实 Anthropic 产品线：Computer Use 已于 2026-03-24 内置 macOS Claude 桌面 app（research preview，Pro/Max）；Claude Cowork 2026-07-07 起支持 web/移动端云端执行（Dispatch 派任务）；另有 Claude in Chrome 浏览器控制。对比结论：个人使用若有 macOS+订阅则 Claude 系体验最完整；科研仍选 UI-TARS 系（唯一开放权重、可集群部署/微调）。两家都无「长期观察学习习惯」能力，观察层仍需 Screenpipe。

2026-07-28 榜单核实（llm-stats 等）：绝对榜首已是闭源模型——OSWorld-Verified 前列 Claude Fable 5 / Mythos 5 约 85%、字节 Seed 2.1 Pro 78.8%、GPT-5.4 自报 75%；ScreenSpot-Pro 榜首 Claude Opus 4.8（87.9%）。UI-TARS-1.5-7B 已非 SOTA，但仍是开放权重里的社区标准 grounding 基线（Agent S3 官方推荐、文献可比性好）；开源替代关注 Qwen3-VL 系列（ScreenSpot 95.8%，榜近饱和）。科研结论不变：基线要「公认+可控」而非 SOTA，实验建议 UI-TARS 与 Qwen3-VL 双 grounding 对比。

**Why:** 用户明确表示两条路线都要，后续大概率会继续推进部署或研究选题。
**How to apply:** 后续讨论 GUI agent 时以此结论为起点，不必重新调研；注意执行层工具需图形桌面（用户 HPC 节点跑不了，但集群 GPU 可托管 UI-TARS-1.5-7B 供远程调用）。参见 [[user-profile]]。
