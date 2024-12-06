from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QMessageBox, QSplitter, QScrollArea, QTextEdit, QFileDialog
)
from PyQt5.QtCore import Qt

from model import load_module, load_isotopes
from gui.module_item import ModuleItem
from gui.module_selection_dialog import ModuleSelectionDialog
from gui.parameter_dialog import ParameterDialog

class MainWindow(QMainWindow):
    def __init__(self, modules_available):
        super().__init__()
        self.setWindowTitle("NJOY Input Builder")
        self.setGeometry(100, 100, 800, 600)
        
        self.modules_available = modules_available
        self.added_modules = []
        
        # Load isotopes once
        self.isotopes = load_isotopes()

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter()
        main_layout.addWidget(splitter)

        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        self.add_module_btn = QPushButton("Add Module")
        self.add_module_btn.clicked.connect(self.add_module)
        left_layout.addWidget(self.add_module_btn)

        self.module_list_container = QVBoxLayout()
        self.module_list_container.setSpacing(5)
        self.module_list_container.setAlignment(Qt.AlignTop)

        scroll_frame = QWidget()
        scroll_frame.setLayout(self.module_list_container)
        scroll_area = QScrollArea()
        scroll_area.setWidget(scroll_frame)
        scroll_area.setWidgetResizable(True)
        left_layout.addWidget(scroll_area)

        self.generate_btn = QPushButton("Generate NJOY Input")
        self.generate_btn.clicked.connect(self.generate_njoy_input)
        left_layout.addWidget(self.generate_btn)

        splitter.addWidget(left_widget)

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
                mod_model = load_module(selected_module)
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
            dialog = ParameterDialog(mod_dict["name"], mod_dict["cards"], mod_dict["parameters"], self)
            if dialog.exec_():
                updated_params = dialog.get_parameters()
                mod_dict["parameters"] = updated_params
                self.update_preview()

    def update_preview(self):
        lines = []
        for mod in self.added_modules:
            name = mod["name"]
            p = mod["parameters"]
            if name == "moder":
                nin = p.get("nin", 20)
                nout = p.get("nout", -21)
                lines.append("moder")
                lines.append(f"{nin} {nout} /")

            elif name == "reconr":
                nendf = p.get("nendf", 20)
                npend = p.get("npend", 21)
                isotope = p.get("material", "U235")
                tolerance = p.get("tolerance", 0.001)
                
                mat = self.isotopes.get(isotope, 9999)
                errmax = p.get("errmax", None)
                errint = p.get("errint", None)

                label = f"reconstructed data for {isotope}"
                tempr = 0 if errmax is not None else 0

                lines.append("reconr")
                lines.append(f"{nendf} {npend} /")
                lines.append(f"'{label}' /")
                lines.append(f"{mat} 0 0 /")

                # card 4
                card4 = f"{tolerance}"
                if tempr is not None:
                    card4 += f" {tempr}"
                if errmax is not None:
                    card4 += f" {errmax}"
                if errint is not None:
                    card4 += f" {errint}"
                card4 += " /"
                lines.append(card4)

                lines.append("0 /")

        preview_text = "\n".join(lines)
        self.preview_text.setText(preview_text)

    def generate_njoy_input(self):
        file_dialog = QFileDialog.getSaveFileName(self, "Save NJOY Input", "input.njoy", "All Files (*.*)")
        if file_dialog[0]:
            with open(file_dialog[0], 'w') as f:
                f.write(self.preview_text.toPlainText())
            QMessageBox.information(self, "Success", f"NJOY input saved to {file_dialog[0]}")
