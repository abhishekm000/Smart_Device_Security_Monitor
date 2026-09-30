# Smart Device Security Monitor

## Architecture Overview

The system consists of three main components:

1. **Machine Learning Pipeline**:
   - `ml/preprocessing.py`: Handles missing values, scaling, label encoding, and dataset splitting.
   - `ml/train.py`: Trains Random Forest, XGBoost, and Isolation Forest models. Saves artifacts to the `models/` directory.

2. **Flask Backend**:
   - Provides a REST API (`/api/predict`, `/api/alerts`, etc.).
   - Uses `services/ml_service.py` to load trained models and execute inference.
   - Uses `services/risk_service.py` to calculate a composite risk score based on the ML prediction, confidence, and anomaly score.
   - Uses `services/explanation_service.py` (SHAP) to explain model decisions.
   - A `simulation_service.py` runs a background thread that replays network traffic from a dataset, feeding it into the prediction pipeline to simulate real-time traffic.

3. **Frontend Dashboard**:
   - A Single Page Application (SPA) using HTML, CSS, Bootstrap, and plain JavaScript.
   - Polls the backend API for real-time alerts, devices, and metrics.
   - Displays real-time charts and an interactive threat timeline.

## Data Flow

1. Traffic features are sent as JSON to `POST /api/predict`.
2. The ML Service preprocesses the data using the saved `preprocessor.pkl`.
3. The data is passed to the primary supervised model (XGBoost) to classify the attack type.
4. The data is passed to the Isolation Forest model to detect anomalous behavior.
5. The Risk Service combines these results to generate a 0-100 risk score and level (LOW/MEDIUM/HIGH).
6. The Explanation Service uses SHAP to identify the top contributing features for the prediction.
7. The result is returned and saved to the SQLite Database as an Alert.
8. The Frontend fetches these alerts and updates the dashboard.
