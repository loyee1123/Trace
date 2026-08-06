"""执行一个 GUI 动作。坐标一律用 screen.png 上的像素坐标, 本脚本自动换算到真实屏幕。

用法:
  python tools/act.py click X Y            # 单击
  python tools/act.py doubleclick X Y      # 双击
  python tools/act.py rightclick X Y       # 右键
  python tools/act.py move X Y             # 移动光标
  python tools/act.py drag X1 Y1 X2 Y2     # 拖拽
  python tools/act.py type "文本"          # 输入文本(先点好输入框)
  python tools/act.py key ctrl+s           # 快捷键(pyautogui 键名, + 分隔)
  python tools/act.py scroll up|down [格数] # 滚动(默认3格)
  python tools/act.py wait [秒]            # 等待(默认1秒)
"""
import json
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

import pyautogui

pyautogui.FAILSAFE = True
HERE = Path(__file__).parent


def real_xy(x, y):
    """screen.png 像素坐标 -> 物理屏幕坐标"""
    meta_file = HERE / "screen_meta.json"
    scale = json.loads(meta_file.read_text())["scale"] if meta_file.exists() else 1.0
    return round(float(x) * scale), round(float(y) * scale)


def robust_click(x, y, button="left", clicks=1):
    """部分 Windows 应用不认瞬时 down/up, 点击要有间隔才生效"""
    pyautogui.moveTo(x, y)
    time.sleep(0.1)
    for i in range(clicks):
        pyautogui.mouseDown(button=button)
        time.sleep(0.06)
        pyautogui.mouseUp(button=button)
        if i < clicks - 1:
            time.sleep(0.1)


def main():
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == "click":
        robust_click(*real_xy(args[0], args[1]))
    elif cmd == "doubleclick":
        robust_click(*real_xy(args[0], args[1]), clicks=2)
    elif cmd == "rightclick":
        robust_click(*real_xy(args[0], args[1]), button="right")
    elif cmd == "move":
        pyautogui.moveTo(*real_xy(args[0], args[1]))
    elif cmd == "drag":
        x1, y1 = real_xy(args[0], args[1])
        x2, y2 = real_xy(args[2], args[3])
        pyautogui.moveTo(x1, y1)
        pyautogui.mouseDown()
        time.sleep(0.1)
        pyautogui.moveTo(x2, y2, duration=0.5)
        pyautogui.mouseUp()
    elif cmd == "type":
        # typewrite 打不了中文, 用剪贴板粘贴
        text = args[0]
        if text.isascii():
            pyautogui.typewrite(text, interval=0.02)
        else:
            import subprocess
            if sys.platform == "win32":
                subprocess.run("clip", input=text.encode("utf-16-le"), check=True)
            else:
                subprocess.run("pbcopy", input=text.encode(), check=True)
            time.sleep(0.2)
            pyautogui.hotkey("ctrl" if sys.platform == "win32" else "command", "v")
    elif cmd == "key":
        pyautogui.hotkey(*args[0].lower().split("+"))
    elif cmd == "scroll":
        n = int(args[1]) if len(args) > 1 else 3
        pyautogui.scroll(n * 120 if args[0] == "up" else -n * 120)
    elif cmd == "wait":
        time.sleep(float(args[0]) if args else 1.0)
    else:
        print(f"未知命令: {cmd}", file=sys.stderr)
        sys.exit(1)
    time.sleep(0.3)
    print("done")


if __name__ == "__main__":
    main()
