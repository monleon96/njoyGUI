# gui/pdf_viewer_dialog.py
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

class PDFViewerDialog(QDialog):
    def __init__(self, pdf_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Module PDF Documentation")

        layout = QVBoxLayout(self)
        self.web_view = QWebEngineView(self)
        
        # Convert to absolute file path if needed
        abs_path = QUrl.fromLocalFile(pdf_path)
        self.web_view.setUrl(abs_path)

        layout.addWidget(self.web_view)
