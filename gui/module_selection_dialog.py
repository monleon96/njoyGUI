from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox

class ModuleSelectionDialog(QDialog):
    def __init__(self, modules_available, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Module")
        self.modules_available = modules_available
        self.selected_module = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        label = QLabel("Choose a module to add:")
        layout.addWidget(label)

        self.combo = QComboBox()
        for m in self.modules_available:
            self.combo.addItem(m)
        layout.addWidget(self.combo)

        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.ok_pressed)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def ok_pressed(self):
        self.selected_module = self.combo.currentText()
        self.accept()

    def get_selected_module(self):
        return self.selected_module
