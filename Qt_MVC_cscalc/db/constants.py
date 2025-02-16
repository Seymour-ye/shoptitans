import requests
import markdown
import os
import re 
import sys
import time 
import subprocess

from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import QMessageBox

MAX_TIER = 14

SWITCHABLES = {
    #Tier: Stone, Sigil
    1: (False, False),
    2: (False, False),
    3: (False, False),
    4: (True, False),
    5: (False, False),
    6: (False, False),
    7: (True, False),
    8: (False, False),
    9: (True, False),
    10: (True, False),
    11: (False, True),
    12: (True, True),
    13: (False, True),
    14: (True, True)
}

QUALITIES = ['普通', '优质', '精良', '史诗', '传说']
STONE_COLOR = '#AAAAAA'
QUALITIY_COLORS = [ "#ffffff",  # 白色
                    "#00ff00",  # 绿色
                    "#4da6ff",  # 蓝色
                    "#a64ca6",  # 紫色
                    "#ffd700"  # 金色
]

LOG_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_MAXIMUM = 50
UPDATE_EXE_URL= "https://github.com/Seymour-ye/shoptitans/raw/refs/heads/main/Qt_MVC_cscalc/dist/序列计算器.exe"
GITHUB_UPDATES_FILE_URL = 'https://raw.githubusercontent.com/Seymour-ye/shoptitans/refs/heads/main/Qt_MVC_cscalc/UPDATES.md'
GITHUB_README_FILE_URL = 'https://raw.githubusercontent.com/Seymour-ye/shoptitans/refs/heads/main/Qt_MVC_cscalc/README.md'

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    else:
        return os.path.join(os.path.dirname(__file__), '..')
    
UI_PATH = os.path.join(get_base_path(),'ui', 'main_window.ui')
MARK_ICON = os.path.join(get_base_path(), 'ui', 'icon_global_timer_sp.png')
WINDOW_ICON = os.path.join(get_base_path(),'ui', 'minte.png')
UPDATES_PATH = os.path.join(get_base_path(), 'UPDATES.md')

def fetch_readme():
    response = requests.get(GITHUB_README_FILE_URL)
    if response.status_code == 200:
        content = response.text
        return f"""
    <style>
        body {{ color: white; word-wrap: break-word; overflow-wrap: break-word;}}
        a {{ color: #00FFFF; text-decoration: none; }}
        a:hover {{ color: #FFA500; text-decoration: underline; }}
    </style>
    {markdown.markdown(content)}
"""
    else:
        return "聪明的人才看得见我，看不见说明你傻。"

def fetch_updates():
    response = requests.get(GITHUB_UPDATES_FILE_URL)
    if response.status_code == 200:
        content = response.text
        return f"""
    <style>
        body {{ color: white; }}
        a {{ color: #00FFFF; text-decoration: none; }}
        a:hover {{ color: #FFA500; text-decoration: underline; }}
    </style>
    {markdown.markdown(content)}
"""
    else:
        return "不联网还想看更新，我快递过去给你？"

def unvisibles(tier, back_switch):
    if not SWITCHABLES[tier][0] and not back_switch : #not switchable
        return [0, -1, -1, -1, -1]
    elif not SWITCHABLES[tier][0] and back_switch: # sigil
        return [0, 4, 3, 2, 1]
    elif SWITCHABLES[tier][0] and not back_switch: # stone
        return [0, 1, 2, 3, 4]
    else: #both
        return [0, 1, 2, 2, 1]
    
def get_latest_version():
    response = requests.get(GITHUB_UPDATES_FILE_URL)
    if response.status_code == 200:
        content = response.text.split('\r\n')
        for line in content:
            match = re.search(r"V\d+\.\d+(?:\.\d+)?", line)  # Match version format V0.18
            if match:
                return match.group()

def get_current_version():
    filepath = UPDATES_PATH
    with open(filepath, "r", encoding="utf-8") as file:
        for line in file:
            match = re.search(r"V\d+\.\d+(?:\.\d+)?", line)  # Match version format V0.18
            if match:
                return match.group()
            
def download_updates():
    NEW_EXE_PATH = os.path.join(os.path.dirname(sys.executable), "_序列计算器.exe")
    CURRENT_EXE_PATH = sys.executable
    try:
        response = requests.get(UPDATE_EXE_URL, stream=True)
        with open(NEW_EXE_PATH, "wb") as f:
            for chunk in response.iter_content(1024):
                f.write(chunk)
        
        QMessageBox.information(None, "更新完成", "下载完成，程序将自动更新并重启。")

        update_script = f"""@echo off
            chcp 65001 >nul
            timeout /t 2 /nobreak >nul
            del "{CURRENT_EXE_PATH}"
            for /d %%i in ("%TEMP%\_MEI*") do rd /s /q "%%i"

            rename "{NEW_EXE_PATH}" "{os.path.basename(CURRENT_EXE_PATH)}"
            start "" cmd /c "{CURRENT_EXE_PATH}"
            del %0
            """
        update_script_path = os.path.join(os.path.dirname(CURRENT_EXE_PATH), "update.bat")

        with open(update_script_path, "w", encoding="utf-8") as f:
            f.write(update_script)

        # **运行 `update.bat` 并退出当前应用**
        subprocess.Popen(["cmd", "/c", update_script_path], creationflags=subprocess.CREATE_NO_WINDOW)
        sys.exit(0)  # 退出当前应用

    except Exception as e:
        QMessageBox.critical(None, "更新失败", f"下载更新时出错: {e}")

WINDOW_TITLE = f"序列计算器(一只猫版) {get_current_version()}"

def check_for_updates():
        curr = get_current_version()
        latest = get_latest_version()
        if curr!= latest:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("更新可用")
            msg_box.setIconPixmap(QPixmap(WINDOW_ICON).scaled(150, 150))
            msg_box.setWindowIcon(QIcon(WINDOW_ICON))
            msg_box.setText(f"检测到新版本 {latest}，是否下载更新？")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            reply = msg_box.exec()
            if reply == QMessageBox.StandardButton.Yes:
                download_updates()