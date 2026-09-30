import pytest
from backend.app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            from backend.database import db
            db.create_all()
        yield client

def test_health(client):
    rv = client.get('/api/health')
    assert rv.status_code == 200
    assert rv.get_json()['status'] == 'healthy'

def test_devices(client):
    rv = client.get('/api/devices')
    assert rv.status_code == 200
    
def test_alerts(client):
    rv = client.get('/api/alerts')
    assert rv.status_code == 200
