from flask import Blueprint, jsonify, request


def create_category_blueprint(controller):
    category_bp = Blueprint('categories', __name__)

    @category_bp.route('/categories', methods=['GET'])
    def get_categories():
        body, status = controller.list_categories()
        return jsonify(body), status

    @category_bp.route('/categories', methods=['POST'])
    def create_category():
        body, status = controller.create_category(request.get_json(silent=True))
        return jsonify(body), status

    @category_bp.route('/categories/<int:cat_id>', methods=['PUT'])
    def update_category(cat_id):
        body, status = controller.update_category(cat_id, request.get_json(silent=True))
        return jsonify(body), status

    @category_bp.route('/categories/<int:cat_id>', methods=['DELETE'])
    def delete_category(cat_id):
        body, status = controller.delete_category(cat_id)
        return jsonify(body), status

    return category_bp
