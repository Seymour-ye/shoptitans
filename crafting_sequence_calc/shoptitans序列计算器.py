import sys
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QPushButton, QLabel, QSpinBox, QScrollArea
from PyQt5.QtCore import Qt
import json

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
            'craft_active': 0
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

    def update_craft_active(self, craft_active):
        self.data['craft_active'] = craft_active
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
        self.craft_active = self.config_manager.data['craft_active']

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

            # 创建 QScrollArea
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)  # 内容自适应大小

            # 序列日志显示框，占 2 列
            log_display = QLabel("")
            log_display.setWordWrap(True)
            log_display.setStyleSheet("""
                background-color: #3a3a3a;
                border: 1px solid #555;
                padding: 5px;
            """)
            self.log_displays[f"石头x{i}"] = log_display

            scroll_area.setWidget(log_display)  # 将 QLabel 添加到 QScrollArea

            self.layout.addWidget(scroll_area, i, 1, 1, 2)  # 占用两列
            

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

        # 最优序列显示
        self.best_sequence_label = QLabel(f"最优序列：\n{' -> '.join(self.best_sequence)}")
        # self.best_sequence_label.setText(f"最优序列：{' -> '.join(self.best_sequence)}")
        self.best_sequence_label.setStyleSheet("""
            background-color: #3a3a3a;
            border: 1px solid #555;
            padding: 5px;
            color: #ffffff;
        """)
        self.best_sequence_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.best_sequence_label.setWordWrap(True)


        #制作按钮
        craft_equipment_button = QPushButton("制作装备")
        craft_equipment_button.clicked.connect(self.craft_equip_)
        self.layout.addWidget(craft_equipment_button, 14, 0)

        craft_stone_button = QPushButton("制作石头")
        craft_stone_button.clicked.connect(self.craft_stone_)
        self.layout.addWidget(craft_stone_button, 14, 1)

        # 创建 QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 内容自适应大小
        scroll_area.setWidget(self.best_sequence_label)  # 将 QLabel 添加到 QScrollArea

        self.layout.addWidget(scroll_area, 13, 0, 1, 3)  # 占用三列

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

    def update_all_sequence_button_text(self):
        for i in range(5):
            current_sequence = f"石头x{i}"
            total_items = len(self.logs[current_sequence])
            self.sequence_buttons[current_sequence].setText(f"石头x{i}(共{total_items}个)")

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

            # 滚动到底部
            scroll_area = self.layout.itemAtPosition(self.active_sequence_index, 1).widget()
            scroll_area.verticalScrollBar().setValue(scroll_area.verticalScrollBar().maximum())
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
            for i in range(5):
                if sequence_indices[i] >= len(self.logs[f"石头x{i}"]):
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
        
        res = dfs([0,0,0,0,0], self.craft_active, memo)
        result = []
        for quality, amount in res[1]:
            result.append(quality+'x'+str(amount))
        self.best_sequence = result
        self.best_sequence_label.setText(f"最优序列：\n{' -> '.join(result)}")
        self.config_manager.update_best_sequence(result)
        print('finish')

    def craft_equip_(self):
        #craft
        crafted='  '
        if self.best_sequence:
            crafted = self.best_sequence.pop(0)
            self.config_manager.update_best_sequence(self.best_sequence)
        print(self.craft_active)
        for i in range(5):
            if self.logs[f"石头x{i}"]:
                self.logs[f"石头x{i}"].pop(0)
        
        if crafted[:2] != '石头':
            self.best_sequence_label.setText(f"最优序列：\n{' -> '.join(self.best_sequence)}")
        else:
            self.calculate_best_sequence()
        self.update_all_logs()
        self.update_all_sequence_button_text()
    
    def craft_stone_(self):
        # craft
        crafted='  '
        if self.best_sequence:
            crafted = self.best_sequence.pop(0)
            self.config_manager.update_best_sequence(self.best_sequence)
        print(self.craft_active)
        for i in range(4):
            if self.logs[f"石头x{self.craft_active}"]:
                self.logs[f"石头x{self.craft_active}"].pop(0)
        self.craft_active = (self.craft_active + 1) % 5
        self.config_manager.update_craft_active(self.craft_active)

        if crafted[:2] == '石头':
            self.best_sequence_label.setText(f"最优序列：\n{' -> '.join(self.best_sequence)}")
        else:
            self.calculate_best_sequence()
        self.update_all_logs()
        self.update_all_sequence_button_text()

    def update_all_logs(self):
        for i in range(5):
            self.update_log_display(i)

    def update_log_display(self, index):
        logs = self.logs[f"石头x{index}"]
        log_text = " | ".join([f"{q}x{a}" for q, a in logs])
        self.log_displays[f"石头x{index}"].setText(log_text)

    def clear_logs(self):
        self.craft_active = 0
        self.config_manager.update_craft_active(0)
        for key in self.logs:
            self.logs[key] = []
            self.sequence_buttons[key].setText(f"{key}(共0个)")
        self.config_manager.update_sequences(self.logs)
        self.best_sequence_label.setText("最优序列：")
        self.config_manager.update_best_sequence([])
        self.update_all_logs()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc_app = SequenceCalculator()
    calc_app.show()
    sys.exit(app.exec_())
