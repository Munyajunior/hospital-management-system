from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any
from datetime import datetime
from models.user import User
from models.patient import Patient
from models.appointment import Appointment, AppointmentStatus
from models.lab import LabTest, LabTestStatus
from models.radiology import RadiologyScan, RadiologyScanStatus
from models.pharmacy import Prescription, PrescriptionStatus
from models.billing import Billing
from models.admission import PatientAdmission, AdmissionStatus
from core.database import get_async_db
from core.dependencies import RoleChecker
from core.cache import cache

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

staff_only = RoleChecker(["admin", "doctor", "nurse", "lab_technician", "pharmacist", "radiologist"])
 
@router.get("/metrics", response_model=Dict[str, Any])
@cache(expire=60)  # Cache for 1 minute
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Fetch dashboard metrics with async operations and caching."""
    metrics = {}
    
    # Total Patients
    result = await db.execute(select(func.count(Patient.id)))
    metrics["total_patients"] = result.scalar()
    
    # Total Appointments
    result = await db.execute(select(func.count(Appointment.id)))
    metrics["total_appointments"] = result.scalar()
    
    # Pending Appointments
    result = await db.execute(
        select(func.count(Appointment.id))
        .where(Appointment.status == AppointmentStatus.PENDING)
    )
    metrics["pending_appointments"] = result.scalar()
    
    # Total Lab Tests
    result = await db.execute(select(func.count(LabTest.id)))
    metrics["total_lab_tests"] = result.scalar()
    
    # Total Scans
    result = await db.execute(select(func.count(RadiologyScan.id)))
    metrics["total_scans"] = result.scalar()
    
    # Total Prescriptions
    result = await db.execute(select(func.count(Prescription.id)))
    metrics["total_prescriptions"] = result.scalar()
    
    # Pending Prescriptions
    result = await db.execute(
        select(func.count(Prescription.id))
        .where(Prescription.status == PrescriptionStatus.PENDING)
    )
    metrics["pending_prescriptions"] = result.scalar()
    
    # Pending Lab Tests
    result = await db.execute(
        select(func.count(LabTest.id))
        .where(LabTest.status == LabTestStatus.PENDING)
    )
    metrics["pending_lab_tests"] = result.scalar()
    
    # Pending Scans
    result = await db.execute(
        select(func.count(RadiologyScan.id))
        .where(RadiologyScan.status == RadiologyScanStatus.PENDING)
    )
    metrics["Pending_scans"] = result.scalar()
    
    # Scans In Progress
    result = await db.execute(
        select(func.count(RadiologyScan.id))
        .where(RadiologyScan.status == RadiologyScanStatus.IN_PROGRESS)
    )
    metrics["scans_in_progress"] = result.scalar()
    
    # Lab Tests In Progress
    result = await db.execute(
        select(func.count(LabTest.id))
        .where(LabTest.status == LabTestStatus.IN_PROGRESS)
    )
    metrics["lab_tests_in_progress"] = result.scalar()
    
    # Total Billing Transactions
    result = await db.execute(select(func.count(Billing.id)))
    metrics["total_billing_transactions"] = result.scalar()

    # Patient Distribution
    result = await db.execute(
        select(Patient.category, func.count(Patient.id))
        .group_by(Patient.category)
    )
    patient_distribution = {
        "outpatients": 0,
        "inpatients": 0,
        "icu": 0,
        "emergency": 0
    }
    for category, count in result.all():
        if category == "outpatient":
            patient_distribution["outpatients"] = count
        elif category == "inpatient":
            patient_distribution["inpatients"] = count
        elif category == "ICU":
            patient_distribution["icu"] = count
    
    result = await db.execute(
        select(func.count(Patient.id))
        .where(Patient.emergency == True)
    )
    patient_distribution["emergency"] = result.scalar()
    metrics["patient_distribution"] = patient_distribution

    # Daily Appointments
    today = datetime.now().date()
    result = await db.execute(
        select(func.count(Appointment.id))
        .where(
            Appointment.status == "Completed", 
            Appointment.datetime >= today
        )
    )
    completed = result.scalar()
    
    result = await db.execute(
        select(func.count(Appointment.id))
        .where(
            Appointment.status == "Pending", 
            Appointment.datetime >= today
        )
    )
    pending = result.scalar()
    metrics["appointments_data"] = {
        "completed": completed,
        "pending": pending
    }

    # Admissions and Discharges
    result = await db.execute(
        select(func.count(PatientAdmission.id))
        .where(PatientAdmission.status == AdmissionStatus.ADMITTED)
    )
    admitted = result.scalar()
    
    result = await db.execute(
        select(func.count(PatientAdmission.id))
        .where(PatientAdmission.status == AdmissionStatus.DISCHARGED)
    )
    discharged = result.scalar()
    metrics["admissions_data"] = {
        "admitted": admitted,
        "discharged": discharged
    }
    
    # Total Admissions
    result = await db.execute(select(func.count(PatientAdmission.id)))
    metrics["total_admissions"] = result.scalar()
    
    return metrics
 
@router.get("/metrics/doctor/{doctor_id}", response_model=Dict[str, Any])
@cache(expire=60)  # Cache for 1 minute
async def get_doctor_dashboard_metrics(
    doctor_id: int, 
    db: AsyncSession = Depends(get_async_db), 
    user: User = Depends(staff_only)
):
    """Fetch doctor-specific metrics with async operations."""
    metrics = {}
    
    # My Patients
    result = await db.execute(
        select(func.count(Patient.id))
        .where(Patient.assigned_doctor_id == doctor_id)
    )
    metrics["my_patients"] = result.scalar()
    
    # My Pending Appointments
    result = await db.execute(
        select(func.count(Appointment.id))
        .where(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.PENDING
        )
    )
    metrics["my_pending_appointments"] = result.scalar()
    
    # My Confirmed Appointments
    result = await db.execute(
        select(func.count(Appointment.id))
        .where(
            Appointment.doctor_id == doctor_id,
            Appointment.status == AppointmentStatus.CONFIRMED
        )
    )
    metrics["my_confirmed_appointments"] = result.scalar()
    
    return metrics