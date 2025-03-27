## Implement threading in PySide Qt Applications
import os
from PySide6.QtWidgets import (QApplication,
    QWidget, QVBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QComboBox, QTextEdit, QTabWidget, QFormLayout, QLineEdit,
    QGridLayout, QGroupBox, QToolBar, QStatusBar, QMainWindow, QScrollArea, QHeaderView, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QObject, QRunnable, QThreadPool
from PySide6.QtGui import QIcon, QAction
from utils.api_utils import fetch_data



class WorkerSignals(QObject):
    """Signals for worker threads."""
    finished = Signal()
    error = Signal(str)
    result = Signal(object)


class Worker(QRunnable):
    """Worker thread for API calls."""
    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
            self.signals.result.emit(result)
        except Exception as e:
            self.signals.error.emit(str(e))
        finally:
            self.signals.finished.emit()



    def load_admissions(self):
            """Fetches and populates the dropdown with admissions using threading."""
            worker = Worker(fetch_data, self, os.getenv("ADMISSION_LIST_URL"), self.token)
            worker.signals.result.connect(self.populate_admission_dropdown)
            worker.signals.error.connect(self.show_error)
            self.thread_pool.start(worker)

    def populate_admission_dropdown(self, admissions):
        """Populates the admission dropdown with fetched data (runs in the main thread)."""
        if admissions:
            self.admission_dropdown.clear()
            for admission in admissions:
                self.admission_dropdown.addItem(f"Admission {admission['id']}", admission["id"])


    def load_admitted_icu(self):
        """Fetches and display icu admissions using threading."""
        worker = Worker(fetch_data, self, os.getenv("GET_ICU_PATIENTS_URL"), self.token)
        worker.signals.result.connect(self.populate_icu_admitted)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_icu_admitted(self, admissions):
        """Populates the icu admitted dropdown with fetched data (runs in the main thread)."""
        if admissions:
            self.patient_dropdown_icu.clear()
            for admission in admissions:
                self.patient_dropdown_icu.addItem(f"Admission {admission['id']}", admission["id"])

    def load_icu_patients(self):
        """Fetches and displays ICU patients using threading."""
        worker = Worker(fetch_data, self, os.getenv("GET_ICU_PATIENTS_URL"), self.token)
        worker.signals.result.connect(self.populate_icu_table)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_icu_table(self, icu_patients):
        """Populates the ICU table with fetched data (runs in the main thread)."""
        if icu_patients:
            self.icu_table.setRowCount(len(icu_patients))
            for row, patient in enumerate(icu_patients):
                self.icu_table.setItem(row, 0, QTableWidgetItem(patient["patient_name"]))
                self.icu_table.setItem(row, 1, QTableWidgetItem(patient["status"]))
                self.icu_table.setItem(row, 2, QTableWidgetItem(patient["condition_evolution"]))
                self.icu_table.setItem(row, 3, QTableWidgetItem(patient["medications"]))
                self.icu_table.setItem(row, 4, QTableWidgetItem(patient["drips"]))
                self.icu_table.setItem(row, 5, QTableWidgetItem(patient["treatment_plan"]))
                self.icu_table.setItem(row, 6, QTableWidgetItem(patient["updated_by"]))
                self.icu_table.setItem(row, 7, QTableWidgetItem(patient["updated_at"]))
            self.icu_table.resizeColumnsToContents()


    def load_admitted_inpatient(self):
        """Fetches and display Inpatient admissions with threading."""
        worker = Worker(fetch_data, self, os.getenv("GET_INPATIENTS_URL"), self.token)
        worker.signals.result.connect(self.populate_inpatient_admitted)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_inpatient_admitted(self, in_patient):
        if in_patient:
            for patient in in_patient:
                self.patient_dropdown_inpatient.addItem(f"Admission {patient['id']}", patient["id"])

    def load_inpatients(self):
        """Fetches and displays inpatients with threading."""
        worker = Worker(fetch_data, self, os.getenv("GET_INPATIENTS_URL"), self.token)
        worker.signals.result.connect(self.populate_inpatient_table)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_inpatient_table(self, inpatients):
        """Populates the Inpatient table with fetched data (runs in the main thread)."""
        if inpatients:
            self.inpatient_table.setRowCount(len(inpatients))
            for row, patient in enumerate(inpatients):
                self.inpatient_table.setItem(row, 0, QTableWidgetItem(patient["patient_name"]))
                self.inpatient_table.setItem(row, 1, QTableWidgetItem(patient["status"]))
                self.inpatient_table.setItem(row, 2, QTableWidgetItem(patient["condition_evolution"]))
                self.inpatient_table.setItem(row, 3, QTableWidgetItem(patient["medications"]))
                self.inpatient_table.setItem(row, 4, QTableWidgetItem(patient["treatment_plan"]))
                self.inpatient_table.setItem(row, 5, QTableWidgetItem(patient["updated_by"]))
                self.inpatient_table.setItem(row, 6, QTableWidgetItem(patient["updated_at"]))
            self.inpatient_table.resizeColumnsToContents()

    def load_departments(self):
        """Fetches and populates the dropdown with departments using threading."""
        worker = Worker(fetch_data, self, os.getenv("GET_DEPARTMENTS_URL"), self.token)
        worker.signals.result.connect(self.populate_department_dropdowns)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_department_dropdowns(self, departments):
        """Populates department dropdowns with fetched data."""
        if departments:
            self.department_dropdown.clear()
            for department in departments:
                self.department_dropdown.addItem(department["name"], department["id"])

    def load_wards(self):
        """Fetches and populates the dropdown with wards using threading."""
        worker = Worker(fetch_data, self, os.getenv("WARD_LIST_URL"), self.token)
        worker.signals.result.connect(self.populate_ward_dropdowns)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_ward_dropdowns(self, wards):
        """Populates ward dropdowns with fetched data."""
        if wards:
            self.ward_dropdown.clear()
            for ward in wards:
                self.ward_dropdown.addItem(ward["name"], ward["id"])

    def load_wards_for_department(self):
        """Fetches and populates the dropdown with wards for a selected department using threading."""
        department_id = self.department_dropdown.currentData()
        if department_id:
            api_url = os.getenv("WARD_LIST_URL") + f"?department_id={department_id}"
            
            # Create a worker to fetch wards
            worker = Worker(fetch_data, self, api_url, self.token)
            worker.signals.result.connect(self.populate_ward_dropdown)
            worker.signals.error.connect(self.show_error)
            self.thread_pool.start(worker)

    def populate_ward_dropdown(self, wards):
        """Populates the ward dropdown with fetched data (runs in the main thread)."""
        if wards:
            self.ward_dropdown.clear()
            for ward in wards:
                self.ward_dropdown.addItem(ward["name"], ward["id"])

    def load_departments_for_ward(self):
        """Fetches and populates the dropdown with departments for ward creation."""
        worker = Worker(fetch_data, self, os.getenv("DEPARTMENT_LIST_URL"), self.token)
        worker.signals.result.connect(self.populate_department_dropdown_ward)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_department_dropdown_ward(self, departments):
        """Populates the department dropdown for ward creation."""
        if departments:
            self.department_dropdown_ward.clear()
            for department in departments:
                self.department_dropdown_ward.addItem(department["name"], department["id"])

    def load_wards_for_bed(self):
        """Fetches and populates the dropdown with wards for bed creation."""
        worker = Worker(fetch_data, self, os.getenv("WARD_LIST_URL"), self.token)
        worker.signals.result.connect(self.populate_ward_dropdown_bed)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_ward_dropdown_bed(self, wards):
        """Populates the ward dropdown for bed creation."""
        if wards:
            self.ward_dropdown_bed.clear()
            for ward in wards:
                self.ward_dropdown_bed.addItem(ward["name"], ward["id"])

    def load_beds(self):
        """Fetches and populates the dropdown with beds."""
        worker = Worker(fetch_data, self, os.getenv("BED_LIST_URL"), self.token)
        worker.signals.result.connect(self.populate_bed_dropdowns)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_bed_dropdowns(self, beds):
        """Populates bed dropdowns with fetched data."""
        if beds:
            self.bed_dropdown.clear()
            for bed in beds:
                self.bed_dropdown.addItem(str(bed["bed_number"]), bed["id"])

    def load_beds_for_ward(self):
        """Fetches and populates the dropdown with beds for a selected ward."""
        ward_id = self.ward_dropdown.currentData()
        if ward_id:
            api_url = os.getenv("BED_LIST_URL") + f"?ward_id={ward_id}&is_occupied=False"
            worker = Worker(fetch_data, self, api_url, self.token)
            worker.signals.result.connect(self.populate_bed_dropdown)
            worker.signals.error.connect(self.show_error)
            self.thread_pool.start(worker)

    def populate_bed_dropdown(self, beds):
        """Populates the bed dropdown with fetched data."""
        if beds:
            self.bed_dropdown.clear()
            for bed in beds:
                self.bed_dropdown.addItem(str(bed["bed_number"]), bed["id"])

    def load_existing_departments(self):
        """Fetches and displays existing departments."""
        worker = Worker(fetch_data, self, os.getenv("DEPARTMENT_LIST_URL"), self.token)
        worker.signals.result.connect(self.populate_existing_departments)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_existing_departments(self, departments):
        """Populates the existing department table with fetched data."""
        if departments:
            self.existing_department_table.setRowCount(len(departments))
            for row, department in enumerate(departments):
                self.existing_department_table.setItem(row, 0, QTableWidgetItem(str(department["id"])))
                self.existing_department_table.setItem(row, 1, QTableWidgetItem(department["name"]))
                self.existing_department_table.setItem(row, 2, QTableWidgetItem(department["category"]))
            self.existing_department_table.resizeColumnsToContents()

    def load_existing_wards(self):
        """Fetches and displays existing wards."""
        worker = Worker(fetch_data, self, os.getenv("WARD_LIST_URL"), self.token)
        worker.signals.result.connect(self.populate_existing_wards)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_existing_wards(self, wards):
        """Populates the existing ward table with fetched data."""
        if wards:
            self.existing_ward_table.setRowCount(len(wards))
            for row, ward in enumerate(wards):
                self.existing_ward_table.setItem(row, 0, QTableWidgetItem(str(ward["id"])))
                self.existing_ward_table.setItem(row, 1, QTableWidgetItem(ward["name"]))
                self.existing_ward_table.setItem(row, 2, QTableWidgetItem(str(ward["department_id"])))
            self.existing_ward_table.resizeColumnsToContents()

    def load_existing_beds(self):
        """Fetches and displays existing beds."""
        worker = Worker(fetch_data, self, os.getenv("BED_LIST_URL"), self.token)
        worker.signals.result.connect(self.populate_existing_beds)
        worker.signals.error.connect(self.show_error)
        self.thread_pool.start(worker)

    def populate_existing_beds(self, beds):
        """Populates the existing bed table with fetched data."""
        if beds:
            self.existing_bed_table.setRowCount(len(beds))
            for row, bed in enumerate(beds):
                self.existing_bed_table.setItem(row, 0, QTableWidgetItem(str(bed["id"])))
                self.existing_bed_table.setItem(row, 1, QTableWidgetItem(bed["bed_number"]))
                self.existing_bed_table.setItem(row, 2, QTableWidgetItem(str(bed["ward_id"])))
            self.existing_bed_table.resizeColumnsToContents()