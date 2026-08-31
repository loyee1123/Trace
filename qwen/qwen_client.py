"""Qwen3.8-27B (vLLM, OpenAI 兼容接口) 控制本机 GUI —— OSWorld 官方 QwenAgent 的 Windows 移植版。

prompt / 工具定义 / 坐标约定 / 历史折叠 都照搬 OSWorld mm_agents/qwen (跑榜用的那套)。
需要: pip install openai pyautogui pillow
用法: python qwen_client.py "打开浏览器搜索今天的天气" [--think] [--confirm]
退出: Ctrl+C, 或把鼠标猛甩到屏幕左上角
"""
import argparse
import base64
import io
import json
import math
import re
import sys
import time
from datetime import datetime

if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

import pyautogui
from PIL import ImageGrab
from openai import OpenAI

BASE_URL = "http://localhost:8000/v1"   # SSH 隧道对端 = 集群 GPU 节点的 vLLM
MODEL = "qwen3.8-27b"
MAX_STEPS = 50
IMAGE_MAX = 3            # 历史里保留最近几张截图, 更早的折叠成文字
COLLAPSE_TEXT = "This screenshot has been collapsed."

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.3


# ---------- 图像: 与 OSWorld qwen harness 完全一致 (factor=32, max_pixels=16*16*4*12800) ----------
def smart_resize(height, width, factor=32, min_pixels=56 * 56, max_pixels=16 * 16 * 4 * 12800):
    h_bar = max(factor, round(height / factor) * factor)
    w_bar = max(factor, round(width / factor) * factor)
    if h_bar * w_bar > max_pixels:
        beta = math.sqrt((height * width) / max_pixels)
        h_bar = math.floor(height / beta / factor) * factor
        w_bar = math.floor(width / beta / factor) * factor
    elif h_bar * w_bar < min_pixels:
        beta = math.sqrt(min_pixels / (height * width))
        h_bar = math.ceil(height * beta / factor) * factor
        w_bar = math.ceil(width * beta / factor) * factor
    return h_bar, w_bar


def take_screenshot():
    """返回 (原始宽, 原始高, 处理后宽, 处理后高, base64)."""
    img = ImageGrab.grab()
    ow, oh = img.size
    rh, rw = smart_resize(oh, ow)
    img = img.resize((rw, rh))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return ow, oh, rw, rh, base64.b64encode(buf.getvalue()).decode()


# ---------- prompt: 照搬 mm_agents/qwen/prompts.py (coordinate_type=relative) ----------
ACTION_DESC = """
* `key`: Performs key down presses on the arguments passed in order, then performs key releases in reverse order.
* `type`: Type a string of text on the keyboard.
* `mouse_move`: Move the cursor to a specified (x, y) pixel coordinate on the screen.
* `left_click`: Click the left mouse button at a specified (x, y) pixel coordinate on the screen. Optional `text` parameter can specify modifier keys (e.g., "ctrl", "shift", "ctrl+shift") that will be held during the click.
* `left_click_drag`: Click and drag the cursor to a specified (x, y) coordinate.
* `right_click`: Click the right mouse button at a specified (x, y) pixel coordinate on the screen. Optional `text` parameter can specify modifier keys that will be held during the click.
* `middle_click`: Click the middle mouse button at a specified (x, y) pixel coordinate on the screen. Optional `text` parameter can specify modifier keys that will be held during the click.
* `double_click`: Double-click the left mouse button at a specified (x, y) pixel coordinate on the screen. Optional `text` parameter can specify modifier keys that will be held during the click.
* `triple_click`: Triple-click the left mouse button at a specified (x, y) pixel coordinate on the screen (simulated as double-click since it's the closest action). Optional `text` parameter can specify modifier keys that will be held during the click.
* `scroll`: Performs a scroll of the mouse scroll wheel. Optional `text` parameter can specify a modifier key (e.g., "shift", "ctrl") that will be held during scrolling.
* `hscroll`: Performs a horizontal scroll (mapped to regular scroll). Optional `text` parameter can specify a modifier key that will be held during scrolling.
* `wait`: Wait specified seconds for the change to happen.
* `terminate`: Terminate the current task and report its completion status.
* `answer`: Answer a question."""


