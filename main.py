import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QPushButton, QTextEdit, QFileDialog, QVBoxLayout, QWidget, QHBoxLayout, QProgressBar
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPalette, QColor, QFont, QPixmap, QIcon
import pytesseract
from PIL import Image
import os
import time

class OcrWorker(QThread):
    log_signal = Signal(str, str)
    result_signal = Signal(str, bool)
    progress_signal = Signal(int)

    def __init__(self, file_path, tesseract_path):
        super().__init__()
        self.file_path = file_path
        self.tesseract_path = tesseract_path

    def run(self):
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        ext = os.path.splitext(self.file_path)[1].lower()
        start_time = time.time()
        try:
            if ext == '.pdf':
                from pdf2image import convert_from_path
                images = convert_from_path(self.file_path, dpi=300)
                all_text = []
                page_times = []
                total_pages = len(images)
                for i, img in enumerate(images):
                    page_start = time.time()
                    self.log_signal.emit(f"Processing PDF page {i+1}/{total_pages}...", "info")
                    text = pytesseract.image_to_string(img, lang='fas')
                    all_text.append(f"\n--- Page {i+1} ---\n{text}")
                    page_elapsed = time.time() - page_start
                    page_times.append(page_elapsed)
                    avg_time = sum(page_times) / len(page_times)
                    pages_left = total_pages - (i + 1)
                    est_time_left = avg_time * pages_left
                    if pages_left > 0:
                        self.log_signal.emit(
                            f"Avg/page: {avg_time:.2f}s | Estimated time left: {est_time_left:.2f}s",
                            "info"
                        )
                    self.progress_signal.emit(int((i+1)/total_pages*100))
                text = '\n'.join(all_text)
            else:
                self.log_signal.emit(f"Processing image: {os.path.basename(self.file_path)}", "info")
                img = Image.open(self.file_path)
                text = pytesseract.image_to_string(img, lang='fas')
                self.progress_signal.emit(100)
            elapsed = time.time() - start_time
            self.log_signal.emit(f"OCR complete! Elapsed time: {elapsed:.2f} seconds", "success")
            self.result_signal.emit(text, True)
        except Exception as e:
            self.log_signal.emit(f"OCR failed: {e}", "error")
            self.result_signal.emit(f"Error: {e}", False)
            self.progress_signal.emit(0)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Persian OCR App")
        self.setGeometry(200, 200, 700, 650)
        self.setAcceptDrops(True)
        self.language = 'en'  # 'en' or 'fa'

        # Widgets
        self.lang_btn = QPushButton()
        self.lang_btn.setIcon(QIcon.fromTheme("preferences-desktop-locale"))
        self.lang_btn.setText("فارسی")
        self.label = QLabel("Select or drag-and-drop an image or PDF, then run OCR.")
        self.label.setAlignment(Qt.AlignCenter)
        self.select_btn = QPushButton()
        self.select_btn.setIcon(QIcon.fromTheme("document-open"))
        self.select_btn.setText("Select Image or PDF")
        self.ocr_btn = QPushButton()
        self.ocr_btn.setIcon(QIcon.fromTheme("system-run"))
        self.ocr_btn.setText("Run OCR")
        self.ocr_btn.setEnabled(False)
        self.save_btn = QPushButton()
        self.save_btn.setIcon(QIcon.fromTheme("document-save"))
        self.save_btn.setText("Save Output")
        self.save_btn.setEnabled(False)
        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.log_edit = QTextEdit()
        self.log_edit.setReadOnly(True)
        self.log_edit.setMaximumHeight(100)
        self.ocr_result_label = QLabel("OCR Result:")
        self.log_label = QLabel("Log:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFixedHeight(20)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setVisible(False)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setFixedHeight(120)
        self.preview_label.setStyleSheet("border: 1px solid #888; border-radius: 8px; background: #23272e;")

        # Layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.lang_btn)
        top_layout.addWidget(self.label)
        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.select_btn)
        layout.addWidget(self.preview_label)
        layout.addWidget(self.ocr_btn)
        layout.addWidget(self.save_btn)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.ocr_result_label)
        layout.addWidget(self.text_edit)
        layout.addWidget(self.log_label)
        layout.addWidget(self.log_edit)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # State
        self.file_path = None
        self.ocr_thread = None
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.tesseract_path = os.path.join(base_dir, "Tesseract", "tesseract.exe")

        # Connections
        self.select_btn.clicked.connect(self.select_file)
        self.ocr_btn.clicked.connect(self.run_ocr)
        self.save_btn.clicked.connect(self.save_output)
        self.lang_btn.clicked.connect(self.toggle_language)

        self.apply_modern_style()
        self.update_language()

    def apply_modern_style(self):
        app = QApplication.instance()
        palette = app.palette()
        base_color = palette.color(QPalette.Window)
        is_dark = base_color.value() < 128
        font = QFont("Segoe UI", 11)
        app.setFont(font)
        accent = "#2196F3"
        bg = "#181a1b" if is_dark else "#f5f6fa"
        fg = "#f5f6fa" if is_dark else "#181a1b"
        btn_bg = accent
        btn_fg = "#fff"
        btn_hover = "#1769aa"
        border = "#444" if is_dark else "#ccc"
        self.setStyleSheet(f"""
            QMainWindow {{ background: {bg}; color: {fg}; }}
            QLabel {{ color: {fg}; font-size: 15px; }}
            QPushButton {{
                background: {btn_bg}; color: {btn_fg}; border-radius: 8px;
                padding: 8px 18px; font-size: 15px; border: 1px solid {border};
            }}
            QPushButton:disabled {{ background: #888; color: #eee; }}
            QPushButton:hover {{ background: {btn_hover}; }}
            QTextEdit {{
                background: #23272e; color: #eee; border-radius: 8px;
                font-size: 14px; padding: 8px; border: 1px solid {border};
            }}
            QProgressBar {{
                border: 1px solid {border}; border-radius: 8px; background: #23272e;
                text-align: center; color: {fg}; font-size: 13px;
            }}
            QProgressBar::chunk {{
                background: {accent}; border-radius: 8px;
            }}
            QScrollBar:vertical {{ width: 12px; }}
        """)
        self.log_edit.setStyleSheet("background:#23272e;color:#8ecae6;font-size:13px;border-radius:8px;")
        self.preview_label.setStyleSheet("border: 1px solid #888; border-radius: 8px; background: #23272e;")

    def update_language(self):
        if self.language == 'en':
            self.setLayoutDirection(Qt.LeftToRight)
            self.lang_btn.setText("فارسی")
            self.label.setText("Select or drag-and-drop an image or PDF, then run OCR.")
            self.select_btn.setText("Select Image or PDF")
            self.ocr_btn.setText("Run OCR")
            self.save_btn.setText("Save Output")
            self.ocr_result_label.setText("OCR Result:")
            self.log_label.setText("Log:")
            self.setWindowTitle("Persian OCR App")
        else:
            self.setLayoutDirection(Qt.RightToLeft)
            self.lang_btn.setText("English")
            self.label.setText("یک تصویر یا PDF را انتخاب یا رها کنید، سپس OCR را اجرا کنید.")
            self.select_btn.setText("انتخاب تصویر یا PDF")
            self.ocr_btn.setText("اجرای OCR")
            self.save_btn.setText("ذخیره خروجی")
            self.ocr_result_label.setText("نتیجه OCR:")
            self.log_label.setText("لاگ:")
            self.setWindowTitle("برنامه OCR فارسی")

    def toggle_language(self):
        self.language = 'fa' if self.language == 'en' else 'en'
        self.update_language()

    def log(self, message, level="info"):
        color = {"info": "#8ecae6", "success": "#38b000", "error": "#e63946"}.get(level, "#eee")
        self.log_edit.append(f'<span style="color:{color}">{message}</span>')
        self.log_edit.verticalScrollBar().setValue(self.log_edit.verticalScrollBar().maximum())

    def select_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, self.select_btn.text(), "", "Images/PDF (*.png *.jpg *.jpeg *.bmp *.pdf)")
        if file_path:
            self.set_selected_file(file_path)
        else:
            self.label.setText("No file selected." if self.language == 'en' else "هیچ فایلی انتخاب نشد.")
            self.ocr_btn.setEnabled(False)
            self.save_btn.setEnabled(False)
            self.preview_label.clear()
            self.log("No file selected." if self.language == 'en' else "هیچ فایلی انتخاب نشد.", "info")

    def set_selected_file(self, file_path):
        self.file_path = file_path
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.pdf':
            self.label.setText(f"Selected PDF: {os.path.basename(file_path)}" if self.language == 'en' else f"PDF انتخاب شده: {os.path.basename(file_path)}")
            self.log(f"Selected PDF: {os.path.basename(file_path)}" if self.language == 'en' else f"PDF انتخاب شده: {os.path.basename(file_path)}", "info")
            # Show preview of first page
            try:
                from pdf2image import convert_from_path
                images = convert_from_path(file_path, dpi=100, first_page=1, last_page=1)
                if images:
                    img = images[0]
                    img.thumbnail((180, 120))
                    img.save("_preview_temp.png")
                    pixmap = QPixmap("_preview_temp.png")
                    self.preview_label.setPixmap(pixmap)
                    os.remove("_preview_temp.png")
                else:
                    self.preview_label.clear()
            except Exception:
                self.preview_label.clear()
        else:
            self.label.setText(f"Selected Image: {os.path.basename(file_path)}" if self.language == 'en' else f"تصویر انتخاب شده: {os.path.basename(file_path)}")
            self.log(f"Selected Image: {os.path.basename(file_path)}" if self.language == 'en' else f"تصویر انتخاب شده: {os.path.basename(file_path)}", "info")
            # Show image preview
            try:
                pixmap = QPixmap(file_path)
                pixmap = pixmap.scaled(180, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.preview_label.setPixmap(pixmap)
            except Exception:
                self.preview_label.clear()
        self.ocr_btn.setEnabled(True)
        self.save_btn.setEnabled(False)
        self.text_edit.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

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
            self.label.setText("No file selected." if self.language == 'en' else "هیچ فایلی انتخاب نشد.")
            self.log("No file selected for OCR." if self.language == 'en' else "هیچ فایلی برای OCR انتخاب نشد.", "error")
            return
        self.label.setText("Running OCR..." if self.language == 'en' else "در حال اجرای OCR ...")
        self.log("Starting OCR..." if self.language == 'en' else "شروع OCR ...", "info")
        self.ocr_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.text_edit.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.ocr_thread = OcrWorker(self.file_path, self.tesseract_path)
        self.ocr_thread.log_signal.connect(self.log)
        self.ocr_thread.result_signal.connect(self.ocr_finished)
        self.ocr_thread.progress_signal.connect(self.progress_bar.setValue)
        self.ocr_thread.start()

    def ocr_finished(self, text, success):
        self.text_edit.setPlainText(text)
        self.progress_bar.setVisible(False)
        if success:
            self.label.setText("OCR complete." if self.language == 'en' else "OCR با موفقیت انجام شد.")
            self.save_btn.setEnabled(True)
        else:
            self.label.setText("OCR failed." if self.language == 'en' else "خطا در اجرای OCR.")
            self.save_btn.setEnabled(False)
        self.ocr_btn.setEnabled(True)

    def save_output(self):
        text = self.text_edit.toPlainText()
        if not text.strip():
            self.log("No OCR result to save." if self.language == 'en' else "نتیجه‌ای برای ذخیره وجود ندارد.", "error")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, self.save_btn.text(), "output.txt", "Text Files (*.txt)")
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                self.log(f"Output saved to: {file_path}" if self.language == 'en' else f"خروجی در {file_path} ذخیره شد.", "success")
            except Exception as e:
                self.log(f"Failed to save output: {e}" if self.language == 'en' else f"ذخیره خروجی با خطا مواجه شد: {e}", "error")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 