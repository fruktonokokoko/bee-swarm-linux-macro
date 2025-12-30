import time
import subprocess
import os
import cv2
import numpy as np
from screeninfo import get_monitors

KEYS = {
    # Letters
    "a": 30, "b": 48, "c": 46, "d": 32, "e": 18, "f": 33, "g": 34,
    "h": 35, "i": 23, "j": 36, "k": 37, "l": 38, "m": 50, "n": 49,
    "o": 24, "p": 25, "q": 16, "r": 19, "s": 31, "t": 20, "u": 22,
    "v": 47, "w": 17, "x": 45, "y": 21, "z": 44,

    # Numbers
    "0": 11, "1": 2, "2": 3, "3": 4, "4": 5, "5": 6,
    "6": 7, "7": 8, "8": 9, "9": 10,

    # Arrow keys
    "up": 103, "down": 108, "left": 105, "right": 106,

    # Function keys
    "f1": 59, "f2": 60, "f3": 61, "f4": 62, "f5": 63, "f6": 64,
    "f7": 65, "f8": 66, "f9": 67, "f10": 68, "f11": 87, "f12": 88,

    # Modifier keys
    "shift": 42, "ctrl": 29, "alt": 56, "super": 125,

    # Special keys
    "space": 57, "enter": 28, "tab": 15, "backspace": 14, "esc": 1,
    "insert": 110, "delete": 111, "home": 102, "end": 107,
    "pageup": 104, "pagedown": 109,

    # Numpad
    "numpad_0": 82, "numpad_1": 79, "numpad_2": 80, "numpad_3": 81,
    "numpad_4": 75, "numpad_5": 76, "numpad_6": 77,
    "numpad_7": 71, "numpad_8": 72, "numpad_9": 73,
    "numpad_enter": 96, "numpad_plus": 78, "numpad_minus": 74,
    "numpad_dot": 83, "numpad_mul": 55, "numpad_div": 53,
}


REGION_W = 0
REGION_H = 0

for m in get_monitors():
    print(f"Monitor {m.name}: {m.width}{m.height}")
    REGION_W = m.width
    REGION_H = m.height

print(REGION_H)
print(REGION_W)

# Config
field = "pine"     # spider | pine | rose
key_delay = 0.2
movespeed = 32.2
# Template to wait for before stopping respawn
start_png_template = "/home/lukasz/linux-natro/assets/start_macro.png"

REGION_X = 0
REGION_Y = 0
THRESHOLD = 0.60  # similarity threshold

at_field = False

# Very complicated input machinery hahahaha
def press_key(k, t):
    subprocess.run(["/usr/bin/ydotool", "key", f"{k}:1"], env={"YDOTOOL_SOCKET": "/run/ydotoold.socket"})
    time.sleep(t)
    subprocess.run(["/usr/bin/ydotool", "key", f"{k}:0"], env={"YDOTOOL_SOCKET": "/run/ydotoold.socket"})

def respawn():
    press_key(KEYS["esc"], 0.1)
    press_key(KEYS["r"], 0.1)
    press_key(KEYS["enter"], 0.1)

def snake(length,wideness,t_before_corner):
    for i in range(t_before_corner):
        for rows in range(wideness):
            press_key(KEYS["w"],length)
            press_key(KEYS["a"],0.25)
            press_key(KEYS["s"],length)
            press_key(KEYS["a"],0.25)

            press_key(KEYS["w"],length)
            press_key(KEYS["d"],0.25)
            press_key(KEYS["s"],length)
            press_key(KEYS["d"],0.25)

def go_pine():
    press_key(KEYS["w"], 2)
    press_key(KEYS["d"], 7)
    press_key(KEYS["space"], 0.1)
    press_key(KEYS["d"], 1)
    press_key(KEYS["w"], 0.1)
    press_key(KEYS["d"], 0.5)
    press_key(KEYS["e"],0.1)
    time.sleep(0.8)
    press_key(KEYS["space"],0.1)
    press_key(KEYS["space"],0.1)
    press_key(KEYS["d"],3)
    press_key(KEYS["s"],3)
    press_key(KEYS["d"],4)
    press_key(KEYS["s"],3)
    press_key(KEYS["w"], 0.1)
    while True:
        snake(1,3,9)

# ===============================
# IMAGE MATCHING
# ===============================
def image_seen(template_path, x, y, w, h, threshold):
    if not os.path.exists(template_path):
        return False

    region_str = f"{x},{y} {w}x{h}"
    subprocess.run(["grim", "-g", region_str, "/tmp/screen_region.png"],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    screen = cv2.imread("/tmp/screen_region.png", 0)
    template = cv2.imread(template_path, 0)

    if screen is None or template is None:
        return False

    res = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, _ = cv2.minMaxLoc(res)
    return max_val >= threshold

def start_macro():
    print(f"[ Info ] Macroing {field}")
    time.sleep(1)
    # Keep respawning until at the hive
    while not image_seen(start_png_template, REGION_X, REGION_Y, REGION_W, REGION_H, THRESHOLD):
        print("[ Info ] Not spawned at hive yet")
        respawn()
        time.sleep(3)

    if field == "pine":
        go_pine()

start_macro()
