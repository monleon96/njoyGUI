# parameter_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QMessageBox, QLineEdit, QSpinBox, QDoubleSpinBox, 
    QComboBox, QGroupBox, QWidget
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QFont

from model import load_isotopes
import config  # Import the configuration module

class ParameterDialog(QDialog):
    def __init__(self, module_name, cards, parameters, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit Parameters: {module_name}")
        self.resize(600, 400)
        self.module_name = module_name
        self.cards = cards
        self.parameters = parameters.copy()

        self.param_widgets = {}

        self.isotopes = load_isotopes()

        # Display name mapping
        self.display_names = {
            # moder
            "nin": "Input tape",
            "nout": "Output tape",
            # reconr
            "nendf": "Input tape",
            "npend": "Output tape",
            "mat": "Isotope",
            "err": "Tolerance",
            "errmax": "Errmax",
            "errint": "Errint"
        }

        # **Set Larger Font for the Entire Dialog**
        dialog_font = config.get_dialog_font()
        self.setFont(dialog_font)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        pdf_btn = QPushButton("View Manual")
        pdf_btn.setFont(config.get_button_font())  # Set font for 'View Manual' button
        pdf_btn.clicked.connect(self.open_pdf)
        top_layout.addStretch()
        top_layout.addWidget(pdf_btn)
        layout.addLayout(top_layout)

        # Separate parameters by card name (Mandatory, Optional, etc.)
        # We'll create QGroupBoxes for each "category" of parameters.
        # In reconr.json, we have "Mandatory", "Optional", "Automatic".
        # For moder, we only have one card (no optional section).

        # Create a dictionary of card_name -> list of parameters
        card_map = {}
        for card in self.cards:
            card_name = card["name"]
            card_map.setdefault(card_name, []).extend(card["parameters"])

        # We'll create a group box for each card_name except 'Automatic'
        for card_name, param_list in card_map.items():
            if card_name == "Automatic":
                # Automatic parameters are not shown to user
                continue

            group_box = QGroupBox(card_name)
            group_box.setFont(config.get_label_font())  # Ensure group box title uses the dialog font
            group_layout = QFormLayout()

            for param in param_list:
                p_name = param["name"]
                p_type = param["type"]
                p_default = self.parameters.get(p_name, param.get("default", None))
                p_help = param.get("help", "")

                # Create widget
                widget = self.create_widget_for_type(p_type, p_default, p_name)

                # **Set Font for the Widget**
                widget.setFont(config.get_label_font())

                # Add help button if help text available
                h_layout = QHBoxLayout()
                h_layout.addWidget(widget)
                if p_help:
                    help_btn = QPushButton("?")
                    help_btn.setFixedWidth(25)
                    help_btn.setFont(config.get_help_button_font())  # Set font for help button
                    help_btn.clicked.connect(lambda checked, text=p_help: self.show_param_help(text))
                    h_layout.addWidget(help_btn)
                # Create a container widget for the row
                row_widget = QWidget()
                row_widget.setLayout(h_layout)

                display_label = self.display_names.get(p_name, p_name)
                label = QLabel(display_label + ":")
                label.setFont(config.get_label_font())  # Set font for label
                group_layout.addRow(label, row_widget)

                if p_type != "auto":
                    self.param_widgets[p_name] = (widget, p_help)

            group_box.setLayout(group_layout)
            layout.addWidget(group_box)

        # Spacer for bottom
        layout.addStretch()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setFont(config.get_button_font())  # Ensure button box uses the dialog font
        button_box.accepted.connect(self.accept_parameters)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_widget_for_type(self, p_type, p_default, p_name):
        if p_type == "int":
            spin = QSpinBox()
            spin.setRange(-9999, 9999)
            if p_default is not None:
                spin.setValue(int(p_default))
            spin.setFont(config.get_label_font())  # Set font for QSpinBox
            return spin
        elif p_type == "float":
            dspin = QDoubleSpinBox()
            dspin.setRange(0.0, 9999.0)
            dspin.setDecimals(6)
            if p_default is not None:
                dspin.setValue(float(p_default))
            dspin.setFont(config.get_label_font())  # Set font for QDoubleSpinBox
            return dspin
        elif p_type == "isotope":
            combo = QComboBox()
            isotope_list = sorted(self.isotopes.keys())
            combo.addItems(isotope_list)
            if p_default in isotope_list:
                combo.setCurrentText(p_default)
            combo.setFont(config.get_label_font())  # Set font for QComboBox
            return combo
        elif p_type == "auto":
            # no widget
            label = QLabel("(Automatically set)")
            label.setFont(config.get_label_font())  # Set font for QLabel
            return label
        else:
            line = QLineEdit()
            if p_default is not None:
                line.setText(str(p_default))
            line.setFont(config.get_label_font())  # Set font for QLineEdit
            return line

    def show_param_help(self, text):
        QMessageBox.information(self, "Parameter Help", text)

    def accept_parameters(self):
        for p_name, (widget, help_text) in self.param_widgets.items():
            if isinstance(widget, QSpinBox):
                self.parameters[p_name] = widget.value()
            elif isinstance(widget, QDoubleSpinBox):
                self.parameters[p_name] = widget.value()
            elif isinstance(widget, QComboBox):
                self.parameters[p_name] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                self.parameters[p_name] = widget.text()
        self.accept()

    def get_parameters(self):
        return self.parameters

    def open_pdf(self):
        pdf_path = f"resources/{self.module_name}.pdf"
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path)):
            QMessageBox.warning(self, "PDF not found", f"Could not open {pdf_path}. Ensure the file exists.")
