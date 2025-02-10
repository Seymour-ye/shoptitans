from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic

import os 

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        ui_path = os.path.join(os.path.dirname(__file__), 'ui', 'main_window.ui')
        uic.loadUi(ui_path, self)

        self.load_updates()

        self.pushButton.clicked.connect(self.on_button_click)

    def on_button_click(self):
        self.label.setText('按钮已点击！')


app = QApplication(sys.argv)
window = MainApp()
window.show()
sys.exit(app.exec())