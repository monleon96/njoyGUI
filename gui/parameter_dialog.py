from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QSpinBox, QDialogButtonBox, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox
)
from PyQt5.QtCore import Qt

class ParameterDialog(QDialog):
    def __init__(self, module_name, cards, parameters, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Parameters: {module_name}")
        self.module_name = module_name
        self.cards = cards
        self.parameters = parameters.copy()  # Copy so we only update on accept

        self.param_widgets = {}  # name -> widget
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        top_layout = QHBoxLayout()
        help_btn = QPushButton("?")
        help_btn.setFixedWidth(30)
        help_btn.clicked.connect(self.show_help)
        top_layout.addStretch()
        top_layout.addWidget(help_btn)
        layout.addLayout(top_layout)

        form_layout = QFormLayout()
        # For each parameter in cards, create a suitable input
        for card in self.cards:
            for param in card["parameters"]:
                pname = param["name"]
                ptype = param["type"]
                pdefault = self.parameters.get(pname, param.get("default", 0))

                # We'll assume int => use QSpinBox for simplicity
                if ptype == "int":
                    spin = QSpinBox()
                    spin.setRange(-99, 99)
                    spin.setValue(int(pdefault))
                    self.param_widgets[pname] = spin
                    form_layout.addRow(f"{pname}:", spin)
                else:
                    # For other types in future, handle accordingly
                    pass

        layout.addLayout(form_layout)

        # Ok/Cancel buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept_parameters)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def accept_parameters(self):
        # Validate and store
        for pname, widget in self.param_widgets.items():
            if isinstance(widget, QSpinBox):
                val = widget.value()
                self.parameters[pname] = val
        self.accept()

    def get_parameters(self):
        return self.parameters

    def show_help(self):
        # Show help text extracted from cards description
        help_text = f"Module: {self.module_name}\n\n"
        for card in self.cards:
            help_text += f"{card['name']}: {card['description']}\n"
            for p in card["parameters"]:
                help_text += f"  {p['name']}: {p['description']}\n"
        QMessageBox.information(self, "Help", help_text)
