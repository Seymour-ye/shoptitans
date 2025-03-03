# Modules
import db.constants as CONSTANTS
from db.ConfigManager import ConfigManager

# Functionalities
import sys
from datetime import datetime

# PyQt6
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWidgets import QSpinBox, QPushButton, QLabel, QTextBrowser, QCheckBox, QComboBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer
from PyQt6 import uic

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(CONSTANTS.UI_PATH, self)
        self.cm = ConfigManager()

        self.setWindowTitle(CONSTANTS.WINDOW_TITLE)
        self.setWindowIcon(QIcon(CONSTANTS.WINDOW_ICON))

        #CONSTANTS ADJUSTMENT
        self.tier_selection_dropbox.addItems([str(i) for i in range(CONSTANTS.MAX_TIER, 0, -1)])
        self.craft_input_active = 0
        self.multi_entry = 1
        self.enchantment_entry = [1,1,1,1]
        self.enchantment_last_entry = None
        self.enchantment_amount = 1
        self.status_bar = QLabel()
        self.status_bar.setFixedWidth(self.tabWidget.width())
        self.statusBar.addWidget(self.status_bar)
        self.timers = {}
        self.last_occurs = self.cm.get_last_occurs()
        # set up window-on-top
        self.window_on_top_checkbox.stateChanged.connect(self.window_on_top)

        # SETUP CONNECTIONS
        self.setup_craft_pane()
        self.setup_craft_summary()
        self.setup_enchantment_pane()
        for npc in CONSTANTS.TIMER_INTERVALS.keys():
            self.setup_npc_timer(npc)

        # LOAD CONTENTS
        self.updates_display.setText(CONSTANTS.fetch_updates())
        self.readme_display.setText(CONSTANTS.fetch_readme())
        self.load_logs()
        self.load_summary_page()
        self.load_craft_page()
        self.load_enchantment_page()
        self.load_timers()

        # CHECK FOR UPDATES
        CONSTANTS.check_for_updates()

    def setup_craft_pane(self):
        # tier selection
        self.tier_selection_dropbox.currentTextChanged.connect(self.set_curr_tier)
        # quality score spinboxes
        for i in range(5):
            spinbox = self.findChild(QSpinBox, f"quality_{i}_score")
            if spinbox:
                spinbox.setProperty("quality_index", i)
                spinbox.valueChanged.connect(self.set_quality_score)
        # quality buttons
        for q in range(5):
            for a in [1, 2]:
                button = self.findChild(QPushButton, f"quality_{q}_x{a}_button")
                if button:
                    button.setProperty("quality_index", q)
                    button.setProperty("amount", a)
                    button.clicked.connect(self.add_record)
        # multi-entry-settings
        self.multi_entry_amount_selection.valueChanged.connect(self.set_multi_entry)
        # back-switch-settings
        self.back_switch_checkbox.stateChanged.connect(self.set_back_switch)
        self.back_switch_rate_selection.valueChanged.connect(self.set_back_switch_rate)
        # sequence buttons
        for i in range(5):
            button = self.findChild(QPushButton, f"sequence_button_{i}")
            button.setProperty('sequence_index', i)
            button.clicked.connect(self.input_sequence_activate)
        # sequence marks
        for i in range(5):
            checkbox = self.findChild(QCheckBox, f"sequence_{i}_mark")
            checkbox.setProperty('sequence_index', i)
            checkbox.stateChanged.connect(self.mark_sequence)
        # clear
        self.clear_button.clicked.connect(self.clear_sequences)
        # backspace
        self.back_space_button.clicked.connect(self.backspace)
        # calculate
        self.calculate_button.clicked.connect(self.calculate_best_sequence)
        # craft buttons
        self.craft_back_switch_item.clicked.connect(self.craft_back_switch_button)
        self.craft_item.clicked.connect(self.craft_item_button)
        self.craft_stone.clicked.connect(self.craft_stone_button)

    def setup_craft_summary(self):
        for i in range(4):
            tier_selector = self.findChild(QComboBox, f"craft_summary_tier_selection_box_{i}")
            tier_selector.setProperty('summary_index', i)
            tier_selector.addItems([str(i) for i in range(CONSTANTS.MAX_TIER, 0, -1)])
            tier_selector.currentTextChanged.connect(self.summary_tier_select)
            
            stone_craft = self.findChild(QPushButton, f"craft_summary_craft_stone_{i}")
            stone_craft.setProperty('summary_index', i)
            stone_craft.clicked.connect(self.summary_craft_stone)

            backswitch_craft = self.findChild(QPushButton, f"craft_summary_craft_backswitch_{i}")
            backswitch_craft.setProperty('summary_index', i)
            backswitch_craft.clicked.connect(self.summary_craft_backswitch)

            item_craft = self.findChild(QPushButton, f"craft_summary_craft_item_{i}")
            item_craft.setProperty('summary_index', i)
            item_craft.clicked.connect(self.summary_craft_item)

    def setup_enchantment_pane(self):
        for i in range(1,5):
            fail_amount = self.findChild(QSpinBox, f"failure_amount_{i}")
            fail_amount.setProperty('quality', i)
            fail_amount.valueChanged.connect(self.fail_amount_change)

            fail_button = self.findChild(QPushButton, f"failure_{i}")
            fail_button.setProperty('quality', i)
            fail_button.setProperty('success', False)
            fail_button.clicked.connect(self.add_enchantment_log)

            success_button = self.findChild(QPushButton, f"success_{i}")
            success_button.setProperty('quality', i)
            success_button.setProperty('success', True)
            success_button.clicked.connect(self.add_enchantment_log)

            count_label = self.findChild(QLabel, f"enchantment_count_label_{i}")
            count_label.setProperty('quality', i)
        self.enchantment_clear.clicked.connect(self.clear_enchantment_log)
        self.enchantment_undo.clicked.connect(self.undo_enchantment_log)
        self.enchantment_calculate.clicked.connect(self.enchantment_analyze)
        self.enchantment_amount_selection.valueChanged.connect(self.set_enchantment_amount)
        self.enchantment_button.clicked.connect(self.enchanting)

    def setup_npc_timer(self, npc):
        reset_button = self.findChild(QPushButton, f"{npc}_reset_button")
        reset_button.setProperty('npc', npc)
        reset_button.clicked.connect(self.reset_timer)
        
        summary_reset = self.findChild(QPushButton, f"summary_{npc}_reset_button")
        summary_reset.setProperty('npc', npc)
        summary_reset.clicked.connect(self.reset_timer)

        self.timers[npc] = QTimer(self)
        self.timers[npc].setProperty('npc', npc)
        self.timers[npc].timeout.connect(self.update_timer)

    def load_timers(self):
        for npc in self.last_occurs.keys():
            self.timers[npc].start(1000)

    def reset_timer(self):
        npc = self.sender().property('npc')
        now = datetime.now()
        self.last_occurs[npc] = now
        self.cm.set_occur_of(npc, now)
        self.timers[npc].start(1000)

    def update_timer(self):
        npc = self.sender().property('npc')
        timer_label = self.findChild(QLabel, f"{npc}_timer")
        interval = CONSTANTS.TIMER_INTERVALS[npc]
        elapsed = (datetime.now() - self.last_occurs[npc]).total_seconds()
        remaining = int(max(interval - elapsed, 0))

        hours = remaining // 3600
        minutes = (remaining % 3600) // 60
        seconds = remaining % 60

        # timer_label.setText(f"{hours:02}:{minutes:02}:{seconds:02}")
        timer_label.setText(f"<span style='color: #32CD32;'>{hours:02}:{minutes:02}:{seconds:02}</span>")

        if remaining <= 0:
            self.timers[npc].stop()
            timer_label.setText("00:00:00")
            # self.add_log("计时器", f"<span style='color: {CONSTANTS.QUALITIY_COLORS[4]};'>{CONSTANTS.NPC_NAMES[npc]}</span> 将在 <span style='color: {CONSTANTS.QUALITIY_COLORS[4]};'>{hours} 小时 {minutes} 分钟</span>后到来！记得重置计时器哦")
            # timer_label.setText("<span style='color:#ffffff;'>00:00:00</span>")
        elif remaining % (60*30) == 0:
            self.add_log("计时器", f"<span style='color: {CONSTANTS.QUALITIY_COLORS[4]};'>{CONSTANTS.NPC_NAMES[npc]}</span> 将在 <span style='color: {CONSTANTS.QUALITIY_COLORS[4]};'>{hours} 小时 {minutes} 分钟</span>后到来！")
        elif remaining < (60*30) and remaining % (60*10) == 0:
            self.add_log("计时器", f"<span style='color: {CONSTANTS.QUALITIY_COLORS[4]};'>{CONSTANTS.NPC_NAMES[npc]}</span> 将在 <span style='color: {CONSTANTS.QUALITIY_COLORS[4]};'>{hours} 小时 {minutes} 分钟</span>后到来！")
        elif remaining < (60*10) and remaining % (60*5) == 0:    
            self.add_log("计时器", f"<span style='color: {CONSTANTS.QUALITIY_COLORS[4]};'>{CONSTANTS.NPC_NAMES[npc]}</span> 将在 <span style='color: {CONSTANTS.QUALITIY_COLORS[4]};'>{hours} 小时 {minutes} 分钟</span>后到来！记得重置计时器哦")

    def enchanting(self):
        quality = self.cm.enchanting(self.enchantment_amount)
        print(quality)
        log_text = ""
        for i in range(5):
            if quality[i] > 0:
                log_text += f"<span style='color:{CONSTANTS.QUALITIY_COLORS[i]};'>{CONSTANTS.QUALITIES[i]} x {quality[i]}</span> "
        self.add_log("附魔", log_text)
        self.enchantment_amount_selection.setValue(1)
        self.enchantment_analyze()
        self.load_enchantment_sequences()

    def set_enchantment_amount(self):
        self.enchantment_amount = self.sender().value()

    def enchantment_analyze(self):
        ench_logs = self.cm.get_enchantment_logs()
        min_length = min([len(lst) for lst in ench_logs if lst], default=0)
        res = []
        for i in range(min_length):
            quality = 0
            for li in range(4):
                if i < len(ench_logs[li]) and ench_logs[li][i]:
                    quality = li + 1
            res.append(quality)
        self.cm.update_enchantment_result(res)
        self.load_enchantment_result()

    def undo_enchantment_log(self):
        if self.enchantment_last_entry:
            quality = self.enchantment_last_entry[0]
            amount = self.enchantment_last_entry[1]
            self.cm.pop_enchantment_log(quality, amount)
            self.enchantment_last_entry = (quality, 1)
            self.load_enchantment_sequence(quality)
        display = self.findChild(QTextBrowser, f"enchantment_sequence_{quality}")
        display.verticalScrollBar().setValue(display.verticalScrollBar().maximum())


    def clear_enchantment_log(self):
        self.cm.clear_enchantment_log()
        self.load_enchantment_page()

    def add_enchantment_log(self):    
        sender = self.sender()
        success = sender.property('success')
        quality = sender.property('quality')
        if success:
            self.cm.add_enchantment_log(quality, success, 1)
            self.enchantment_last_entry = (quality, 1)
        else:
            amount = self.enchantment_entry[quality-1]
            self.cm.add_enchantment_log(quality, success, amount)
            self.enchantment_last_entry = (quality, amount)
        self.load_enchantment_sequence(quality)
        display = self.findChild(QTextBrowser, f"enchantment_sequence_{quality}")
        display.verticalScrollBar().setValue(display.verticalScrollBar().maximum())


    def get_enchantment_log(self, quality):
        return self.cm.get_enchantment_log(quality)

    def fail_amount_change(self):
        sender = self.sender()
        i = sender.property('quality')-1
        self.enchantment_entry[i] = sender.value()

    def get_summary_tiers(self):
        return self.cm.get_summary_tiers()
    
    def summary_tier_select(self):
        selector = self.sender()
        value = int(selector.currentText())
        i = selector.property('summary_index')
        self.summary_tier_change(i, value)

    def summary_tier_change(self, i, tier):
        self.cm.update_summary_tiers(i, tier)

        stone = self.findChild(QPushButton, f"craft_summary_craft_stone_{i}")
        stone.setProperty('tier', tier)

        backswitch = self.findChild(QPushButton, f"craft_summary_craft_backswitch_{i}")
        backswitch.setProperty('tier', tier)

        item = self.findChild(QPushButton, f"craft_summary_craft_item_{i}")
        item.setProperty('tier', tier)

        display = self.findChild(QTextBrowser, f"best_sequence_display_{i}")
        display.setProperty('tier', tier)

        # hide craft button for unswitchables:
        if CONSTANTS.SWITCHABLES[tier][0]:
            stone.show()
        else:
            stone.hide()
        if self.cm.get_back_switch(tier):
            backswitch.show()
        else:
            backswitch.hide()

        self.load_summary_display(i)

    def summary_craft_stone(self):
        button = self.sender()
        tier = button.property('tier')
        self.stone_craft(tier)
        self.load_summary_displays()
        if tier == self.get_curr_tier():
            self.load_craft_page()
    
    def summary_craft_backswitch(self):
        button = self.sender()
        tier = button.property('tier')
        self.back_switch_craft(tier)
        self.load_summary_displays()
        if tier == self.get_curr_tier():
            self.load_craft_page()

    def summary_craft_item(self):
        button = self.sender()
        tier = button.property('tier')
        self.item_craft(tier)
        self.load_summary_displays()
        if tier == self.get_curr_tier():
            self.load_craft_page()

    def window_on_top(self):
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, self.window_on_top_checkbox.isChecked())
        self.show()

    def get_curr_tier(self):
        return self.cm.data['active_tier']
    
    def set_curr_tier(self):
        value = int(self.tier_selection_dropbox.currentText())
        self.cm.update_active_tier(value)
        self.craft_input_active = 0
        self.load_craft_page()

    def set_quality_score(self):
        spinbox = self.sender() #get the QSpinBox that triggered the event.
        quality_index = spinbox.property("quality_index")
        self.cm.update_quality_score(self.get_curr_tier(), quality_index, spinbox.value())
    
    def get_curr_quality_scores(self):
        return self.cm.data[self.get_curr_tier()]['scores']
        
    def set_multi_entry(self):
        self.multi_entry = self.multi_entry_amount_selection.value()
    
    def reset_multi_entry(self):
        self.multi_entry_amount_selection.setValue(1)

    def set_back_switch(self):
        self.cm.update_back_switch(self.get_curr_tier(),
                                   self.back_switch_checkbox.isChecked())
        self.calculate_best_sequence()
        self.load_craft_page()
        
    def get_back_switch(self):
        return self.cm.get_back_switch(self.get_curr_tier())

    def set_back_switch_rate(self):
        self.cm.update_back_switch_rate(self.get_curr_tier(), self.back_switch_rate_selection.value())
        self.calculate_best_sequence()

    def get_back_switch_rate(self):
        return self.cm.get_back_switch_rate(self.get_curr_tier())

    def get_craft_active(self):
        return self.cm.get_craft_active(self.get_curr_tier())

    def get_craft_sequence(self, i):
        return self.cm.get_craft_sequence(self.get_curr_tier(), i)

    def add_record(self):
        button = self.sender()
        quality = button.property("quality_index")
        amount = button.property('amount')
        for i in range(self.multi_entry):
            self.cm.add_sequence_log(self.get_curr_tier(),
                                     self.craft_input_active,
                                     quality, 
                                     amount)
        self.reset_multi_entry()
        self.load_craft_sequence(self.craft_input_active)
        sequence_display_label = self.findChild(QTextBrowser, f"sequence_{self.craft_input_active}_display")
        sequence_display_label.verticalScrollBar().setValue(sequence_display_label.verticalScrollBar().maximum())

    def input_sequence_activate(self):
        self.craft_input_active = self.sender().property('sequence_index')
        self.load_craft_sequence_button_style()

    def backspace(self):
        self.cm.sequence_log_backspace(self.get_curr_tier(), self.craft_input_active)
        self.load_craft_sequence(self.craft_input_active)
        sequence_display_label = self.findChild(QTextBrowser, f"sequence_{self.craft_input_active}_display")
        sequence_display_label.verticalScrollBar().setValue(sequence_display_label.verticalScrollBar().maximum())


    def clear_sequences(self):
        self.cm.reset_sequences(self.get_curr_tier())
        self.load_craft_page()

    def item_craft(self,tier):
        crafted = self.cm.craft_item(tier)
        if crafted:
            craft = CONSTANTS.QUALITIES[crafted[0]]
            amount = crafted[1]
            color = CONSTANTS.QUALITIY_COLORS[crafted[0]]
            note =  f"<span style='color: {color};'>{craft}x{amount}</span>"
        else:
            craft = '未知'
            amount = 1
            note = f"{craft}x{amount}"
        self.add_log("制作", f"T{tier} {note}")
        self.craft_calculator(tier)

    def craft_item_button(self):
        self.item_craft(self.get_curr_tier())
        self.load_best_sequence()
        self.load_craft_sequences()

    def stone_craft(self, tier):
        crafted = self.cm.craft_stone(tier)
        note =  f"<span style='color: {CONSTANTS.STONE_COLOR};'>{crafted[0]}x{crafted[1]}</span>"
        self.add_log("制作", f"T{tier} {note}")
        self.craft_calculator(tier)

    def craft_stone_button(self):
        self.stone_craft(self.get_curr_tier())
        self.load_best_sequence()
        self.load_craft_sequences()

    def back_switch_craft(self, tier):
        crafted = self.cm.craft_back_switch(tier)
        craft = '反切'
        if crafted:
            amount = crafted[1]
            color = CONSTANTS.QUALITIY_COLORS[crafted[0]]
            note =  f"<span style='color: {color};'>{craft}x{amount}</span>"
        else:
            amount = 1
            note = f"{craft}x{amount}"
        self.add_log("制作", f"T{tier} {note}")
        self.craft_calculator(tier)

    def craft_back_switch_button(self):
        self.back_switch_craft(self.get_curr_tier())
        self.load_best_sequence()
        self.load_craft_sequences()

    def get_best_sequence(self, tier):
        return self.cm.get_best_sequence(tier)

    def _craft_stone(self, craft_active, sequence_indices):
        for i in range(5):
            if i != craft_active:
                sequence_indices[i] = sequence_indices[i]+1
        return (craft_active+1)%5, sequence_indices, ['石头', -1, 1, False], 0

    def _craft_item(self, tier, craft_active, sequence_indices, sequences):
        marked = self.cm.get_sequence_mark(tier, craft_active)
        curr_sequence = sequences[craft_active]
        result_index = sequence_indices[craft_active]
        if result_index < len(curr_sequence):
            craft_result = curr_sequence[result_index]
            quality = craft_result[0]
            amount = craft_result[1]
            score = self.cm.get_quality_score(tier, quality) * amount
            for i in range(5):
                sequence_indices[i] = sequence_indices[i] + 1
        return craft_active, sequence_indices, [None, quality, amount, marked], score

    def _craft_back_switch(self, tier, craft_active, sequence_indices, sequences):
        craft_active = (craft_active - 1)%5 #更新
        sequence_indices[craft_active] += 1  #多消耗一个
        a, s, res, score = self._craft_item(tier, craft_active, sequence_indices, sequences)
        res[0] = '反切'
        return a, s, res, score

    def craft_calculator(self, tier):
        memo = {}
        sequences = self.cm.get_craft_sequences(tier)
        unvisibles = CONSTANTS.unvisibles(tier, self.cm.get_back_switch(tier))
        stone_switchable = CONSTANTS.SWITCHABLES[tier][0]
        back_switchable = self.cm.get_back_switch(tier)
        def dfs(sequence_indices, craft_active, memo):
            # tracked
            key = (craft_active, tuple(sequence_indices))
            if key in memo:
                return memo[key]
            if stone_switchable or back_switchable:
            # any sequence reaches end
                for i in range(5):
                    unv = unvisibles[(i-craft_active)%5]
                    if sequence_indices[i] >= (len(self.cm.get_craft_sequence(tier,i))-unv):
                        memo[key] = (0, [])
                        return 0, []
            else:
                if sequence_indices[self.cm.get_craft_active(tier)] >= (len(self.cm.get_craft_sequence(tier,self.cm.get_craft_active(tier)))):
                    memo[key] = (0, [])
                    return 0, []
            # craft item
            active, indices, res, score = self._craft_item(tier, craft_active, sequence_indices[:], sequences)
            crafted = dfs(indices, active, memo)
            full_score = crafted[0] + score
            full_sequence = [res] + crafted[1]
            # craft stone
            if stone_switchable:
                active, indices, res, score = self._craft_stone(craft_active, sequence_indices[:])
                crafted = dfs(indices, active, memo)
                if crafted[0] + score > full_score:
                    full_score = crafted[0] + score 
                    full_sequence = [res] + crafted[1]
            # craft back-switch
            if back_switchable:
                active, indices, res, score = self._craft_back_switch(tier, craft_active, sequence_indices[:], sequences)
                crafted = dfs(indices, active, memo)
                _score = crafted[0] + score * self.cm.get_back_switch_rate(tier)
                if _score > full_score:
                    full_score = _score 
                    full_sequence = [res] + crafted[1]
            memo[key] = (full_score, full_sequence)
            return full_score, full_sequence
            
        result = dfs([0,0,0,0,0], self.cm.get_craft_active(tier), memo) #(score, sequence)
        best_sequence =  result[1] # (craft, quality, amount, marked)
        self.cm.update_best_sequence(tier, best_sequence)
        return best_sequence

    def calculate_best_sequence(self):
        self.craft_calculator(self.get_curr_tier()) # (craft, quality, amount, marked)
        self.load_best_sequence()
        
    def get_sequence_mark(self, i):
        return self.cm.get_sequence_mark(self.get_curr_tier(), i)

    def mark_sequence(self):
        tier = self.get_curr_tier()
        checkbox = self.sender()
        i = checkbox.property('sequence_index')
        checked = checkbox.isChecked()
        self.cm.update_sequence_mark(tier, i, checked)
        self.load_sequence_icon(i, checkbox)
        self.calculate_best_sequence()

    def add_log(self, action, description):
        time = datetime.now().strftime(CONSTANTS.LOG_TIME_FORMAT)
        self.cm.add_log((time, action, description))
        self.status_bar.setText(self.cm.get_last_log())
        self.load_logs()

    def load_sequence_icon(self, i, checkbox):
        checkbox.setChecked(self.get_sequence_mark(i))
        icon = QIcon(CONSTANTS.MARK_ICON) if checkbox.isChecked() else QIcon()
        checkbox.setIcon(icon)

    def best_sequence_warning(self, tier):
        if CONSTANTS.SWITCHABLES[tier][0] or self.cm.get_back_switch(tier):
            seq_lst = []
            for i in range(5):
                if len(self.cm.get_craft_sequence(tier, i)) <= 4:
                    seq_lst.append(self.get_button_name(tier, i))
            if len(seq_lst) > 0:
                return f"<span style='color: #ff0000;'>序列过短可能导致最优序列计算有误，请延长T{tier}序列:<br> {", ".join(seq_lst)}</span><br>"
        return ""
    
    def format_best_sequence(self, tier):
        sequence = self.get_best_sequence(tier)
        warning = self.best_sequence_warning(tier)
        result = []
        for rec in sequence:
            if len(rec) < 4:
                marked = ""
            else:
                marked = f"<img src='{CONSTANTS.MARK_ICON}' width=12 height=12 >" if rec[3] else ""
            quality = rec[1]
            craft = rec[0] if rec[0] else CONSTANTS.QUALITIES[quality] #石头/反切/品质
            amount = rec[2]
            color = CONSTANTS.STONE_COLOR if craft == '石头' else CONSTANTS.QUALITIY_COLORS[quality] 
            result.append((craft, amount, color, marked))
        text = " -> ".join([f"<span style='color: {color};'>{marked}{craft}x{amount}</span>" for craft, amount, color, marked in result])
        return warning + text
    
    def load_best_sequence(self):
        text = self.format_best_sequence(self.get_curr_tier())
        self.best_sequence_display.setText(text)
        self.load_summary_page()

    def load_summary_displays(self):
        for i in range(4):
            self.load_summary_display(i)

    def load_summary_display(self, i):
        display = self.findChild(QTextBrowser, f"best_sequence_display_{i}")
        tier = display.property('tier')
        display.setText(self.format_best_sequence(tier))
        
        epic = self.findChild(QLabel, f"craft_summary_tier_epic_{i}")
        if self.cm.epic_to_be_craft(tier):
            epic.show()
        else:
            epic.hide()

        legendary = self.findChild(QLabel, f"craft_summary_tier_legendary_{i}")
        if self.cm.legendary_to_be_craft(tier):
            legendary.show()
        else:
            legendary.hide()

    def load_summary_page(self):
        tiers = self.get_summary_tiers()
        for i in range(4):
            tier_selector = self.findChild(QComboBox, f"craft_summary_tier_selection_box_{i}")
            tier_selector.blockSignals(True)
            tier_selector.setCurrentText(str(tiers[i]))
            tier_selector.blockSignals(False)
            self.summary_tier_change(i, tiers[i])

    def load_craft_page(self):
        # load tier selection
        self.tier_selection_dropbox.blockSignals(True)
        self.tier_selection_dropbox.setCurrentText(str(self.get_curr_tier()))
        self.tier_selection_dropbox.blockSignals(False)
        # load quality scores
        self.load_quality_scores()
        # load back-switch settings
        self.back_switch_checkbox.setChecked(self.get_back_switch())
        self.back_switch_rate_selection.blockSignals(True)
        self.back_switch_rate_selection.setValue(self.get_back_switch_rate())
        self.back_switch_rate_selection.blockSignals(False)
        # load craft sequences
        self.load_craft_sequences()
        self.load_craft_sequence_button_style()
        # load best_sequence
        self.load_best_sequence()
        # hide objects
        if CONSTANTS.SWITCHABLES[self.get_curr_tier()][1]:
            self.back_switch_checkbox.show()
        else:
            self.back_switch_checkbox.hide() 
        
        if CONSTANTS.SWITCHABLES[self.get_curr_tier()][0]:
            self.craft_stone.show()
        else:
            self.craft_stone.hide()       
        
        if self.get_back_switch():
            self.back_switch_rate_selection.show()
            self.back_switch_rate_label.show()
            self.craft_back_switch_item.show()
        else:
            self.back_switch_rate_selection.hide()
            self.back_switch_rate_label.hide()
            self.craft_back_switch_item.hide()  

    def load_craft_sequence_button_style(self):
        for i in range(5):
            button = self.findChild(QPushButton, f"sequence_button_{i}")
            if i == self.craft_input_active:
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

    def load_craft_sequences(self):
        for i in range(5):
            self.load_craft_sequence(i)

    def get_stone_index(self, tier, i):
        return (i - self.cm.get_craft_active(tier)) % 5
    
    def get_backswitch_index(self, tier, i):
        return (self.cm.get_craft_active(tier) - i) % 5

    def get_button_name(self, tier, i):
        backswitch_index = self.get_backswitch_index(tier, i)
        stone_index = self.get_stone_index(tier, i)

        backswitch = self.cm.get_back_switch(tier)
        stone = CONSTANTS.SWITCHABLES[tier][0]

        if not stone and not backswitch:
            return "序列"
        elif stone and not backswitch:
            return f"石头x{stone_index}"
        elif not stone and backswitch:
            return f"反切x{backswitch_index}"
        else:
            if stone_index > 2:
                return f"反切x{backswitch_index}"
            else:
                return f"石头x{stone_index}"
            
    def load_craft_sequence(self, i):
        # button
        button = self.findChild(QPushButton, f"sequence_button_{i}") 
        button.setText(self.get_button_name(self.get_curr_tier(), i))

        # constants
        backswitch = self.get_back_switch()
        stone_index = self.get_stone_index(self.get_curr_tier(),i)
        unv = CONSTANTS.unvisibles(self.get_curr_tier(),backswitch)[stone_index]

        
        # count label
        sequence = self.get_craft_sequence(i)
        count_label = self.findChild(QLabel, f"sequence_{i}_count_label")
        count_label.setText(f"共 {len(sequence)-unv} 个")
        # sequence_display
        text = " | ".join([f"<span style='color: {CONSTANTS.QUALITIY_COLORS[q]};'>{CONSTANTS.QUALITIES[q]}x{a}</span>" for q, a in sequence[unv:]])
        sequence_display_label = self.findChild(QTextBrowser, f"sequence_{i}_display")
        sequence_display_label.setText(text)
        # sequence mark checkbox
        checkbox = self.findChild(QCheckBox, f"sequence_{i}_mark")
        self.load_sequence_icon(i, checkbox)

        # hide if not switchable
        if CONSTANTS.SWITCHABLES[self.get_curr_tier()][0] or self.get_back_switch() or i==self.get_craft_active():
            button.show()
            count_label.show()
            sequence_display_label.show()
            checkbox.show()
        else:
            button.hide()
            count_label.hide()
            sequence_display_label.hide()
            checkbox.hide()

    def load_quality_scores(self):
        quality_scores = self.get_curr_quality_scores()
        for i in range(5):
            spinbox = self.findChild(QSpinBox, f"quality_{i}_score")
            if spinbox:
                spinbox.blockSignals(True)
                spinbox.setValue(quality_scores[i])
                spinbox.blockSignals(False)

    def load_logs(self):
        logs = self.cm.data['logs']
        text = '<h3>操作日志</h3>'
        for log in logs:
            text += '<br>' #new line
            for element in log:
                text += element + '    '
        self.log_display.setText(text)

    def load_enchantment_sequence(self, quality):
        display = self.findChild(QTextBrowser, f"enchantment_sequence_{quality}")
        label = self.findChild(QLabel, f"enchantment_count_label_{quality}")
        color = CONSTANTS.QUALITIY_COLORS[quality]
        sequence = self.get_enchantment_log(quality)
        res = []
        for result in sequence:
            if result:
                res.append( f"<span style='color:{color};'>成功</span>")
            else:
                res.append( "失败")
        text = " | ".join(res)
        display.setText(text)
        label.setText(f"共 {len(res)} 次")

    def load_enchantment_sequences(self):
        for i in range(1,5):
            self.load_enchantment_sequence(i)

    def load_enchantment_result(self):
        res = self.cm.get_enchantment_result()
        ret = []
        if res:
            quality = res[0]
            amount = 1
            i = 1
            while i < len(res):
                if res[i] == quality:
                    amount += 1
                else: 
                    color = CONSTANTS.QUALITIY_COLORS[quality]
                    quality_text = CONSTANTS.QUALITIES[quality]
                    ret.append(f"<span style='color:{color};'>{quality_text}x{amount}</span>")
                    quality = res[i]
                    amount = 1
                i += 1
            color = CONSTANTS.QUALITIY_COLORS[quality]
            quality_text = CONSTANTS.QUALITIES[quality]
            ret.append(f"<span style='color:{color};'>{quality_text}x{amount}</span>")
        text = " -> ".join(ret)
        self.enchantment_result.setText(text)

    def load_enchantment_page(self):
        self.load_enchantment_result()
        self.load_enchantment_sequences()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())