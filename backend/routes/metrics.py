from flask import Blueprint, jsonify
import json
import os
from ..config import Config

metrics_bp = Blueprint('metrics', __name__)

@metrics_bp.route('/metrics', methods=['GET'])
def get_metrics():
    metrics_path = os.path.join(Config.RESULTS_DIR, 'metrics.json')
    try:
        with open(metrics_path, 'r') as f:
            metrics_data = json.load(f)
        return jsonify(metrics_data)
    except FileNotFoundError:
        return jsonify({'error': 'Metrics not found. Please train models first.'}), 404
