from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QFileDialog
)

class ModerForm(QWidget):
    def __init__(self, module_model, parent=None):
        super().__init__(parent)
        self.module_model = module_model
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        card = self.module_model.cards[0]
        nin_param = [p for p in card["parameters"] if p["name"] == "nin"][0]
        nout_param = [p for p in card["parameters"] if p["name"] == "nout"][0]

        self.input_file_edit = QLineEdit()
        self.input_file_edit.setPlaceholderText("Select input ENDF file")

        browse_input_btn = QPushButton("Browse")
        browse_input_btn.clicked.connect(self.browse_input_file)
        input_layout = QHBoxLayout()
        input_layout.addWidget(self.input_file_edit)
        input_layout.addWidget(browse_input_btn)
        layout.addRow("Input ENDF File (nin):", input_layout)

        self.output_file_edit = QLineEdit()
        self.output_file_edit.setPlaceholderText("Select output file")

        browse_output_btn = QPushButton("Browse")
        browse_output_btn.clicked.connect(self.browse_output_file)
        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_file_edit)
        output_layout.addWidget(browse_output_btn)
        layout.addRow("Output File (nout):", output_layout)

        self.setLayout(layout)

    def browse_input_file(self):
        file_dialog = QFileDialog.getOpenFileName(self, "Select Input ENDF File", "", "All Files (*.*)")
        if file_dialog[0]:
            self.input_file_edit.setText(file_dialog[0])

    def browse_output_file(self):
        file_dialog = QFileDialog.getSaveFileName(self, "Select Output File", "", "All Files (*.*)")
        if file_dialog[0]:
            self.output_file_edit.setText(file_dialog[0])

    def get_parameters(self):
        return {
            "nin_file": self.input_file_edit.text(),
            "nout_file": self.output_file_edit.text()
        }
