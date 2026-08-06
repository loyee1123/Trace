# Claude 作为 GUI Agent 核心模型

两种方式，都在**你自己的电脑**上运行（不需要集群/GPU）。

## 方案 A：Claude Code（走订阅额度，零 API 费用）

前提：有 Claude Pro/Max 订阅。

```bash
# 1. 安装依赖 (一次性)
npm install -g @anthropic-ai/claude-code
pip install pyautogui pillow

# 2. 进入本目录, 启动 Claude Code 并登录订阅账号
cd Trace/claude
claude

# 3. 直接下任务
> 打开浏览器搜索今天的天气
```

Claude Code 会按 `CLAUDE.md` 里的工作循环干活：`tools/screenshot.py` 截屏 → 看图 → `tools/act.py` 执行动作 → 再截屏确认。

## 方案 C：Claude API（computer use 工具，按 token 计费）

前提：在 platform.claude.com 充值并拿到 API key（与订阅额度无关）。

```bash
pip install anthropic pyautogui pillow
set ANTHROPIC_API_KEY=sk-ant-...    # Windows; macOS/Linux 用 export

python computer_client.py "打开浏览器搜索今天的天气"
```

参考成本：截图约 1-2k token/张，一个十几步的任务约 $0.2–0.5（claude-opus-5）。

## 共同注意

- Windows 首次运行注意给终端"屏幕录制/辅助功能"类权限（macOS 必须）
- 紧急停止：Ctrl+C 或把鼠标猛甩到屏幕左上角
- 国内网络访问 Anthropic API/登录可能需要代理
