from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, 
    QWidget, QGroupBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt

class ModuleSelectionDialog(QDialog):
    def __init__(self, modules_available, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Module")
        self.resize(400, 300)  # Make the dialog bigger
        self.modules_available = modules_available
        self.selected_module = None

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        title_label = QLabel("Choose a module to add:")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setSpacing(10)

        # Create a nice button or frame for each module
        for mod in self.modules_available:
            mod_button = QPushButton(mod)
            mod_button.setStyleSheet("font-size: 14px; padding: 10px;")
            mod_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            mod_button.clicked.connect(lambda checked, m=mod: self.select_module(m))
            scroll_layout.addWidget(mod_button)

        # Add some space at the bottom
        scroll_layout.addStretch()
        scroll_area.setWidget(container)

        # Optional: a cancel button at the bottom
        bottom_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addStretch()
        bottom_layout.addWidget(cancel_btn)
        layout.addLayout(bottom_layout)

    def select_module(self, module_name):
        self.selected_module = module_name
        self.accept()

    def get_selected_module(self):
        return self.selected_module
