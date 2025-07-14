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
        self.setGeometry(200, 200, 600, 550)
        self.setAcceptDrops(True)

        # Widgets
        self.label = QLabel("Select or drag-and-drop an image or PDF, then run OCR.")
        self.label.setAlignment(Qt.AlignCenter)
        self.select_btn = QPushButton("Select Image or PDF")
        self.ocr_btn = QPushButton("Run OCR")
        self.ocr_btn.setEnabled(False)
        self.save_btn = QPushButton("Save Output")
        self.save_btn.setEnabled(False)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumHeight(100)
        self.log_edit.setStyleSheet("background:#222;color:#eee;font-size:12px;")

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.select_btn)
        layout.addWidget(self.ocr_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(QLabel("OCR Result:"))
        layout.addWidget(self.text_edit)
        layout.addWidget(QLabel("Log:"))
        layout.addWidget(self.log_edit)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # State
        self.file_path = None

        # Connections
        self.select_btn.clicked.connect(self.select_file)
        self.ocr_btn.clicked.connect(self.run_ocr)
        self.save_btn.clicked.connect(self.save_output)

        # Set up Tesseract path
        base_dir = os.path.dirname(os.path.abspath(__file__))
        tesseract_path = os.path.join(base_dir, "Tesseract", "tesseract.exe")
        pytesseract.pytesseract.tesseract_cmd = tesseract_path

    def log(self, message, level="info"):
        color = {"info": "#8ecae6", "success": "#38b000", "error": "#e63946"}.get(level, "#eee")
        self.log_edit.append(f'<span style="color:{color}">{message}</span>')
        self.log_edit.verticalScrollBar().setValue(self.log_edit.verticalScrollBar().maximum())

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Image or PDF", "", "Images/PDF (*.png *.jpg *.jpeg *.bmp *.pdf)")
        if file_path:
            self.set_selected_file(file_path)
        else:
            self.label.setText("No file selected.")
            self.ocr_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.log("No file selected.", "info")

    def set_selected_file(self, file_path):
        self.file_path = file_path
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            self.label.setText(f"Selected PDF: {os.path.basename(file_path)}")
            self.log(f"Selected PDF: {os.path.basename(file_path)}", "info")
        else:
            self.label.setText(f"Selected Image: {os.path.basename(file_path)}")
            self.log(f"Selected Image: {os.path.basename(file_path)}", "info")
        self.ocr_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.text_edit.clear()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                ext = os.path.splitext(urls[0].toLocalFile())[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.pdf']:
                    event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if urls:
                file_path = urls[0].toLocalFile()
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.png', '.jpg', '.jpeg', '.bmp', '.pdf']:
                    self.set_selected_file(file_path)

    def run_ocr(self):
        if not self.file_path:
            self.label.setText("No file selected.")
            self.log("No file selected for OCR.", "error")
            return
        ext = os.path.splitext(self.file_path)[1].lower()
        self.label.setText("Running OCR...")
        self.log("Starting OCR...", "info")
        QApplication.processEvents()
        try:
            if ext == '.pdf':
                from pdf2image import convert_from_path
                images = convert_from_path(self.file_path, dpi=300)
                all_text = []
                for i, img in enumerate(images):
                    self.log(f"Processing PDF page {i+1}/{len(images)}...", "info")
                    text = pytesseract.image_to_string(img, lang='fas')
                    all_text.append(f"\n--- Page {i+1} ---\n{text}")
                text = '\n'.join(all_text)
            else:
                self.log(f"Processing image: {os.path.basename(self.file_path)}", "info")
                img = Image.open(self.file_path)
                text = pytesseract.image_to_string(img, lang='fas')
            self.text_edit.setPlainText(text)
            self.label.setText("OCR complete.")
            self.log("OCR complete!", "success")
            self.save_btn.setEnabled(True)
        except Exception as e:
            self.text_edit.setPlainText(f"Error: {e}")
            self.label.setText("OCR failed.")
            self.log(f"OCR failed: {e}", "error")
            self.save_btn.setEnabled(False)

    def save_output(self):
        text = self.text_edit.toPlainText()
        if not text.strip():
            self.log("No OCR result to save.", "error")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Save OCR Output", "output.txt", "Text Files (*.txt)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.log(f"Output saved to: {file_path}", "success")
            except Exception as e:
                self.log(f"Failed to save output: {e}", "error")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 