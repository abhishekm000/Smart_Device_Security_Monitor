# Machine Learning Pipeline

## Preprocessing (`ml/preprocessing.py`)
1. **Cleaning**: Drops duplicate rows and removes `NaN` / `Inf` values.
2. **Target Encoding**: The `normalize_label` function groups dozens of specific attack subtypes into broader, normalized categories (e.g., `DDoS`, `DoS`, `Reconnaissance`). The classes are then integer-encoded.
3. **Scaling**: A scikit-learn `Pipeline` applies `SimpleImputer` (median) and `StandardScaler` to all numeric features.
4. **Export**: The fitted scaler and label encoder are saved to `models/` using `joblib` so they can be perfectly reproduced during live inference.

## Training (`ml/train.py`)
Trains three models concurrently:
- **Random Forest**: Good baseline ensemble method.
- **XGBoost**: High-performance gradient boosting. Generally selected as the primary classifier.
- **Isolation Forest**: Unsupervised anomaly detection.

Evaluates precision, recall, f1, and false positive rates. Output artifacts include `metrics.json`, `confusion_matrix.png`, and `feature_importance.png`.
