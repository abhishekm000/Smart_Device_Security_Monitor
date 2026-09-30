from flask import Flask, jsonify
from flask_cors import CORS
from .config import Config
from .database import db
import os

def create_app():
    # Serve the frontend directory at the root URL
    frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
    app = Flask(__name__, static_folder=frontend_dir, static_url_path='')
    app.config.from_object(Config)
    CORS(app)
    
    db.init_app(app)
    
    # Import blueprints
    from .routes.prediction import prediction_bp
    from .routes.alerts import alerts_bp
    from .routes.metrics import metrics_bp
    from .routes.simulation import simulation_bp
    from .routes.devices import devices_bp
    
    # Register blueprints
    app.register_blueprint(prediction_bp, url_prefix='/api')
    app.register_blueprint(alerts_bp, url_prefix='/api')
    app.register_blueprint(metrics_bp, url_prefix='/api')
    app.register_blueprint(simulation_bp, url_prefix='/api')
    app.register_blueprint(devices_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'API is running'})
        
    # Ensure database tables are created
    with app.app_context():
        db.create_all()
        # Create a dummy device if none exists
        from .models import Device
        if not Device.query.first():
            dummy = Device(id='DEV-001', name='Smart Camera', device_type='Camera', ip_address='192.168.1.20')
            db.session.add(dummy)
            db.session.commit()
            
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
