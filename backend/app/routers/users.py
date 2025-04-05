from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta, datetime, timezone
import os
from models.user import User
from models.patient import Patient
from schemas.auth import (UserResponse, IsActive, UserUpdate, AllUserResponse,ProfileUpdateResponse,
                          ChangePasswordRequest, ResetPasswordRequest, ForgotPasswordRequest, UserSettingsUpdate,
                          SecurityQuestion, NotificationSettings)
from utils.security import hash_password, verify_password, create_reset_token, verify_reset_token
from utils.email_util import send_reset_email
from core.database import get_db
from core.dependencies import RoleChecker
from utils.security import hash_password
import base64
import json


router = APIRouter(prefix="/user", tags=["Users"])

admin_only = RoleChecker(["admin"])
staff = RoleChecker(["admin","doctor","nurse", "lab_technician", "pharmacist","radiologist"])

@router.get("/", response_model=List[AllUserResponse])
def all_users(db: Session = Depends(get_db), _: User = Depends(admin_only)):
    """Get all users"""
    all_users = db.query(User).all()
    if not all_users:
        return []
    return all_users

@router.get("/user/{user_id}", response_model=UserResponse)
def get_staff_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(staff)):
    """
    Fetch a user by their ID.
    Only the user themselves or an admin can access this endpoint.
    """
    # Check authorization
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this user's information")

    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Convert to response model and handle profile picture
    user_data = user.__dict__
    
    # Get base64 encoded profile picture if it exists
    if user.profile_picture and user.profile_picture_type:
        profile_pic_base64 = base64.b64encode(user.profile_picture).decode('utf-8')
        user_data['profile_picture'] = f"data:{user.profile_picture_type};base64,{profile_pic_base64}"
    else:
        user_data['profile_picture'] = None  # Or set a default image URL

    return UserResponse(**user_data)


@router.get("/patient/{patient_id}", response_model=UserResponse)
def get_patient_by_id(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["patient"]))):
    """
    Fetch a patient by their ID.
    Only the patient themselves or an admin can access this endpoint.
    """
    # Check authorization
    if current_user.id != patient_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this patient's information")

    # Fetch the patient from the database
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Convert to response model and handle profile picture
    patient_data = patient.__dict__
    
    # Get base64 encoded profile picture if it exists
    if patient.profile_picture and patient.profile_picture_type:
        profile_pic_base64 = base64.b64encode(patient.profile_picture).decode('utf-8')
        patient_data['profile_picture'] = f"data:{patient.profile_picture_type};base64,{profile_pic_base64}"
    else:
        patient_data['profile_picture'] = None  # Or set a default image URL

    return UserResponse(**patient_data)


