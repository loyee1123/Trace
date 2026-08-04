#!/usr/bin/env python3
"""OpenCUA-7B 试用客户端 —— 在你自己的电脑上运行（不是集群）。

准备:
  pip install openai pyautogui pillow
  ssh -L 8000:<GPU节点>:8000 <你的集群登录节点>   # 保持这个隧道开着

用法:
  python demo_client.py "Open the browser and search for weather"
  （任务用英文写，训练数据以英文指令为主，效果更稳）

安全机制:
  - 每一步动作先打印出来，你按回车确认后才真正执行；s 跳过，q 退出
  - pyautogui 自带 failsafe：鼠标甩到屏幕左上角可紧急中断
  - macOS 首次运行需在 系统设置->隐私与安全 给终端授予"屏幕录制"和"辅助功能"权限
"""

import argparse
import base64
import io
import math
import re
import sys
import time

# Windows 高分屏: 必须在导入 pyautogui 前声明 DPI 感知，
# 否则截图是物理像素而点击坐标是逻辑像素，两者错位
if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

import pyautogui
from openai import OpenAI

BASE_URL = "http://localhost:8000/v1"   # SSH 隧道对端 = 集群 GPU 节点的 vLLM
MODEL = "opencua-7b"
MAX_STEPS = 15
MAX_IMAGES = 3   # 官方 OpenCUAAgent 默认: 只保留最近 3 张截图作为历史

SYSTEM_PROMPT = (
    "You are a GUI agent. You are given a task and a screenshot of the screen. "
    "You need to perform a series of pyautogui actions to complete the task."
)

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

# 部分 Windows 应用不认 pyautogui 默认的瞬时 down/up，点击要有间隔才生效
_raw_move = pyautogui.moveTo
_raw_down = pyautogui.mouseDown
_raw_up = pyautogui.mouseUp

def _robust_click(x=None, y=None, clicks=1, interval=0.1, button="left", **kw):
    if x is not None and y is not None:
        _raw_move(x, y)
        time.sleep(0.1)
    for i in range(int(clicks)):
        _raw_down(button=button)
        time.sleep(0.06)
        _raw_up(button=button)
        if i < clicks - 1:
            time.sleep(interval)

pyautogui.click = _robust_click
pyautogui.doubleClick = lambda x=None, y=None, **kw: _robust_click(x, y, clicks=2)
pyautogui.rightClick = lambda x=None, y=None, **kw: _robust_click(x, y, button="right")


def smart_resize(height, width, factor=28, min_pixels=3136, max_pixels=12845056):
    """Qwen2.5-VL 官方预处理: 模型输出的坐标基于 resize 后的这个尺寸。"""
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
    img = pyautogui.screenshot()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return img.size, base64.b64encode(buf.getvalue()).decode()


def model_xy_to_screen(mx, my, img_w, img_h):
    """模型坐标(smart-resize 图上) -> 相对坐标 -> pyautogui 逻辑屏幕坐标。

    经 pyautogui.size() 换算兼容 Retina 等截图分辨率 != 逻辑分辨率的情况。
    """
    rh, rw = smart_resize(img_h, img_w)
    scr_w, scr_h = pyautogui.size()
    return int(mx / rw * scr_w), int(my / rh * scr_h)


def extract_actions(text):
    """从模型输出提取动作行(CoT 之后通常是 ```python 代码块)。"""
    blocks = re.findall(r"```(?:python)?\s*(.*?)```", text, re.S)
    code = "\n".join(blocks) if blocks else text
    lines = [ln.strip() for ln in code.splitlines()]
    return [ln for ln in lines
            if ln.startswith(("pyautogui.", "time.sleep", "terminate"))]


def rescale_coords(line, img_w, img_h):
    xm = re.search(r"x=(\d+(?:\.\d+)?)", line)
    ym = re.search(r"y=(\d+(?:\.\d+)?)", line)
    if xm and ym:
        nx, ny = model_xy_to_screen(float(xm.group(1)), float(ym.group(1)),
                                    img_w, img_h)
        line = re.sub(r"x=\d+(?:\.\d+)?", f"x={nx}", line, count=1)
        line = re.sub(r"y=\d+(?:\.\d+)?", f"y={ny}", line, count=1)
    return line


def build_messages(task, history):
    """system + 历史步骤(仅最近 MAX_IMAGES 步带截图) + 当前截图。"""
    msgs = [{"role": "system", "content": SYSTEM_PROMPT}]
    n = len(history)
    for i, step in enumerate(history):
        if i >= n - (MAX_IMAGES - 1):
            user_content = [
                {"type": "image_url",
                 "image_url": {"url": f"data:image/png;base64,{step['b64']}"}},
                {"type": "text", "text": step["text"]},
            ]
        else:
            user_content = [{"type": "text", "text": step["text"]}]
        msgs.append({"role": "user", "content": user_content})
        msgs.append({"role": "assistant", "content": step["reply"]})
    (img_w, img_h), b64 = take_screenshot()
    prompt = (f"Task: {task}" if not history
              else f"Task: {task}\nPlease continue with the next action.")
    msgs.append({"role": "user", "content": [
        {"type": "image_url",
         "image_url": {"url": f"data:image/png;base64,{b64}"}},
        {"type": "text", "text": prompt},
    ]})
    return msgs, (img_w, img_h), b64, prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task", help="任务描述(英文)")
    ap.add_argument("--confirm", action="store_true", help="每步回车确认(默认连续执行)")
    args = ap.parse_args()

    client = OpenAI(base_url=BASE_URL, api_key="EMPTY")
    history = []

    for step_no in range(1, MAX_STEPS + 1):
        msgs, (img_w, img_h), b64, prompt = build_messages(args.task, history)
        print(f"\n===== Step {step_no}: 请求模型... =====")
        reply = client.chat.completions.create(
            model=MODEL, messages=msgs, max_tokens=1024, temperature=0,
        ).choices[0].message.content
        print(reply)

        actions = extract_actions(reply)
        if not actions:
            print("[!] 未解析到动作，结束。")
            break
        if any("terminate" in a for a in actions):
            print("[✓] 模型判定任务结束。")
            break

        for act in actions:
            act = rescale_coords(act, img_w, img_h)
            if args.confirm:
                ans = input(f"  -> {act}   [回车=执行 / s=跳过 / q=退出] ")
                if ans.strip().lower() == "q":
                    return
                if ans.strip().lower() == "s":
                    continue
            else:
                print(f"  -> 执行: {act}")
            exec(act, {"pyautogui": pyautogui, "time": time})

        history.append({"b64": b64, "text": prompt, "reply": reply})
        time.sleep(1.0)  # 等界面响应后再截下一张


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[✗] 已退出 (Ctrl+C)。")
    except pyautogui.FailSafeException:
        print("\n[✗] 已紧急停止 (鼠标甩到屏幕左上角)。")
