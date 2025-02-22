from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QMessageBox
from PySide6.QtCore import Qt

class BaseView(QWidget):
    def __init__(self, title, column_headers):
        super().__init__()
        self.title = title
        self.column_headers = column_headers
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.column_headers))
        self.table.setHorizontalHeaderLabels(self.column_headers)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def populate_table(self, data):
        """Populate the table with data."""
        self.table.setRowCount(len(data))
        for row, item in enumerate(data):
            for col, value in enumerate(item.values()):
                self.table.setItem(row, col, QTableWidgetItem(str(value)))