from flask import Blueprint, jsonify, request


def create_user_blueprint(controller):
    user_bp = Blueprint('users', __name__)

    @user_bp.route('/users', methods=['GET'])
    def get_users():
        body, status = controller.list_users()
        return jsonify(body), status

    @user_bp.route('/users/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        body, status = controller.get_user(user_id)
        return jsonify(body), status

    @user_bp.route('/users', methods=['POST'])
    def create_user():
        body, status = controller.create_user(request.get_json(silent=True), request.headers.get('Authorization'))
        return jsonify(body), status

    @user_bp.route('/users/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        body, status = controller.update_user(
            user_id, request.get_json(silent=True), request.headers.get('Authorization'))
        return jsonify(body), status

    @user_bp.route('/users/<int:user_id>', methods=['DELETE'])
    def delete_user(user_id):
        body, status = controller.delete_user(user_id, request.headers.get('Authorization'))
        return jsonify(body), status

    @user_bp.route('/users/<int:user_id>/tasks', methods=['GET'])
    def get_user_tasks(user_id):
        body, status = controller.get_user_tasks(user_id)
        return jsonify(body), status

    @user_bp.route('/login', methods=['POST'])
    def login():
        body, status = controller.login(request.get_json(silent=True))
        return jsonify(body), status

    return user_bp
