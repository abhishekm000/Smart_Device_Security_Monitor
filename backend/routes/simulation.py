from flask import Blueprint, jsonify, request
from ..services.simulation_service import simulation_service

simulation_bp = Blueprint('simulation', __name__)

@simulation_bp.route('/simulation/start', methods=['POST'])
def start_simulation():
    data = request.json or {}
    speed = float(data.get('speed', 1.0))
    success, message = simulation_service.start(speed)
    if success:
        return jsonify({"message": message})
    return jsonify({"error": message}), 400

@simulation_bp.route('/simulation/stop', methods=['POST'])
def stop_simulation():
    success, message = simulation_service.stop()
    return jsonify({"message": message})

@simulation_bp.route('/simulation/status', methods=['GET'])
def get_simulation_status():
    return jsonify(simulation_service.get_status())
