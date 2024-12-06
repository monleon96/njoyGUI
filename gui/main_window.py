from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QMessageBox, QSplitter, QListWidget, QListWidgetItem, QFrame, QFileDialog, 
    QAction
)
from PyQt5.QtCore import Qt

from model import load_module
from gui.module_item import ModuleItem
from gui.module_selection_dialog import ModuleSelectionDialog
from gui.parameter_dialog import ParameterDialog

class MainWindow(QMainWindow):
    def __init__(self, modules_available):
        super().__init__()
        self.setWindowTitle("NJOY Input Builder")
        self.setGeometry(100, 100, 800, 600)
        
        # List of added modules: each element will be a dict
        # with keys: {'name': str, 'parameters': dict, 'cards': list}
        self.modules_available = modules_available
        self.added_modules = []  # Each element: {"name":..., "cards":..., "parameters": {...}}

        self.init_ui()

    def init_ui(self):
        # Main container widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter()
        main_layout.addWidget(splitter)

        # Left side: module list and add button
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.add_module_btn = QPushButton("Add Module")
        self.add_module_btn.clicked.connect(self.add_module)
        left_layout.addWidget(self.add_module_btn)

        # Container for module items
        self.module_list_container = QVBoxLayout()
        self.module_list_container.setSpacing(5)
        self.module_list_container.setAlignment(Qt.AlignTop)

        # A frame with a scroll area might be ideal for many modules. For simplicity:
        scroll_frame = QFrame()
        scroll_frame.setLayout(self.module_list_container)

        # Make it scrollable if many modules:
        from PyQt5.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_frame)
        scroll_area.setWidgetResizable(True)
        left_layout.addWidget(scroll_area)

        # Generate NJOY Input button
        self.generate_btn = QPushButton("Generate NJOY Input")
        self.generate_btn.clicked.connect(self.generate_njoy_input)
        left_layout.addWidget(self.generate_btn)

        # Add left_widget to splitter
        splitter.addWidget(left_widget)

        # Right side: preview text
        from PyQt5.QtWidgets import QTextEdit
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.update_preview()
        splitter.addWidget(self.preview_text)

        splitter.setSizes([300, 500])

    def add_module(self):
        dialog = ModuleSelectionDialog(self.modules_available, self)
        if dialog.exec_():
            selected_module = dialog.get_selected_module()
            if selected_module:
                # Load module definition
                mod_model = load_module(selected_module)
                # Initialize parameters dict from defaults
                parameters = {}
                for card in mod_model.cards:
                    for param in card["parameters"]:
                        parameters[param["name"]] = param.get("default", None)
                
                module_dict = {
                    "name": mod_model.module_name,
                    "cards": mod_model.cards,
                    "parameters": parameters
                }
                self.added_modules.append(module_dict)
                self.add_module_item(module_dict)
                self.update_preview()

    def add_module_item(self, module_dict):
        item_widget = ModuleItem(module_dict["name"], self)
        item_widget.module_up.connect(lambda: self.move_module_up(item_widget))
        item_widget.module_down.connect(lambda: self.move_module_down(item_widget))
        item_widget.module_remove.connect(lambda: self.remove_module(item_widget))
        item_widget.module_edit.connect(lambda: self.edit_module_parameters(item_widget))
        
        self.module_list_container.addWidget(item_widget)
        item_widget.show()

    def remove_module(self, item_widget):
        # Find index of this module in added_modules
        idx = self.index_of_module_item(item_widget)
        if idx >= 0:
            self.added_modules.pop(idx)
            self.module_list_container.removeWidget(item_widget)
            item_widget.deleteLater()
            self.update_preview()

    def move_module_up(self, item_widget):
        idx = self.index_of_module_item(item_widget)
        if idx > 0:
            # swap
            self.added_modules[idx], self.added_modules[idx-1] = self.added_modules[idx-1], self.added_modules[idx]
            # Reorder widgets
            self.reorder_module_items()
            self.update_preview()

    def move_module_down(self, item_widget):
        idx = self.index_of_module_item(item_widget)
        if idx < len(self.added_modules)-1:
            # swap
            self.added_modules[idx], self.added_modules[idx+1] = self.added_modules[idx+1], self.added_modules[idx]
            # Reorder widgets
            self.reorder_module_items()
            self.update_preview()

    def reorder_module_items(self):
        # Clear and re-add all items in order
        for i in reversed(range(self.module_list_container.count())):
            widget = self.module_list_container.itemAt(i).widget()
            self.module_list_container.removeWidget(widget)
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
            dialog = ParameterDialog(mod_dict["name"], mod_dict["cards"], mod_dict["parameters"], self)
            if dialog.exec_():
                # Update parameters
                updated_params = dialog.get_parameters()
                mod_dict["parameters"] = updated_params
                self.update_preview()

    def update_preview(self):
        # Construct NJOY input from added_modules
        lines = []
        for mod in self.added_modules:
            lines.append(mod["name"])
            # For this example, we know moder has "nin" and "nout"
            # In general, you'd loop over cards and parameters.
            # Just for demonstration:
            nin = mod["parameters"].get("nin", 20)
            nout = mod["parameters"].get("nout", -21)
            lines.append(f"{nin} {nout} /")
        preview_text = "\n".join(lines)
        self.preview_text.setText(preview_text)

    def generate_njoy_input(self):
        # Ask user where to save the file
        file_dialog = QFileDialog.getSaveFileName(self, "Save NJOY Input", "input.njoy", "All Files (*.*)")
        if file_dialog[0]:
            with open(file_dialog[0], 'w') as f:
                f.write(self.preview_text.toPlainText())
            QMessageBox.information(self, "Success", f"NJOY input saved to {file_dialog[0]}")
