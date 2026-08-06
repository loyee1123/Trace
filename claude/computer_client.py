"""方案C: Claude API (computer use 工具) 控制本机 GUI。

需要: pip install anthropic pyautogui pillow
     环境变量 ANTHROPIC_API_KEY (在 platform.claude.com 充值获取, 与订阅无关)

用法: python computer_client.py "打开浏览器搜索今天的天气"
退出: Ctrl+C, 或把鼠标猛甩到屏幕左上角
"""
import argparse
import base64
import io
import sys
import time

if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

import pyautogui
from PIL import ImageGrab
from anthropic import Anthropic

MODEL = "claude-opus-5"
MAX_STEPS = 40
MAX_IMAGES = 3      # 历史里只保留最近 N 张截图, 控制 token
MAX_LONG_EDGE = 1366  # 发给模型的截图长边; 模型坐标基于这个尺寸

pyautogui.FAILSAFE = True

PHYS_W, PHYS_H = ImageGrab.grab().size
SCALE = max(1.0, max(PHYS_W, PHYS_H) / MAX_LONG_EDGE)
DISP_W, DISP_H = round(PHYS_W / SCALE), round(PHYS_H / SCALE)

SYSTEM = (
    "You are controlling the user's real Windows desktop. Be careful and "
    "efficient. After each action, take a screenshot to verify the result "
    "before proceeding. To open an app, prefer pressing the win key, typing "
    "the app name, then enter. If the screen shows a login, payment, or "
    "permission dialog, stop and report to the user instead of acting."
)


def real_xy(coord):
    return round(coord[0] * SCALE), round(coord[1] * SCALE)


def robust_click(x, y, button="left", clicks=1):
    pyautogui.moveTo(x, y)
    time.sleep(0.1)
    for i in range(clicks):
        pyautogui.mouseDown(button=button)
        time.sleep(0.06)
        pyautogui.mouseUp(button=button)
        if i < clicks - 1:
            time.sleep(0.1)


def take_screenshot():
    img = ImageGrab.grab()
    if SCALE > 1:
        img = img.resize((DISP_W, DISP_H))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def type_text(text):
    if text.isascii():
        pyautogui.typewrite(text, interval=0.02)
    else:  # 中文走剪贴板
        import subprocess
        subprocess.run("clip", input=text.encode("utf-16-le"), check=True)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")


def run_action(inp):
    """执行一个 computer_20251124 动作, 返回 tool_result 的 content."""
    action = inp["action"]
    print(f"  -> {action} {({k: v for k, v in inp.items() if k != 'action'})}")

    if action == "screenshot":
        pass  # 最后统一截图返回
    elif action in ("left_click", "right_click", "middle_click",
                    "double_click", "triple_click"):
        x, y = real_xy(inp["coordinate"])
        button = {"right_click": "right", "middle_click": "middle"}.get(action, "left")
        clicks = {"double_click": 2, "triple_click": 3}.get(action, 1)
        if inp.get("text"):  # 按住修饰键点击
            for k in inp["text"].split("+"):
                pyautogui.keyDown(k)
            robust_click(x, y, button, clicks)
            for k in reversed(inp["text"].split("+")):
                pyautogui.keyUp(k)
        else:
            robust_click(x, y, button, clicks)
    elif action == "mouse_move":
        pyautogui.moveTo(*real_xy(inp["coordinate"]))
    elif action == "left_click_drag":
        x1, y1 = real_xy(inp["start_coordinate"])
        x2, y2 = real_xy(inp["coordinate"])
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        time.sleep(0.1)
        pyautogui.moveTo(x2, y2, duration=0.5)
        pyautogui.mouseUp()
    elif action in ("left_mouse_down", "left_mouse_up"):
        if inp.get("coordinate"):
            pyautogui.moveTo(*real_xy(inp["coordinate"]))
        (pyautogui.mouseDown if action == "left_mouse_down" else pyautogui.mouseUp)()
    elif action == "type":
        type_text(inp["text"])
    elif action == "key":
        pyautogui.hotkey(*inp["text"].lower().replace("super", "win").split("+"))
    elif action == "hold_key":
        pyautogui.keyDown(inp["text"])
        time.sleep(inp.get("duration", 1))
        pyautogui.keyUp(inp["text"])
    elif action == "scroll":
        if inp.get("coordinate"):
            pyautogui.moveTo(*real_xy(inp["coordinate"]))
        n = inp.get("scroll_amount", 3) * 120
        pyautogui.scroll(n if inp["scroll_direction"] == "up" else -n)
    elif action == "wait":
        time.sleep(inp.get("duration", 1))
    else:
        return [{"type": "text", "text": f"Unsupported action: {action}"}]

    time.sleep(0.8)  # 等界面响应
    return [{"type": "image", "source": {
        "type": "base64", "media_type": "image/png", "data": take_screenshot()}}]


def prune_images(messages):
    """只保留最近 MAX_IMAGES 张截图, 旧的换成文字占位, 控制 token 消耗."""
    seen = 0
    for msg in reversed(messages):
        if not isinstance(msg.get("content"), list):
            continue
        for block in msg["content"]:
            if isinstance(block, dict) and block.get("type") == "tool_result":
                content = block.get("content") or []
                if any(isinstance(c, dict) and c.get("type") == "image" for c in content):
                    seen += 1
                    if seen > MAX_IMAGES:
                        block["content"] = [{"type": "text",
                                             "text": "(screenshot omitted to save space)"}]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task", help="任务描述")
    args = ap.parse_args()

    client = Anthropic()
    tools = [{"type": "computer_20251124", "name": "computer",
              "display_width_px": DISP_W, "display_height_px": DISP_H}]
    messages = [{"role": "user", "content": args.task}]
    print(f"屏幕 {PHYS_W}x{PHYS_H} -> 模型视图 {DISP_W}x{DISP_H} (scale={SCALE:.3f})")

    for step in range(1, MAX_STEPS + 1):
        prune_images(messages)
        response = client.beta.messages.create(
            model=MODEL, max_tokens=4096,
            betas=["computer-use-2025-11-24"],
            system=SYSTEM, tools=tools, messages=messages,
        )

        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n[Claude] {block.text}")

        if response.stop_reason == "refusal":
            print("\n[✗] 请求被安全分类器拒绝。")
            return
        if response.stop_reason != "tool_use":
            print(f"\n[✓] 完成 (共 {step} 步)。")
            return

        tool_results = []
        for block in response.content:
            if block.type == "tool_use" and block.name == "computer":
                tool_results.append({
                    "type": "tool_result", "tool_use_id": block.id,
                    "content": run_action(block.input),
                })
        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

    print(f"\n[!] 达到 {MAX_STEPS} 步上限, 停止。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[✗] 已退出 (Ctrl+C)。")
    except pyautogui.FailSafeException:
        print("\n[✗] 已紧急停止 (鼠标甩到屏幕左上角)。")
