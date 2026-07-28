---
name: trace-github-repo
description: 工作目录 Trace 对应的 GitHub 远端仓库地址与推送约定
metadata:
  type: reference
---

工作目录 `/scratch4/kding1/Trace` 的远端仓库：https://github.com/loyee1123/Trace.git（remote 名 `origin`，分支 `main`）。每次工作完成、记忆更新后都要 push 到这里（见 [[memory-workflow-conventions]]）。

集群上无 `gh` CLI，SSH key 未绑定 GitHub 账号。2026-07-28 首次 push 成功，用的是用户提供的 PAT（HTTPS，一次性 credential helper 方式）。token 本身绝不写入仓库或记忆；若 `git push` 提示无凭证，说明用户尚未在本机持久化 token（`credential.helper store` + ~/.git-credentials），需请用户提供 token 或自行配置后再推。
