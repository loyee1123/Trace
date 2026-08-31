# Qwen3.8-27B 本地 computer-use 方案

OSWorld-Verified 84.3%（开源第一梯队，与 Claude 差 1 分）。跑在集群 ica100（A100 80GB）2 卡上，笔记本经 SSH 隧道控制。

## 集群侧

```bash
sbatch qwen/serve_qwen38.slurm          # 2×A100, TP=2, 2 小时
tail -f qwen/logs/vllm-<jobid>.log       # 出现 "Application startup complete" 即就绪
```

环境用现有 `trace`（vllm 0.19.1 已含 Qwen3_5 架构；Qwen3.8 与 Qwen3.5 同架构）。

## 笔记本侧

```bash
ssh -L 8000:<gpu节点>:8000 <登录节点>      # 隧道
pip install openai pyautogui pillow
cd Trace\qwen
python qwen_client.py "打开浏览器搜索今天的天气"          # 连续执行
python qwen_client.py "..." --think                       # 开 thinking, 更准更慢
python qwen_client.py "..." --confirm                     # 每步回车确认
```

`qwen_client.py` 是 OSWorld 官方 `mm_agents/qwen`（跑榜 harness）的 Windows 移植：
同一套系统提示、`computer_use` 函数定义、XML `<tool_call>` 解析、相对坐标（1000×1000）、
smart_resize(factor=32, max_pixels≈3.3M)、旧截图折叠。加了 DPI 适配、稳健点击、中文输入走剪贴板、防死循环。

## 演示学习（先示范，再让它照做）

```bash
pip install pynput                                     # 一次性
python record_demo.py download_ct                      # 开录: 亲手做一遍任务, 按 F10 结束
python qwen_client.py "choose the test patient with prostate cancer and download the ct niigz" --demo demos/download_ct --think
```

录制器记录你的点击/输入/快捷键/滚动（含每步前截图），存到 `demos/<名字>/`；
`--demo` 会把演示转成步骤清单注入提示词，模型照着流程执行、允许对界面小变化做适配。
