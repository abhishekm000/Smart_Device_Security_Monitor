from flask import Blueprint, request, jsonify
from datetime import datetime
import json
from ..services.ml_service import ml_service
from ..services.risk_service import calculate_risk
from ..services.explanation_service import ExplanationService
from ..models import Alert
from ..database import db

prediction_bp = Blueprint('prediction', __name__)
explanation_service = ExplanationService(ml_service)

@prediction_bp.route('/predict', methods=['POST'])
def predict():
    data = request.json
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    try:
        # Predict
        result = ml_service.predict(data)
        
        # Risk
        risk_score, risk_level = calculate_risk(
            result['prediction'], 
            result['confidence'], 
            result['is_anomaly']
        )
        
        # Explain
        explanation = explanation_service.explain_prediction(result['processed_features'])
        
        response = {
            "prediction": result['prediction'],
            "confidence": result['confidence'],
            "anomaly": result['is_anomaly'],
            "anomaly_score": result['anomaly_score_raw'],
            "risk_score": risk_score,
            "risk_level": risk_level,
            "explanation": explanation,
            "timestamp": datetime.utcnow().isoformat() + 'Z'
        }
        
        # Auto-save to database if risk is not LOW, or optionally save everything
        # For demo purposes, let's save everything to show traffic
        alert = Alert(
            device_id=data.get('device_id', 'DEV-000'),
            source_ip=data.get('source_ip', '0.0.0.0'),
            destination_ip=data.get('destination_ip', '0.0.0.0'),
            protocol=str(data.get('Protocol Type', 'Unknown')),
            prediction=result['prediction'],
            confidence=result['confidence'],
            anomaly_score=result['anomaly_score_raw'],
            risk_score=risk_score,
            risk_level=risk_level,
            explanation=json.dumps(explanation) # Store as JSON string or text
        )
        db.session.add(alert)
        db.session.commit()
        
        return jsonify(response)
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500
