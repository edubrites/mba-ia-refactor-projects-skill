import logging

from flask import jsonify
from werkzeug.exceptions import HTTPException

from models.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify(e.to_dict()), e.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return jsonify({"erro": e.description}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        logger.exception("Erro não tratado")
        return jsonify({"erro": "Erro interno do servidor"}), 500
