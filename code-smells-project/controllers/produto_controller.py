import logging

from models import produto_model
from models.errors import ValidationError

logger = logging.getLogger(__name__)


class ProdutoController:
    def __init__(self, get_db):
        self.get_db = get_db

    def listar(self):
        produtos = produto_model.listar(self.get_db())
        logger.info("Listando %s produtos", len(produtos))
        return {"dados": produtos, "sucesso": True}, 200

    def buscar_por_id(self, produto_id):
        produto = produto_model.buscar_por_id(self.get_db(), produto_id)
        if not produto:
            return {"erro": "Produto não encontrado", "sucesso": False}, 404
        return {"dados": produto, "sucesso": True}, 200

    def buscar(self, termo, categoria, preco_min, preco_max):
        try:
            preco_min = float(preco_min) if preco_min else None
            preco_max = float(preco_max) if preco_max else None
        except ValueError:
            raise ValidationError("preco_min/preco_max devem ser numéricos")

        resultados = produto_model.buscar(self.get_db(), termo, categoria, preco_min, preco_max)
        return {"dados": resultados, "total": len(resultados), "sucesso": True}, 200

    def criar(self, dados):
        campos = produto_model.validar(dados)
        produto_id = produto_model.criar(self.get_db(), **campos)
        logger.info("Produto criado com ID: %s", produto_id)
        return {"dados": {"id": produto_id}, "sucesso": True, "mensagem": "Produto criado"}, 201

    def atualizar(self, produto_id, dados):
        db = self.get_db()
        if not produto_model.buscar_por_id(db, produto_id):
            return {"erro": "Produto não encontrado"}, 404
        campos = produto_model.validar(dados)
        produto_model.atualizar(db, produto_id, **campos)
        return {"sucesso": True, "mensagem": "Produto atualizado"}, 200

    def deletar(self, produto_id):
        db = self.get_db()
        if not produto_model.buscar_por_id(db, produto_id):
            return {"erro": "Produto não encontrado"}, 404
        produto_model.deletar(db, produto_id)
        logger.info("Produto %s deletado", produto_id)
        return {"sucesso": True, "mensagem": "Produto deletado"}, 200
