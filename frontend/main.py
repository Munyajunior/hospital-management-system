import sys
from PySide6.QtWidgets import QApplication, QMainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hospital Management System")
        self.setGeometry(100, 100, 1024, 768)  # Default window size

        # Placeholder UI - We will replace this with actual UI later
        self.init_ui()

    def init_ui(self):
        pass  # UI elements will be added in the next step

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
