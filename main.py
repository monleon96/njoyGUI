import sys
from PyQt5.QtWidgets import QApplication
import qdarkstyle

from gui.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    
    # For now, we only have 'moder' available
    modules_available = ["moder"]

    window = MainWindow(modules_available)
    window.show()
    sys.exit(app.exec_())
