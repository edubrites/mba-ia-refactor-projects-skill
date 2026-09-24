from flask import Blueprint, jsonify, request


def create_task_blueprint(controller):
    task_bp = Blueprint('tasks', __name__)

    @task_bp.route('/tasks', methods=['GET'])
    def get_tasks():
        body, status = controller.list_tasks()
        return jsonify(body), status

    @task_bp.route('/tasks/<int:task_id>', methods=['GET'])
    def get_task(task_id):
        body, status = controller.get_task(task_id)
        return jsonify(body), status

    @task_bp.route('/tasks', methods=['POST'])
    def create_task():
        body, status = controller.create_task(request.get_json(silent=True))
        return jsonify(body), status

    @task_bp.route('/tasks/<int:task_id>', methods=['PUT'])
    def update_task(task_id):
        body, status = controller.update_task(task_id, request.get_json(silent=True))
        return jsonify(body), status

    @task_bp.route('/tasks/<int:task_id>', methods=['DELETE'])
    def delete_task(task_id):
        body, status = controller.delete_task(task_id)
        return jsonify(body), status

    @task_bp.route('/tasks/search', methods=['GET'])
    def search_tasks():
        body, status = controller.search_tasks(request.args)
        return jsonify(body), status

    @task_bp.route('/tasks/stats', methods=['GET'])
    def task_stats():
        body, status = controller.task_stats()
        return jsonify(body), status

    return task_bp
