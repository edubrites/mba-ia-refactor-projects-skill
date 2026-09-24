from flask import Blueprint, jsonify


def create_report_blueprint(controller):
    report_bp = Blueprint('reports', __name__)

    @report_bp.route('/reports/summary', methods=['GET'])
    def summary_report():
        body, status = controller.summary_report()
        return jsonify(body), status

    @report_bp.route('/reports/user/<int:user_id>', methods=['GET'])
    def user_report(user_id):
        body, status = controller.user_report(user_id)
        return jsonify(body), status

    return report_bp
