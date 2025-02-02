from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.session import engine, Base
from routers import auth, patients, doctors, pharmacy, lab, radiology, icu
#from backend.websockets.websockets import router as websocket_router
#from backend.websockets import websockets

# Auto-create tables (alternative to Alembic migrations)
Base.metadata.create_all(bind=engine)

# Create FastAPI app instance
app = FastAPI(title="Hospital Management System API", version="1.0.0")

# Enable CORS for frontend or external apps
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change this to specific domains for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers for different modules
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(patients.router, prefix="/patients", tags=["Patients"])
app.include_router(doctors.router, prefix="/doctors", tags=["Doctors"])
app.include_router(pharmacy.router, prefix="/pharmacy", tags=["Pharmacy"])
app.include_router(lab.router, prefix="/lab", tags=["Medical Lab"])
app.include_router(radiology.router, prefix="/radiology", tags=["Radiology"])
app.include_router(icu.router, prefix="/icu", tags=["ICU"])
#app.include_router(websocket_router, prefix="/ws", tags=["WebSockets"])
#app.include_router(websockets.router, prefix="/ws", tags=["WebSockets"])

# Root endpoint (for API status check)
@app.get("/")
async def root():
    return {"message": "Hospital Management System API is running!"}
