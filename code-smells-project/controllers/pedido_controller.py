from models import pedido_model
from models.errors import ValidationError


class PedidoController:
    def __init__(self, get_db, pedido_service):
        self.get_db = get_db
        self.pedido_service = pedido_service

    def criar(self, dados):
        usuario_id, itens = pedido_model.validar_criacao(dados)
        resultado = self.pedido_service.criar(self.get_db(), usuario_id, itens)
        return {"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}, 201

    def listar_todos(self):
        return {"dados": pedido_model.listar_todos(self.get_db()), "sucesso": True}, 200

    def listar_por_usuario(self, usuario_id):
        return {"dados": pedido_model.listar_por_usuario(self.get_db(), usuario_id), "sucesso": True}, 200

    def atualizar_status(self, pedido_id, dados):
        if not dados:
            raise ValidationError("Dados inválidos")
        self.pedido_service.atualizar_status(self.get_db(), pedido_id, dados.get("status", ""))
        return {"sucesso": True, "mensagem": "Status atualizado"}, 200
