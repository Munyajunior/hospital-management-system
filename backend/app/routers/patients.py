from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, aliased
from typing import List, Optional
from models.patient import Patient
from models.admission import PatientAdmission, Bed, Ward, Department, Inpatient, ICUPatient
from models.user import User
from schemas.patients import PatientCreate, PatientCreateResponse, PatientResponse, PatientUpdate
from schemas.admission import AdmissionCategory
from core.database import get_db
from utils.security import hash_password, generate_password
from utils.email_util import send_password_email
from core.dependencies import RoleChecker

router = APIRouter(prefix="/patients", tags=["Patients"])

staff_only = RoleChecker(["admin", "nurse", "receptionist"])
doctor_or_nurse = RoleChecker(["doctor", "nurse", "admin"])

@router.post("/", response_model=PatientCreateResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(
    patient: PatientCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff_only)
):
    """
    Register a new patient. If it's an emergency, automatically assign an available bed
    in the selected ward and admit the patient.
    """
    # Check if the email is already registered
    existing_patient = db.query(Patient).filter(Patient.email == patient.email).first()
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )

    # Generate password and hash it
    password = generate_password()
    password_hash = hash_password(password)

    # Prepare patient data
    patient_data = patient.model_dump()
    patient_data["hashed_password"] = password_hash
    patient_data["registered_by"] = current_user.id
    patient_data["category"] = "inpatient" if patient.emergency else "outpatient"

    # Create the patient
    new_patient = Patient(**patient_data)
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)

    # Automatically admit the patient if it's an emergency
    if patient.emergency:
        # Validate category, department, and ward
        if not patient.category or not patient.department_id or not patient.ward_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category, department, and ward are required for emergency admission."
            )

        # Validate category
        if patient.category not in [AdmissionCategory.INPATIENT, AdmissionCategory.ICU]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid category for emergency admission. Must be 'Inpatient' or 'ICU'."
            )

        # Validate department
        department = db.query(Department).filter(Department.id == patient.department_id).first()
        if not department:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Department not found."
            )

        # Validate ward
        ward = db.query(Ward).filter(Ward.id == patient.ward_id).first()
        if not ward:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ward not found."
            )

        # Ensure the ward belongs to the selected department
        if ward.department_id != department.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ward does not belong to the selected department."
            )

        # Find an available bed in the selected ward
        bed = db.query(Bed).filter(
            Bed.ward_id == ward.id,
            Bed.is_occupied == False
        ).first()

        if not bed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No available beds in the selected ward."
            )

        # Create an admission record
        admission_data = {
            "patient_id": new_patient.id,
            "category": patient.category,
            "department_id": department.id,
            "ward_id": ward.id,
            "bed_id": bed.id,
            "assigned_doctor_id": patient.assigned_doctor_id,
            "admitted_by": current_user.id,
            "status": "Admitted"
        }
        new_admission = PatientAdmission(**admission_data)
        db.add(new_admission)

        # Mark the bed as occupied
        bed.is_occupied = True
        db.commit()
         # If the category is ICU, create an ICU patient record
        if admission_data.category == AdmissionCategory.ICU:
            icu_patient = ICUPatient(
                patient_id=admission_data.patient_id,
                admission_id=new_admission.id,
                status="Critical",  
                updated_by=current_user.id
            )
            db.add(icu_patient)
            db.commit()
            db.refresh(icu_patient)

        # If the category is Inpatient, create an Inpatient record
        elif admission_data.category == AdmissionCategory.INPATIENT:
            inpatient = Inpatient(
                patient_id=admission_data.patient_id,
                admission_id=new_admission.id,
                status="Stable",  # Default status
                updated_by=current_user.id
            )
            db.add(inpatient)
            db.commit()
            db.refresh(inpatient)

        # Send the generated password to the patient's email
        email_sent = await send_password_email(new_patient.email, password)
        if not email_sent:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send password to email."
            )

    return {**new_patient.__dict__, "password": password}

@router.get("/", response_model=List[PatientResponse])
def get_patients( emergency: Optional[bool] = Query(None), 
                 patient_id: Optional[int] = Query(None),
                 db: Session = Depends(get_db), 
                 user: User = Depends(doctor_or_nurse)):
    Doctor = aliased(User)
    query = (db.query(Patient.id,Patient.full_name,
                     Patient.date_of_birth,Patient.gender,
                     Patient.role,Patient.email,
                     Patient.address, Patient.contact_number, Patient.category, 
                     Patient.emergency,Patient.assigned_doctor_id,
                     Doctor.full_name.label("assigned_doctor_name"),
                     Patient.registered_by,
                     User.id.label("registered_by_name"),
                     Patient.created_at
                     ).outerjoin(Doctor, Patient.assigned_doctor_id == Doctor.id)
                      .join(User, Patient.registered_by == User.id)
             )
    if emergency:
        query = query.filter(Patient.emergency == emergency)
    if patient_id:
        query = query.filter(Patient.id == patient_id)
    patient = query.all()
    
    return patient


@router.put("/{patient_id}", response_model=PatientResponse)
async def update_patient(patient_id: int, patient_data: PatientUpdate, db: Session = Depends(get_db),
                   user: User = Depends(doctor_or_nurse)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    for key, value in patient_data.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)

    db.commit()
    db.refresh(patient)
    return patient


@router.put("/{patient_id}/assign-category/{category}", response_model=PatientResponse)
async def update_patient_category(patient_id: int, category: str, db: Session = Depends(get_db),
                            user: User = Depends(doctor_or_nurse)):
    if category not in ["outpatient", "inpatient", "ICU"]:
        raise HTTPException(status_code=400, detail="Invalid category")

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    patient.category = category
    db.commit()
    db.refresh(patient)
    return patient 

@router.put("/{patient_id}/assign/{doctor_id}", response_model=PatientResponse)
async def assign_patient_to_doctor(patient_id: int, doctor_id: int, db: Session = Depends(get_db),
                             user: User = Depends(staff_only)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    doctor = db.query(User).filter(User.id == doctor_id, User.role == "doctor").first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    patient.assigned_doctor_id = doctor_id
    db.commit()
    db.refresh(patient) 
    return patient


@router.put("/{patient_id}/update-medical-records", response_model=PatientResponse)
def update_medical_records(patient_id: int, updates: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(patient, key, value)
    
    db.commit()
    db.refresh(patient)
    return patient






