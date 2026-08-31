"""录制你的一次人工演示: 鼠标点击/输入/快捷键/滚动 + 每步之前的截图。

用法:  python record_demo.py 任务名
停止:  按 F10
输出:  demos/任务名/demo.jsonl + step_*.png
需要:  pip install pynput pillow
"""
import json
import sys
import threading
import time
from pathlib import Path

if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

from PIL import ImageGrab
from pynput import keyboard, mouse

OUT = Path(__file__).parent / "demos" / (sys.argv[1] if len(sys.argv) > 1 else "demo")
OUT.mkdir(parents=True, exist_ok=True)

steps = []
text_buf = []
mods = set()
last_click = {"t": 0, "x": 0, "y": 0, "idx": -1}
_shot = {"img": None}
_stop = threading.Event()
SCREEN_W, SCREEN_H = ImageGrab.grab().size

MOD_KEYS = {keyboard.Key.ctrl_l: "ctrl", keyboard.Key.ctrl_r: "ctrl",
            keyboard.Key.alt_l: "alt", keyboard.Key.alt_r: "alt",
            keyboard.Key.shift: "shift", keyboard.Key.shift_r: "shift",
            keyboard.Key.cmd: "win"}
NAMED = {keyboard.Key.enter: "enter", keyboard.Key.tab: "tab", keyboard.Key.esc: "esc",
         keyboard.Key.backspace: "backspace", keyboard.Key.delete: "delete",
         keyboard.Key.up: "up", keyboard.Key.down: "down", keyboard.Key.left: "left",
         keyboard.Key.right: "right", keyboard.Key.home: "home", keyboard.Key.end: "end",
         keyboard.Key.page_up: "pageup", keyboard.Key.page_down: "pagedown",
         keyboard.Key.space: "space"}


def shooter():
    """后台每 0.5s 缓存一张截图, 点击时取的是'动作前'的画面."""
    while not _stop.is_set():
        try:
            _shot["img"] = ImageGrab.grab()
        except Exception:
            pass
        time.sleep(0.5)


def save_shot():
    img = _shot["img"] or ImageGrab.grab()
    name = f"step_{len(steps):03d}.png"
    img.save(OUT / name)
    return name


def flush_text():
    if text_buf:
        steps.append({"type": "type", "text": "".join(text_buf)})
        text_buf.clear()
        print(f"  [{len(steps):02d}] type {steps[-1]['text']!r}")


def on_click(x, y, button, pressed):
    if not pressed:
        return
    flush_text()
    now = time.time()
    # 双击合并
    if (now - last_click["t"] < 0.45 and abs(x - last_click["x"]) < 6
            and abs(y - last_click["y"]) < 6 and last_click["idx"] == len(steps) - 1
            and steps and steps[-1]["type"] == "click"):
        steps[-1]["clicks"] += 1
        print(f"  [{len(steps):02d}] -> double/triple click")
    else:
        steps.append({"type": "click", "x": x, "y": y, "button": button.name,
                      "clicks": 1, "screenshot": save_shot()})
        print(f"  [{len(steps):02d}] {button.name}_click ({x},{y})")
    last_click.update(t=now, x=x, y=y, idx=len(steps) - 1)


def on_scroll(x, y, dx, dy):
    flush_text()
    if steps and steps[-1]["type"] == "scroll" and (dy > 0) == (steps[-1]["dy"] > 0):
        steps[-1]["dy"] += dy
    else:
        steps.append({"type": "scroll", "x": x, "y": y, "dy": dy, "screenshot": save_shot()})
        print(f"  [{len(steps):02d}] scroll {dy}")


def on_press(key):
    if key == keyboard.Key.f10:
        flush_text()
        _stop.set()
        return False
    if key in MOD_KEYS:
        mods.add(MOD_KEYS[key])
        return
    if hasattr(key, "char") and key.char and not (mods - {"shift"}):
        text_buf.append(key.char)
        return
    name = NAMED.get(key, getattr(key, "char", None) or str(key).replace("Key.", ""))
    combo = sorted(mods - {"shift"}) if name not in NAMED else sorted(mods)
    if name == "backspace" and text_buf and not combo:
        text_buf.pop()
        return
    flush_text()
    keys = (combo if name not in [c for c in combo] else []) + [name] if combo else [name]
    steps.append({"type": "key", "keys": keys, "screenshot": save_shot()})
    print(f"  [{len(steps):02d}] key {'+'.join(keys)}")


def on_release(key):
    if key in MOD_KEYS:
        mods.discard(MOD_KEYS[key])


print(f"开始录制到 {OUT}/ ,屏幕 {SCREEN_W}x{SCREEN_H}。做你的演示吧,按 F10 结束。")
threading.Thread(target=shooter, daemon=True).start()
ml = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
ml.start()
with keyboard.Listener(on_press=on_press, on_release=on_release) as kl:
    kl.join()
ml.stop()

(OUT / "demo.jsonl").write_text(
    json.dumps({"screen_w": SCREEN_W, "screen_h": SCREEN_H}) + "\n"
    + "\n".join(json.dumps(s, ensure_ascii=False) for s in steps), encoding="utf-8")
print(f"\n录制完成: {len(steps)} 步 -> {OUT / 'demo.jsonl'}")
