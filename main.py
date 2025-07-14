import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QTextEdit, QFileDialog, QVBoxLayout, QWidget
)
from PySide6.QtCore import Qt
import pytesseract
from PIL import Image
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Persian OCR App")
        self.setGeometry(200, 200, 600, 400)

        # Widgets
        self.label = QLabel("Select an image and run OCR.")
        self.label.setAlignment(Qt.AlignCenter)
        self.select_btn = QPushButton("Select Image")
        self.ocr_btn = QPushButton("Run OCR")
        self.ocr_btn.setEnabled(False)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.select_btn)
        layout.addWidget(self.ocr_btn)
        layout.addWidget(self.text_edit)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # State
        self.image_path = None

        # Connections
        self.select_btn.clicked.connect(self.select_image)
        self.ocr_btn.clicked.connect(self.run_ocr)

    def select_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.image_path = file_path
            self.label.setText(f"Selected: {os.path.basename(file_path)}")
            self.ocr_btn.setEnabled(True)
            self.text_edit.clear()
        else:
            self.label.setText("No image selected.")
            self.ocr_btn.setEnabled(False)

    def run_ocr(self):
        if not self.image_path:
            self.label.setText("No image selected.")
            return
        self.label.setText("Running OCR...")
        QApplication.processEvents()
        try:
            img = Image.open(self.image_path)
            text = pytesseract.image_to_string(img, lang='fas')
            self.text_edit.setPlainText(text)
            self.label.setText("OCR complete.")
        except Exception as e:
            self.text_edit.setPlainText(f"Error: {e}")
            self.label.setText("OCR failed.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 