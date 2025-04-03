from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import timedelta
import os
from models.user import User
from models.patient import Patient
from schemas.auth import (UserResponse, IsActive, UserUpdate, AllUserResponse,ProfileUpdateResponse,
                          ChangePasswordRequest, ResetPasswordRequest, ForgotPasswordRequest)
from models.user import User
from models.patient import Patient
from utils.security import hash_password, verify_password, create_reset_token, verify_reset_token
from utils.email_util import send_reset_email
from core.database import get_db
from core.dependencies import RoleChecker, get_current_active_user
from utils.security import hash_password


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
def get_staff_by_id(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Fetch a user by their ID.
    Only the user themselves or an admin can access this endpoint.
    """
    # Check if the current user is the same as the requested user or an admin
    if current_user.id != user_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this user's information")

    # Fetch the user from the database
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@router.get("/patient/{patient_id}", response_model=UserResponse)
def get_patient_by_id(patient_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
    """
    Fetch a user by their ID.
    Only the user themselves or an admin can access this endpoint.
    """
    # Check if the current user is the same as the requested user or an admin
    if current_user.id != patient_id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You are not authorized to access this user's information")

    # Fetch the user from the database
    user = db.query(Patient).filter(Patient.id == patient_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


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

@router.put("/patient/{patient_id}/update", response_model=ProfileUpdateResponse)
def update_patient_profile(patient_id: int, 
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    contact_number: Optional[str] = Form(None),
    date_of_birth: Optional[str] = Form(None),
    gender: Optional[str] = Form(None),
    profile_picture: UploadFile = File(None), db: Session = Depends(get_db), current_user: User = Depends(RoleChecker(["patient"]))):
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
    if profile_picture:
        try:
            # Read and encode the image
            image_data = profile_picture.file.read()
            content_type = profile_picture.content_type
            patient.set_profile_picture(image_data, content_type)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")
        finally:
            profile_picture.file.close()
            
    db.commit()
    db.refresh(patient)

    return patient
    


@router.put("/staff/{staff_id}/update", response_model=ProfileUpdateResponse)
def update_staff_profile(staff_id: int,
    full_name: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    contact_number: Optional[str] = Form(None),
    profile_picture: UploadFile = File(None), db: Session = Depends(get_db), current_user: User = Depends(staff)):
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
    if profile_picture:
        try:
            # Read the image synchronously
            image_data = profile_picture.file.read()
            content_type = profile_picture.content_type
            staff.set_profile_picture(image_data, content_type)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to process image: {str(e)}")
        finally:
            profile_picture.file.close()

    db.commit()
    db.refresh(staff)

    return staff
    


    
  
    
@router.post("/change-password", status_code=status.HTTP_200_OK)
def change_password(request: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_active_user)):
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
    