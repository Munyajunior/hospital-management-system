# Hospital Management System Backend (Updated)

## Project Overview

This project is a **Hospital Management System** with a **desktop application** (PySide6) for admins, nurses, and department users. The **mobile application** (to be developed later) will be for doctors and patients.

### **Project Structure**

#### **Frontend**

```
hospital_management_system_desktop/
frontend/
│── main.py                # Entry point for the frontend
│── views/
│   ├── login.py           # Login UI
│   ├── dashboard.py       # Dashboard UI
│   ├── patient.py         # Patient Management UI
│   ├── doctor.py          # Doctor Management UI
│   ├── pharmacy.py        # Pharmacy UI
│   ├── lab.py             # Lab Management UI
│   ├── radiology.py       # Radiology UI
│   ├── icu.py             # ICU Management UI
│── components/
│   ├── sidebar.py         # Sidebar navigation
│   ├── header.py          # Header bar
│── core/
│   ├── api.py             # API calls
│   ├── auth.py            # Authentication handler
│── utils/
│   ├── config.py          # Environment variables & settings
│── assets/                # Icons, images, etc.

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

## **API Updates to secure endpoints**

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

## **Next Steps for future enhancements**

✅ **Refactor existing code to reduce redundancy and make code base modular.**  
✅ **Ensure all endpoints follow new access control rules.**  
✅ **Update test cases **  
⏳ **Implement frontend (PySide6) once backend is finalized.**

## How to RUN/Start Project

### In the terminal: Create virtual environment

```
python -m venv .venv
```

**Activate virtual environment**

```
.venv/scripts/activate
```

**Install required libraries**

```pip install -r requirements.txt```

**Navigate to backend/app**

```cd backend/app```

**Start Server and initialize all routes**

```uvicorn main:app --reload```

**Navigate to frontend/**

```cd ../../frontend/```

**run main.py**

```
python main.py
```