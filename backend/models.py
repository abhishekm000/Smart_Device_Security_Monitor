from .database import db
from datetime import datetime
import json

class Device(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.String(50), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50))
    ip_address = db.Column(db.String(50))
    status = db.Column(db.String(20), default='Online')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Alert(db.Model):
    __tablename__ = 'alerts'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    device_id = db.Column(db.String(50), db.ForeignKey('devices.id'), nullable=True)
    source_ip = db.Column(db.String(50), nullable=True)
    destination_ip = db.Column(db.String(50), nullable=True)
    protocol = db.Column(db.String(20), nullable=True)
    prediction = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    anomaly_score = db.Column(db.Float, nullable=True)
    risk_score = db.Column(db.Integer, nullable=False)
    risk_level = db.Column(db.String(20), nullable=False)
    explanation = db.Column(db.Text, nullable=True) # JSON string
    status = db.Column(db.String(20), default='OPEN') # OPEN, ACKNOWLEDGED, RESOLVED

    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() + 'Z',
            'device_id': self.device_id,
            'source_ip': self.source_ip,
            'destination_ip': self.destination_ip,
            'protocol': self.protocol,
            'prediction': self.prediction,
            'confidence': self.confidence,
            'anomaly_score': self.anomaly_score,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'explanation': json.loads(self.explanation) if self.explanation else [],
            'status': self.status
        }
