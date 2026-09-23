from models import pedido_model, produto_model
from models.errors import ValidationError


class PedidoService:
    def __init__(self, notificacao_service):
        self.notificacao_service = notificacao_service

    def criar(self, db, usuario_id, itens):
        # Transação única: qualquer erro desfaz pedido, itens e baixa de estoque.
        with db:
            total = 0
            precos = {}
            for item in itens:
                produto = produto_model.buscar_por_id(db, item["produto_id"])
                if produto is None:
                    raise ValidationError("Produto " + str(item["produto_id"]) + " não encontrado", sucesso=False)
                if produto["estoque"] < item["quantidade"]:
                    raise ValidationError("Estoque insuficiente para " + produto["nome"], sucesso=False)
                precos[item["produto_id"]] = produto["preco"]
                total += produto["preco"] * item["quantidade"]

            pedido_id = pedido_model.inserir(db, usuario_id, total)
            for item in itens:
                pedido_model.inserir_item(db, pedido_id, item["produto_id"], item["quantidade"], precos[item["produto_id"]])
                # Débito condicional evita estoque negativo em pedidos concorrentes.
                if not produto_model.debitar_estoque(db, item["produto_id"], item["quantidade"]):
                    raise ValidationError("Estoque insuficiente para produto " + str(item["produto_id"]), sucesso=False)

        self.notificacao_service.notificar_pedido_criado(pedido_id, usuario_id)
        return {"pedido_id": pedido_id, "total": total}

    def atualizar_status(self, db, pedido_id, status):
        status = pedido_model.validar_status(status)
        pedido_model.atualizar_status(db, pedido_id, status)
        self.notificacao_service.notificar_status_pedido(pedido_id, status)
