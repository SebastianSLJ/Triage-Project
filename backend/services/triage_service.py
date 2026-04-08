import joblib
import pandas as pd
from pathlib import Path
from ..schemas.triage import PatientCondition

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "triage_pipeline.pkl"

model = None

FEATURE_ORDER = [
    "symptoms", "age", "gender", "HR", "spo2",
    "temperature", "SBP", "RR",
    "duration_hours", "severe_history"
]

def get_model():
    global model
    if model is None:
        model = joblib.load(MODEL_PATH)
    return model

def predict_triage(data: PatientCondition):
    gender_map = {"male": 1, "female": 0}

    input_dict = {
        "symptoms": " ".join(data.symptoms) if isinstance(data.symptoms, list) else data.symptoms,
        "age": data.age,
        "gender": gender_map.get(data.gender.lower(), 0),
        "HR": data.HR,
        "spo2": data.spo2,
        "temperature": data.temperature,
        "SBP": data.SBP,
        "RR": data.RR,
        "duration_hours": data.duration_hours,
        "severe_history": 1 if data.severe_history else 0
    }

    df_input = pd.DataFrame([input_dict])[FEATURE_ORDER]

    prediction = get_model().predict(df_input)[0]

    return int(prediction)