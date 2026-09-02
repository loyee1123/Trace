# Memory Index

- [用户背景](user-profile.md) — 中文交流；HPC 集群（无 GUI 节点、有 GPU）；ML 研究者；对 GUI agent 双重兴趣（个人使用 + 科研二开）
- [GUI agent 调研 2026-07](gui-agent-survey-2026-07.md) — 三层架构结论 + 推荐组合（Screenpipe + UI-TARS / Agent S3）+ 报告 Artifact 链接
- [记忆库工作规范](memory-workflow-conventions.md) — 用户指定：一文一事实、先查重、绝对日期、更新后 commit
- [产出必须放工作目录](outputs-under-working-dir.md) — 所有文件一律放 /scratch4/kding1/Trace/ 底下，记忆库已迁移至此，旧路径为软链接
- [GitHub 远端仓库](trace-github-repo.md) — origin = github.com/loyee1123/Trace.git，每次工作后记忆更新 + commit + push
- [OSWorld 跑分路径](osworld-run-options.md) — 集群无 Docker/KVM；用 Modal/Daytona 云沙箱或个人电脑 Docker，claude-fable-5 直接可跑
- [重动作先确认](confirm-before-heavy-actions.md) — 下大模型/提交GPU任务/装大环境前必须等用户明确同意；**批准选型≠批准起服务**，GPU 服务任务要用户当场说"起"才 sbatch，用完即 scancel
- [Fara vs OpenCUA 对比](fara-vs-opencua.md) — 桌面+习惯学习选 OpenCUA（AgentNet 真人演示管线），网页自动化选 Fara
- [trace 环境与 OpenCUA 部署](trace-env-opencua.md) — conda env trace（vllm/hf/openai）已建；OpenCUA-7B 权重下载与 GPU 任务待批准
- [工作日志 2026-07-28](worklog-2026-07-28.md) — 调研→三轮选型定 OpenCUA→trace 环境就绪；权重与 GPU 任务待批准
- [集群 GPU/CUDA 硬约束](cluster-gpu-cuda-constraint.md) — 驱动 575=CUDA≤12.9 + glibc 2.28，PyPI vllm 全不可用，走 conda-forge cuda129 构建
- [工作日志 2026-07-29](worklog-2026-07-29.md) — 权重 16G 下载毕、demo_client.py 写好、部署踩坑四连、conda-forge 解法；GPU 任务等批准
- [工作日志 2026-08-04](worklog-2026-08-04.md) — demo 首次端到端跑通；Triton 工具链缺件、encoder 缓存、Windows DPI/点击/死循环修复
- [工作日志 2026-08-06](worklog-2026-08-06.md) — demo 防死循环/终止判定迭代；Claude 双方案落地（Claude Code 订阅版 + API computer use 版）
- [开源 CUA 模型候选 2026-08](open-cua-models-2026-08.md) — 4×A100 80GB 可跑：Qwen3.8-27B(84.3%) / Holo3.1-35B-A3B；需新环境 vllm 0.27.1 cuda129
- [工作日志 2026-08-29](worklog-2026-08-29.md) — Claude Code 方案 A 实测成功；Qwen3.8-27B 在现有 trace 环境(vllm 0.19.1)服务跑通，客户端 qwen/qwen_client.py 已移植；GPU 任务必须用户当场允许
- [工作日志 2026-08-31](worklog-2026-08-31.md) — Qwen3.8 实测(死循环两轮修复+未决的点击拦截问题)；演示学习落地 record_demo.py + --demo 多演示；LoRA 微调路径设计
- [工作日志 2026-09-02](worklog-2026-09-02.md) — 客户端 Mac 跨平台化；Retina 坐标 bug(截图物理px vs pyautogui逻辑坐标差2倍)修复待验证；多显示器是已知边界
