from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.cache import init_redis
from core.database import async_engine, Base
from routers import (
    auth, patients, doctors, pharmacy, lab, radiology, 
    icu, appointment, admissions, users, medical_record,
    inpatient, patient_vitals, dashboard, billing, ai_routes,
    beds, departments, wards
)

app = FastAPI(title="Hospital Management System")

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Redis cache on startup
@app.on_event("startup")
async def startup():
    # Initialize database
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize Redis cache
    await init_redis(app)

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

@app.get("/")
async def root():
    return {"message": "Hospital Management System API"}