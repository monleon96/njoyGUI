from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, 
    QWidget, QGroupBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt
import config 

class ModuleSelectionDialog(QDialog):
    def __init__(self, modules_available, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Module")
        self.resize(400, 300)
        self.modules_available = modules_available
        self.selected_module = None
        self.module_data = {}
        self.load_module_data()

        # Set the base font for the entire dialog
        self.setFont(config.get_base_font())

        self.setStyleSheet("""
            QToolTip {
                background-color: #333333;
                color: white;
                border: none;
                padding: 5px;     
            }
        """)

        self.init_ui()

    def load_module_data(self):
        import json
        import os
        
        # Assuming modules JSON files are in a 'modules' directory relative to the script
        modules_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules')
        
        for module in self.modules_available:
            json_path = os.path.join(modules_dir, f"{module.lower()}.json")
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    self.module_data[module] = json.load(f)

    def create_styled_tooltip(self, text):
        return f"""
        <div style='
            color: white;
            padding: 10px 10px;
            min-width: 400px;
            max-width: 500px;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            font-size: 16px;
            line-height: 1.3;
        '>
            {text}
        </div>
        """

    def init_ui(self):
        layout = QVBoxLayout(self)

        title_label = QLabel("Choose a module to add:")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(config.get_dialog_element_font())  # Set font size to 11
        layout.addWidget(title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)

        container = QWidget()
        scroll_layout = QVBoxLayout(container)
        scroll_layout.setSpacing(10)

        # Create buttons for each module with proper font
        for mod in self.modules_available:
            mod_button = QPushButton(mod)
            mod_button.setFont(config.get_dialog_element_font())  # Use consistent font size
            mod_button.setStyleSheet("padding: 10px;")
            mod_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            mod_button.clicked.connect(lambda checked, m=mod: self.select_module(m))
            
            if mod in self.module_data and 'tooltip' in self.module_data[mod]:
                mod_button.setToolTip(self.create_styled_tooltip(self.module_data[mod]['tooltip']))
            
            scroll_layout.addWidget(mod_button)


        # Style for the GroupBox using centralized color configurations
        container.setStyleSheet(f"""
            QGroupBox {{
                border: 2px solid gray;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;  /* Add padding inside the group box */
                color: {config.get_label_color().name()};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }}
            
            /* Add hover effect for buttons using centralized colors */
            QPushButton {{
                background-color: {config.get_button_background_color().name()};
                color: {config.get_base_color().name()};
                border: none;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                background-color: {config.get_button_hover_color().name()};
            }}
        """)
        


        # Add some space at the bottom
        scroll_layout.addStretch()
        scroll_area.setWidget(container)

        # Cancel button with proper font and wider size
        bottom_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFont(config.get_dialog_element_font())
        cancel_btn.setFixedWidth(100)  # Set a fixed width for the cancel button
        cancel_btn.clicked.connect(self.reject)
        bottom_layout.addStretch()
        bottom_layout.addWidget(cancel_btn)
        layout.addLayout(bottom_layout)

    def select_module(self, module_name):
        self.selected_module = module_name
        self.accept()

    def get_selected_module(self):
        return self.selected_module
