import os
import sys

# Add backend directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.app import create_app
from backend.database import db
from backend.models import Device

app = create_app()

devices = [
    {"id": "DEV-001", "name": "Smart Camera", "type": "Camera", "ip": "192.168.1.20"},
    {"id": "DEV-002", "name": "Smart TV", "type": "TV", "ip": "192.168.1.21"},
    {"id": "DEV-003", "name": "Smart Bulb", "type": "Bulb", "ip": "192.168.1.22"},
    {"id": "DEV-004", "name": "Alexa Echo", "type": "Voice Assistant", "ip": "192.168.1.23"},
    {"id": "DEV-005", "name": "Door Camera", "type": "Security", "ip": "192.168.1.24"},
]

with app.app_context():
    # Delete existing to prevent duplicate DEV-001 if exists
    Device.query.delete()
    for d in devices:
        db.session.add(Device(id=d['id'], name=d['name'], device_type=d['type'], ip_address=d['ip'], status='Online'))
    db.session.commit()
    print("Added devices.")
