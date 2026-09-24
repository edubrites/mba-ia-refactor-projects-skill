from datetime import datetime

from flask import Blueprint


def create_system_blueprint(app_version):
    system_bp = Blueprint('system', __name__)

    @system_bp.route('/health')
    def health():
        return {'status': 'ok', 'timestamp': str(datetime.now())}

    @system_bp.route('/')
    def index():
        return {'message': 'Task Manager API', 'version': app_version}

    return system_bp
