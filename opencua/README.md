# OpenCUA-7B 集群部署（Trace 项目主线）

选型结论见 `memory/fara-vs-opencua.md`：桌面动作空间 + AgentNet 真人演示管线，契合"学习用户使用习惯"的研究目标。

## 组件

- `serve_opencua.slurm` — vLLM 服务脚本（1×A100，端口 8000，`--trust-remote-code`）
- `OpenCUA-ref/` — 官方仓库浅克隆（参考用，不入 git）：
  - `model/inference/vllm_inference.py` — 标准 OpenAI 客户端调用示例
  - `data/data-process/` — 演示录制→标准化轨迹→CoT 生成管线（后续研究复用）
  - `tool/` — AgentNetTool 录制工具（submodule）
  - `evaluation/agentnetbench/` — 离线动作评估

## 部署流程

```bash
# 1. 环境（已建好）：conda env "trace" = Python 3.11 + vllm≥0.12 + huggingface_hub + openai
# 2. 下载权重（约 17GB，需批准）
HF_HOME=/scratch4/kding1/huggingface/hf-home \
  /scratch4/kding1/envs/trace/bin/hf download xlangai/OpenCUA-7B
# 3. 起服务（需批准）
sbatch serve_opencua.slurm
# 4. 笔记本 SSH 隧道 -L 8000:<GPU节点>:8000，客户端连 http://localhost:8000/v1
```

## 模型交互格式

- system prompt: "You are a GUI agent... perform a series of pyautogui actions"
- user: 截图（base64 image_url）+ 任务文本；temperature=0
- 输出：`pyautogui.click(x=…, y=…)` 式动作（绝对坐标，smart-resize 后）

## 试用客户端（待写）

笔记本端小循环：截屏 → 发给模型 → 解析 pyautogui 动作 → 确认后执行。基于官方 `vllm_inference.py` 改造。
