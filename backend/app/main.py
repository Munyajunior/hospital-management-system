from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  
from routers import (auth, patients, doctors, pharmacy, 
                     lab, radiology, icu, appointment, admissions, 
                     medical_record, admissions, beds, departments, wards, inpatient, patient_vitals,
                     dashboard, billing, ai_routes)
from core.database import Base, engine

# Initialize the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospital Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (or specify your Flutter app's origin)
    allow_credentials=True,
    allow_methods=["POST", "GET", "PUT", "DELETE", "OPTIONS"],  # Allow all methods (or specify ["POST", "OPTIONS"])
    allow_headers=["*"],  # Allow all headers
)
# Include authentication routes
app.include_router(auth.router)
app.include_router(patients.router) 
app.include_router(doctors.router)
app.include_router(pharmacy.router)
app.include_router(lab.router)
app.include_router(radiology.router)
app.include_router(icu.router)
app.include_router(appointment.router)
app.include_router(admissions.router)
app.include_router(medical_record.router)
app.include_router(inpatient.router)
app.include_router(beds.router)
app.include_router(wards.router)
app.include_router(departments.router)
app.include_router(patient_vitals.router)
app.include_router(dashboard.router)
app.include_router(billing.router)
app.include_router(ai_routes.router)


@app.get("/")
def root():
    return {"message": "Hospital Management System API"}
