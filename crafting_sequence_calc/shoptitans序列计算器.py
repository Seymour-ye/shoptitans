import sys
import ctypes
import os
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QSpinBox, QFileDialog
from PyQt5.QtCore import Qt
import json

import subprocess

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.data = {
            "quality_scores": {
                "普通": 1,
                "优质": 5,
                "精良": 30,
                "史诗": 200,
                "传说": 1500
            },
            "sequences": {
                "石头x0": [],
                "石头x1": [],
                "石头x2": [],
                "石头x3": [],
                "石头x4": []
            },
            "best_sequence": [],
            'game_path': ''
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
        self.data['game_path'] = path 
        self.save_config()

    def update_quality_scores(self, scores):
        self.data["quality_scores"] = scores
        self.save_config()

    def update_sequences(self, sequences):
        self.data["sequences"] = sequences
        self.save_config()

    def update_best_sequence(self, best_sequence):
        self.data["best_sequence"] = best_sequence
        self.save_config()



class SequenceCalculator(QWidget):
    def __init__(self):
        self.config_manager = ConfigManager()
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("制作工具")  # 窗口标题
        self.setGeometry(100, 100, 800, 600)


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

        # 初始化品质评分表和输入框
        self.score_inputs = {}
        self.quality_scores = self.config_manager.data["quality_scores"]
        self.logs = self.config_manager.data["sequences"]
        self.best_sequence = self.config_manager.data["best_sequence"]
        
        # 初始化序列日志和显示框
        self.sequence_buttons = {}  # 存储序列激活按钮
        self.active_sequence_index = 0  # 当前序列的索引，默认激活石头x0
        self.log_displays = {}  # 存储 QLabel 显示每条序列的日志

        qualities = [
            ("普通", "#ffffff"),  # 白色
            ("优质", "#00ff00"),  # 绿色
            ("精良", "#0000ff"),  # 蓝色
            ("史诗", "#500050"),  # 紫色
            ("传说", "#ffd700"),  # 金色
        ]
        default_scores = [1, 5, 30, 200, 1500]


        # 创建序列按钮和日志框
        for i in range(5):
            # 序列激活按钮
            sequence_button = QPushButton(f"石头x{i}(共{len(self.logs[f"石头x{i}"])}个)")
            sequence_button.clicked.connect(self.activate_sequence(i))
            self.sequence_buttons[f"石头x{i}"] = sequence_button
            self.layout.addWidget(sequence_button, i, 0)

            # 序列日志显示框，占 2 列
            log_display = QLabel("")
            log_display.setWordWrap(True)
            log_display.setStyleSheet("""
                background-color: #3a3a3a;
                border: 1px solid #555;
                padding: 5px;
            """)
            self.log_displays[f"石头x{i}"] = log_display
            self.layout.addWidget(log_display, i, 1, 1, 2)  # 占用两列

        # 品质按钮 + 打分栏
        for i, (quality, color) in enumerate(qualities):
            default_score = default_scores[i]

            # 单件按钮
            single_button = QPushButton(quality)
            single_button.clicked.connect(self.add_log(quality, 1))
            single_button.setStyleSheet(f"color: {color};")  # 设置按钮字体颜色
            self.layout.addWidget(single_button, i + 6, 0)

            # 双件按钮
            double_button = QPushButton(f"{quality}x2")
            double_button.clicked.connect(self.add_log(quality, 2))
            double_button.setStyleSheet(f"color: {color};")  # 设置按钮字体颜色
            self.layout.addWidget(double_button, i + 6, 1)

            # 打分栏
            spin_box = QSpinBox()
            spin_box.setRange(0, 5000)  # 设置分数范围
            spin_box.setValue(default_score)  # 默认值
            spin_box.setFixedWidth(60)  # 设置固定宽度，足够显示4位数
            spin_box.valueChanged.connect(self.update_scores(quality))
            self.layout.addWidget(spin_box, i + 6, 2)

            self.quality_scores[quality] = default_score
            self.score_inputs[quality] = spin_box

        # 清空按钮
        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear_logs)
        self.layout.addWidget(clear_button, 11, 0)

        # 计算最优序列按钮
        calculate_button = QPushButton("计算最优序列")
        calculate_button.clicked.connect(self.calculate_best_sequence)
        self.layout.addWidget(calculate_button, 11, 1)

        # 撤销按钮
        undo_button = QPushButton("撤销")
        undo_button.clicked.connect(self.undo_last_entry)
        self.layout.addWidget(undo_button, 11, 2)  

        # 制作按钮
        # craft_equipment_button = QPushButton("制作装备")
        # craft_equipment_button.clicked.connect(self.craft_equipment)
        # self.layout.addWidget(craft_equipment_button, 12, 0)

        # craft_stone_button = QPushButton("制作石头")
        # craft_stone_button.clicked.connect(self.craft_stone)
        # self.layout.addWidget(craft_stone_button, 12, 1)

        # 最优序列显示
        self.best_sequence_label = QLabel(f"最优序列：{' -> '.join(self.best_sequence)}")
        # self.best_sequence_label.setText(f"最优序列：{' -> '.join(self.best_sequence)}")
        self.best_sequence_label.setStyleSheet("""
            background-color: #3a3a3a;
            border: 1px solid #555;
            padding: 5px;
            color: #ffffff;
        """)
        self.best_sequence_label.setWordWrap(True)
        self.layout.addWidget(self.best_sequence_label, 13, 0, 1, 3)  # 占用三列

        # # 从配置管理器加载路径
        # self.game_path = self.config_manager.data["game_path"]

        # # 初始化选择游戏路径按钮
        # self.select_path_button = QPushButton(self.game_path if self.game_path else "请选择游戏路径")
        # self.select_path_button.clicked.connect(self.select_game_path)
        # self.layout.addWidget(self.select_path_button, 14, 0)  # 放置在适当位置


        # # 添加网络切换按钮
        # self.toggle_net_button = QPushButton("断网")
        # self.toggle_net_button.clicked.connect(self.toggle_network_access)
        # self.layout.addWidget(self.toggle_net_button, 14, 1)  # 放置在适当的位置

        # 初始化网络状态
        self.is_blocked = False  # 初始状态为“未断网”

        # 添加切换窗口前置的按钮
        self.toggle_button = QPushButton("开启窗口前置", self)
        self.toggle_button.clicked.connect(self.toggle_window_stay_on_top)
        self.layout.addWidget(self.toggle_button, 14, 2)  

        # 刷新窗口数据
        self.update_all_logs()

        # 设置主布局
        self.setLayout(self.layout)

        # 初始化激活序列样式
        self.update_sequence_styles()

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

    def undo_last_entry(self):
    # 当前激活的序列
        current_sequence = f"石头x{self.active_sequence_index}"

        # 检查是否有可撤销的记录
        if self.logs[current_sequence]:
            # 移除最后一个记录
            self.logs[current_sequence].pop()

            # 更新按钮文本和日志显示
            self.update_sequence_button_text()
            self.update_log_display(self.active_sequence_index)

    def update_sequence_button_text(self):
        current_sequence = f"石头x{self.active_sequence_index}"
        total_items = len(self.logs[current_sequence])
        self.sequence_buttons[current_sequence].setText(f"石头x{self.active_sequence_index}(共{total_items}个)")

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

    def update_scores(self, quality):
        def update(value):
            self.quality_scores[quality] = value
            self.config_manager.update_quality_scores(self.quality_scores)
        return update

    def activate_sequence(self, index):
        def activate():
            self.active_sequence_index = index
            self.update_sequence_styles()
        return activate

    def update_sequence_styles(self):
        # 更新序列按钮样式
        for i, button in enumerate(self.sequence_buttons.values()):
            if i == self.active_sequence_index:
                button.setStyleSheet("""
                    background-color: #707070;
                    color: #ffffff;
                    font-weight: bold;
                """)
            else:
                button.setStyleSheet("""
                    background-color: #3a3a3a;
                    color: #ffffff;
                """)

    def add_log(self, quality, amount):
        def log_action():
            current_sequence = f"石头x{self.active_sequence_index}"
            self.logs[current_sequence].append((quality, amount))
            self.update_sequence_button_text()
            self.update_log_display(self.active_sequence_index)
            self.config_manager.update_sequences(self.logs)
        return log_action

    def craft_equipment(self, curr_sequence, sequence_indices):
        current_sequence = f"石头x{curr_sequence}"
        if self.logs[current_sequence]:
            quality, amount = self.logs[current_sequence][sequence_indices[curr_sequence]]
            sequence = []
        for i in range(5):
            sequence.append(sequence_indices[i] + 1)
        return curr_sequence, self.quality_scores[quality] * amount, (quality, amount), sequence

    def craft_stone(self, curr_sequence, sequence_indices):
        sequence = list(sequence_indices)
        sequence[curr_sequence] += 4
        curr_sequence = (curr_sequence + 1) % 5
        return curr_sequence, sequence

    def calculate_best_sequence(self):
        memo = {}
        def dfs(sequence_indices, curr_sequence_index, memo):
            key = (curr_sequence_index, tuple(sequence_indices))
            if key in memo:
                return memo[key]
            n = len(self.logs[f"石头x{curr_sequence_index}"])
            if sequence_indices[curr_sequence_index] >= n:
                memo[key] = (0,[])
                return 0, []
            item_curr, item_score, item, item_seq= self.craft_equipment(curr_sequence_index, sequence_indices)
            stone_curr, stone_seq = self.craft_stone(curr_sequence_index, sequence_indices)
            #if craft equipment
            item_crafted = dfs(item_seq, item_curr, memo)
            item_full_score = item_crafted[0] + item_score
            item_full_sequence = [item] + item_crafted[1]
            # if craft stone
            stone = dfs(stone_seq, stone_curr, memo)
            stone_full_score = stone[0] 
            stone_full_sequence = [('石头',1)] + stone[1]
            if stone_full_score > item_full_score:
                memo[key] = (stone_full_score, stone_full_sequence)
                return stone_full_score, stone_full_sequence
            memo[key] = (item_full_score, item_full_sequence)
            return item_full_score, item_full_sequence
        
        res = dfs([0,0,0,0,0], 0, memo)
        result = []
        for quality, amount in res[1]:
            result.append(quality+'x'+str(amount))
        self.best_sequence = result
        self.best_sequence_label.setText(f"最优序列：{' -> '.join(result)}")
        self.config_manager.update_best_sequence(result)
        print('finish')


    def update_all_logs(self):
        for i in range(5):
            self.update_log_display(i)

    def update_log_display(self, index):
        logs = self.logs[f"石头x{index}"]
        log_text = " | ".join([f"{q}x{a}" for q, a in logs])
        self.log_displays[f"石头x{index}"].setText(log_text)

    def clear_logs(self):
        for key in self.logs:
            self.logs[key] = []
            self.sequence_buttons[key].setText(f"石头x{self.active_sequence_index}")
        self.config_manager.update_sequences(self.logs)
        self.best_sequence_label.setText("最优序列：")
        self.config_manager.update_best_sequence([])
        self.update_all_logs()

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
    
    # 启动程序
    app = QApplication(sys.argv)
    calc_app = SequenceCalculator()
    calc_app.show()
    sys.exit(app.exec_())
