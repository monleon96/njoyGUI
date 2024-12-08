# parameter_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox, 
    QGroupBox, QWidget, QCompleter, QListView
)
from PyQt5.QtCore import Qt, QUrl, QRegExp
from PyQt5.QtGui import QDesktopServices, QRegExpValidator, QIntValidator, QFont

from model import load_isotopes
import config
from functools import partial

class ParameterDialog(QDialog):
    def __init__(self, module_name, cards, parameters, parent=None,  module_description=""):
        super().__init__(parent)
        self.module_name = module_name
        self.cards = cards
        self.parameters = parameters.copy()
        self.module_description = module_description
        self.param_widgets = {}
        self.isotopes = load_isotopes()
        self.resize(600, 400) 

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
            "tempr": "Temperature",
            # broadr
            'temp2': "Temperature"
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
            # A regex that matches a positive float, optionally in scientific notation
            float_regex = QRegExp(r'^\d+(\.\d+)?([eE][+-]?\d+)?$')
            val = QRegExpValidator(float_regex, self)
            line.setValidator(val)

            # If there's a default value, set it
            if p_value is not None:
                line.setText(str(p_value))
            else:
                line.setText("")

        elif p_type == "isotope":
            # Create your QComboBox
            combo = QComboBox()
            isotope_list = sorted(self.isotopes.keys())

            combo.setEditable(True)
            combo.addItem("")
            combo.addItems(isotope_list)

            # Set the font for the combo box and the line edit as before
            font = config.get_label_font()
            combo.setFont(font)
            combo.lineEdit().setFont(font)

            if p_value is not None:
                combo.setCurrentText(str(p_value))
            else:
                combo.setCurrentText("")

            # Assign a custom QListView to the combo
            view = QListView()
            view.setFont(font)
            combo.setView(view)

            # Set up the completer as needed
            completer = QCompleter(isotope_list, combo)
            completer.setCaseSensitivity(Qt.CaseSensitive)
            completer.setFilterMode(Qt.MatchContains)
            combo.setCompleter(completer)

            return combo

        elif p_type == "multi":
            widget = self.create_multi_widget(p_value)
            return widget

        elif p_type == "auto":
            label = QLabel("(Automatically set)")
            label.setFont(config.get_label_font())
            return label

        # For all QLineEdit widgets (including float/temperature inputs)
        line.setFont(config.get_label_font())
        
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
        for p_name, (widget, help_text) in self.param_widgets.items():
            p_def = self.find_parameter_definition(p_name)
            p_type = p_def["type"]
            constraints = p_def.get("constraints", {})

            if p_type == "multi":
                # Handle the multi-type widget
                lines = []
                for edit in widget.line_edits:
                    val_str = edit.text().strip()
                    if val_str:
                        try:
                            val = float(val_str)
                        except ValueError:
                            self.show_error(f"{p_name} values must be numeric.")
                            return
                        # Check min/max constraints for each entry
                        if "min" in constraints and val < constraints["min"]:
                            self.show_error(f"{p_name} must be >= {constraints['min']}")
                            return
                        if "max" in constraints and val > constraints["max"]:
                            self.show_error(f"{p_name} must be <= {constraints['max']}")
                            return
                        lines.append(val_str)
                        
                if len(lines) == 0:
                    self.parameters.pop(p_name, None)
                else:
                    self.parameters[p_name] = " ".join(lines)

            if isinstance(widget, QLineEdit):
                value_str = widget.text().strip()
                if value_str == "":
                    self.parameters.pop(p_name, None)
                else:
                    if p_type == "int":
                        # value_str should pass the validator, so it's an integer
                        value = int(value_str)

                        # Check min/max constraints
                        if "min" in constraints and value < constraints["min"]:
                            self.show_error(f"{p_name} must be >= {constraints['min']}")
                            return
                        if "max" in constraints and value > constraints["max"]:
                            self.show_error(f"{p_name} must be <= {constraints['max']}")
                            return
                        self.parameters[p_name] = value

                    elif p_type == "float":
                        try:
                            value = float(value_str)
                        except ValueError:
                            self.show_error(f"{p_name} is not a valid number.")
                            return
                        # Check min/max constraints
                        if "min" in constraints and value < constraints["min"]:
                            self.show_error(f"{p_name} must be >= {constraints['min']}")
                            return
                        if "max" in constraints and value > constraints["max"]:
                            self.show_error(f"{p_name} must be <= {constraints['max']}")
                            return
                        self.parameters[p_name] = value

            elif isinstance(widget, QComboBox):
                value = widget.currentText().strip()
                if value == "":
                    self.parameters.pop(p_name, None)
                else:
                    self.parameters[p_name] = value

        if self.module_name.lower() == "broadr":
            temp2_str = self.parameters.get("temp2", "")
            if temp2_str == "":
                self.parameters.pop("ntemp2", None)
            else:
                temps = temp2_str.split()
                self.parameters["ntemp2"] = len(temps)

        self.accept()


    def get_parameters(self):
        return self.parameters

    def find_parameter_definition(self, p_name):
        for card in self.cards:
            for param in card["parameters"]:
                if param["name"] == p_name:
                    return param
        return None

    def show_error(self, message):
        QMessageBox.warning(self, "Invalid Input", message)

    def open_pdf(self):
        pdf_path = f"resources/{self.module_name}.pdf"
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path)):
            QMessageBox.warning(self, "PDF not found", f"Could not open {pdf_path}. Ensure the file exists.")


    def create_multi_widget(self, p_value):
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(5)

        container.line_edits = []

        def add_line(value=""):
            line_layout = QHBoxLayout()
            line_edit = QLineEdit()
            line_edit.setText(value)
            line_edit.setFont(config.get_label_font())
            remove_btn = QPushButton("x")
            remove_btn.setFixedWidth(25)
            remove_btn.setFont(config.get_label_font()) 

            def remove_line():
                v_layout.removeItem(line_layout)
                line_layout.removeWidget(line_edit)
                line_layout.removeWidget(remove_btn)
                line_edit.deleteLater()
                remove_btn.deleteLater()
                container.line_edits.remove(line_edit)

            remove_btn.clicked.connect(remove_line)

            line_layout.addWidget(line_edit)
            line_layout.addWidget(remove_btn)
            v_layout.addLayout(line_layout)
            container.line_edits.append(line_edit)

        # Initialize the lines from p_value
        values = str(p_value).split() if p_value else []
        for val in values:
            add_line(val)

        # If no default given, start with one empty line or just skip:
        if not values:
            add_line("")

        add_btn = QPushButton("+")
        add_btn.setFixedWidth(25)
        add_btn.setFont(config.get_label_font())  # Opcional: también aplicar la fuente al botón de añadir
        add_btn.clicked.connect(lambda: add_line(""))
        v_layout.addWidget(add_btn, 0, Qt.AlignLeft)

        return container