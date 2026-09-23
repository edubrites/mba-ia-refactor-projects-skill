import logging

from flask import Flask
from flask_cors import CORS

from config import settings
from controllers.pedido_controller import PedidoController
from controllers.produto_controller import ProdutoController
from controllers.relatorio_controller import RelatorioController
from controllers.sistema_controller import SistemaController
from controllers.usuario_controller import UsuarioController
from middlewares.error_handler import register_error_handlers
from models.database import close_db, get_db, init_db
from routes.routes import register_routes
from services.notificacao_service import NotificacaoService
from services.pedido_service import PedidoService


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = settings.SECRET_KEY
    app.config["DEBUG"] = settings.DEBUG
    app.config["DB_PATH"] = settings.DB_PATH
    CORS(app)

    init_db(settings.DB_PATH, settings.SEED_USER_PASSWORD)
    app.teardown_appcontext(close_db)

    pedido_service = PedidoService(NotificacaoService())
    controllers = {
        "produtos": ProdutoController(get_db),
        "usuarios": UsuarioController(get_db),
        "pedidos": PedidoController(get_db, pedido_service),
        "relatorios": RelatorioController(get_db),
        "sistema": SistemaController(get_db, settings.APP_VERSION, settings.APP_ENV, settings.ADMIN_TOKEN),
    }
    register_routes(app, controllers, settings.ADMIN_RESET_ENABLED)
    register_error_handlers(app)
    return app


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    app = create_app()
    logging.getLogger(__name__).info("Servidor iniciado em http://%s:%s", settings.HOST, settings.PORT)
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
