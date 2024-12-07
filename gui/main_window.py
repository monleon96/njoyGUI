# main_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QMessageBox, QSplitter, QScrollArea, QTextEdit, QFileDialog,
    QSizePolicy
)
from PyQt5.QtCore import Qt

from model import load_module, load_isotopes
from gui.module_item import ModuleItem
from gui.module_selection_dialog import ModuleSelectionDialog
from gui.parameter_dialog import ParameterDialog
import config  # Import the configuration module

class MainWindow(QMainWindow):
    def __init__(self, modules_available):
        super().__init__()
        self.setWindowTitle("NJOY Input Builder")
        self.setGeometry(100, 100, 900, 700)
        
        self.modules_available = modules_available
        self.added_modules = []
        
        # Load isotopes once
        self.isotopes = load_isotopes()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)  # Overall margins
        main_layout.setSpacing(10)  # Space between splitter and other elements

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(5, 5, 5, 5)  # Margins inside left panel
        left_layout.setSpacing(5)  # Spacing inside left panel

        self.add_module_btn = QPushButton("Add Module")
        self.add_module_btn.setMinimumSize(120, 35)
        # **Set Font for 'Add Module' Button**
        self.add_module_btn.setFont(config.get_button_font())
        self.add_module_btn.clicked.connect(self.add_module)
        left_layout.addWidget(self.add_module_btn)

        self.module_list_container = QVBoxLayout()
        self.module_list_container.setSpacing(2)  # Reduced spacing between module items
        self.module_list_container.setAlignment(Qt.AlignTop)

        scroll_frame = QWidget()
        scroll_frame.setLayout(self.module_list_container)
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_frame)
        scroll_area.setWidgetResizable(True)
        left_layout.addWidget(scroll_area)

        self.generate_btn = QPushButton("Generate NJOY Input")
        self.generate_btn.setMinimumSize(120, 30)
        # **Set Font for 'Generate NJOY Input' Button**
        self.generate_btn.setFont(config.get_button_font())
        self.generate_btn.clicked.connect(self.generate_njoy_input)
        left_layout.addWidget(self.generate_btn)

        left_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        splitter.addWidget(left_widget)

        # Right panel
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # **Set Larger Font for Preview Text**
        preview_font = config.get_preview_font()
        self.preview_text.setFont(preview_font)
        
        self.update_preview()
        splitter.addWidget(self.preview_text)

        # Set stretch factors
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        splitter.setSizes([330, 570])

    def add_module(self):
        dialog = ModuleSelectionDialog(self.modules_available, self)
        if dialog.exec_():
            selected_module = dialog.get_selected_module()
            if selected_module:
                mod_model = load_module(selected_module)
                parameters = {}
                # Set all parameters from JSON defaults upfront
                for card in mod_model.cards:
                    for param in card["parameters"]:
                        p_name = param["name"]
                        p_default = param.get("default", None)
                        parameters[p_name] = p_default

                # Make sure you include the description from the mod_model
                module_dict = {
                    "name": mod_model.module_name,
                    "description": getattr(mod_model, "description", "No description available."),
                    "cards": mod_model.cards,
                    "parameters": parameters
                }

                self.added_modules.append(module_dict)
                self.add_module_item(module_dict)
                self.update_preview()


    def add_module_item(self, module_dict):
        # Extract module name and description from module_dict
        module_name = module_dict.get("name", "Unnamed Module")
        module_description = module_dict.get("description", "No description available.")
        
        # Create the ModuleItem with name and description
        item_widget = ModuleItem(module_name, module_description, self)
        
        # Connect signals to appropriate slots
        item_widget.module_up.connect(lambda: self.move_module_up(item_widget))
        item_widget.module_down.connect(lambda: self.move_module_down(item_widget))
        item_widget.module_remove.connect(lambda: self.remove_module(item_widget))
        item_widget.module_edit.connect(lambda: self.edit_module_parameters(item_widget))
        
        # Add the widget to the container and show it
        self.module_list_container.addWidget(item_widget)
        item_widget.show()

    def remove_module(self, item_widget):
        idx = self.index_of_module_item(item_widget)
        if idx >= 0:
            self.added_modules.pop(idx)
            self.module_list_container.removeWidget(item_widget)
            item_widget.deleteLater()
            self.update_preview()

    def move_module_up(self, item_widget):
        idx = self.index_of_module_item(item_widget)
        if idx > 0:
            self.added_modules[idx], self.added_modules[idx-1] = self.added_modules[idx-1], self.added_modules[idx]
            self.reorder_module_items()
            self.update_preview()

    def move_module_down(self, item_widget):
        idx = self.index_of_module_item(item_widget)
        if idx < len(self.added_modules)-1:
            self.added_modules[idx], self.added_modules[idx+1] = self.added_modules[idx+1], self.added_modules[idx]
            self.reorder_module_items()
            self.update_preview()

    def reorder_module_items(self):
        # Remove all widgets and re-add them in the new order
        for i in reversed(range(self.module_list_container.count())):
            w = self.module_list_container.itemAt(i).widget()
            self.module_list_container.removeWidget(w)
            w.deleteLater()
        for mod in self.added_modules:
            self.add_module_item(mod)

    def index_of_module_item(self, item_widget):
        for i in range(self.module_list_container.count()):
            w = self.module_list_container.itemAt(i).widget()
            if w == item_widget:
                return i
        return -1

    def edit_module_parameters(self, item_widget):
        idx = self.index_of_module_item(item_widget)
        if idx >= 0:
            mod_dict = self.added_modules[idx]
            module_description = mod_dict.get("description", "No description available.")
            
            # Pass the module_description to ParameterDialog
            dialog = ParameterDialog(
                mod_dict["name"],
                mod_dict["cards"],
                mod_dict["parameters"],
                self,
                module_description  # New argument
            )
            if dialog.exec_():
                updated_params = dialog.get_parameters()
                mod_dict["parameters"] = updated_params
                self.update_preview()

    def update_preview(self):
        lines = []
        for mod in self.added_modules:
            name = mod["name"]
            p = mod["parameters"]

            if name == "MODER":
                nin = p.get("nin")  
                nout = p.get("nout")
                lines.append("moder")
                lines.append(f"{nin} {nout} /")

            elif name == "RECONR":
                nendf = p.get("nendf")
                npend = p.get("npend")
                isotope = p.get("mat", "U235")  
                mat = self.isotopes.get(isotope, 9228)
                tolerance_str = p.get("err")
                tolerance = float(tolerance_str) if tolerance_str is not None else 0.001

                user_tempr = p.get("tempr", None)
                user_errmax = p.get("errmax", None)
                user_errint = p.get("errint", None)

                # Dependency logic
                if user_errint is not None and user_errmax is None:
                    user_errmax = 10 * tolerance
                if user_errmax is not None and user_tempr is None:
                    user_tempr = 0.0

                # Build the RECONR card
                lines.append("reconr")
                lines.append(f"{nendf} {npend} /")
                label = f"reconstructed data for '{isotope}' @ {user_tempr if user_tempr is not None else '0'} K"
                lines.append(f"{label} /")
                lines.append(f"{mat} /")

                card4_parts = [str(tolerance)]
                if user_tempr is not None:
                    card4_parts.append(str(user_tempr))
                if user_errmax is not None:
                    card4_parts.append(str(user_errmax))
                if user_errint is not None:
                    card4_parts.append(str(user_errint))
                card4_line = " ".join(card4_parts) + " /"
                lines.append(card4_line)

                lines.append("0 /")

        if lines:
            lines.append("stop")

        preview_text = "\n".join(lines)
        self.preview_text.setText(preview_text)

    def generate_njoy_input(self):
        file_dialog = QFileDialog.getSaveFileName(self, "Save NJOY Input", "input.njoy", "All Files (*.*)")
        if file_dialog[0]:
            with open(file_dialog[0], 'w') as f:
                f.write(self.preview_text.toPlainText())
            QMessageBox.information(self, "Success", f"NJOY input saved to {file_dialog[0]}")
