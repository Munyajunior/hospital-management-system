from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from models.user import User
from sqlalchemy import func
from models.patient import Patient
from models.appointment import Appointment, AppointmentStatus
from models.lab import LabTest, LabTestStatus
from models.radiology import RadiologyScan, RadiologyScanStatus
from models.pharmacy import Prescription, PrescriptionStatus
from models.billing import Billing
from models.admission import PatientAdmission, AdmissionStatus
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

staff_only = RoleChecker(["admin", "doctor", "nurse", "lab_technician", "pharmacist", "radiologist"])
 
@router.get("/metrics", response_model=Dict[str, Any])
def get_dashboard_metrics(db: Session = Depends(get_db), user: User = Depends(staff_only)):
    """Fetch all metrics for the dashboard."""
    # Total Patients
    total_patients = db.query(func.count(Patient.id)).scalar()
    # Total Appointments
    total_appointments = db.query(func.count(Appointment.id)).scalar()
    # Pending Appointments
    pending_appointments = db.query(func.count(Appointment.id)).filter(Appointment.status == AppointmentStatus.PENDING).scalar()
    # Total Lab Tests
    total_lab_tests = db.query(func.count(LabTest.id)).scalar()
    # Total Scans
    total_scans = db.query(func.count(RadiologyScan.id)).scalar()
    # Total Prescriptions
    total_prescriptions = db.query(func.count(Prescription.id)).scalar()
    # Pending Prescriptions
    pending_prescriptions = db.query(func.count(Prescription.id)).filter(Prescription.status == PrescriptionStatus.PENDING).scalar()
    # Pending Lab Tests
    pending_lab_tests = db.query(func.count(LabTest.id)).filter(LabTest.status == LabTestStatus.PENDING).scalar()
    # Pending Scans
    pending_scans = db.query(func.count(RadiologyScan.id)).filter(RadiologyScan.status == RadiologyScanStatus.PENDING).scalar()
    # In Progress Scan
    scans_in_progress = db.query(func.count(RadiologyScan.id)).filter(RadiologyScan.status == RadiologyScanStatus.IN_PROGRESS).scalar()
    # Lab Test In Progress
    lab_tests_in_progress = db.query(func.count(LabTest.id)).filter(LabTest.status == LabTestStatus.IN_PROGRESS).scalar()
    # Total Billing Transactions
    total_billing_transactions = db.query(func.count(Billing.id)).scalar()

    # Patient Distribution (Outpatients, Inpatients, ICU, Emergency)
    patient_distribution = {
        "outpatients": db.query(func.count(Patient.id)).filter(Patient.category == "outpatient").scalar(),
        "inpatients": db.query(func.count(Patient.id)).filter(Patient.category == "inpatient").scalar(),
        "icu": db.query(func.count(Patient.id)).filter(Patient.category == "ICU").scalar(),
        "emergency": db.query(func.count(Patient.id)).filter(Patient.emergency == True).scalar(),
    }

    # Daily Appointments (Completed vs Pending)
    today = datetime.now().date()
    appointments_data = {
        "completed": db.query(func.count(Appointment.id)).filter(
            Appointment.status == "Completed", Appointment.datetime >= today
        ).scalar(),
        "pending": db.query(func.count(Appointment.id)).filter(
            Appointment.status == "Pending", Appointment.datetime >= today
        ).scalar(),
    }

    # Admissions and Discharges
    admissions_data = {
        "admitted": db.query(func.count(PatientAdmission.id)).filter(
            PatientAdmission.status == AdmissionStatus.ADMITTED
        ).scalar(),
        "discharged": db.query(func.count(PatientAdmission.id)).filter(
            PatientAdmission.status == AdmissionStatus.DISCHARGED
        ).scalar(),
    }
    
    # Totol Admissions
    total_admissions = db.query(func.count(PatientAdmission.id)).scalar()
    

    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "total_lab_tests": total_lab_tests,
        "total_scans": total_scans,
        "pending_lab_tests": pending_lab_tests,
        "Pending_scans": pending_scans,
        "scans_in_progress":scans_in_progress,
        "lab_tests_in_progress":lab_tests_in_progress,
        "total_billing_transactions": total_billing_transactions,
        "patient_distribution": patient_distribution,
        "appointments_data": appointments_data,
        "admissions_data": admissions_data,
        "total_admissions": total_admissions,
        "total_prescription": total_prescriptions,
        "pending_appointments":pending_appointments,
        "pending_prescriptions": pending_prescriptions,
    }
 
@router.get("/metrics/doctor/{doctor_id}", response_model=Dict[str, Any])
def get_doctor_dashboard_metrics(doctor_id: int, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    """Fetch doctor specific metrics for the dashboard."""
    my_patients = db.query(func.count(Patient.id)).filter(Patient.assigned_doctor_id == doctor_id).scalar()
    my_pending_appointments = db.query(func.count(Appointment.id)).filter(Appointment.doctor_id == doctor_id, Appointment.status == AppointmentStatus.PENDING).scalar()
    my_confirmed_appointments = db.query(func.count(Appointment.id)).filter(Appointment.doctor_id == doctor_id, Appointment.status == AppointmentStatus.CONFIRMED).scalar()
    
    
    return {
        "my_patients": my_patients,
        "my_pending_appointments": my_pending_appointments,
        "my_confirmed_appointments": my_confirmed_appointments
    }