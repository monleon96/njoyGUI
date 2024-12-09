# module_item.py

from PyQt5.QtWidgets import (
    QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox, QMessageBox, 
    QPlainTextEdit
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

import config 

class ModuleItem(QWidget):
    module_up = pyqtSignal()
    module_down = pyqtSignal()
    module_remove = pyqtSignal()
    module_edit = pyqtSignal()

    def __init__(self, module_name, module_description, parent=None):
        super().__init__(parent)
        
        self.module_name = module_name
        self.module_description = module_description

        # Create the main GroupBox
        self.group_box = QGroupBox(module_name)
        
        # Main layout inside the GroupBox
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 5, 10, 5)  # Adjust margins as needed
        main_layout.setSpacing(10)  # Adjust spacing between elements
        self.group_box.setLayout(main_layout)
        
        # Layout for the entire widget
        widget_layout = QVBoxLayout()
        widget_layout.setContentsMargins(0, 0, 0, 0)  # Remove outer margins
        widget_layout.setSpacing(0)  # Remove spacing between widgets
        self.setLayout(widget_layout)
        widget_layout.addWidget(self.group_box)
        
        # Buttons Layout
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        button_layout.setSpacing(5)  # Reduced spacing between buttons
        
        # Create Buttons
        edit_btn = QPushButton("Edit")
        up_btn = QPushButton("↑")
        down_btn = QPushButton("↓")
        remove_btn = QPushButton("Remove")
        info_btn = QPushButton("?") 
        
        # Set individual sizes
        arrow_button_size = 25  # Reduced size for arrow buttons
        edit_button_height = 25
        remove_button_height = 25
        remove_button_width = 70  # Increased width for 'Remove' button
        edit_button_width = 50    # Width for 'Edit' button
        info_button_size = 25
        
        # Configure arrow buttons
        for btn in [up_btn, down_btn]:
            btn.setFixedSize(arrow_button_size, arrow_button_size)
        
        # Configure Edit button
        edit_btn.setFixedSize(edit_button_width, edit_button_height)
        
        # Configure Remove button
        remove_btn.setFixedSize(remove_button_width, remove_button_height)

        # Configure Info button
        info_btn.setFixedSize(info_button_size, info_button_size)
        
        # **Set Larger Font for Buttons**
        button_font = config.get_button_font()
        for btn in [edit_btn, up_btn, down_btn, remove_btn, info_btn]:  # Added info_btn
            btn.setFont(button_font)
        
        # Connect signals
        up_btn.clicked.connect(self.module_up.emit)
        down_btn.clicked.connect(self.module_down.emit)
        remove_btn.clicked.connect(self.module_remove.emit)
        edit_btn.clicked.connect(self.module_edit.emit)
        info_btn.clicked.connect(self.show_module_info) 
        
        # Add buttons to the layout
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(up_btn)
        button_layout.addWidget(down_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addWidget(info_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Optionally, add additional widgets or spacing to increase height
        # For example, adding a spacer or an invisible widget
        spacer = QWidget()
        spacer.setFixedHeight(10)  # Adjust as needed
        main_layout.addWidget(spacer, alignment=Qt.AlignTop)
        
        # Style for the GroupBox using centralized color configurations
        self.group_box.setStyleSheet(f"""
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
        
        # Set a minimum height for the ModuleItem to ensure it's not too short
        self.setMinimumHeight(60) 

    def show_module_info(self):
        """
        Display the module's description in a QMessageBox with rich text formatting,
        matching the style used in ParameterDialog.
        """
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"{self.module_name} Information")
        msg_box.setTextFormat(Qt.RichText)
        
        # Assume module_description may contain HTML tags (e.g., "<b>...</b>")
        msg_box.setText(self.module_description if self.module_description else "<b>No description available.</b>")
        msg_box.setIcon(QMessageBox.NoIcon)
        
        # Use a readable font
        custom_font = QFont("Arial", 11)
        msg_box.setFont(custom_font)
        
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()