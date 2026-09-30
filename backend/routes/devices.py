from flask import Blueprint, jsonify, request
from ..models import Device
from ..database import db

devices_bp = Blueprint('devices', __name__)

@devices_bp.route('/devices', methods=['GET'])
def get_devices():
    devices = Device.query.all()
    return jsonify([{
        'id': d.id,
        'name': d.name,
        'device_type': d.device_type,
        'ip_address': d.ip_address,
        'status': d.status
    } for d in devices])

@devices_bp.route('/devices', methods=['POST'])
def add_device():
    data = request.json
    device = Device(
        id=data.get('id'),
        name=data.get('name'),
        device_type=data.get('device_type'),
        ip_address=data.get('ip_address')
    )
    db.session.add(device)
    db.session.commit()
    return jsonify({'message': 'Device added'})
