import pytest
import os
from backend.config import Config
from backend.services.ml_service import MLService

def test_ml_service_load():
    # Only test if models have been trained
    if os.path.exists(os.path.join(Config.MODEL_DIR, 'xgboost.pkl')):
        service = MLService()
        assert service.xgb_model is not None
        assert service.preprocessor is not None
        
        # Test basic prediction with dummy data
        dummy_data = {feature: 0 for feature in service.feature_names}
        result = service.predict(dummy_data)
        
        assert 'prediction' in result
        assert 'confidence' in result
        assert 'is_anomaly' in result