@router.put("/{user_id}/is_active", response_model=UserResponse)
def activate_deactivate_user(user_id: int, active:IsActive, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    """Activate or Deactivate a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = active.is_active
    
    db.commit()
    db.refresh(user)
    
    return user


@router.put("/{user_id}/update", response_model=UserResponse)
def update_user_login_by_admin(user_id: int,update: UserUpdate,db: Session = Depends(get_db), current_user: User = Depends(admin_only)):
    """Admin Update a user."""  
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the new email is already in use
    existing_user = db.query(User).filter(User.email == update.email).first()
    if existing_user and existing_user.id != user_id:
        raise HTTPException(status_code=400, detail="Email already in use")
    
    password_hash = hash_password(update.password)
    user.email = update.email
    user.hashed_password = password_hash
    
    db.commit()
    db.refresh(user)

    return user

@router.put("/{user_id}/picture", response_model=UserResponse)
async def update_user_picture(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(staff)
):
    """Update only the user's profile picture"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        image_data = await file.read()
        content_type = file.content_type
        user.set_profile_picture(image_data, content_type)
        db.commit()
        db.refresh(user)
        
        user_data = user.__dict__
        # Get base64 encoded profile picture if it exists
        if user.profile_picture and user.profile_picture_type:
            profile_pic_base64 = base64.b64encode(user.profile_picture).decode('utf-8')
            user_data['profile_picture'] = f"data:{user.profile_picture_type};base64,{profile_pic_base64}"
        else:
            user_data['profile_picture'] = None  # Or set a default image URL

        return UserResponse(**user_data) 
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating picture: {str(e)}")
    finally:
           file.close()

# Similar endpoint for patients
@router.put("/patient/{patient_id}/picture", status_code=status.HTTP_200_OK)
async def update_patient_picture(
    patient_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: Patient = Depends(RoleChecker(["patient"]))
):
    """Update only the user's profile picture"""
    if current_user.id != patient_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to update this user")
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    try:
        image_data = await file.read()
        content_type = file.content_type
        patient.set_profile_picture(image_data, content_type)
        db.commit()
        return
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating picture: {str(e)}")
    finally:
           file.close()


@router.put("/patient/{patient_id}/update", response_model=ProfileUpdateResponse)
def update_patient_profile(patient_id: int, 
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    contact_number: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["patient"]))):
    """Update a patient's profile."""
    if current_user.id != patient_id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this patient's profile")

    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Check if the new email is already in use
    if email:
        existing_patient = db.query(Patient).filter(Patient.email == email).first()
        if existing_patient and existing_patient.id != patient_id:
            raise HTTPException(status_code=400, detail="Email already in use")
        patient.email = email

    if address:
        patient.address = address
    if contact_number:
        patient.contact_number = contact_number
    if gender:
        patient.gender = gender
    if date_of_birth:
        patient.date_of_birth = date_of_birth
    if full_name:
        patient.full_name = full_name   
    db.commit()
    db.refresh(patient)

    return patient
    


@router.put("/staff/{staff_id}/update", response_model=ProfileUpdateResponse)
def update_staff_profile(staff_id: int,
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    contact_number: Optional[str] = Form(None),
    db: Session = Depends(get_db), current_user: User = Depends(staff)):
    """Update a staff's profile."""
    if current_user.id != staff_id:
        raise HTTPException(status_code=403, detail="You are not authorized to update this staff's profile")
    
    staff = db.query(User).filter(User.id == staff_id).first()
    if not staff:
        raise HTTPException(status_code=404, detail="Staff not found")

    if email:
        # Check if email is already in use
        existing_staff = db.query(User).filter(User.email == email).first()
        if existing_staff and existing_staff.id != staff_id:
            raise HTTPException(status_code=400, detail="Email already in use")
        staff.email = email

    if address:
        staff.address = address
    if contact_number:
        staff.contact_number = contact_number
    if full_name:
        staff.full_name = full_name
    if email:
        staff.email = email
    db.commit()
    db.refresh(staff)

    return staff
    

    
@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(staff)):
    user = db.query(User).filter(User.id == current_user.id).first()
    
    # Verify current password
    if not verify_password(request.current_password, user.hashed_password):
        raise HTTPException(status_code=404, detail="Current password is incorrect")
    # Hash new password
    hashed_new_password = hash_password(request.new_password)
    user.hashed_password = hashed_new_password
    db.commit()
    db.refresh(user)

    return user


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Handle password reset requests."""
    # Check if the email is registered
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Email not registered")

    # Generate a reset token with an expiration time (e.g., 1 hour)
    reset_token = create_reset_token(user.id, expires_delta=timedelta(hours=1))
    # Create the reset link
    reset_link = f"{os.getenv('RESET_LINK')}?token={reset_token}"
    # Send the reset email using Mailgun
    email_sent = await send_reset_email(request.email, reset_link)
    if not email_sent:
        raise HTTPException(status_code=500, detail="Failed to send reset email")
 
    return {"message": "Reset link sent to your email"}



@router.put("/reset-password")
def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Handle password reset requests."""
    # Verify the reset token
    user_id = verify_reset_token(request.token)
    if not user_id:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    # Find the user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Hash the new password and update the user
    user.hashed_password = hash_password(request.new_password)
    db.commit()

    return {"message": "Password reset successfully"}



