import hmac
import logging
import sqlite3

from models import admin_model, pedido_model, produto_model, usuario_model
from models.errors import UnauthorizedError

logger = logging.getLogger(__name__)


class SistemaController:
    def __init__(self, get_db, versao, ambiente, admin_token=None):
        self.get_db = get_db
        self.versao = versao
        self.ambiente = ambiente
        self.admin_token = admin_token

    def index(self):
        return {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": self.versao,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }, 200

    def health(self):
        try:
            db = self.get_db()
            counts = {
                "produtos": produto_model.contar(db),
                "usuarios": usuario_model.contar(db),
                "pedidos": pedido_model.contar(db),
            }
        except sqlite3.Error:
            logger.exception("Health check falhou")
            return {"status": "erro", "database": "disconnected"}, 500

        return {
            "status": "ok",
            "database": "connected",
            "counts": counts,
            "versao": self.versao,
            "ambiente": self.ambiente,
        }, 200

    def reset_db(self, token):
        if not self.admin_token or not token or not hmac.compare_digest(token, self.admin_token):
            raise UnauthorizedError("Não autorizado")
        admin_model.limpar_tabelas(self.get_db())
        logger.warning("Banco de dados resetado via /admin/reset-db")
        return {"mensagem": "Banco de dados resetado", "sucesso": True}, 200
