from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from models.appointment import Appointment, AppointmentStatus
from models.patient import Patient
from models.user import User
from schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentUpdate, DoctorAppointmentResponse,  AppointmentReschedule
from core.database import get_db
from core.dependencies import RoleChecker

router = APIRouter(prefix="/appointments", tags=["Appointments"])

staff_only = RoleChecker(["doctor","nurse"])



# Schedule an appointment
@router.post("/", response_model=AppointmentResponse)
def create_appointment(appointment: AppointmentCreate, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    patient = db.query(Patient).filter(Patient.id == appointment.patient_id).first()
    if not patient:
        raise HTTPException(status_code=400, detail="Invalid patient ID")

    new_appointment = Appointment(**appointment.model_dump())
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment



@router.get("/", response_model=List[AppointmentResponse])
def get_appointments(db: Session = Depends(get_db), user: User = Depends(staff_only)):
    appointments = db.query(Appointment).all()
    
    if not appointments:
        return []  
    
    return appointments 

# Get appointments of a specific doctor (with filtering options)
@router.get("/doctor/{doctor_id}/", response_model=List[DoctorAppointmentResponse])
def get_appointments(doctor_id: int, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    appointments = db.query(Appointment).filter(Appointment.doctor_id == doctor_id).all()
    
    if not appointments:
        return []  
    
    return appointments  


# Get a specific appointment
@router.get("/{appointment_id}/", response_model=AppointmentResponse)
def get_appointment(appointment_id: int, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return appointment

# Update appointment status
@router.put("/{appointment_id}/update", response_model=AppointmentResponse)
def update_appointment(appointment_id: int, update_data: AppointmentUpdate, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = update_data.status
    db.commit()
    db.refresh(appointment)
    return appointment

# Reschedule appointment 
@router.put("/{appointment_id}/reschedule", response_model=AppointmentResponse)
def reschedule_appointment(appointment_id: int, update_data: AppointmentReschedule, db: Session = Depends(get_db), user: User =Depends(staff_only)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = update_data.status
    appointment.datetime = update_data.datetime
    db.commit()
    db.refresh(appointment)
    return appointment

# Delete an appointment
@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_appointment(appointment_id: int, db: Session = Depends(get_db), user: User = Depends(staff_only)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    db.delete(appointment)
    db.commit()
