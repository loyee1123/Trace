---
name: memory-workflow-conventions
description: 用户指定的记忆库工作规范：一文一事实、先查重、绝对日期、会话循环末尾 commit
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 2ea9e7a0-b0ac-4b96-acd7-b8701fa5c08c
  modified: 2026-07-28T16:08:13.280Z
---

用户于 2026-07-28 给出一套可移植的记忆系统规范，与默认记忆指令基本一致，额外增量：工作循环为「读记忆 → 干活 → 更新共享记忆 → commit」——记忆目录应作为 git 仓库版本控制，每次更新后 commit；重要实测结果、决策、踩坑要随手沉淀，不等会话结束。

2026-07-28 补充：整个工作目录 `/scratch4/kding1/Trace` 是一个 git 仓库（memory/ 不再嵌套独立 git），远端为 [[trace-github-repo]]。每次工作完成后：把本次的 findings、结果、经验写入 memory/ → 更新 MEMORY.md 索引 → 在仓库根 commit → `git push origin main`。

**Why:** 用户希望记忆库跨会话共享且有版本历史，并通过 GitHub 跨机器同步、可追溯。
**How to apply:** 每次会话开始读 MEMORY.md；工作结束把新发现沉淀成记忆后，在 /scratch4/kding1/Trace 执行 git commit 并 push 到 origin main；一文件一事实、先查重再存、日期写绝对值、错误记忆直接删。