def build_tools_def():
    desc = "\n".join([
        "Use a mouse and keyboard to interact with a computer, and take screenshots.",
        "* This is an interface to a Microsoft Windows 11 desktop GUI. You do not have access to a terminal.",
        "* Windows conventions: desktop icons need `double_click` to open; taskbar icons, Start menu entries, links and buttons need a single `left_click`. A reliable way to open any application: press the `win` key, type the application name, then press `enter`.",
        "* Some applications may take time to start or process actions, so you may need to wait and take successive screenshots to see the results of your actions.",
        "* The screen's resolution is 1000x1000.",
        "* Whenever you intend to move the cursor to click on an element like an icon, you should consult a screenshot to determine the coordinates of the element before moving the cursor.",
        "* If you tried clicking on a program or link but it failed to load, even after waiting, try adjusting your cursor position so that the tip of the cursor visually falls on the element that you want to click.",
        "* Make sure to click any buttons, links, icons, etc with the cursor tip in the center of the element. Don't click boxes on their edges unless asked.",
    ])
    return {"type": "function", "function": {
        "name": "computer_use", "description": desc,
        "parameters": {"type": "object", "required": ["action"], "properties": {
            "action": {"type": "string", "description": ACTION_DESC,
                       "enum": ["key", "type", "mouse_move", "left_click", "left_click_drag",
                                "right_click", "middle_click", "double_click", "triple_click",
                                "scroll", "hscroll", "wait", "terminate", "answer"]},
            "keys": {"type": "array", "description": "Required only by `action=key`."},
            "text": {"type": "string", "description": "Required by `action=type` and `action=answer`. Optional for click actions (left_click, right_click, middle_click, double_click, triple_click) to specify modifier keys (e.g., 'ctrl', 'shift', 'ctrl+shift'). Optional for scroll actions (scroll, hscroll) to specify a modifier key (e.g., 'shift', 'ctrl') to hold during scrolling."},
            "coordinate": {"type": "array", "description": "(x, y) coordinates."},
            "pixels": {"type": "number", "description": "Scroll amount."},
            "time": {"type": "number", "description": "Seconds to wait."},
            "status": {"type": "string", "description": "Task status for terminate.", "enum": ["success", "failure"]},
        }}}}


def build_system_prompt():
    return (
        "You are a multi-purpose intelligent assistant. Based on my requests, you can use tools to help me complete various tasks.\n\n"
        "# Tools\n\nYou have access to the following functions:\n\n<tools>\n"
        + json.dumps(build_tools_def()) + "\n</tools>\n\n"
        "If you choose to call a function ONLY reply in the following format with NO suffix:\n\n"
        "<tool_call>\n<function=example_function_name>\n<parameter=example_parameter_1>\nvalue_1\n</parameter>\n"
        "<parameter=example_parameter_2>\nThis is the value for the second parameter\nthat can span\nmultiple lines\n</parameter>\n"
        "</function>\n</tool_call>\n\n"
        "<IMPORTANT>\nReminder:\n"
        "- Function calls MUST follow the specified format: an inner <function=...></function> block must be nested within <tool_call></tool_call> XML tags\n"
        "- Required parameters MUST be specified\n"
        "- You may provide optional reasoning for your function call in natural language BEFORE the function call, but NOT after\n"
        "- If there is no function call available, answer the question like normal with your current knowledge and do not tell the user about function calls\n"
        f"- The current date is {datetime.today().strftime('%A, %B %d, %Y')}.\n"
        f"- Collapsed screenshots appear as text: {COLLAPSE_TEXT}\n"
        "</IMPORTANT>\n\n"
        "# Response format\n\nResponse format for every step:\n"
        "1) Action: a short imperative describing what to do in the UI.\n"
        "2) A single <tool_call>...</tool_call> block.\n\nRules:\n"
        "- Output exactly in the order: Action, <tool_call>.\n"
        "- Be brief: one sentence for Action.\n"
        "- Do not output anything else outside those parts.\n"
        "- If finishing, use action=terminate in the tool call."
    )


def _demo_steps(demo_dir):
    """demos/<name>/demo.jsonl -> 步骤清单文本 (坐标转 0-999 相对)."""
    lines = open(f"{demo_dir}/demo.jsonl", encoding="utf-8").read().strip().split("\n")
    meta = json.loads(lines[0])
    sw, sh = meta["screen_w"], meta["screen_h"]
    out = []
    for i, ln in enumerate(lines[1:], 1):
        s = json.loads(ln)
        if s["type"] == "click":
            rx, ry = round(s["x"] * 999 / sw), round(s["y"] * 999 / sh)
            n = {1: "left_click", 2: "double_click", 3: "triple_click"}.get(s["clicks"], "left_click")
            n = "right_click" if s["button"] == "right" else n
            out.append(f"{i}. {n} at ({rx}, {ry})")
        elif s["type"] == "type":
            out.append(f"{i}. type \"{s['text']}\"")
        elif s["type"] == "key":
            out.append(f"{i}. press key {'+'.join(s['keys'])}")
        elif s["type"] == "scroll":
            out.append(f"{i}. scroll {'up' if s['dy'] > 0 else 'down'}")
    return "\n".join(out)


