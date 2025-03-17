from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime
from models.user import User
from sqlalchemy import func
from models.patient import Patient
from models.appointment import Appointment
from models.lab import LabTest, LabTestStatus
from models.billing import Billing
from models.admission import PatientAdmission, AdmissionStatus
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

staff_only = RoleChecker(["admin", "doctor", "nurse"])
 
@router.get("/metrics", response_model=Dict[str, Any])
def get_dashboard_metrics(db: Session = Depends(get_db), user: User = Depends(staff_only)):
    """Fetch all metrics for the dashboard."""
    # Total Patients
    total_patients = db.query(func.count(Patient.id)).scalar()

    # Total Appointments
    total_appointments = db.query(func.count(Appointment.id)).scalar()

    # Pending Lab Tests
    pending_lab_tests = db.query(func.count(LabTest.id)).filter(LabTest.status == LabTestStatus.PENDING).scalar()

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

    return {
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "pending_lab_tests": pending_lab_tests,
        "total_billing_transactions": total_billing_transactions,
        "patient_distribution": patient_distribution,
        "appointments_data": appointments_data,
        "admissions_data": admissions_data,
    }