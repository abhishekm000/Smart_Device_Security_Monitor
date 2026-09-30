from flask import Blueprint, jsonify, request
from ..models import Alert
from ..database import db

alerts_bp = Blueprint('alerts', __name__)

@alerts_bp.route('/alerts', methods=['GET'])
def get_alerts():
    limit = request.args.get('limit', 100, type=int)
    alerts = Alert.query.order_by(Alert.timestamp.desc()).limit(limit).all()
    return jsonify([alert.to_dict() for alert in alerts])

@alerts_bp.route('/alerts/<int:id>', methods=['GET'])
def get_alert(id):
    alert = Alert.query.get_or_404(id)
    return jsonify(alert.to_dict())

@alerts_bp.route('/alerts/<int:id>/analysis', methods=['GET'])
def get_alert_analysis(id):
    from ..services.llm_service import generate_threat_report
    alert = Alert.query.get_or_404(id)
    report = generate_threat_report(alert.to_dict())
    return jsonify({"ai_report": report})

@alerts_bp.route('/alerts/<int:id>/status', methods=['PUT'])
def update_alert_status(id):
    alert = Alert.query.get_or_404(id)
    data = request.json
    if 'status' in data and data['status'] in ['OPEN', 'ACKNOWLEDGED', 'RESOLVED']:
        alert.status = data['status']
        db.session.commit()
        return jsonify(alert.to_dict())
    return jsonify({'error': 'Invalid status'}), 400

@alerts_bp.route('/alerts', methods=['DELETE'])
def clear_alerts():
    try:
        db.session.query(Alert).delete()
        db.session.commit()
        return jsonify({'message': 'All alerts cleared successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
