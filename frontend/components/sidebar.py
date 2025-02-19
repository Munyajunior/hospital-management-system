from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Qt

class Sidebar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        self.setFixedWidth(200)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        self.patient_btn = QPushButton("Patients")
        self.patient_btn.clicked.connect(lambda: self.parent.switch_module(0))
        layout.addWidget(self.patient_btn)

        self.doctor_btn = QPushButton("Doctors")
        self.doctor_btn.clicked.connect(lambda: self.parent.switch_module(1))
        layout.addWidget(self.doctor_btn)

        self.pharmacy_btn = QPushButton("Pharmacy")
        self.pharmacy_btn.clicked.connect(lambda: self.parent.switch_module(2))
        layout.addWidget(self.pharmacy_btn)

        self.lab_btn = QPushButton("Lab")
        self.lab_btn.clicked.connect(lambda: self.parent.switch_module(3))
        layout.addWidget(self.lab_btn)

        self.radiology_btn = QPushButton("Radiology")
        self.radiology_btn.clicked.connect(lambda: self.parent.switch_module(4))
        layout.addWidget(self.radiology_btn)

        self.icu_btn = QPushButton("ICU")
        self.icu_btn.clicked.connect(lambda: self.parent.switch_module(5))
        layout.addWidget(self.icu_btn)

        self.setLayout(layout)
