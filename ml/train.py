import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from preprocessing import load_and_preprocess_data

def evaluate_model(model, X_test, y_test, label_encoder, model_name):
    print(f"\nEvaluating {model_name}...")
    y_pred = model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    # Calculate FPR and FNR (macro average approximation)
    cm = confusion_matrix(y_test, y_pred)
    FP = cm.sum(axis=0) - np.diag(cm)
    FN = cm.sum(axis=1) - np.diag(cm)
    TP = np.diag(cm)
    TN = cm.sum() - (FP + FN + TP)
    
    FPR = np.mean(FP / (FP + TN + 1e-10))
    FNR = np.mean(FN / (FN + TP + 1e-10))
    
    metrics = {
        'accuracy': float(accuracy),
        'precision': float(precision),
        'recall': float(recall),
        'f1_score': float(f1),
        'fpr': float(FPR),
        'fnr': float(FNR),
        'detection_rate': float(recall) # Overall recall is often used as detection rate
    }
    
    # Save Confusion Matrix plot
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=label_encoder.classes_,
                yticklabels=label_encoder.classes_)
    plt.title(f'{model_name} Confusion Matrix')
    plt.ylabel('Actual')
    plt.xlabel('Predicted')
    plt.tight_layout()
    os.makedirs('results', exist_ok=True)
    plt.savefig(f'results/{model_name.lower().replace(" ", "_")}_confusion_matrix.png')
    plt.close()
    
    return metrics

def train_models():
    print("========================================")
    print("SMART DEVICE SECURITY MONITOR")
    print("MODEL TRAINING")
    print("========================================")
    
    X_train, X_test, y_train, y_test, label_encoder = load_and_preprocess_data()
    if X_train is None:
        return
        
    print(f"\nClasses: {label_encoder.classes_}")
    
    # 1. Random Forest
    print("\nTraining Random Forest...")
    rf_model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
    rf_model.fit(X_train, y_train)
    joblib.dump(rf_model, 'models/random_forest.pkl')
    print("DONE")
    
    # 2. XGBoost
    print("\nTraining XGBoost...")
    xgb_model = XGBClassifier(n_estimators=100, max_depth=6, random_state=42, use_label_encoder=False, eval_metric='mlogloss')
    xgb_model.fit(X_train, y_train)
    joblib.dump(xgb_model, 'models/xgboost.pkl')
    print("DONE")
    
    # 3. Isolation Forest (Anomaly Detection)
    print("\nTraining Isolation Forest...")
    # Train only on 'Benign' traffic for anomaly detection if possible, or train on everything.
    # We will train on a sample of the whole training set for simplicity in this demo.
    iso_model = IsolationForest(contamination=0.1, random_state=42)
    iso_model.fit(X_train)
    joblib.dump(iso_model, 'models/isolation_forest.pkl')
    print("DONE")
    
    # Evaluation
    rf_metrics = evaluate_model(rf_model, X_test, y_test, label_encoder, "Random Forest")
    xgb_metrics = evaluate_model(xgb_model, X_test, y_test, label_encoder, "XGBoost")
    
    all_metrics = {
        'Random Forest': rf_metrics,
        'XGBoost': xgb_metrics
    }
    
    with open('results/metrics.json', 'w') as f:
        json.dump(all_metrics, f, indent=4)
        
    # Generate Feature Importance for Best Model (Assuming XGBoost is usually better)
    feature_names = joblib.load('models/feature_names.pkl')
    importances = xgb_model.feature_importances_
    indices = np.argsort(importances)[::-1][:20] # Top 20
    
    plt.figure(figsize=(10, 8))
    plt.title("Top 20 Feature Importances (XGBoost)")
    plt.bar(range(20), importances[indices], align="center")
    plt.xticks(range(20), [feature_names[i] for i in indices], rotation=45, ha='right')
    plt.xlim([-1, 20])
    plt.tight_layout()
    plt.savefig('results/feature_importance.png')
    plt.close()
    
    print("\nEvaluation complete.")
    
    best_model_name = "XGBoost" if xgb_metrics['f1_score'] > rf_metrics['f1_score'] else "Random Forest"
    print(f"\nBest model: {best_model_name}")
    print("Models saved to 'models/' directory.")
    print("========================================")

if __name__ == '__main__':
    train_models()
