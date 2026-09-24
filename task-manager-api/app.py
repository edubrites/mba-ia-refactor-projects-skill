import logging

from flask import Flask
from flask_cors import CORS

from config import settings
from controllers.category_controller import CategoryController
from controllers.report_controller import ReportController
from controllers.task_controller import TaskController
from controllers.user_controller import UserController
from database import db
from middlewares.error_handler import register_error_handlers
from routes import register_routes
from services.auth_service import AuthService
from services.notification_service import EmailConfig, NotificationService
from services.report_service import ReportService


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = settings.DATABASE_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = settings.SECRET_KEY
    app.config['DEBUG'] = settings.DEBUG

    CORS(app)
    db.init_app(app)

    notification_service = NotificationService(EmailConfig(
        enabled=settings.EMAIL_ENABLED,
        host=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        user=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
    ))
    report_service = ReportService()
    auth_service = AuthService(settings.SECRET_KEY, settings.TOKEN_MAX_AGE)
    controllers = {
        'tasks': TaskController(notification_service, report_service),
        'users': UserController(auth_service),
        'categories': CategoryController(),
        'reports': ReportController(report_service),
    }
    register_routes(app, controllers, settings.APP_VERSION)
    register_error_handlers(app)

    with app.app_context():
        db.create_all()

    return app


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(name)s: %(message)s')
    app = create_app()
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
