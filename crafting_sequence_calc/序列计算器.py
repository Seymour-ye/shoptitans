import sys
import webbrowser
from PyQt5.QtWidgets import QComboBox, QApplication, QWidget, QGridLayout, QPushButton, QLabel, QSpinBox, QScrollArea
from PyQt5.QtCore import Qt
from config import ConfigManager



class SequenceCalculator(QWidget):
    def __init__(self):
        self.config_manager = ConfigManager('scConfig.json')
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("序列计算器 - 不更新就提需求椰子鲨了你！！！")  # 窗口标题
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

        self.qualities = {
            "普通": "#ffffff",  # 白色
            "优质": "#00ff00",  # 绿色
            "精良": "#4da6ff",  # 蓝色
            "史诗": "#a64ca6",  # 紫色
            "传说": "#ffd700",  # 金色
        }

        # 初始化品质评分表和输入框
        self.score_inputs = {}
        self.load_data()
        
        # 初始化序列日志和显示框
        self.sequence_buttons = {}  # 存储序列激活按钮
        self.active_sequence_index = 0  # 当前序列的索引，默认激活石头x0
        self.log_displays = {}  # 存储 QLabel 显示每条序列的日志

        default_scores = [1, 5, 30, 200, 1500]

        # 添加选择 Tier 的输入框
        tier_selector_label = QLabel("选择 Tier (T级):")
        tier_selector_label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    background: none;  /* 去掉背景色 */
                    border: none;      /* 去掉边框 */
                    color: #ffffff;    /* 字体颜色 */
                }
            """)
        tier_selector_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # 右对齐，垂直居中
        self.layout.addWidget(tier_selector_label, 0, 0)

        self.tier_selector = QComboBox()
        self.tier_selector.addItems([str(i) for i in range(1, 15)])  # 添加 1 到 14 的选项
        self.tier_selector.setCurrentText(str(self.config_manager.tier))  # 设置默认值
        self.tier_selector.setStyleSheet("""
            QComboBox {
                background-color: #3a3a3a; /* 深灰背景 */
                border: 1px solid #555;    /* 边框 */
                color: #ffffff;            /* 字体颜色 */
                font-size: 14px;           /* 字体大小 */
                padding: 2px;              /* 内边距 */
            }
            QComboBox QAbstractItemView {
                background-color: #3a3a3a; /* 下拉选项背景色 */
                color: #ffffff;            /* 下拉选项字体颜色 */
                border: 1px solid #555;    /* 边框 */
            }
        """)
        self.tier_selector.currentTextChanged.connect(self.change_tier)  # 绑定值变化事件
        self.layout.addWidget(self.tier_selector, 0, 1)

        # 添加跳转按钮
        web_button = QPushButton("使用说明")
        web_button.clicked.connect(self.open_web_link)
        web_button.setStyleSheet("""
            QPushButton {
                background-color: #3a3a3a; /* 按钮背景色 */
                color: #ffffff;            /* 字体颜色 */
                border: 1px solid #555;    /* 边框 */
                border-radius: 5px;        /* 圆角按钮 */
                padding: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #505050; /* 鼠标悬停时背景色 */
            }
            QPushButton:pressed {
                background-color: #707070; /* 按钮按下时背景色 */
            }
        """)

        # 添加到右上角
        self.layout.addWidget(web_button, 0, 2)

        # 创建序列按钮和日志框
        for i in range(5):
            # 序列激活按钮
            sequence_button = QPushButton(f"石头x{(i-self.craft_active)%5}(共{len(self.logs[f"石头x{i}"])}个)")
            sequence_button.clicked.connect(self.activate_sequence(i))
            self.sequence_buttons[f"石头x{i}"] = sequence_button
            self.layout.addWidget(sequence_button, i+1, 0)

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

            self.layout.addWidget(scroll_area, i+1, 1, 1, 2)  # 占用两列
            

        # 品质按钮 + 打分栏
        for i, quality in enumerate(self.qualities):
            color = self.qualities[quality]
            default_score = default_scores[i]

            # 单件按钮
            single_button = QPushButton(quality)
            single_button.clicked.connect(self.add_log(quality, 1))
            single_button.setStyleSheet(f"color: {color};")  # 设置按钮字体颜色
            self.layout.addWidget(single_button, i + 7, 0)

            # 双件按钮
            double_button = QPushButton(f"{quality}x2")
            double_button.clicked.connect(self.add_log(quality, 2))
            double_button.setStyleSheet(f"color: {color};")  # 设置按钮字体颜色
            self.layout.addWidget(double_button, i + 7, 1)

            # 打分栏
            spin_box = QSpinBox()
            spin_box.setRange(0, 5000)  # 设置分数范围
            spin_box.setValue(default_score)  # 默认值
            spin_box.setFixedWidth(60)  # 设置固定宽度，足够显示4位数
            spin_box.valueChanged.connect(self.update_scores(quality))
            self.layout.addWidget(spin_box, i + 7, 2)

            self.quality_scores[quality] = default_score
            self.score_inputs[quality] = spin_box

        # 清空按钮
        clear_button = QPushButton("清空")
        clear_button.clicked.connect(self.clear_logs)
        self.layout.addWidget(clear_button, 13, 0)

        # 计算最优序列按钮
        calculate_button = QPushButton("计算最优序列")
        calculate_button.clicked.connect(self.calculate_best_sequence)
        self.layout.addWidget(calculate_button, 13, 1)

        # 撤销按钮
        undo_button = QPushButton("撤销")
        undo_button.clicked.connect(self.undo_last_entry)
        self.layout.addWidget(undo_button, 13, 2)  

        # 最优序列显示
        self.best_sequence_label = QLabel("最优序列：\n")
        self.best_sequence_label.setStyleSheet("""
            background-color: #3a3a3a;
            border: 1px solid #555;
            padding: 5px;
            color: #ffffff;
        """)
        self.best_sequence_label.setTextInteractionFlags(Qt.TextSelectableByMouse | Qt.TextSelectableByKeyboard)
        self.best_sequence_label.setWordWrap(True)
        self.update_best_sequence_display()

        #制作按钮
        craft_equipment_button = QPushButton("制作装备")
        craft_equipment_button.clicked.connect(self.craft_equip_)
        self.layout.addWidget(craft_equipment_button, 15, 0)

        craft_stone_button = QPushButton("制作石头")
        craft_stone_button.clicked.connect(self.craft_stone_)
        self.layout.addWidget(craft_stone_button, 15, 1)

        # 创建 QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)  # 内容自适应大小
        scroll_area.setWidget(self.best_sequence_label)  # 将 QLabel 添加到 QScrollArea

        self.layout.addWidget(scroll_area, 14, 0, 1, 3)  # 占用三列

        # 添加切换窗口前置的按钮
        self.toggle_button = QPushButton("开启窗口前置", self)
        self.toggle_button.clicked.connect(self.toggle_window_stay_on_top)
        self.layout.addWidget(self.toggle_button, 15, 2)  

        # 刷新窗口数据
        self.update_all_logs()

        # 设置主布局
        self.setLayout(self.layout)

        # 初始化激活序列样式
        self.update_sequence_styles()

    def open_web_link(self):
        webbrowser.open("https://github.com/Seymour-ye/shoptitans")  # 替换为你的链接

    def load_data(self, tier=-1):
        if tier == -1:
            tier = self.config_manager.tier

        self.craft_active = self.config_manager.data[tier]['craft_active']
        self.quality_scores = self.config_manager.data['quality_scores']
        self.logs = self.config_manager.data[tier]['sequences']
        self.best_sequence = self.config_manager.data[tier]['best_sequence']
        
        self.config_manager.update_tier(tier)

    def change_tier(self, value):
        # 更新配置管理器中的 tier
        value = int(value)
        self.config_manager.update_tier(value)

        # 加载新 tier 的数据
        self.load_data(value)

        # 刷新界面
        self.update_all_logs()
        self.update_all_sequence_button_text()
        self.update_best_sequence_display()

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
            self.config_manager.update_sequences(self.logs)

    def update_sequence_button_text(self):
        current_sequence = f"石头x{self.active_sequence_index}"
        total_items = len(self.logs[current_sequence])
        self.sequence_buttons[current_sequence].setText(f"石头x{(self.active_sequence_index-self.craft_active)%5}(共{total_items}个)")

    def update_all_sequence_button_text(self):
        for i in range(5):
            current_sequence = f"石头x{i}"
            total_items = len(self.logs[current_sequence])
            self.sequence_buttons[current_sequence].setText(f"石头x{(i-self.craft_active)%5}(共{total_items}个)")

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
            scroll_area = self.layout.itemAtPosition(self.active_sequence_index+1, 1).widget()
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
            # prior = True
            # for i in range(self.craft_active, self.craft_active+5):
            #     if i%5 == curr_sequence_index:
            #         prior = False 
            #     if prior and sequence_indices[i%5] + 4 >= len(self.logs[f"石头x{i%5}"]):
            #         memo[key] = (0,[])
            #         return 0, []
            #     elif not prior and sequence_indices[i%5] >= len(self.logs[f"石头x{i%5}"]):
            #         memo[key] = (0,[])
            #         return 0, []
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
            if stone_full_score <= item_full_score:
                memo[key] = (item_full_score, item_full_sequence)
                return item_full_score, item_full_sequence
            memo[key] = (stone_full_score, stone_full_sequence)
            return stone_full_score, stone_full_sequence
        
        res = dfs([0,0,0,0,0], self.craft_active, memo)
        self.best_sequence = res[1]
        self.update_best_sequence_display()
        self.config_manager.update_best_sequence(self.best_sequence)

    def craft_equip_(self):
        #craft
        if self.best_sequence:
            self.best_sequence.pop(0)
            self.config_manager.update_best_sequence(self.best_sequence)
        for i in range(5):
            if self.logs[f"石头x{i}"]:
                self.logs[f"石头x{i}"].pop(0)
        
        self.calculate_best_sequence()
        self.update_all_logs()
        self.update_all_sequence_button_text()
    
    def craft_stone_(self):
        # craft
        if self.best_sequence:
            self.best_sequence.pop(0)
            self.config_manager.update_best_sequence(self.best_sequence)
        for i in range(4):
            if self.logs[f"石头x{self.craft_active}"]:
                self.logs[f"石头x{self.craft_active}"].pop(0)
        self.craft_active = (self.craft_active + 1) % 5
        self.config_manager.update_craft_active(self.craft_active)

        self.calculate_best_sequence()
        self.update_all_logs()
        self.update_all_sequence_button_text()

    def update_best_sequence_display(self):
        tl = []
        for i in self.best_sequence:
            quality = i[0]
            amount = i[1]
            color = '#AAAAAA' if quality == '石头' else self.qualities[quality]
            tl.append((quality, amount, color))
        text = f"最优序列：<br>{' -> '.join([
                f"<span style='color: {color};'>{quality}x{amount}</span>" 
                for quality, amount, color in tl
            ])}"
        self.best_sequence_label.setText(text)

    def update_all_logs(self):
        for i in range(5):
            self.update_log_display(i)
            self.config_manager.update_sequences(self.logs)


    def update_log_display(self, index):
        logs = self.logs[f"石头x{index}"]
        log_text = " | ".join([f"<span style='color: {self.qualities[q]};'>{q}x{a}</span>" for q, a in logs])
        self.log_displays[f"石头x{index}"].setText(log_text)

    def clear_logs(self):
        self.craft_active = 0
        self.config_manager.update_craft_active(0)
        for key in self.logs:
            self.logs[key] = []
            self.sequence_buttons[key].setText(f"{key}(共0个)")
        self.config_manager.update_sequences(self.logs)
        self.update_best_sequence_display()
        self.config_manager.update_best_sequence([])
        self.update_all_logs()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    calc_app = SequenceCalculator()
    calc_app.show()
    sys.exit(app.exec_())
