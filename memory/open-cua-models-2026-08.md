---
name: open-cua-models-2026-08
description: 2026-08-29 调研：可在 4×ica100(A100 80GB) 本地跑的开源 computer-use 模型候选与 vLLM 兼容性
metadata:
  type: project
---

2026-08-29 调研结论（目标：本地化替代 Claude 做 GUI 控制；资源上限 4×ica100 = A100 80GB PCIe ×4 = 320GB 显存，驱动 575.51.03/CUDA≤12.9 约束不变，见 [[cluster-gpu-cuda-constraint]]）：

| 模型 | OSWorld-Verified | 权重 | 架构 | 许可 |
|---|---|---|---|---|
| Qwen/Qwen3.8-27B (2026-08-14) | 84.3%（自报；Claude Fable 5 为 85%） | 55.6GB bf16 dense | Qwen3_5ForConditionalGeneration | Apache-2.0 |
| Hcompany/Holo-3.1-35B-A3B (2026-06) | Holo3 官方 77.8%，第三方榜 82.6% | 70.2GB MoE，3B 激活 | Qwen3_5MoeForConditionalGeneration | Apache-2.0 |
| Hcompany/Holo-3.1-9B | 未公布 OSWorld | 18.8GB | Qwen3_5 | Apache-2.0 |
| meituan/EvoCUA-32B-20260105 | 56.7% | 66.7GB | Qwen3VL | Apache-2.0 |
| mPLUG/GUI-Owl-1.5-32B-Instruct | 56.5% | 66.7GB | Qwen3VL | MIT |
| xlangai/OpenCUA-7B（现用） | ~27% | 16GB | OpenCUA | — |

关键事实：
- 以上全部**不需要申请**（gated=False）；Holo3 的 122B 版本仅 API 不开源
- **vLLM 0.27.1 registry 含全部所需架构**（Qwen3_5 / Qwen3_5Moe / Qwen3VL / OpenCUA）；conda-forge 已有 `vllm 0.27.1 cuda129_py312`（2026-08-28 上传）——现有 trace 环境是 0.19.1，**跑 Qwen3.8/Holo 必须新建环境升级**
- Holo3.1 有完整文档化的 agent loop（hub.hcompany.ai/agent-loop）：截图包在 `<observation>` 里、只留最近 3 图、结构化 JSON 输出 `{note, thought, tool_call}` 或 function calling、坐标归一化到 [0,1000]、`answer` 动作终止；明确面向本地 Windows/Mac 桌面 agent
- Qwen3.8-27B 是通用 VLM（可微调，对习惯学习研究线有利），计算机操作的 harness 未在模型卡说明（走 Qwen-Agent 的 computer_use 工具格式）；默认开 thinking，`enable_thinking`/`reasoning_effort` 可调
- 显存：27B dense bf16 约 56GB+KV → TP=2 舒适；35B-A3B 70GB → TP=2；4 卡可同时起两个模型对比
- 推荐顺序：**Qwen3.8-27B（首选，分数最高、通用、可微调）→ Holo3.1-35B-A3B（专用、3B 激活推理快、有现成 loop 规范）**；EvoCUA/GUI-Owl 仅作对照
