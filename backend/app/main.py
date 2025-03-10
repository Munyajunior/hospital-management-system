from fastapi import FastAPI
from routers import auth, patients, doctors, pharmacy, lab, radiology, icu, nurse, appointment
from core.database import Base, engine

# Initialize the database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Hospital Management System")

# Include authentication routes
app.include_router(auth.router)
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(pharmacy.router)
app.include_router(lab.router)
app.include_router(radiology.router)
app.include_router(icu.router)
app.include_router(nurse.router)
app.include_router(appointment.router)

@app.get("/")
def root():
    return {"message": "Hospital Management System API"}
