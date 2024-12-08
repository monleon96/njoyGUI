# parameter_dialog.py

from PyQt5.QtWidgets import (
    QDialog, QFormLayout, QDialogButtonBox, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QMessageBox, QLineEdit, QComboBox, 
    QGroupBox, QWidget, QCompleter, QListView, QScrollArea
)
from PyQt5.QtCore import Qt, QUrl, QRegExp
from PyQt5.QtGui import QDesktopServices, QRegExpValidator, QIntValidator, QFont

from model import load_isotopes
import config
from config import get_dialog_element_font  # Import the new font function
from config import get_button_style, BUTTON_HOVER_COLOR

class ParameterDialog(QDialog):
    def __init__(self, module_name, cards, parameters, parent=None,  module_description=""):
        super().__init__(parent)
        self.module_name = module_name
        self.cards = cards
        self.parameters = parameters.copy()
        self.module_description = module_description
        self.param_widgets = {}
        self.isotopes = load_isotopes()
        self.setFixedSize(600, 600)

        # Set default font size 10 for the entire dialog
        self.setFont(get_dialog_element_font())

        self.init_ui()

    def apply_button_style(self, button):
        """Helper method to apply consistent button styling"""
        button.setStyleSheet(get_button_style())

    def init_ui(self):
        # Create main layout
        main_layout = QVBoxLayout(self)

        # Create a container widget to hold all the widgets
        container_widget = QWidget()
        container_layout = QVBoxLayout(container_widget)

        # Add a button to view the manual
        top_layout = QHBoxLayout()
        pdf_btn = QPushButton("View Manual")
        pdf_btn.setFont(config.get_button_font())
        pdf_btn.setFixedWidth(120)  # Set a fixed width for the button
        self.apply_button_style(pdf_btn)
        pdf_btn.clicked.connect(self.open_pdf)
        top_layout.addStretch()
        top_layout.addWidget(pdf_btn)
        container_layout.addLayout(top_layout)

        # Create a dictionary of card_name -> list of parameters
        card_map = {}
        for card in self.cards:
            card_name = card["name"]
            card_map.setdefault(card_name, []).extend(card["parameters"])

        for card_name, param_list in card_map.items():
            if (card_name == "Automatic"):
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
                p_display_name = param.get("display_name", p_name)

                # Determine the displayed value:
                # If user previously set this param, use that.
                # Else use JSON default if available.
                # If none, leave blank for optional parameters.
                if p_name in self.parameters:
                    p_value = self.parameters[p_name]
                else:
                    p_value = p_default

                widget = self.create_widget_for_type(p_type, p_value, p_name, p_constraints, card_name)
                widget.setFont(get_dialog_element_font())

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

                label = QLabel(p_display_name + ":")
                label.setFont(get_dialog_element_font())
                group_layout.addRow(label, row_widget)

                if p_type != "auto":
                    self.param_widgets[p_name] = (widget, p_help)

            group_box.setLayout(group_layout)
            container_layout.addWidget(group_box)

        container_layout.addStretch()

        # Creamos un QScrollArea y establecemos el widget contenedor
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(container_widget)

        # Añadimos el QScrollArea y los botones al layout principal
        main_layout.addWidget(scroll_area)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.setFont(config.get_button_font())
        # Set a larger font for OK and Cancel buttons
        for button in button_box.buttons():
            font = button.font()
            font.setPointSize(font.pointSize() + 2)  # Increase font size by 2 points
            button.setFont(font)
            self.apply_button_style(button)
        button_box.accepted.connect(self.accept_parameters)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)

    def create_widget_for_type(self, p_type, p_value, p_name, p_constraints, card_name):
        # All parameters now use QLineEdit.
        line = QLineEdit()

        if p_type == "int":
            # Integer validator that respects only defined constraints
            min_val = p_constraints.get("min", -2147483647)  # Use Python's min int as default
            max_val = p_constraints.get("max", 2147483647)   # Use Python's max int as default
            int_validator = QIntValidator(min_val, max_val, self)
            line.setValidator(int_validator)

        elif p_type == "float":
            # A regex that matches a positive float, optionally in scientific notation
            float_regex = QRegExp(r'^\d+(\.\d+)?([eE][+-]?\d+)?$')
            val = QRegExpValidator(float_regex, self)
            line.setValidator(val)

            if p_value is not None:
                if isinstance(p_value, str):
                    line.setText(p_value)
            else:
                line.setText("")

        elif p_type == "option":
            container = QWidget()
            layout = QHBoxLayout(container)
            layout.setContentsMargins(0, 0, 0, 0)
            
            # Create a button group to manage exclusive selection
            button_group = []
            
            # Create toggle buttons for each option
            options = p_constraints.get("options", ["Option1", "Option2", "Option3"])
            for option in options:
                btn = QPushButton(option)
                btn.setCheckable(True)
                btn.setAutoExclusive(True)
                btn.setFont(config.get_dialog_element_font())  # Set font
                # Modified style to keep hover color when checked
                base_style = get_button_style()
                btn.setStyleSheet(f"{base_style}\nQPushButton:checked {{background-color: {BUTTON_HOVER_COLOR.name()};}}")
                if p_value == option:
                    btn.setChecked(True)
                button_group.append(btn)
                layout.addWidget(btn)
                
            # Add clear button
            clear_btn = QPushButton("x")
            clear_btn.setFixedWidth(25)
            clear_btn.setFont(config.get_dialog_element_font())  # Set font
            self.apply_button_style(clear_btn)
            
            def clear_selection():
                # Temporarily disable auto-exclusive behavior
                for btn in button_group:
                    btn.setAutoExclusive(False)
                    btn.setChecked(False)
                    btn.setAutoExclusive(True)
                    
            clear_btn.clicked.connect(clear_selection)
            layout.addWidget(clear_btn)
            
            # Store buttons in the container for later access
            container.buttons = button_group
            return container

        elif p_type == "isotope":
            combo = QComboBox()
            isotope_list = sorted(self.isotopes.keys())

            combo.setEditable(True)
            combo.addItem("")
            combo.addItems(isotope_list)

            # Set the font for the combo box and the line edit
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

            # Set up the completer
            completer = QCompleter(isotope_list, self)
            completer.setCaseSensitivity(Qt.CaseSensitive)
            completer.setFilterMode(Qt.MatchContains)
            completer.popup().setFont(font)
            combo.setCompleter(completer)

            # Store the valid items list in the combo box
            combo.valid_items = isotope_list

            return combo

        elif p_type == "multi":
            widget = self.create_multi_widget(p_value, p_name)
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
                    if p_type == "isotope" and value not in widget.valid_items:
                        self.show_error(f"'{value}' is not a valid isotope.")
                        return
                    self.parameters[p_name] = value

            elif p_type == "option":
                # Handle the option-type widget with toggle buttons
                selected_value = None
                for btn in widget.buttons:
                    if btn.isChecked():
                        selected_value = btn.text()
                        break
                if selected_value:
                    self.parameters[p_name] = selected_value
                else:
                    self.parameters.pop(p_name, None)

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


    def create_multi_widget(self, p_value, p_name):
        container = QWidget()
        v_layout = QVBoxLayout(container)
        v_layout.setContentsMargins(0, 0, 0, 0)
        v_layout.setSpacing(5)

        container.line_edits = []

        def get_current_values():
            return [edit.text().strip() for edit in container.line_edits if edit.text().strip()]

        def validate_value(value):
            if not value:
                return True
            try:
                val = float(value)
                # Check constraints from parameter definition
                p_def = self.find_parameter_definition(p_name)
                constraints = p_def.get("constraints", {})
                if "min" in constraints and val < constraints["min"]:
                    QMessageBox.warning(container, "Invalid Value", 
                                    f"Value must be >= {constraints['min']}")
                    return False
                if "max" in constraints and val > constraints["max"]:
                    QMessageBox.warning(container, "Invalid Value", 
                                    f"Value must be <= {constraints['max']}")
                    return False
            except ValueError:
                QMessageBox.warning(container, "Invalid Value", 
                                "Please enter a valid number")
                return False
                
            current_values = get_current_values()
            return value not in current_values

        def create_value_line(value):
            line_layout = QHBoxLayout()
            line_edit = QLineEdit()
            # Preserve scientific notation if present
            if isinstance(value, str) and 'e' in value.lower():
                line_edit.setText(value)  # Keep original format
            else:
                line_edit.setText(str(value))
            line_edit.setFont(config.get_label_font())
            
            remove_btn = QPushButton("x")
            remove_btn.setFixedWidth(25)
            remove_btn.setFont(config.get_label_font())
            self.apply_button_style(remove_btn)
            
            def remove_line():
                v_layout.removeItem(line_layout)
                line_edit.deleteLater()
                remove_btn.deleteLater()
                container.line_edits.remove(line_edit)
            
            remove_btn.clicked.connect(remove_line)
            
            line_layout.addWidget(line_edit)
            line_layout.addWidget(remove_btn)
            v_layout.addLayout(line_layout)
            container.line_edits.append(line_edit)
            
        def on_add():
            text = input_line.text().strip()
            if text and validate_value(text):
                create_value_line(text)
                input_line.setText("")
            elif text and text in get_current_values():
                QMessageBox.warning(container, "Duplicate Value", 
                                 "This value is already in the list!")
        
        input_layout = QHBoxLayout()
        input_line = QLineEdit()
        input_line.setFont(config.get_label_font())
        # Override key press event to fully capture Enter
        def keyPressEvent(event):
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                on_add()
                event.accept()  # Prevent propagation
            else:
                QLineEdit.keyPressEvent(input_line, event)  # Handle other keys normally
                
        input_line.keyPressEvent = keyPressEvent
        
        add_btn = QPushButton("Add")
        add_btn.setFixedWidth(50)
        add_btn.setFont(config.get_label_font())
        self.apply_button_style(add_btn)
        
        add_btn.clicked.connect(on_add)
        
        # Add the input line with Add button at the top
        input_layout.addWidget(input_line)
        input_layout.addWidget(add_btn)
        v_layout.addLayout(input_layout)
        
        # Initialize existing values below the input line
        values = str(p_value).split() if p_value else []
        for val in values:
            create_value_line(val)

        return container