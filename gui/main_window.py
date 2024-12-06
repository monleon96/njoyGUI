from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QMessageBox
from model import load_module
from gui.module_form import ModerForm

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("NJOY Input Builder")

        # Set a default geometry to have a nice sized window
        self.setGeometry(100, 100, 600, 400)

        self.init_ui()

    def init_ui(self):
        widget = QWidget()
        layout = QVBoxLayout()

        # Load the moder module
        self.moder_model = load_module("moder")
        self.moder_form = ModerForm(self.moder_model)
        layout.addWidget(self.moder_form)

        # Button to generate the NJOY input
        generate_btn = QPushButton("Generate NJOY Input")
        generate_btn.clicked.connect(self.generate_input)
        layout.addWidget(generate_btn)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def generate_input(self):
        params = self.moder_form.get_parameters()
        # Just show a message box for now
        message = f"Generated input:\n\nmoder\n{params['nin_file']} {params['nout_file']} /"
        QMessageBox.information(self, "NJOY Input Generated", message)
