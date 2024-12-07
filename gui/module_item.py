# module_item.py

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QGroupBox
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QFont

import config  # Import the configuration module

class ModuleItem(QWidget):
    module_up = pyqtSignal()
    module_down = pyqtSignal()
    module_remove = pyqtSignal()
    module_edit = pyqtSignal()

    def __init__(self, module_name, parent=None):
        super().__init__(parent)
        
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
        
        # Set individual sizes
        arrow_button_size = 25  # Reduced size for arrow buttons
        edit_button_height = 25
        remove_button_height = 25
        remove_button_width = 70  # Increased width for 'Remove' button
        edit_button_width = 50    # Width for 'Edit' button
        
        # Configure arrow buttons
        for btn in [up_btn, down_btn]:
            btn.setFixedSize(arrow_button_size, arrow_button_size)
        
        # Configure Edit button
        edit_btn.setFixedSize(edit_button_width, edit_button_height)
        
        # Configure Remove button
        remove_btn.setFixedSize(remove_button_width, remove_button_height)
        
        # **Set Larger Font for Buttons**
        button_font = config.get_button_font()
        for btn in [edit_btn, up_btn, down_btn, remove_btn]:
            btn.setFont(button_font)
        
        # Connect signals
        up_btn.clicked.connect(self.module_up.emit)
        down_btn.clicked.connect(self.module_down.emit)
        remove_btn.clicked.connect(self.module_remove.emit)
        edit_btn.clicked.connect(self.module_edit.emit)
        
        # Add buttons to the layout
        button_layout.addWidget(up_btn)
        button_layout.addWidget(down_btn)
        button_layout.addWidget(edit_btn)
        button_layout.addWidget(remove_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        # Optionally, add additional widgets or spacing to increase height
        # For example, adding a spacer or an invisible widget
        spacer = QWidget()
        spacer.setFixedHeight(10)  # Adjust as needed
        main_layout.addWidget(spacer, alignment=Qt.AlignTop)
        
        # Style for the GroupBox
        self.group_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid gray;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
                font-size: 14px;
                padding: 10px;  /* Add padding inside the group box */
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            
            /* Optional: Add hover effect for buttons */
            QPushButton {
                background-color: #44475a;
                color: #f8f8f2;
                border: none;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #6272a4;
            }
        """)
        
        # Set a minimum height for the ModuleItem to ensure it's not too short
        self.setMinimumHeight(60)  # Adjust the value as needed
