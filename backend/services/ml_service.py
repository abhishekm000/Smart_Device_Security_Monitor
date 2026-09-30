import os
import joblib
import pandas as pd
import numpy as np
from ..config import Config

class MLService:
    def __init__(self):
        self.rf_model = None
        self.xgb_model = None
        self.iso_model = None
        self.preprocessor = None
        self.label_encoder = None
        self.feature_names = None
        self.load_models()

    def load_models(self):
        try:
            self.rf_model = joblib.load(os.path.join(Config.MODEL_DIR, 'random_forest.pkl'))
            self.xgb_model = joblib.load(os.path.join(Config.MODEL_DIR, 'xgboost.pkl'))
            self.iso_model = joblib.load(os.path.join(Config.MODEL_DIR, 'isolation_forest.pkl'))
            self.preprocessor = joblib.load(os.path.join(Config.MODEL_DIR, 'preprocessor.pkl'))
            self.label_encoder = joblib.load(os.path.join(Config.MODEL_DIR, 'label_encoder.pkl'))
            self.feature_names = joblib.load(os.path.join(Config.MODEL_DIR, 'feature_names.pkl'))
            print("Models loaded successfully.")
        except FileNotFoundError as e:
            print(f"Warning: Models not found. Please train models first. Details: {e}")

    def predict(self, features_dict):
        if not self.xgb_model or not self.preprocessor:
            raise ValueError("Models not initialized. Run training first.")
            
        # Ensure input has all expected features
        for f in self.feature_names:
            if f not in features_dict:
                features_dict[f] = 0.0 # Default fallback
                
        df_input = pd.DataFrame([features_dict], columns=self.feature_names)
        
        # Preprocess
        X_processed = self.preprocessor.transform(df_input)
        
        # Classify
        # We use XGBoost as primary
        pred_idx = self.xgb_model.predict(X_processed)[0]
        prediction = self.label_encoder.inverse_transform([pred_idx])[0]
        
        # Confidence
        proba = self.xgb_model.predict_proba(X_processed)[0]
        confidence = float(np.max(proba))
        
        # Anomaly Detection
        iso_pred = self.iso_model.predict(X_processed)[0]
        # isolation forest returns 1 for inliers, -1 for outliers
        is_anomaly = (iso_pred == -1)
        
        # Anomaly score (negative distance to decision boundary, smaller is more anomalous)
        anomaly_score_raw = self.iso_model.score_samples(X_processed)[0]
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "is_anomaly": bool(is_anomaly),
            "anomaly_score_raw": float(anomaly_score_raw),
            "processed_features": X_processed
        }

ml_service = MLService()