@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db), _: User = Depends(admin_only)):
    """"Delete a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    db.delete(user)
    db.commit()
    return user
    
    
@router.delete("/{user_id}/picture", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_picture(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff)
):
    """Remove user's profile picture"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.profile_picture = None
    user.profile_picture_type = None
    db.commit()
    return 


@router.delete("/{patient_id}/picture", status_code=status.HTTP_204_NO_CONTENT)
def delete_patient_picture(
    patient_id: int,
    db: Session = Depends(get_db),
    current_patient: Patient = Depends(RoleChecker(["patient"]))
):
    """Remove patient's profile picture"""
    if current_patient.id != patient_id and current_patient.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    patient.profile_picture = None
    patient.profile_picture_type = None
    db.commit()
    return 



@router.get("/{user_id}/updates")
def check_user_updates(
    user_id: int,
    since: datetime,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff)
):
    """
    Check for updates since a specific timestamp.
    Returns only the fields that have changed.
    """
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if since.tzinfo is None:
        since = since.replace(tzinfo=timezone.utc)
    
    if user.updated_at is None:
        return {'updated': False, 'changes': {}}
    
    user_updated_at = user.updated_at.replace(tzinfo=timezone.utc)
    
    
    updates = {}
    if user.updated_at > since:
        # Compare each field to see what changed
        original_values = {
            'full_name': user.full_name,
            'email': user.email,
            'contact_number': user.contact_number,
            'address': user.address,
            'profile_picture': user.profile_picture is not None,
            'settings': user.settings if hasattr(user, 'settings') else None
        }
        
        current_values = {
            'full_name': user.full_name,
            'email': user.email,
            'contact_number': user.contact_number,
            'address': user.address,
            'profile_picture': user.profile_picture is not None,
            'settings': user.settings if hasattr(user, 'settings') else None
        }
        
        for field in original_values:
            if original_values[field] != current_values[field]:
                updates[field] = current_values[field]
    
    return {'updated': bool(updates), 'changes': updates}

@router.put("/{user_id}/settings", response_model=UserResponse)
def update_user_settings(
    user_id: int,
    settings: UserSettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff)
):
    """Update user settings including notifications and preferences"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Convert settings to JSON string for storage
        settings_json = json.dumps(settings.model_dump())
        user.settings = settings_json
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating settings: {str(e)}")

@router.put("/{user_id}/security-questions", response_model=UserResponse)
def update_security_questions(
    user_id: int,
    questions: List[SecurityQuestion],
    db: Session = Depends(get_db),
    current_user: User = Depends(staff)
):
    """Update user security questions"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        # Hash answers before storing
        for question in questions:
            question.answer = hash_password(question.answer)
        
        user.security_questions = json.dumps([q.model_dump() for q in questions])
        db.commit()
        db.refresh(user)
        return user
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating security questions: {str(e)}")

@router.get("/{user_id}/notifications", response_model=NotificationSettings)
def get_notification_settings(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff)
):
    """Get user notification settings"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.settings:
        return NotificationSettings()
    
    try:
        settings = json.loads(user.settings)
        return NotificationSettings(**settings.get('notifications', {}))
    except:
        return NotificationSettings()

@router.put("/{user_id}/notifications", response_model=NotificationSettings)
def update_notification_settings(
    user_id: int,
    settings: NotificationSettings,
    db: Session = Depends(get_db),
    current_user: User = Depends(staff)
):
    """Update user notification settings"""
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    current_settings = {}
    if user.settings:
        current_settings = json.loads(user.settings)
    
    current_settings['notifications'] = settings.model_dump()
    
    try:
        user.settings = json.dumps(current_settings)
        db.commit()
        db.refresh(user)
        return settings
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Error updating notifications: {str(e)}")

