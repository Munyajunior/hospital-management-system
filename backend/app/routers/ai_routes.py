from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import pandas as pd
from models.admission import PatientAdmission, PatientVitals
from models.appointment import Appointment
from core.database import get_async_db
from utils.ai_utils import PredictiveAnalytics, AnomalyDetection, NLPProcessor
from models.lab import LabTest
from models.radiology import RadiologyScan
from typing import List, Dict
from core.cache import cache

router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/predict-admissions", response_model=Dict[str, float])
@cache(expire=3600)  # Cache for 1 hour
async def predict_admissions(db: AsyncSession = Depends(get_async_db)):
    """Predict patient admissions with async data fetching."""
    result = await db.execute(select(PatientAdmission))
    admissions_data = result.scalars().all()
    
    if not admissions_data:
        raise HTTPException(status_code=404, detail="No admissions data found")

    admissions = [admission.admission_date for admission in admissions_data]
    admissions_df = pd.DataFrame(admissions, columns=['admissions'])
    admissions_df['admissions'] = pd.to_datetime(admissions_df['admissions'])
    admissions_df.set_index('admissions', inplace=True)

    if admissions_df.empty:
        raise HTTPException(status_code=400, detail="Insufficient data for prediction")

    ai = PredictiveAnalytics(admissions_df)
    forecast = await ai.predict_patient_admissions()
    return {"predictions": forecast.tolist()}

@router.get("/no-show-rate", response_model=Dict[str, float])
@cache(expire=3600)  # Cache for 1 hour
async def get_no_show_rate(db: AsyncSession = Depends(get_async_db)):
    """Calculate no-show rate with async operations."""
    result = await db.execute(select(Appointment))
    appointments = result.scalars().all()
    
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointment data found")

    appointments_df = pd.DataFrame([a.__dict__ for a in appointments])
    ai = PredictiveAnalytics(appointments_df)
    no_show_rate = await ai.calculate_no_show_rate()
    return {"no_show_rate": no_show_rate}

@router.get("/detect-anomalies/vitals", response_model=Dict[str, List[int]])
@cache(expire=600)  # Cache for 10 minutes
async def detect_anomalies_in_vitals(db: AsyncSession = Depends(get_async_db)):
    """Detect anomalies in vitals with async data fetching."""
    result = await db.execute(select(PatientVitals))
    vitals = result.scalars().all()
    vitals_df = pd.DataFrame([v.__dict__ for v in vitals])
    ai = AnomalyDetection(vitals_df)
    anomalies = await ai.detect_anomalies_in_vitals()
    return {"anomalies": anomalies.tolist()}

@router.get("/detect-anomalies/lab-tests", response_model=Dict[str, List[int]])
@cache(expire=600)  # Cache for 10 minutes
async def detect_anomalies_in_lab_tests(db: AsyncSession = Depends(get_async_db)):
    """Detect anomalies in lab tests with async operations."""
    result = await db.execute(select(LabTest))
    lab_tests = result.scalars().all()
    lab_tests_df = pd.DataFrame([lt.__dict__ for lt in lab_tests])
    ai = AnomalyDetection(lab_tests_df)
    anomalies = await ai.detect_anomalies_in_vitals()
    return {"anomalies": anomalies.tolist()}

@router.get("/detect-anomalies/radiology-scans", response_model=Dict[str, List[int]])
@cache(expire=600)  # Cache for 10 minutes
async def detect_anomalies_in_radiology_scans(db: AsyncSession = Depends(get_async_db)):
    """Detect anomalies in radiology scans with async operations."""
    result = await db.execute(select(RadiologyScan))
    scans = result.scalars().all()
    scans_df = pd.DataFrame([s.__dict__ for s in scans])
    ai = AnomalyDetection(scans_df)
    anomalies = await ai.detect_anomalies_in_vitals()
    return {"anomalies": anomalies.tolist()}

@router.post("/summarize-text", response_model=Dict[str, str])
@cache(expire=3600)  # Cache for 1 hour
async def summarize_text(text: str):
    """Summarize text with caching."""
    nlp = NLPProcessor()
    summary = await nlp.summarize_text(text)
    return {"summary": summary}