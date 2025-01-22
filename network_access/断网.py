import sys
import ctypes 
import os 
import subprocess
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QFileDialog, QInputDialog
from PyQt5.QtCore import Qt
import json

import threading
import keyboard  # 用于全局热键
import mouse  # 用于捕获鼠标事件

class ConfigManager:
    def __init__(self, config_file="naConfig.json"):
        self.config_file = config_file
        self.data = {
            'game_path': '',
            'hotkey': 'ctrl+shift+d' #默认快捷键
        }
        self.load_config()

    def load_config(self):
        try:
            with open(self.config_file, "r", encoding="utf-8") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.save_config()  # 如果文件不存在，创建一个默认配置文件

    def save_config(self):
        with open(self.config_file, "w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=4)

    def update_game_path(self, path):
        self.data["game_path"] = path
        self.save_config()

    def update_hotkey(self, hotkey):
        self.data["hotkey"] = hotkey
        self.save_config()

class NetworkToggle(QWidget):
    def __init__(self):
        self.config_manager = ConfigManager()
        super().__init__()
        self.registered_hotkeys = []  # 记录已注册的热键
        self.registered_mouse_buttons = []  # 记录已注册的鼠标事件
        self.initUI()
        self.setup_hotkey()  # 设置全局热键

    def initUI(self):
        title = "管理员权限已获取，可以断网" if is_admin() else "未获得管理员权限，无法断网"
        self.setWindowTitle(title )  # 窗口标题
        self.setGeometry(100, 100, 400, 200)

        self.setStyleSheet("""
            QWidget {
                background-color: #2e2e2e;  /* 背景色深灰 */
                color: #ffffff;             /* 全局字体颜色白色 */
            }
            QPushButton {
                background-color: #3a3a3a; /* 按钮背景色 */
                color: #ffffff;            /* 默认字体颜色 */
                border: 1px solid #555;    /* 按钮边框 */
                border-radius: 5px;        /* 圆角按钮 */
                padding: 8px;              /* 按钮内边距 */
                font-weight: bold;         /* 字体加粗 */
            }
            QPushButton:hover {
                background-color: #505050; /* 鼠标悬停时背景色 */
            }
            QPushButton:pressed {
                background-color: #707070; /* 按钮按下时背景色 */
            }
            QLabel {
                background-color: #3a3a3a;
                border: 1px solid #555;
                padding: 5px;
                color: #ffffff;
                margin: 5px;
            }
            QSpinBox {
                background-color: #3a3a3a; /* 数字输入框背景色 */
                border: 1px solid #555;    /* 边框 */
                color: #ffffff;            /* 字体颜色 */
                padding: 2px;              /* 内边距 */
                min-width: 50px;           /* 设置最小宽度 */
            }
        """)

        self.layout = QGridLayout()
        self.config_manager.load_config()
        self.game_path = self.config_manager.data['game_path']
        self.hotkey = self.config_manager.data['hotkey']

        # 初始化选择游戏路径按钮
        self.select_path_button = QPushButton(self.game_path if self.game_path else "请选择游戏路径")
        self.select_path_button.clicked.connect(self.select_game_path)
        self.layout.addWidget(self.select_path_button, 0, 0, 1, 2)  # 放置在适当位置

        # # 添加网络切换按钮
        self.toggle_net_button = QPushButton("断网")
        self.toggle_net_button.clicked.connect(self.toggle_network_access)
        self.layout.addWidget(self.toggle_net_button, 1, 0)  # 放置在适当的位置

        # 添加快捷键设置按钮
        self.hotkey_button = QPushButton(f"设置快捷键 ({self.hotkey})")
        self.hotkey_button.clicked.connect(self.set_hotkey)
        self.layout.addWidget(self.hotkey_button, 2, 1)  # 放置在适当位置

        # 初始化网络状态
        self.is_blocked = False  # 初始状态为“未断网”

        # 添加切换窗口前置的按钮
        self.toggle_button = QPushButton("开启窗口前置", self)
        self.toggle_button.clicked.connect(self.toggle_window_stay_on_top)
        self.layout.addWidget(self.toggle_button, 1, 1)  

        # 设置主布局
        self.setLayout(self.layout)

    def setup_hotkey(self):
        """设置全局热键，支持键盘和鼠标"""
        def hotkey_action():
            self.toggle_network_access()

        # 清除之前的绑定
        self.clear_hotkeys()

        # 判断快捷键是否为鼠标按键
        if self.hotkey.startswith("mouse_"):
            button = self.hotkey.replace("mouse_", "").lower()  # 去除前缀并小写
            valid_buttons = ["left", "right", "middle", "x", "x2"]
            if button in valid_buttons:
                print(f"绑定鼠标按键: {button}")
                mouse.on_button(hotkey_action, buttons=(button,), types=('down',))
                self.registered_mouse_buttons.append(button)
            else:
                print(f"无效的鼠标按键: {button}")
        else:
            hotkey_id = keyboard.add_hotkey(self.hotkey, hotkey_action)
            self.registered_hotkeys.append(hotkey_id)

    def clear_hotkeys(self):
        """清除已注册的热键和鼠标绑定"""
        for hotkey_id in self.registered_hotkeys:
            keyboard.remove_hotkey(hotkey_id)
        self.registered_hotkeys.clear()

        for button in self.registered_mouse_buttons:
            mouse.unhook_all_buttons()  # 清除所有鼠标绑定（仅限当前库内绑定）
        self.registered_mouse_buttons.clear()

    def set_hotkey(self):
        """设置自定义快捷键，支持鼠标按键"""
        new_hotkey, ok = QInputDialog.getText(self, "设置快捷键", "请输入新的快捷键或鼠标按键 (例如 'ctrl+shift+d' 或 'mouse_x'):", text=self.hotkey)
        if ok and new_hotkey.strip():
            self.hotkey = new_hotkey.strip()
            self.config_manager.update_hotkey(self.hotkey)
            self.hotkey_button.setText(f"设置快捷键 ({self.hotkey})")
            self.setup_hotkey()  # 重新设置新的快捷键

    def select_game_path(self):
        # 打开文件选择对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择游戏路径",
            "",
            "可执行文件 (*.exe);;所有文件 (*)"
        )

        if file_path:  # 如果用户选择了路径
            if not os.path.normpath(file_path):
                self.select_path_button.setText("文件路径无效，请重新选择")
                return 
            self.game_path = os.path.normpath(file_path)
            self.config_manager.update_game_path(self.game_path)  # 更新配置文件
            self.select_path_button.setText(file_path)  # 更新按钮显示
            print(f"已选择游戏路径: {file_path}")
        else:
            self.select_path_button.setText("未选择游戏路径，请选择")

    def toggle_network_access(self):
        if not self.game_path:
            self.select_path_button.setText("请先选择游戏路径")
            return

        # 规范化路径并检查文件是否存在
        program_path = self.game_path
        if not os.path.isfile(self.game_path):
            self.select_path_button.setText("文件路径无效，请选择")
            return

        # 确保路径用双引号括起来
        program_path = f'"{self.game_path}"'

        if not self.is_blocked:
            # 删除可能已存在的规则
            subprocess.run(
                [
                    "netsh", "advfirewall", "firewall", "delete", "rule",
                    "name=BlockShopTitansNetwork"
                ],
                check=False,
                shell=True
            )

            # 添加阻止规则
            try:
                subprocess.run(
                    [
                        "netsh", "advfirewall", "firewall", "add", "rule",
                        "name=BlockShopTitansNetwork",
                        f"program={program_path}",
                        "dir=out",
                        "action=block"
                    ],
                    check=True,
                    shell=True
                )
                print(f"已阻止程序 {self.game_path} 的网络访问")
                self.toggle_net_button.setText("联网")
                self.is_blocked = True
            except subprocess.CalledProcessError as e:
                print(f"设置防火墙规则时出错: {e}")
        else:
            # 删除规则
            try:
                subprocess.run(
                    [
                        "netsh", "advfirewall", "firewall", "delete", "rule",
                        "name=BlockShopTitansNetwork"
                    ],
                    check=True,
                    shell=True
                )
                print(f"已恢复程序 {self.game_path} 的网络访问")
                self.toggle_net_button.setText("断网")
                self.is_blocked = False
            except subprocess.CalledProcessError as e:
                print(f"删除防火墙规则时出错: {e}")

    def toggle_window_stay_on_top(self):
        # 检查窗口是否已经设置为总是前置
        if self.windowFlags() & Qt.WindowStaysOnTopHint:
            # 取消总是前置
            self.setWindowFlag(Qt.WindowStaysOnTopHint, False)
            self.toggle_button.setText("开启窗口前置")
        else:
            # 设置总是前置
            self.setWindowFlag(Qt.WindowStaysOnTopHint, True)
            self.toggle_button.setText("关闭窗口前置")

        # 重新应用窗口设置
        self.show()
    
def is_admin():
    """检查程序是否以管理员权限运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员权限重新启动程序"""
    if not is_admin():
        try:
            # 提升权限重新运行程序
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, " ".join(sys.argv), None, 1
            )
        except Exception as e:
            print(f"无法提升权限: {e}")
        sys.exit()

if __name__ == '__main__':
    # 确保以管理员权限运行
    if not is_admin():
        run_as_admin()
    
    #启动程序
    app = QApplication(sys.argv)
    toggle_app = NetworkToggle()
    toggle_app.show()
    sys.exit(app.exec_())
