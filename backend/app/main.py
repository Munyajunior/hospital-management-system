# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import (
    auth, patients, doctors, pharmacy, lab, radiology, icu, 
    appointment, admissions, users, medical_record, beds, 
    departments, wards, inpatient, patient_vitals, dashboard, 
    billing, ai_routes
)
from core.database import Base
from alembic.config import Config
from alembic import command

app = FastAPI(title="Hospital Management System")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
) 



# Include all routers
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
app.include_router(users.router)


def run_migrations():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

@app.get("/")
async def root():
    run_migrations()
    return {"message": "Hospital Management System API"}