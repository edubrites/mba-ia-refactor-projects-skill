import re

from werkzeug.security import check_password_hash, generate_password_hash

from models.constants import TipoUsuario
from models.errors import ValidationError

# Nunca inclui a coluna senha: é o único formato serializado para fora.
COLUNAS_PUBLICAS = "id, nome, email, tipo, criado_em"

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validar_cadastro(dados):
    if not dados:
        raise ValidationError("Dados inválidos")

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not all(isinstance(v, str) for v in (nome, email, senha)):
        raise ValidationError("Nome, email e senha devem ser texto")
    if not EMAIL_REGEX.match(email):
        raise ValidationError("Email inválido")

    return {"nome": nome, "email": email, "senha": senha}


def listar(db):
    rows = db.execute(f"SELECT {COLUNAS_PUBLICAS} FROM usuarios").fetchall()
    return [dict(row) for row in rows]


def buscar_por_id(db, usuario_id):
    row = db.execute(f"SELECT {COLUNAS_PUBLICAS} FROM usuarios WHERE id = ?", (usuario_id,)).fetchone()
    return dict(row) if row else None


def autenticar(db, email, senha):
    row = db.execute("SELECT id, nome, email, tipo, senha FROM usuarios WHERE email = ?", (email,)).fetchone()
    if row is None or not check_password_hash(row["senha"], senha):
        return None
    return {"id": row["id"], "nome": row["nome"], "email": row["email"], "tipo": row["tipo"]}


def criar(db, nome, email, senha, tipo=TipoUsuario.CLIENTE):
    with db:
        cursor = db.execute(
            "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
            (nome, email, generate_password_hash(senha), tipo),
        )
    return cursor.lastrowid


def contar(db):
    return db.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0]
