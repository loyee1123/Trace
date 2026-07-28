---
name: trace-github-repo
description: 工作目录 Trace 对应的 GitHub 远端仓库地址与推送约定
metadata:
  type: reference
---

工作目录 `/scratch4/kding1/Trace` 的远端仓库：https://github.com/loyee1123/Trace.git（remote 名 `origin`，分支 `main`）。每次工作完成、记忆更新后都要 push 到这里（见 [[memory-workflow-conventions]]）。

集群上无 `gh` CLI；HTTPS 无存储凭证，SSH key（~/.ssh/id_ecdsa.pub / id_rsa.pub）截至 2026-07-28 尚未绑定 GitHub 账号——push 前需确认认证已配置。
