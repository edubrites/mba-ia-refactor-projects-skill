import logging

from models import usuario_model
from models.errors import ValidationError

logger = logging.getLogger(__name__)


class UsuarioController:
    def __init__(self, get_db):
        self.get_db = get_db

    def listar(self):
        return {"dados": usuario_model.listar(self.get_db()), "sucesso": True}, 200

    def buscar_por_id(self, usuario_id):
        usuario = usuario_model.buscar_por_id(self.get_db(), usuario_id)
        if not usuario:
            return {"erro": "Usuário não encontrado"}, 404
        return {"dados": usuario, "sucesso": True}, 200

    def criar(self, dados):
        campos = usuario_model.validar_cadastro(dados)
        usuario_id = usuario_model.criar(self.get_db(), **campos)
        logger.info("Usuário criado: id=%s", usuario_id)
        return {"dados": {"id": usuario_id}, "sucesso": True}, 201

    def login(self, dados):
        if not dados:
            raise ValidationError("Dados inválidos")
        email = dados.get("email", "")
        senha = dados.get("senha", "")
        if not email or not senha:
            raise ValidationError("Email e senha são obrigatórios")

        usuario = usuario_model.autenticar(self.get_db(), email, senha)
        if not usuario:
            logger.info("Login falhou")
            return {"erro": "Email ou senha inválidos", "sucesso": False}, 401

        logger.info("Login bem-sucedido: id=%s", usuario["id"])
        return {"dados": usuario, "sucesso": True, "mensagem": "Login OK"}, 200
