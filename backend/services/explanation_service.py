import shap
import numpy as np

class ExplanationService:
    def __init__(self, ml_service):
        self.ml_service = ml_service
        self.explainer = None

    def initialize_explainer(self, sample_background):
        if self.ml_service.xgb_model:
            # TreeExplainer is fast for XGBoost
            self.explainer = shap.TreeExplainer(self.ml_service.xgb_model)

    def explain_prediction(self, processed_features):
        if not self.explainer:
            if self.ml_service.xgb_model:
                self.explainer = shap.TreeExplainer(self.ml_service.xgb_model)
            else:
                return []

        try:
            shap_values = self.explainer.shap_values(processed_features)
            
            # For multi-class, shap_values might be a list of arrays (one per class).
            # We want the explanation for the predicted class.
            pred_idx = self.ml_service.xgb_model.predict(processed_features)[0]
            
            if isinstance(shap_values, list):
                class_shap_values = shap_values[pred_idx][0]
            else:
                # Binary or newer shap version format
                if len(shap_values.shape) == 3:
                    class_shap_values = shap_values[0, :, pred_idx]
                else:
                    class_shap_values = shap_values[0]

            feature_names = self.ml_service.feature_names
            
            # Combine names and absolute shap values to find most important
            importance = np.abs(class_shap_values)
            top_indices = np.argsort(importance)[::-1][:5] # Top 5
            
            explanation = []
            for idx in top_indices:
                explanation.append({
                    "feature": feature_names[idx],
                    "importance": float(importance[idx]),
                    "value_contribution": float(class_shap_values[idx])
                })
            return explanation
        except Exception as e:
            print(f"SHAP explanation failed: {e}")
            return []
