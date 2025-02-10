from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic

import markdown
import db.constants as CONSTANTS
import sys
import os 

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'main_window.ui')
        uic.loadUi(ui_path, self)

        self.updates_label.setText(markdown.markdown(CONSTANTS.fetch_updates()))


app = QApplication(sys.argv)
window = MainApp()
window.show()
sys.exit(app.exec())