def load_demo(demo_arg):
    """逗号分隔的多个演示目录 -> 合并的参考文本."""
    dirs = [d.strip() for d in demo_arg.split(",") if d.strip()]
    blocks = []
    for k, d in enumerate(dirs, 1):
        head = (f"Demonstration {k} of {len(dirs)}:" if len(dirs) > 1
                else "Demonstration steps (coordinates are on the same 1000x1000 grid):")
        blocks.append(head + "\n" + _demo_steps(d))
    intro = ("A human has previously demonstrated exactly this task on this same computer"
             + (" multiple times. All demonstrations follow the same underlying procedure; "
                "differences between them show where flexibility is allowed. Coordinates are "
                "on the same 1000x1000 grid." if len(dirs) > 1 else ". "))
    return (intro + "\n" + "\n\n".join(blocks)
            + "\nFollow the demonstrated procedure step by step. The current screen should look "
            "similar; verify each step's effect on the screenshot, re-locate the target element "
            "if it moved slightly, and only deviate from the demonstration when necessary.")


def build_instruction_prompt(instruction, actions, note="", demo=""):
    prev = "\n".join(f"Step {i + 1}: {a}" for i, a in enumerate(actions)) or "None"
    return ("\nPlease generate the next move according to the UI screenshot, instruction and previous actions.\n\n"
            f"Instruction: {instruction}\n\n" + (f"{demo}\n\n" if demo else "")
            + f"Previous actions:\n{prev}" + (f"\n\n{note}" if note else ""))


def wrap_tool_response(parts):
    return [{"type": "text", "text": "<tool_response>\n"}] + parts + [{"type": "text", "text": "\n</tool_response>"}]


def build_messages(instruction, screenshots, responses, actions, note="", demo=""):
    """照搬 history.py: 第一轮 = 截图+指令, 后续轮 = <tool_response>截图</tool_response>; 旧截图折叠成文字."""
    total = len(screenshots)
    collapsed_before = max(0, total - IMAGE_MAX)   # 前 k 步折叠
    msgs = [{"role": "system", "content": [{"type": "text", "text": build_system_prompt()}]}]
    instr = build_instruction_prompt(instruction, actions, note, demo)
    for step in range(1, total + 1):
        first = step == 1
        if step <= collapsed_before:
            content = [{"type": "text", "text": instr}] if first else wrap_tool_response([{"type": "text", "text": COLLAPSE_TEXT}])
        else:
            img = {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshots[step - 1]}"}}
            content = [img, {"type": "text", "text": instr}] if first else wrap_tool_response([img])
        msgs.append({"role": "user", "content": content})
        if step <= total - 1 and step - 1 < len(responses):
            msgs.append({"role": "assistant", "content": [{"type": "text", "text": responses[step - 1]}]})
    return msgs


# ---------- 解析: 照搬 parser.py ----------
def parse_tool_calls(text):
    calls = []
    for m in re.finditer(r"<tool_call>(.*?)</tool_call>", text, re.S):
        body = m.group(1)
        if not re.search(r"<function=([^>]+)>", body):
            continue
        params = {}
        for pm in re.finditer(r"<parameter=([^>]+)>\s*(.*?)\s*</parameter>", body, re.S):
            name, val = pm.group(1).strip(), pm.group(2)
            try:
                params[name] = json.loads(val)
            except Exception:
                params[name] = val
        calls.append(params)
    return calls


def extract_action_line(text):
    m = re.search(r"Action:\s*(.+)", text)
    return m.group(1).strip() if m else text.strip().split("\n")[0][:120]


def to_list(v):
    if isinstance(v, str):
        try:
            v = json.loads(v)
        except Exception:
            v = [x.strip() for x in v.strip("[]").split(",")]
    return v if isinstance(v, list) else [v]


# ---------- 执行 ----------
KEY_MAP = {"super": "win", "cmd": "win", "meta": "win", "control": "ctrl", "return": "enter",
           "escape": "esc", "page_down": "pagedown", "page_up": "pageup", "arrowup": "up",
           "arrowdown": "down", "arrowleft": "left", "arrowright": "right"}


def norm_key(k):
    k = str(k).strip().lower()
    return KEY_MAP.get(k, k)


def robust_click(x, y, button="left", clicks=1):
    pyautogui.moveTo(x, y)
    time.sleep(0.1)
    for i in range(clicks):
        pyautogui.mouseDown(button=button)
        time.sleep(0.06)
        pyautogui.mouseUp(button=button)
        if i < clicks - 1:
            time.sleep(0.1)


def type_text(text):
    if text.isascii():
        pyautogui.typewrite(text, interval=0.02)
    else:
        import subprocess
        subprocess.run("clip", input=text.encode("utf-16-le"), check=True)
        time.sleep(0.2)
        pyautogui.hotkey("ctrl", "v")


