from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from models.admission import PatientAdmission, PatientVitals
from models.appointment import Appointment
from core.database import get_db
from utils.ai_utils import PredictiveAnalytics, AnomalyDetection, NLPProcessor
from models.admission import PatientVitals
from models.lab import LabTest
from models.radiology import RadiologyScan
from typing import List, Dict


router = APIRouter(prefix="/ai", tags=["AI"])

@router.get("/predict-admissions", response_model=Dict[str, float])
def predict_admissions(db: Session = Depends(get_db)):
    """Predict patient admissions for the next 7 days."""
    admissions_data = db.query(PatientAdmission).all()
    
    if not admissions_data:
        raise HTTPException(status_code=404, detail="No admissions data found")

    admissions = [admission.admission_date for admission in admissions_data]
    admissions_df = pd.DataFrame(admissions, columns=['admissions'])
    admissions_df['admissions'] = pd.to_datetime(admissions_df['admissions'])
    admissions_df.set_index('admissions', inplace=True)


    if admissions_df.empty:
        raise HTTPException(status_code=400, detail="Insufficient data for prediction")

    ai = PredictiveAnalytics(admissions_df)
    forecast = ai.predict_patient_admissions()
    return {"predictions": forecast.tolist()}


@router.get("/no-show-rate", response_model=Dict[str, float])
def get_no_show_rate(db: Session = Depends(get_db)):
    """Calculate the no-show rate for appointments."""
    appointments = db.query(Appointment).all()
    if not appointments:
        raise HTTPException(status_code=404, detail="No appointment data found")

    # Convert appointments to DataFrame
    appointments_df = pd.DataFrame([a.__dict__ for a in appointments])

    # Calculate no-show rate
    ai = PredictiveAnalytics(appointments_df)
    no_show_rate = ai.calculate_no_show_rate()
    return {"no_show_rate": no_show_rate}

@router.get("/detect-anomalies/vitals", response_model=Dict[str, List[int]])
def detect_anomalies_in_vitals(db: Session = Depends(get_db)):
    """Detect anomalies in all patients' vitals."""
    vitals = db.query(PatientVitals).all()
    vitals_df = pd.DataFrame([v.__dict__ for v in vitals])
    ai = AnomalyDetection(vitals_df)
    anomalies = ai.detect_anomalies_in_vitals()
    return {"anomalies": anomalies.tolist()}

@router.get("/detect-anomalies/lab-tests", response_model=Dict[str, List[int]])
def detect_anomalies_in_lab_tests(db: Session = Depends(get_db)):
    """Detect anomalies in lab test results."""
    lab_tests = db.query(LabTest).all()
    lab_tests_df = pd.DataFrame([lt.__dict__ for lt in lab_tests])
    ai = AnomalyDetection(lab_tests_df)
    anomalies = ai.detect_anomalies_in_vitals()  # Reuse the same method for simplicity
    return {"anomalies": anomalies.tolist()}

@router.get("/detect-anomalies/radiology-scans", response_model=Dict[str, List[int]])
def detect_anomalies_in_radiology_scans(db: Session = Depends(get_db)):
    """Detect anomalies in radiology scans."""
    scans = db.query(RadiologyScan).all()
    scans_df = pd.DataFrame([s.__dict__ for s in scans])
    ai = AnomalyDetection(scans_df)
    anomalies = ai.detect_anomalies_in_vitals()  # Reuse the same method for simplicity
    return {"anomalies": anomalies.tolist()}

@router.post("/summarize-text", response_model=Dict[str, str])
def summarize_text(text: str):
    """Summarize patient notes or medical records."""
    nlp = NLPProcessor()
    summary = nlp.summarize_text(text)
    return {"summary": summary}
