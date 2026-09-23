CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
CATEGORIA_PADRAO = "geral"

NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200


class StatusPedido:
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"

    TODOS = [PENDENTE, APROVADO, ENVIADO, ENTREGUE, CANCELADO]


class TipoUsuario:
    ADMIN = "admin"
    CLIENTE = "cliente"


# (faturamento mínimo exclusivo, percentual de desconto), do maior para o menor
FAIXAS_DESCONTO = [
    (10000, 0.10),
    (5000, 0.05),
    (1000, 0.02),
]
