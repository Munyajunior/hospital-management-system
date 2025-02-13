# Hospital Management System Backend (Updated)

## Project Overview

This project is a **Hospital Management System** with a **desktop application** (PySide6) for admins, nurses, and department users. The **mobile application** (to be developed later) will be for doctors and patients.

### **Project Structure**

#### **Frontend**

```
/hms_desktop/
/frontend/
│── main.py                 # Entry point of the application
│── requirements.txt         # Dependencies
│── config.py                # Configuration settings
│── database.py              # (If local storage or caching is needed)
│── utils.py                 # Utility functions (e.g., validation, formatting)
│
├─── core/                   # Core logic (backend interaction)
│    ├── api_client.py       # Handles API requests to FastAPI backend
│    ├── auth.py             # Authentication logic (JWT/session handling)
│    ├── rbac.py             # Role-Based Access Control enforcement
│
├─── models/                 # Data models (Sync with backend)
│    ├── user.py             # User model
│    ├── patient.py          # Patient model
│    ├── doctor.py           # Doctor model
│    ├── pharmacy.py         # Pharmacy model
│    ├── lab.py              # Lab model
│    ├── radiology.py        # Radiology model
│    ├── icu.py              # ICU model
│
├─── views/                  # UI components (QWidgets & QMainWindow)
│    ├── main_window.py      # Main application window
│    ├── login.py            # Login screen UI
│    ├── dashboard.py        # Dashboard UI
│    ├── user_management.py  # User management UI (Admin Panel)
│    ├── patient_view.py     # Patient management UI
│    ├── doctor_view.py      # Doctor management UI
│    ├── pharmacy_view.py    # Pharmacy UI
│    ├── lab_view.py         # Lab UI
│    ├── radiology_view.py   # Radiology UI
│    ├── icu_view.py         # ICU UI
│
├─── controllers/            # Handles logic between UI and backend
│    ├── main_controller.py  # Main application controller
│    ├── auth_controller.py  # Login & authentication handling
│    ├── user_controller.py  # User management logic
│    ├── patient_controller.py # Patient management logic
│    ├── doctor_controller.py # Doctor management logic
│    ├── pharmacy_controller.py # Pharmacy logic
│    ├── lab_controller.py # Lab logic
│    ├── radiology_controller.py # Radiology logic
│    ├── icu_controller.py # ICU logic
│
├─── assets/                 # Static assets (icons, images, stylesheets)
│    ├── icons/              # Icons for UI elements
│    ├── styles.qss          # Global stylesheet
│
└─── tests/                  # Unit and integration tests
     ├── test_auth.py        # Tests for authentication
     ├── test_patient.py     # Tests for patient management
     ├── test_doctor.py      # Tests for doctor management

```

#### **Backend**

```
backend/
app/
│── api/
│   ├── auth.py 
│── models/
│   ├── user.py         # User models (Admin, Nurse, Receptionist, Pharmacist, Lab Technician,Radiologist)
│   ├── patient.py      # Patient models (Admissions, Records, Appointments, Billing)
│   ├── doctor.py       # Doctor models (Doctors assigned to patients)
│   ├── pharmacy.py     # Pharmacy models (Prescriptions, Inventory, Billing)
│   ├── lab.py          # Lab models (Lab Requests, Lab Results)
│   ├── radiology.py    # Radiology models (Scan Requests, Scan Results)
│   ├── icu.py          # ICU models (Admissions, Beds)
│── schemas/
│   ├── auth.py         # Authentication schemas
│   ├── user.py         # User schemas
│   ├── patient.py      # Patient schemas
│   ├── doctor.py       # Doctor schemas
│   ├── pharmacy.py     # Pharmacy schemas
│   ├── lab.py          # Lab schemas
│   ├── radiology.py    # Radiology schemas
│   ├── icu.py          # ICU schemas
│── routers/
│   ├── auth.py         # User authentication & JWT handling
│   ├── user.py         # Admin manages users
│   ├── patient.py      # Patient management (Receptionist, Nurse access)
│   ├── doctor.py       # Doctor assignments (Admin assigns doctors)
│   ├── pharmacy.py     # Pharmacy management
│   ├── lab.py          # Lab management
│   ├── radiology.py    # Radiology management
│   ├── icu.py          # ICU management
│── core/
│   ├── database.py         # Database session handling
│   ├── security.py      # Database session handling
│── main.py             # Application entry point
│── utils/
    ├──security.py
```

