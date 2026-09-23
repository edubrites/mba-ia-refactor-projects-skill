from models.constants import StatusPedido
from models.errors import ValidationError


def validar_criacao(dados):
    if not dados:
        raise ValidationError("Dados inválidos")

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not itens or not isinstance(itens, list):
        raise ValidationError("Pedido deve ter pelo menos 1 item")
    for item in itens:
        if not isinstance(item, dict):
            raise ValidationError("Item de pedido inválido")
        quantidade = item.get("quantidade")
        if "produto_id" not in item or not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade <= 0:
            raise ValidationError("Cada item precisa de produto_id e quantidade inteira positiva")

    return usuario_id, itens


def validar_status(status):
    if status not in StatusPedido.TODOS:
        raise ValidationError("Status inválido")
    return status


def inserir(db, usuario_id, total):
    """Não faz commit: usado dentro da transação do service."""
    cursor = db.execute(
        "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
        (usuario_id, StatusPedido.PENDENTE, total),
    )
    return cursor.lastrowid


def inserir_item(db, pedido_id, produto_id, quantidade, preco_unitario):
    """Não faz commit: usado dentro da transação do service."""
    db.execute(
        "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario) VALUES (?, ?, ?, ?)",
        (pedido_id, produto_id, quantidade, preco_unitario),
    )


def _listar(db, where="", params=()):
    # Um único JOIN no lugar de 1 query por pedido + 1 por item (N+1).
    rows = db.execute(
        f"""
        SELECT p.id, p.usuario_id, p.status, p.total, p.criado_em,
               ip.id AS item_id, ip.produto_id, ip.quantidade, ip.preco_unitario,
               COALESCE(pr.nome, 'Desconhecido') AS produto_nome
        FROM pedidos p
        LEFT JOIN itens_pedido ip ON ip.pedido_id = p.id
        LEFT JOIN produtos pr ON pr.id = ip.produto_id
        {where}
        ORDER BY p.id, ip.id
        """,
        params,
    ).fetchall()

    pedidos = {}
    for row in rows:
        pedido = pedidos.get(row["id"])
        if pedido is None:
            pedido = {
                "id": row["id"],
                "usuario_id": row["usuario_id"],
                "status": row["status"],
                "total": row["total"],
                "criado_em": row["criado_em"],
                "itens": [],
            }
            pedidos[row["id"]] = pedido
        if row["item_id"] is not None:
            pedido["itens"].append({
                "produto_id": row["produto_id"],
                "produto_nome": row["produto_nome"],
                "quantidade": row["quantidade"],
                "preco_unitario": row["preco_unitario"],
            })
    return list(pedidos.values())


def listar_todos(db):
    return _listar(db)


def listar_por_usuario(db, usuario_id):
    return _listar(db, "WHERE p.usuario_id = ?", (usuario_id,))


def atualizar_status(db, pedido_id, status):
    with db:
        db.execute("UPDATE pedidos SET status = ? WHERE id = ?", (status, pedido_id))


def contar(db):
    return db.execute("SELECT COUNT(*) FROM pedidos").fetchone()[0]


def agregados_vendas(db):
    row = db.execute(
        """
        SELECT COUNT(*) AS total_pedidos,
               COALESCE(SUM(total), 0) AS faturamento,
               SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) AS pendentes,
               SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) AS aprovados,
               SUM(CASE WHEN status = ? THEN 1 ELSE 0 END) AS cancelados
        FROM pedidos
        """,
        (StatusPedido.PENDENTE, StatusPedido.APROVADO, StatusPedido.CANCELADO),
    ).fetchone()
    return {
        "total_pedidos": row["total_pedidos"],
        "faturamento": row["faturamento"],
        "pendentes": row["pendentes"] or 0,
        "aprovados": row["aprovados"] or 0,
        "cancelados": row["cancelados"] or 0,
    }
