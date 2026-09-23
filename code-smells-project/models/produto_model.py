from models.constants import CATEGORIA_PADRAO, CATEGORIAS_VALIDAS, NOME_PRODUTO_MAX, NOME_PRODUTO_MIN
from models.errors import ValidationError

COLUNAS = "id, nome, descricao, preco, estoque, categoria, ativo, criado_em"


def _is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def validar(dados):
    """Valida o payload de criação/atualização e devolve os campos normalizados."""
    if not dados:
        raise ValidationError("Dados inválidos")
    if "nome" not in dados:
        raise ValidationError("Nome é obrigatório")
    if "preco" not in dados:
        raise ValidationError("Preço é obrigatório")
    if "estoque" not in dados:
        raise ValidationError("Estoque é obrigatório")

    nome = dados["nome"]
    descricao = dados.get("descricao", "")
    preco = dados["preco"]
    estoque = dados["estoque"]
    categoria = dados.get("categoria", CATEGORIA_PADRAO)

    if not isinstance(nome, str):
        raise ValidationError("Nome deve ser texto")
    if not isinstance(descricao, str):
        raise ValidationError("Descrição deve ser texto")
    if not _is_number(preco):
        raise ValidationError("Preço deve ser numérico")
    if not _is_number(estoque) or int(estoque) != estoque:
        raise ValidationError("Estoque deve ser um número inteiro")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": int(estoque),
        "categoria": categoria,
    }


def listar(db):
    rows = db.execute(f"SELECT {COLUNAS} FROM produtos").fetchall()
    return [dict(row) for row in rows]


def buscar_por_id(db, produto_id):
    row = db.execute(f"SELECT {COLUNAS} FROM produtos WHERE id = ?", (produto_id,)).fetchone()
    return dict(row) if row else None


def buscar(db, termo=None, categoria=None, preco_min=None, preco_max=None):
    condicoes = []
    params = []
    if termo:
        condicoes.append("(nome LIKE ? OR descricao LIKE ?)")
        params.extend([f"%{termo}%", f"%{termo}%"])
    if categoria:
        condicoes.append("categoria = ?")
        params.append(categoria)
    if preco_min is not None:
        condicoes.append("preco >= ?")
        params.append(preco_min)
    if preco_max is not None:
        condicoes.append("preco <= ?")
        params.append(preco_max)

    where = " AND ".join(["1=1", *condicoes])
    rows = db.execute(f"SELECT {COLUNAS} FROM produtos WHERE {where}", params).fetchall()
    return [dict(row) for row in rows]


def criar(db, nome, descricao, preco, estoque, categoria):
    with db:
        cursor = db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
    return cursor.lastrowid


def atualizar(db, produto_id, nome, descricao, preco, estoque, categoria):
    with db:
        db.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )


def deletar(db, produto_id):
    with db:
        db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))


def contar(db):
    return db.execute("SELECT COUNT(*) FROM produtos").fetchone()[0]


def debitar_estoque(db, produto_id, quantidade):
    """Debita estoque só se houver saldo; retorna False quando insuficiente. Não faz commit."""
    cursor = db.execute(
        "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
        (quantidade, produto_id, quantidade),
    )
    return cursor.rowcount == 1
