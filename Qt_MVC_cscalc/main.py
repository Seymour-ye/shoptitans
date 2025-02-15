# Modules
import db.constants as CONSTANTS
from db.ConfigManager import ConfigManager

# Functionalities
import sys

# PyQt6
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWidgets import QSpinBox, QPushButton, QLabel, QTextBrowser, QCheckBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from PyQt6 import uic

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(CONSTANTS.UI_PATH, self)
        self.cm = ConfigManager()

        #CONSTANTS ADJUSTMENT
        self.tier_selection_dropbox.addItems([str(i) for i in range(CONSTANTS.MAX_TIER, 0, -1)])
        self.craft_input_active = 0
        self.multi_entry = 1

        # SET HOME PANE CONTENTS
        self.updates_display.setText(CONSTANTS.fetch_updates())
        self.readme_display.setText(CONSTANTS.fetch_readme())
        self.load_logs()
        self.load_craft_page()

        # SET CRAFT PANE ACTIONS
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
        # window-on-top
        self.window_on_top_checkbox.stateChanged.connect(self.window_on_top)
        # craft buttons
        self.craft_back_switch_item.clicked.connect(self.craft_back_switch_button)
        self.craft_item.clicked.connect(self.craft_item_button)
        self.craft_stone.clicked.connect(self.craft_stone_button)

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

    def input_sequence_activate(self):
        self.craft_input_active = self.sender().property('sequence_index')
        self.load_craft_sequence_button_style()

    def backspace(self):
        self.cm.sequence_log_backspace(self.get_curr_tier(), self.craft_input_active)
        self.load_craft_sequence(self.craft_input_active)

    def clear_sequences(self):
        self.cm.reset_sequences(self.get_curr_tier())
        self.load_craft_sequences()

    def craft_item_button(self):
        self.cm.craft_item(self.get_curr_tier())
        self.load_craft_sequences()

    def craft_stone_button(self):
        self.cm.craft_stone(self.get_curr_tier())
        self.load_craft_sequences()

    def craft_back_switch_button(self):
        self.cm.craft_back_switch(self.get_curr_tier())
        self.load_craft_sequences()

    def get_best_sequence(self, tier):
        return self.cm.get_best_sequence(tier)

    def _craft_stone(self, craft_active, sequence_indices):
        for i in range(5):
            if i != craft_active:
                sequence_indices[i] = sequence_indices[i]+1
        return (craft_active+1)%5, sequence_indices, ['石头', -1, 1], 0

    def _craft_item(self, tier, craft_active, sequence_indices, sequences):
        curr_sequence = sequences[craft_active]
        result_index = sequence_indices[craft_active]
        if result_index < len(curr_sequence):
            craft_result = curr_sequence[result_index]
            quality = craft_result[0]
            amount = craft_result[1]
            score = self.cm.get_quality_score(tier, quality) * amount
            for i in range(5):
                sequence_indices[i] = sequence_indices[i] + 1
        return craft_active, sequence_indices, [None, quality, amount], score

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
                    if sequence_indices[i] >= (len(self.get_craft_sequence(i))-unv):
                        memo[key] = (0, [])
                        return 0, []
            else:
                if sequence_indices[0] >= (len(self.get_craft_sequence(0))):
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
        return result[1] # (craft, quality, amount)

    def calculate_best_sequence(self):
        result = self.craft_calculator(self.get_curr_tier()) # (craft, quality, amount)
        self.cm.update_best_sequence(self.get_curr_tier(), result)
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

    def load_sequence_icon(self, i, checkbox):
        checkbox.setChecked(self.get_sequence_mark(i))
        icon = QIcon(CONSTANTS.MARK_ICON) if checkbox.isChecked() else QIcon()
        checkbox.setIcon(icon)

    def load_best_sequence(self):
        best_sequence = self.get_best_sequence(self.get_curr_tier())
        result = []
        for rec in best_sequence:
            quality = rec[1]
            craft = rec[0] if rec[0] else CONSTANTS.QUALITIES[quality] #石头/反切/品质
            amount = rec[2]
            color = '#AAAAAA' if craft == '石头' else CONSTANTS.QUALITIY_COLORS[quality] 
            result.append((craft, amount, color))
        text = " -> ".join([f"<span style='color: {color};'>{craft}x{amount}</span>" for craft, amount, color in result])
        self.best_sequence_display.setText(text)

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
            
    def load_craft_sequence(self, i):
        # button
        button = self.findChild(QPushButton, f"sequence_button_{i}") 
        backswitch_index = (self.get_craft_active() - i) % 5
        stone_index = (i - self.get_craft_active()) % 5

        # constants
        backswitch = self.get_back_switch()
        stone = CONSTANTS.SWITCHABLES[self.get_curr_tier()][0]
        unv = CONSTANTS.unvisibles(self.get_curr_tier(),backswitch)[stone_index]

        if not stone and not backswitch:
            button.setText("序列")
        elif (stone and not backswitch):     
            button.setText(f"石头x{stone_index}")
        elif not stone and backswitch:
            button.setText(f"反切x{backswitch_index}")
        else:
            if stone_index > 2:
                button.setText(f"反切x{backswitch_index}")
            else:
                button.setText(f"石头x{stone_index}")
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
        if CONSTANTS.SWITCHABLES[self.get_curr_tier()][0] or self.get_back_switch() or i==0:
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())