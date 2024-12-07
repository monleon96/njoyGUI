# main.py

import sys
from PyQt5.QtWidgets import QApplication

import qdarkstyle

from gui.main_window import MainWindow
import config  # Import the configuration module

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # **Set a Base Font for the Entire Application**
    base_font = config.get_base_font()
    app.setFont(base_font)
    
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    # Now we have both MODER and RECONR modules
    modules_available = ["MODER", "RECONR"]

    window = MainWindow(modules_available)
    window.show()
    sys.exit(app.exec_())