## **Authentication & User Roles**
1. **Admin**
   - Logs in after splash screen
   - Manages all users (creates receptionists, nurses, pharmacists, lab techs, radiologists, and doctors)
   - Full system control

2. **Receptionist/Nurse**
   - Logs in after splash screen
   - Manages patient records (register, update, view)
   - Schedules appointments based on doctor availability
   - Assigns patients to doctors for follow-up
   - Requests lab/radiology tests
   - Admits/discharges patients, assigns to wards/beds
   - Processes payments & billing
   - Manages ICU department

3. **Pharmacist**
   - Logs in after splash screen
   - Views prescriptions assigned by doctors
   - Manages inventory & dispenses medications

4. **Lab Technician**
   - Logs in after splash screen
   - Receives test requests from receptionists & doctors
   - Processes & updates lab results

5. **Radiologist**
   - Logs in after splash screen
   - Receives scan requests from receptionists & doctors
   - Processes & updates radiology reports

6. **Doctor (Mobile App)** *(Not implemented yet, for future development)*
   - Views assigned patients
   - Updates medical records
   - Prescribes medications (sent to pharmacy)
   - Requests lab/radiology tests
   - Communicates with patients via real-time chat

## **API Updates Based on New Logic**

### **Authentication (auth.py)**

- Secure JWT authentication for all users.
- Only **admins** can create other users (receptionist, nurse, lab, radiology, pharmacy users).

### **User Management (user.py)**

- `POST /users/` → Admin creates new users.
- `GET /users/` → Admin retrieves all users.
- `GET /users/{user_id}` → Retrieve user details.

### **Patient Management (patient.py)**

- `POST /patients/` → Receptionist/Nurse registers a new patient.
- `GET /patients/` → Retrieve all patient records.
- `PUT /patients/{id}` → Update patient details.
- `POST /patients/assign-doctor/` → Assign patient to a doctor.
- `POST /patients/admit/` → Admit patient to a ward/ICU.
- `POST /patients/discharge/` → Discharge patient.
- `POST /patients/request-lab/` → Request a lab test.
- `POST /patients/request-radiology/` → Request a scan.

### **Doctor Management (doctor.py)**

- `POST /doctors/` → Admin registers a new doctor.
- `GET /doctors/` → Retrieve all doctors.
- `POST /doctors/assign-patient/` → Assign a patient to a doctor.

### **Pharmacy Management (pharmacy.py)**

- `POST /pharmacy/prescription/` → Doctor assigns prescription.
- `GET /pharmacy/` → Pharmacist views prescriptions.
- `PUT /pharmacy/update-stock/` → Update drug inventory.

### **Lab Management (lab.py)**

- `POST /lab/request/` → Request a lab test.
- `GET /lab/` → Lab tech views all test requests.
- `PUT /lab/update-result/` → Upload lab results.

### **Radiology Management (radiology.py)**

- `POST /radiology/request/` → Request a scan.
- `GET /radiology/` → Radiologist views scan requests.
- `PUT /radiology/update-result/` → Upload scan results.

### **ICU Management (icu.py)**

- `POST /icu/admit/` → Admit patient to ICU.
- `GET /icu/` → Retrieve all ICU patients.
- `POST /icu/discharge/` → Discharge patient.

## **Next Steps**

✅ **Refactor existing code to match new structure.**  
✅ **Ensure all endpoints follow new access control rules.**  
✅ **Update test cases based on new logic.**  
⏳ **Implement frontend (PySide6) once backend is finalized.**

