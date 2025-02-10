from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic


import db.constants as CONSTANTS
import sys
import os 

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'main_window.ui')
        uic.loadUi(ui_path, self)

        self.updates_label.setText(CONSTANTS.fetch_updates())
        self.readme_label.setText(CONSTANTS.fetch_readme())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec())