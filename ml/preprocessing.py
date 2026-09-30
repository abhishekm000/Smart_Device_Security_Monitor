import pandas as pd
import numpy as np
import os
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

# Normalize attack categories
def normalize_label(label):
    label = label.lower()
    if 'benign' in label:
        return 'Benign'
    elif 'ddos' in label:
        return 'DDoS'
    elif 'dos' in label:
        return 'DoS'
    elif 'mirai' in label:
        return 'Mirai'
    elif 'recon' in label:
        return 'Reconnaissance'
    elif 'spoof' in label:
        return 'Spoofing'
    elif 'brute' in label:
        return 'Brute Force'
    elif 'web' in label or 'xss' in label or 'sql' in label:
        return 'Web-based attacks'
    else:
        return 'Other'

def load_and_preprocess_data(data_path='data/sample/ciciot2023_sample.csv', target_col='label'):
    """Loads and preprocesses the CICIoT2023 dataset."""
    print(f"Loading dataset from {data_path}...")
    try:
        df = pd.read_csv(data_path)
    except FileNotFoundError:
        print(f"Error: Dataset not found at {data_path}")
        return None, None, None, None, None
    
    print(f"Original shape: {df.shape}")
    
    # 1. Clean basic issues
    df = df.drop_duplicates()
    df = df.replace([np.inf, -np.inf], np.nan)
    
    # 2. Extract features and target
    if target_col not in df.columns:
        print(f"Error: Target column '{target_col}' not found.")
        return None, None, None, None, None
        
    y_raw = df[target_col]
    X = df.drop(columns=[target_col])
    
    # Normalize labels
    y_normalized = y_raw.apply(normalize_label)
    
    # Encode target labels
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_normalized)
    
    # Identify numeric and categorical columns
    numeric_features = X.select_dtypes(include=['int64', 'float64']).columns.tolist()
    categorical_features = X.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # 3. Create Preprocessing Pipeline
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])
    
    # For this specific dataset, almost all are numeric. If any are categorical, impute and encode.
    # To avoid complex OneHotEncoding on unknown columns, we drop string columns in this simple demo if they exist,
    # except we expect all to be numeric based on CICIoT2023 spec.
    
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features)
        ],
        remainder='drop' # Drop categorical features if any exist unexpectedly
    )
    
    # 4. Fit transform
    print("Fitting preprocessor...")
    X_processed = preprocessor.fit_transform(X)
    
    # 5. Train-test split
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X_processed, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Save artifacts
    os.makedirs('models', exist_ok=True)
    joblib.dump(preprocessor, 'models/preprocessor.pkl')
    joblib.dump(label_encoder, 'models/label_encoder.pkl')
    
    # Save feature names for later use (e.g., SHAP)
    joblib.dump(numeric_features, 'models/feature_names.pkl')
    
    print(f"Training set: {X_train.shape}, Test set: {X_test.shape}")
    return X_train, X_test, y_train, y_test, label_encoder

if __name__ == '__main__':
    load_and_preprocess_data()
