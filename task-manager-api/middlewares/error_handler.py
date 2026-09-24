import logging

from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import HTTPException

from database import db
from models.errors import AppError

logger = logging.getLogger(__name__)


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        db.session.rollback()
        return jsonify(e.to_dict()), e.status_code

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        return jsonify({'error': e.description}), e.code

    @app.errorhandler(SQLAlchemyError)
    def handle_db_error(e):
        db.session.rollback()
        logger.exception("Erro de banco de dados")
        return jsonify({'error': 'Erro interno'}), 500

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        db.session.rollback()
        logger.exception("Erro não tratado")
        return jsonify({'error': 'Erro interno'}), 500
