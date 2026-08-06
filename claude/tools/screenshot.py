"""截取当前屏幕 -> claude/tools/screen.png (缩放到长边<=1366省token)。

用法: python tools/screenshot.py
输出: screen.png + screen_meta.json(记录缩放比例, act.py 用它换算回真实坐标)
"""
import json
import sys
from pathlib import Path

# Windows 高分屏: 必须声明 DPI 感知, 否则截图与点击坐标错位
if sys.platform == "win32":
    import ctypes
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        ctypes.windll.user32.SetProcessDPIAware()

from PIL import ImageGrab

MAX_LONG_EDGE = 1366
HERE = Path(__file__).parent

img = ImageGrab.grab()
phys_w, phys_h = img.size

scale = max(img.size) / MAX_LONG_EDGE
if scale > 1:
    img = img.resize((round(phys_w / scale), round(phys_h / scale)))
else:
    scale = 1.0

img.save(HERE / "screen.png")
meta = {"scale": scale, "img_w": img.size[0], "img_h": img.size[1],
        "phys_w": phys_w, "phys_h": phys_h}
(HERE / "screen_meta.json").write_text(json.dumps(meta))
print(f"saved {HERE / 'screen.png'}  ({img.size[0]}x{img.size[1]}, "
      f"物理分辨率 {phys_w}x{phys_h}, scale={scale:.3f})")
