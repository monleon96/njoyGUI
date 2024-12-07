# parameter_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox, 
    QGroupBox, QWidget, QCompleter
)
from PyQt5.QtCore import Qt, QUrl, QRegExp
from PyQt5.QtGui import QDesktopServices, QRegExpValidator, QIntValidator, QFont

from model import load_isotopes
import config
from functools import partial

class ParameterDialog(QDialog):
    def __init__(self, module_name, cards, parameters, parent=None,  module_description=""):
        super().__init__(parent)
        
        self.setWindowTitle(f"Edit Parameters: {module_name}")
        self.resize(600, 400)
        self.module_name = module_name
        self.cards = cards
        self.parameters = parameters.copy()
        self.module_description = module_description  # Store the description

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
            "errint": "Errint",
            "tempr": "Temperature"
        }

        # Set Larger Font for the Entire Dialog
        dialog_font = config.get_dialog_font()
        self.setFont(dialog_font)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        top_layout = QHBoxLayout()
        pdf_btn = QPushButton("View Manual")
        pdf_btn.setFont(config.get_button_font())
        pdf_btn.clicked.connect(self.open_pdf)
        top_layout.addStretch()
        top_layout.addWidget(pdf_btn)
        layout.addLayout(top_layout)

        # Create a dictionary of card_name -> list of parameters
        card_map = {}
        for card in self.cards:
            card_name = card["name"]
            card_map.setdefault(card_name, []).extend(card["parameters"])

        for card_name, param_list in card_map.items():
            if card_name == "Automatic":
                continue
            group_box = QGroupBox(card_name)
            group_box.setFont(config.get_label_font())
            group_layout = QFormLayout()

            for param in param_list:
                p_name = param["name"]
                p_type = param["type"]
                p_default = param.get("default", None)
                p_constraints = param.get("constraints", {})
                p_help = param.get("help", "")

                # Determine the displayed value:
                # If user previously set this param, use that.
                # Else use JSON default if available.
                # If none, leave blank for optional parameters.
                if p_name in self.parameters:
                    p_value = self.parameters[p_name]
                else:
                    p_value = p_default

                widget = self.create_widget_for_type(p_type, p_value, p_name, p_constraints, card_name)
                widget.setFont(config.get_label_font())

                h_layout = QHBoxLayout()
                h_layout.addWidget(widget)
                if p_help:
                    help_btn = QPushButton("?")
                    help_btn.setFixedWidth(25)
                    help_btn.setFont(config.get_help_button_font())
                    help_btn.clicked.connect(lambda checked, text=p_help: self.show_param_help(text))
                    h_layout.addWidget(help_btn)
                row_widget = QWidget()
                row_widget.setLayout(h_layout)

                display_label = self.display_names.get(p_name, p_name)
                label = QLabel(display_label + ":")
                label.setFont(config.get_label_font())
                group_layout.addRow(label, row_widget)

                if p_type != "auto":
                    self.param_widgets[p_name] = (widget, p_help)

            group_box.setLayout(group_layout)
            layout.addWidget(group_box)

        layout.addStretch()

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setFont(config.get_button_font())
        button_box.accepted.connect(self.accept_parameters)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def create_widget_for_type(self, p_type, p_value, p_name, p_constraints, card_name):
        # All parameters now use QLineEdit.
        line = QLineEdit()

        if p_type == "int":
            # Integer validator
            min_val = p_constraints.get("min", -99)
            max_val = p_constraints.get("max", 99)
            int_validator = QIntValidator(min_val, max_val, self)
            line.setValidator(int_validator)

        elif p_type == "float":
            # Float validator
            float_regex = QRegExp(r'^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$')
            val = QRegExpValidator(float_regex, self)
            line.setValidator(val)

        elif p_type == "isotope":
            # For isotopes, use QComboBox
            combo = QComboBox()
            isotope_list = sorted(self.isotopes.keys())
            combo.setEditable(True)
            combo.addItem("")  # empty option
            combo.addItems(isotope_list)

            if p_value is not None:
                combo.setCurrentText(str(p_value))
            else:
                combo.setCurrentText("")

            completer = QCompleter(isotope_list, combo)
            completer.setCaseSensitivity(Qt.CaseSensitive)
            completer.setFilterMode(Qt.MatchContains)
            combo.setCompleter(completer)

            return combo

        elif p_type == "auto":
            label = QLabel("(Automatically set)")
            label.setFont(config.get_label_font())
            return label

        # For mandatory parameters with defaults, set value.
        # For optional without defaults, leave blank.
        if p_value is not None:
            line.setText(str(p_value))
        else:
            line.setText("")

        return line

    def validate_selection(self, combo, isotope_list, text):
        if text in isotope_list or text == "":
            combo._previous_valid_text = text
        else:
            combo.setCurrentText(combo._previous_valid_text)

    def show_param_help(self, text):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Parameter Help")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(text)  # text can now contain HTML tags for formatting
        msg_box.setIcon(QMessageBox.NoIcon)

        # Use a similar font as module help
        custom_font = QFont("Arial", 11)
        msg_box.setFont(custom_font)

        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def show_module_help(self):
        """
        Display the module's description in a QMessageBox with rich text formatting.
        """
        if not self.module_description:
            help_text = "<b>No description available for this module.</b>"
        else:
            # Assuming module_description can contain HTML formatting
            help_text = self.module_description

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"{self.module_name} - Description")
        msg_box.setTextFormat(Qt.RichText)
        msg_box.setText(help_text)
        msg_box.setIcon(QMessageBox.NoIcon)

        # Set a readable font
        custom_font = QFont("Arial", 12)
        msg_box.setFont(custom_font)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()

    def accept_parameters(self):
        # Collect all inputs
        for p_name, (widget, help_text) in self.param_widgets.items():
            if isinstance(widget, QLineEdit):
                value = widget.text().strip()
                if value == "":
                    self.parameters.pop(p_name, None)
                else:
                    self.parameters[p_name] = value

            elif isinstance(widget, QComboBox):
                value = widget.currentText().strip()
                if value == "":
                    self.parameters.pop(p_name, None)
                else:
                    self.parameters[p_name] = value

        self.accept()

    def get_parameters(self):
        return self.parameters

    def open_pdf(self):
        pdf_path = f"resources/{self.module_name}.pdf"
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path)):
            QMessageBox.warning(self, "PDF not found", f"Could not open {pdf_path}. Ensure the file exists.")
