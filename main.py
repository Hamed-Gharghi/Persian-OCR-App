import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel
from PySide6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Persian OCR App")
        self.setGeometry(200, 200, 500, 300)
        label = QLabel("Welcome to Persian OCR App!", self)
        label.setGeometry(100, 120, 300, 40)
        label.setAlignment(Qt.AlignCenter)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec()) 