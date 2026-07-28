---
name: outputs-under-working-dir
description: 用户强烈要求：所有产出（记忆库、报告、脚本等）一律放在工作目录底下，不要放 home 或其他位置
metadata:
  type: feedback
---

2026-07-28 用户明确（且强烈）纠正：所有东西都必须放在工作目录 `/scratch4/kding1/Trace` 底下。记忆库已从 `~/.claude/projects/-scratch4-kding1/memory/` 迁移到 `/scratch4/kding1/Trace/memory/`，旧路径保留为指向新位置的软链接（这样默认记忆加载机制仍然生效）。调研报告源文件也已放到 `/scratch4/kding1/Trace/reports/`。

**Why:** 用户在 HPC 集群上工作，scratch 空间才是项目数据的正确归属；散落在 home 下的文件不便管理，也可能受 home 配额限制。
**How to apply:** 今后任何新文件——记忆、报告、脚本、数据、临时产物的正式版本——默认都创建在 `/scratch4/kding1/Trace/` 下的合适子目录；除非用户明确指定其他位置。参见 [[memory-workflow-conventions]]。
