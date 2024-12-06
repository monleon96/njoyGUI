from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

class ModuleItem(QWidget):
    module_up = pyqtSignal()
    module_down = pyqtSignal()
    module_remove = pyqtSignal()
    module_edit = pyqtSignal()

    def __init__(self, module_name, parent=None):
        super().__init__(parent)
        self.module_name = module_name
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        self.label = QLabel(self.module_name)
        layout.addWidget(self.label)

        # Edit button
        edit_btn = QPushButton("Edit")
        edit_btn.clicked.connect(self.module_edit.emit)
        layout.addWidget(edit_btn)

        # Move up button
        up_btn = QPushButton("Up")
        up_btn.clicked.connect(self.module_up.emit)
        layout.addWidget(up_btn)

        # Move down button
        down_btn = QPushButton("Down")
        down_btn.clicked.connect(self.module_down.emit)
        layout.addWidget(down_btn)

        # Remove button
        remove_btn = QPushButton("Remove")
        remove_btn.clicked.connect(self.module_remove.emit)
        layout.addWidget(remove_btn)
