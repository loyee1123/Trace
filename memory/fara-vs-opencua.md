---
name: fara-vs-opencua
description: Fara1.5 与 OpenCUA 对比结论：桌面+习惯学习选 OpenCUA，网页自动化选 Fara
metadata:
  type: project
---

2026-07-28 对比（用户在两者间选型）：共同点——端到端 native agent、Qwen 系基座、MIT、vLLM 部署（都需新环境：Fara 要 vllm≥0.19.1，OpenCUA 要 ≥0.12.0 + trust-remote-code）。

关键区别：Fara1.5（微软）仅浏览器（Playwright），合成数据训练，fara-cli/Magentic-UI 产品化好，web 基准强；OpenCUA（XLANG，NeurIPS 2025 Spotlight）完整桌面键鼠动作空间，22.6K 真人演示训练（AgentNet），配 AgentNetTool 录制工具，OSWorld-Verified 开源最强（7B 26.6%/32B 34.8%/72B 45%），无现成客户端。

结论：用户目标（桌面 app + 学习使用习惯）→ OpenCUA 契合度最高——AgentNetTool 管线（录人类操作→归并→CoT→微调）可直接换成"录用户自己的习惯"，即用户设想的研究本身。Fara 留作网页任务对照。7B 单卡可跑，32B 需 2×A100 或量化。

**Why:** 用户原本想试 Fara1.5-9B，对比后 OpenCUA 与其研究命题（[[gui-agent-survey-2026-07]]）对口得多。
**How to apply:** 部署前出方案等用户确认（[[confirm-before-heavy-actions]]）；试用需自建交互循环或走 OSWorld harness。