def execute(p, ow, oh):
    """执行一个 computer_use 调用. 返回 'terminate'/'answer'/None."""
    action = p.get("action")
    coord = p.get("coordinate")
    if coord is not None:
        cx, cy = to_list(coord)[:2]
        x, y = int(float(cx) * ow / 999), int(float(cy) * oh / 999)   # relative 1000x1000 -> 真实像素
    mods = [norm_key(k) for k in str(p.get("text") or "").split("+") if k.strip()] \
        if action in ("left_click", "right_click", "middle_click", "double_click", "triple_click", "scroll", "hscroll") else []

    for k in mods:
        pyautogui.keyDown(k)
    try:
        if action in ("left_click", "right_click", "middle_click", "double_click", "triple_click"):
            btn = {"right_click": "right", "middle_click": "middle"}.get(action, "left")
            n = {"double_click": 2, "triple_click": 3}.get(action, 1)
            if coord is not None:
                robust_click(x, y, btn, n)
            else:
                robust_click(*pyautogui.position(), btn, n)
        elif action == "mouse_move":
            pyautogui.moveTo(x, y)
        elif action == "left_click_drag":
            pyautogui.mouseDown(); time.sleep(0.1)
            pyautogui.moveTo(x, y, duration=0.5)
            pyautogui.mouseUp()
        elif action == "type":
            type_text(str(p.get("text", "")))
        elif action == "key":
            keys = [norm_key(k) for k in to_list(p.get("keys", []))]
            if len(keys) > 1:
                pyautogui.hotkey(*keys)
            elif keys:
                pyautogui.press(keys[0])
        elif action in ("scroll", "hscroll"):
            if coord is not None:
                pyautogui.moveTo(x, y)
            px = int(float(p.get("pixels", 0) or 0))
            (pyautogui.hscroll if action == "hscroll" else pyautogui.scroll)(px)
        elif action == "wait":
            time.sleep(float(p.get("time", 1) or 1))
        elif action == "terminate":
            return "terminate"
        elif action == "answer":
            print(f"\n[答复] {p.get('text', '')}")
            return "answer"
        else:
            print(f"  [!] 未知动作 {action}")
    finally:
        for k in reversed(mods):
            pyautogui.keyUp(k)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task")
    ap.add_argument("--think", action="store_true", help="开启模型 thinking(更准但更慢)")
    ap.add_argument("--confirm", action="store_true", help="每步回车确认")
    ap.add_argument("--demo", default="", help="演示目录, 多个用逗号分隔: demos/a,demos/b")
    args = ap.parse_args()

    client = OpenAI(base_url=BASE_URL, api_key="EMPTY")
    demo_text = load_demo(args.demo) if args.demo else ""
    if demo_text:
        print(f"[演示模式] 已加载 {args.demo}")
    screenshots, responses, actions = [], [], []
    last_key, repeat = None, 0

    for step in range(1, MAX_STEPS + 1):
        ow, oh, rw, rh, b64 = take_screenshot()
        screenshots.append(b64)
        note, temp = "", 0
        if repeat >= 1:
            note = ("Note: your previous action was executed but the screen did not change as "
                    "expected. Do NOT repeat the same action. Try a different approach: e.g. "
                    "double_click instead of left_click, a different element or position, or a "
                    "keyboard shortcut.")
            temp = 0.6
        msgs = build_messages(args.task, screenshots, responses, actions, note, demo_text)
        print(f"\n===== Step {step}: 请求模型 (截图 {ow}x{oh} -> {rw}x{rh}) =====")
        resp = client.chat.completions.create(
            model=MODEL, messages=msgs, temperature=temp, max_tokens=8192 if args.think else 2048,
            extra_body={"chat_template_kwargs": {"enable_thinking": bool(args.think)}},
        )
        reply = resp.choices[0].message.content or ""
        responses.append(reply)
        print(reply)

        calls = parse_tool_calls(reply)
        actions.append(extract_action_line(reply))
        if not calls:
            print("[✓] 模型给出最终答复, 结束。")
            break

        key = json.dumps(calls, sort_keys=True)
        if key == last_key:
            repeat += 1
            if repeat >= 3:
                print("[!] 同一动作连续 4 次, 疑似死循环, 停止。")
                break
        else:
            last_key, repeat = key, 0

        done = None
        for p in calls:
            if args.confirm:
                ans = input(f"  -> {p}   [回车=执行 / s=跳过 / q=退出] ")
                if ans.strip().lower() == "q":
                    return
                if ans.strip().lower() == "s":
                    continue
            else:
                print(f"  -> 执行: {p}")
            done = execute(p, ow, oh)
            if done:
                break
        if done == "terminate":
            print(f"[✓] 模型判定任务结束 (status={calls[-1].get('status')})。")
            break
        if done == "answer":
            break
        time.sleep(1.5)
    else:
        print(f"[!] 达到 {MAX_STEPS} 步上限。")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[✗] 已退出 (Ctrl+C)。")
    except pyautogui.FailSafeException:
        print("\n[✗] 已紧急停止 (鼠标甩到屏幕左上角)。")
