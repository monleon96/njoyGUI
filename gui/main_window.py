# main_window.py

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QMessageBox, QSplitter, QScrollArea, QTextEdit, QFileDialog,
    QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from model import load_module, load_json_source
from gui.module_item import ModuleItem
from gui.module_selection_dialog import ModuleSelectionDialog
from gui.parameter_dialog import ParameterDialog
import config 
from config import get_large_button_font, get_dialog_font  
import json 

class MainWindow(QMainWindow):
    def __init__(self, modules_available):
        super().__init__()
        self.setWindowTitle("NJOY Input Builder")
        self.setGeometry(100, 100, 900, 700)
        
        self.modules_available = modules_available
        self.added_modules = []
        
        # Load json files
        self.isotopes = load_json_source("resources/isotopes.json")
        self.energies = load_json_source("resources/energies.json")

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

        # Add buttons container for horizontal layout BEFORE add_module_btn
        buttons_container = QHBoxLayout()
        
        self.save_config_btn = QPushButton("Save Workflow")
        self.save_config_btn.setMinimumSize(120, 30)  # Slightly smaller height
        save_load_font = QFont()
        save_load_font.setPointSize(config.LARGE_BUTTON_FONT_SIZE - 1)  # One point smaller
        self.save_config_btn.setFont(save_load_font)
        self.save_config_btn.clicked.connect(self.save_configuration)
        
        self.load_config_btn = QPushButton("Load Workflow")
        self.load_config_btn.setMinimumSize(120, 30)  # Slightly smaller height
        self.load_config_btn.setFont(save_load_font)
        self.load_config_btn.clicked.connect(self.load_configuration)
        
        buttons_container.addWidget(self.save_config_btn)
        buttons_container.addWidget(self.load_config_btn)
        
        left_layout.addLayout(buttons_container)

        self.add_module_btn = QPushButton("Add Module")
        self.add_module_btn.setMinimumSize(120, 35)
        # **Set Font for 'Add Module' Button**
        self.add_module_btn.setFont(config.get_button_font())
        self.add_module_btn.setFont(get_large_button_font())
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
        self.generate_btn.setFont(get_large_button_font())
        self.generate_btn.clicked.connect(self.generate_njoy_input)
        left_layout.addWidget(self.generate_btn)

        left_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        splitter.addWidget(left_widget)

        # Right panel
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Set larger font for preview text
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

                # Handle temperature parameters for both BROADR and PURR
                if mod_model.module_name.lower() in ["broadr", "purr"]:
                    temp_param = "temp2" if mod_model.module_name.lower() == "broadr" else "temp"
                    if isinstance(parameters.get(temp_param), (int, float)):
                        parameters[temp_param] = str(parameters[temp_param])
                    if not parameters.get(temp_param, '').strip():
                        parameters[temp_param] = "293.6"

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
                module_description 
            )
            if dialog.exec_():
                updated_params = dialog.get_parameters()
                # Convert temperature parameter to string for PURR
                if mod_dict["name"].lower() == "purr":
                    temp_param = "temp"
                    if isinstance(updated_params.get(temp_param), (int, float)):
                        updated_params[temp_param] = str(updated_params[temp_param])
                    if not updated_params.get(temp_param, '').strip():
                        updated_params[temp_param] = "293.6"
                self.added_modules[idx]["parameters"] = updated_params
                self.update_preview()

    def update_preview(self):
        lines = []
        for mod in self.added_modules:
            name = mod["name"]
            p = mod["parameters"]

            if name == "MODER":
                # Card 1
                nin = p.get("nin", "")
                nout = p.get("nout", "")

                # Build the MODER module
                lines.append("moder")
                lines.append(f"{nin} {nout}")

            elif name == "RECONR":
                # Card 1
                nendf = p.get("nendf", "")
                npend = p.get("npend", "")

                # Card 2 (label)
                isotope = p.get("mat", "U235")
                mat = self.isotopes.get(isotope, 9228)
                
                # Get tempr value from parameters, use 0 as default for label
                tempr = p.get("tempr")
                try:
                    if tempr is not None:
                        tempr = float(tempr)
                    else:
                        tempr = 0.0
                except (ValueError, TypeError):
                    tempr = 0.0
                
                # Always show temperature in label
                label = f'reconstructed data for {isotope} @ {tempr} K'

                # Card 3
                tolerance_str = p.get("err", "0.001")
                tolerance = float(tolerance_str)

                # Get optional parameters
                user_errmax = p.get("errmax")
                user_errint = p.get("errint")

                # Build Card 4 with dependencies (keep tempr optional in card 4)
                card4_parts = [str(tolerance)]
                if user_errint is not None:
                    if user_errmax is None:
                        user_errmax = 10 * tolerance
                    card4_parts.extend([str(p.get("tempr", 0.0)), str(user_errmax), str(user_errint)])
                elif user_errmax is not None:
                    card4_parts.extend([str(p.get("tempr", 0.0)), str(user_errmax)])
                elif p.get("tempr") is not None:
                    card4_parts.append(str(tempr))

                card4_line = " ".join(card4_parts) + " /"

                # Build the RECONR module
                lines.append("-- reconstruct, linearise and unionize data")
                lines.append("reconr")
                lines.append(f"{nendf} {npend}")
                lines.append(f"{label} /")
                lines.append(f"{mat} /")
                lines.append(card4_line)
                lines.append("0 /")

            elif name == "BROADR":
                # Card 1
                nendf = p.get("nendf", "")
                nin = p.get("nin", "")
                nout = p.get("nout", "")

                # Card 2
                mat_str = p.get("mat", "U235")
                mat_num = self.isotopes.get(mat_str, 9228)
                temp2_str = p.get("temp2", "")
                temps = temp2_str.split()
                ntemp2 = len(temps)

                # Card 3 parameters
                errthn_str = p.get("errthn", "0.001")
                errthn = float(errthn_str)
                user_thnmax = p.get("thnmax")
                user_errmax = p.get("errmax")
                user_errint = p.get("errint")

                # Build Card 3 with dependencies
                card3_parts = [str(errthn)]
                if user_errint is not None:
                    if user_errmax is None:
                        user_errmax = 10 * errthn
                    if user_thnmax is None:
                        user_thnmax = 1
                    card3_parts.extend([str(user_thnmax), str(user_errmax), str(user_errint)])
                elif user_errmax is not None:
                    if user_thnmax is None:
                        user_thnmax = 1
                    card3_parts.extend([str(user_thnmax), str(user_errmax)])
                elif user_thnmax is not None:
                    card3_parts.append(str(user_thnmax))

                card3_line = " ".join(card3_parts) + " /"

                # Build the BROADR module
                lines.append("-- calculate doppler broadening")
                lines.append("broadr")
                lines.append(f"{nendf} {nin} {nout}")
                lines.append(f"{mat_num} {ntemp2} /")
                lines.append(card3_line)
                if ntemp2 > 0:
                    lines.append(" ".join(temps) + " /")
                lines.append("0 /")

            elif name == "HEATR":
                # Card 1
                nendf = p.get("nendf", "")
                nin = p.get("nin", "")
                nout = p.get("nout", "")
                nplot = p.get("nplot") or "0"  # Set default value to "0" if None or empty

                # Card 2 mandatory parameters
                mat_str = p.get("matd", "U235")
                mat_num = self.isotopes.get(mat_str, 9228)
                mtk_str = p.get("mtk", "")
                mtk_list = str(mtk_str).split()
                npk = len(mtk_list)

                # Handle optional Card 2 parameters
                user_ed = p.get("ed")
                user_iprint = p.get("iprint")
                user_local = p.get("local")
                
                # Convert text options to numbers - simplified iprint handling
                if user_iprint == "min":
                    iprint = 0
                elif user_iprint == "max":
                    iprint = 1
                else:
                    iprint = None

                if user_local == "Transported":
                    local = 0
                elif user_local == "Deposited":
                    local = 1
                else:
                    local = None

                # Build Card 2 based on rightmost specified parameter
                card2_parts = [str(mat_num), str(npk)]
                
                if user_ed is not None:
                    # If ed is specified, include all parameters
                    card2_parts.extend([
                        "0",  # nqa
                        "0",  # ntemp
                        str(local if local is not None else 0),
                        str(iprint if iprint is not None else 0),
                        str(user_ed)
                    ])
                elif user_iprint is not None:
                    # If iprint is specified (but not ed), include up to iprint
                    card2_parts.extend([
                        "0",  # nqa
                        "0",  # ntemp
                        str(local if local is not None else 0),
                        str(iprint)
                    ])
                elif user_local is not None:
                    # If only local is specified, include up to local
                    card2_parts.extend([
                        "0",  # nqa
                        "0",  # ntemp
                        str(local)
                    ])

                # Build the HEATR module
                lines.append("-- calculate heating values")
                lines.append("heatr")
                lines.append(f"{nendf} {nin} {nout} {nplot}")
                lines.append(" ".join(card2_parts) + " /")
                if npk > 0:
                    lines.append(" ".join(mtk_list) + " /")

            elif name == "PURR":
                # Card 1
                nendf = p.get("nendf", "")
                nin = p.get("nin", "")
                nout = p.get("nout", "")

                # Card 2
                mat_str = p.get("matd", "U235")
                mat_num = self.isotopes.get(mat_str, 9228)
                
                # Process temperatures
                temp_str = str(p.get("temp", ""))  # Ensure temp is a string
                temps = temp_str.split()
                ntemp = len(temps)
                
                # Process sigma zero values
                sigz_str = str(p.get("sigz", ""))  # Ensure sigz is a string
                sigz_values = sigz_str.split()
                nsigz = len(sigz_values)
                
                # Get optional parameters
                nbin = p.get("nbin", "20")
                nladr = p.get("nladr", "64")
                user_iprint = p.get("iprint")
                nunx = p.get("nunx")
                
                # Convert text options to numbers - fixed iprint handling
                if user_iprint == "min":
                    iprint = 0
                elif user_iprint == "max":
                    iprint = 1
                else:
                    iprint = None
                    
                # Build card 2 parameters
                card2_parts = [str(mat_num), str(ntemp), str(nsigz), str(nbin), str(nladr)]
                
                # Add iprint and nunx if either is specified
                if nunx is not None or user_iprint is not None:
                    card2_parts.append(str(iprint if iprint is not None else "1"))
                    card2_parts.append(str(nunx if nunx is not None else ""))

                # Build the PURR module
                lines.append("-- calculate ptables")
                lines.append("purr")
                lines.append(f"{nendf} {nin} {nout}")
                lines.append(" ".join(card2_parts) + " /")
                if ntemp > 0:
                    lines.append(" ".join(temps) + " /")
                if nsigz > 0:
                    lines.append(" ".join(sigz_values) + " /")
                lines.append("0 /")
            
            elif name == "UNRESR":
                # Card 1
                nendf = p.get("nendf", "")
                nin = p.get("nin", "")
                nout = p.get("nout", "")

                # Card 2
                mat_str = p.get("matd", "U235")
                mat_num = self.isotopes.get(mat_str, 9228)
                
                # Process temperatures
                temp_str = str(p.get("temp", ""))  # Ensure temp is a string
                temps = temp_str.split()
                ntemp = len(temps)
                
                # Process sigma zero values
                sigz_str = str(p.get("sigz", ""))  # Ensure sigz is a string
                sigz_values = sigz_str.split()
                nsigz = len(sigz_values)
                
                # Get optional parameters
                user_iprint = p.get("iprint")
                
                # Convert text options to numbers - fixed iprint handling
                if user_iprint == "min":
                    iprint = 0
                elif user_iprint == "max":
                    iprint = 1
                else:
                    iprint = None
                    
                # Build card 2 parameters
                card2_parts = [str(mat_num), str(ntemp), str(nsigz)]
                
                # Add iprint and nunx if either is specified
                if user_iprint is not None:
                    card2_parts.append(str(iprint if iprint is not None else "0"))

                # Build the unresr module
                lines.append("-- calculate unresolved shelf-shielding")
                lines.append("unresr")
                lines.append(f"{nendf} {nin} {nout}")
                lines.append(" ".join(card2_parts) + " /")
                if ntemp > 0:
                    lines.append(" ".join(temps) + " /")
                if nsigz > 0:
                    lines.append(" ".join(sigz_values) + " /")
                lines.append("0 /")

            elif name == "GASPR":
                # Card 1
                nendf = p.get("nendf", "")
                nin = p.get("nin", "")
                nout = p.get("nout", "")

                # Build the PURR module
                lines.append("-- calculate production")
                lines.append("gaspr")
                lines.append(f"{nendf} {nin} {nout}")

            elif name == "ACER":
                # Card 1
                nendf = p.get("nendf", "")
                npend = p.get("npend", "")
                ngend = p.get("ngend", "")
                nace = p.get("nace", "")
                ndir = p.get("ndir", "")

                # Process iprint
                user_iprint = p.get("iprint")
                if user_iprint == "min":
                    iprint = 0
                elif user_iprint == "max":
                    iprint = 1
                else:
                    iprint = 1  # default value

                # Get itype and suff
                itype = p.get("itype", 1)
                if itype is None:
                    itype = 1
                suff = p.get("suff", "")
                iopt = p.get("iopt", "")
                suff_trunc = int(suff * 100) / 100 if suff > 0 else suff

                # Get material and temperature
                isotope = p.get("matd", "U235")
                mat_num = self.isotopes.get(isotope, 9228)
                tempd = p.get("tempd", "")

                # Generate automatic hk label
                hk = f"{isotope} @ {tempd} K ACE data"

                # Build the ACER module
                lines.append("-- generate ACE file")
                lines.append("acer")
                lines.append(f"{nendf} {npend} {ngend} {nace} {ndir}")
                lines.append(f"{iopt} {iprint} {itype} {suff_trunc:.2f} /")
                lines.append(f"'{hk}' /")
                lines.append(f"{mat_num} {tempd} /")
                lines.append('/')
                lines.append('/')

            if name == "VIEWR":
                # Card 1
                nin = p.get("infile", "")
                nout = p.get("nps", "")

                # Build the MODER module
                lines.append("-- produce plots")
                lines.append("viewr")
                lines.append(f"{nin} {nout}")

        if lines:
            lines.append("stop")

        preview_text = "\n".join(lines)
        self.preview_text.setText(preview_text)

    def generate_njoy_input(self):
        file_dialog = QFileDialog.getSaveFileName(self, "Save NJOY Input", "input.njoy", "All Files (*.*)")
        if file_dialog[0]:
            with open(file_dialog[0], 'w') as f:
                f.write(self.preview_text.toPlainText())
            msg = QMessageBox(self)
            msg.setFont(get_dialog_font())
            msg.setIcon(QMessageBox.Information)
            msg.setText(f"NJOY input saved to {file_dialog[0]}")
            msg.setWindowTitle("Success")
            msg.exec_()

    def save_configuration(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        if file_path:
            config_data = {
                "modules": self.added_modules
            }
            try:
                with open(file_path, 'w') as f:
                    json.dump(config_data, f, indent=2)
                msg = QMessageBox(self)
                msg.setFont(get_dialog_font())
                msg.setIcon(QMessageBox.Information)
                msg.setText("Configuration saved successfully!")
                msg.setWindowTitle("Success")
                msg.exec_()
            except Exception as e:
                msg = QMessageBox(self)
                msg.setFont(get_dialog_font())
                msg.setIcon(QMessageBox.Critical)
                msg.setText(f"Failed to save configuration: {str(e)}")
                msg.setWindowTitle("Error")
                msg.exec_()

    def load_configuration(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Configuration",
            "",
            "JSON Files (*.json);;All Files (*.*)"
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    config_data = json.load(f)
                
                # Clear existing modules
                self.added_modules.clear()
                for i in reversed(range(self.module_list_container.count())):
                    widget = self.module_list_container.itemAt(i).widget()
                    self.module_list_container.removeWidget(widget)
                    widget.deleteLater()
                
                # Load new modules
                if "modules" in config_data:
                    self.added_modules = config_data["modules"]
                    for module in self.added_modules:
                        self.add_module_item(module)
                    
                self.update_preview()
                msg = QMessageBox(self)
                msg.setFont(get_dialog_font())
                msg.setIcon(QMessageBox.Information)
                msg.setText("Configuration loaded successfully!")
                msg.setWindowTitle("Success")
                msg.exec_()
            except Exception as e:
                msg = QMessageBox(self)
                msg.setFont(get_dialog_font())
                msg.setIcon(QMessageBox.Critical)
                msg.setText(f"Failed to load configuration: {str(e)}")
                msg.setWindowTitle("Error")
                msg.exec_()
