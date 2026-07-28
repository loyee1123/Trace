# Trace

工作与研究记录仓库：每次工作会话产生的 findings、结果、经验都沉淀在这里。

## 结构

- `memory/` — 跨会话记忆库，一文件一事实（格式见 `memory/memory-workflow-conventions.md`）。`memory/MEMORY.md` 是索引，每次会话开始先读它。
- `reports/` — 调研报告、分析产出。

## 工作循环

读 `memory/MEMORY.md` → 干活 → 把本次的 findings / 结果 / 踩坑写入 `memory/` 并更新索引 → commit → push 到本仓库。
