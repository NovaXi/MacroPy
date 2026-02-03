import subprocess
import os
import time
import logging
from dotenv import load_dotenv
import tkinter as tk
from tkinter import ttk
import json

load_dotenv()

logger = logging.getLogger("macropy")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("MacroPy__Logs.txt")
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)

logging.basicConfig(
    filemode='a',
    format='%(asctime)s,%(msecs)03d %(name)s %(levelname)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

PLAYING_AUDIO_PATH = os.getenv("PLAYING_AUDIO_PATH")
ERROR_AUDIO_PATH = os.getenv("ERROR_AUDIO_PATH")
ABBREVIATIONS_JSON_PATH = os.getenv("ABBREVIATIONS_JSON_PATH")
with open(ABBREVIATIONS_JSON_PATH, "r", encoding="utf-8") as f:
    ABBREVIATIONS = json.load(f)


MAX_ABBR_LENGTH = max(len(k) for k in ABBREVIATIONS)


def show_trigger_gui():
    root = tk.Tk()
    root.title("Trigger List")
    root.geometry("700x500")
    root.attributes("-topmost", True)

    frame = ttk.Frame(root, padding=10)
    frame.pack(fill="both", expand=True)

    scrollbar = ttk.Scrollbar(frame)
    scrollbar.pack(side="right", fill="y")

    text = tk.Text(
        frame,
        wrap="word",
        yscrollcommand=scrollbar.set,
        font=("Monospace", 10)
    )
    text.pack(fill="both", expand=True)

    scrollbar.config(command=text.yview)

    for k, v in ABBREVIATIONS.items():
        if k != "TRIGGERLIST":
            text.insert("end", f"{k}\n{v}\n{'-'*len(v)}\n\n")

    text.config(state="disabled")

    root.mainloop()

def play_sound(audioPath: str):
    subprocess.run(["paplay", audioPath])
    logger.info("Playing Sound.")

def delete_shift_block():
    env = {"YDOTOOL_SOCKET": os.path.expanduser("~/.ydotool_socket")}
    subprocess.run(
        ["ydotool", "key", "42:1", "29:1", "105:1", "14:1", "42:0", "29:0", "105:0", "14:0"],
        env=env,
        check=True
    )

def backspace_once():
    env = {"YDOTOOL_SOCKET": os.path.expanduser("~/.ydotool_socket")}
    subprocess.run(
        ["ydotool", "key", "42:1", "105:1", "46:1", "42:0", "105:0", "46:0"],
        env=env,
        check=True
    )
    subprocess.run(["ydotool", "key", "106:1", "106:0"], env=env)
    subprocess.run(["ydotool", "key", "14:1", "14:0"], env=env)

def paste(text):
    subprocess.run(["wl-copy"], input=text.encode())
    time.sleep(0.1)
    env = {"YDOTOOL_SOCKET": os.path.expanduser("~/.ydotool_socket")}
    subprocess.run(["ydotool", "key", "29:1", "47:1", "29:0", "47:0"], env=env) # LEFTCTRL + V

def release_all_keys():
    time.sleep(0.1)
    env = {"YDOTOOL_SOCKET": os.path.expanduser("~/.ydotool_socket")}
    subprocess.run(["ydotool", "key", "29:0", "47:0", "42:0", "105:0", "14:0", "46:0", "106:0", ], env=env) 

def get_last_text():
    logger.debug("Running get_last_text (select-copy-delete method)")
    env = {"YDOTOOL_SOCKET": os.path.expanduser("~/.ydotool_socket")}

    deleted = ""

    subprocess.run(
        ["ydotool", "key", "42:1", "29:1", "105:1", "42:0", "29:0", "105:0"], # LEFTSHIFT + LEFTCTRL + ARROWLEFT
        env=env,
        check=True
    )
    time.sleep(0.02)
    subprocess.run(
        ["ydotool", "key", "29:1", "46:1" "29:0", "46:0"], # LEFTCTRL + C
        env=env,
        check=True
    )
    time.sleep(0.02)

    cp = subprocess.run(
        ["timeout", "0.1", "wl-paste", "--primary"],
        capture_output=True,
        text=True
    )
    time.sleep(0.02)

    char = cp.stdout if (cp.returncode == 0 and cp.stdout) else ""
    if char:
        char = char.replace("\n", "")
    else:
        char = ""

    deleted = (char + deleted) if char else deleted

    logger.debug(f"Iteration : copied={char!r} deleted_so_far={deleted!r}")

    logger.debug(f"get_last_text returning: {char!r}")
    return char

def build_trigger_list():
    lines = []
    for k, v in ABBREVIATIONS.items():
        lines.append(f"{k} → {v}")
    return "\n".join(lines)


def main():
    logger.debug("Main loop running")

    last_text = get_last_text()
    logger.debug(f"last_text extracted = {last_text!r}")

    found = False
    if last_text.upper().endswith("TRIGGERLIST"):
        logger.info("Matched abbreviation: TRIGGERLIST")
        found = True
        play_sound(PLAYING_AUDIO_PATH)
        release_all_keys()
        show_trigger_gui()
        play_sound(PLAYING_AUDIO_PATH)
    else:
        for abbr, expansion in ABBREVIATIONS.items():
            if last_text.upper().endswith(abbr):
                logger.info(f"Matched abbreviation: {abbr}")
                paste(expansion)
                found = True
                play_sound(PLAYING_AUDIO_PATH)
                break
    
    release_all_keys()

    if not found:
        play_sound(ERROR_AUDIO_PATH)

if __name__ == "__main__":
    logger.info("✅ Service is ready.")
    logger.info("💡 Remember! Start ydotool using the following command WITHOUT sudo:")
    logger.info("ydotoold --socket-path=\"$HOME/.ydotool_socket\"")
    logger.info("-----------")
    time.sleep(0.02)
    main()
