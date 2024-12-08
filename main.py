# main.py

import sys
from PyQt5.QtWidgets import QApplication
import qdarkstyle
from gui.main_window import MainWindow
import config  # Import config if not already imported

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    modules_available = ["MODER", "RECONR", "BROADR", "HEATR"]
    window = MainWindow(modules_available)
    window.show()
    sys.exit(app.exec_())
