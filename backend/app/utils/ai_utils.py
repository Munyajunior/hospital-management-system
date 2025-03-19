from statsmodels.tsa.arima.model import ARIMA
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import LocalOutlierFactor
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from transformers import pipeline

class PredictiveAnalytics:
    def __init__(self, data):
        self.data = data

    def predict_patient_admissions(self):
        if len(self.data) < 10:  # Ensure enough data points
            raise ValueError("Not enough data to train ARIMA model")

        model = ARIMA(self.data['admissions'], order=(5, 1, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=7)  # Predict next 7 days
        return forecast

    def calculate_no_show_rate(self):
        """Calculate the no-show rate based on appointment data."""
        if self.data.empty:
            raise ValueError("No appointment data provided")

        # Filter appointments with status "Completed" or "Canceled"
        completed_appointments = self.data[self.data['status'] == 'Completed']
        canceled_appointments = self.data[self.data['status'] == 'Canceled']

        # Total appointments (excluding rescheduled)
        total_appointments = len(completed_appointments) + len(canceled_appointments)

        if total_appointments == 0:
            return 0  # Avoid division by zero

        # No-shows are canceled appointments
        no_shows = len(canceled_appointments)

        # Calculate no-show rate
        no_show_rate = (no_shows / total_appointments) * 100
        return no_show_rate


class AnomalyDetection:
    def __init__(self, data):
        self.data = data

    def detect_anomalies_in_vitals(self):
        """Detect anomalies in patient vitals using Isolation Forest."""
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(self.data[['blood_pressure', 'heart_rate', 'temperature']])
        model = IsolationForest(contamination=0.1)  # 10% of data is considered anomalous
        anomalies = model.fit_predict(scaled_data)
        return anomalies

class NLPProcessor:
    def __init__(self):
        self.summarizer = pipeline("summarization")

    def summarize_text(self, text):
        """Summarize patient notes or medical records."""
        summary = self.summarizer(text, max_length=50, min_length=25, do_sample=False)
        return summary[0]['summary_text']