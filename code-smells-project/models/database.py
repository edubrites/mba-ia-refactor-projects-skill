import logging
import secrets
import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash

from models.constants import TipoUsuario

logger = logging.getLogger(__name__)

HASH_PREFIXES = ("scrypt:", "pbkdf2:")

SCHEMA = [
    """
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        descricao TEXT,
        preco REAL,
        estoque INTEGER,
        categoria TEXT,
        ativo INTEGER DEFAULT 1,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT,
        email TEXT,
        senha TEXT,
        tipo TEXT DEFAULT 'cliente',
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        status TEXT DEFAULT 'pendente',
        total REAL,
        criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER,
        produto_id INTEGER,
        quantidade INTEGER,
        preco_unitario REAL
    )
    """,
]

PRODUTOS_SEED = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

USUARIOS_SEED = [
    ("Admin", "admin@loja.com", TipoUsuario.ADMIN),
    ("João Silva", "joao@email.com", TipoUsuario.CLIENTE),
    ("Maria Santos", "maria@email.com", TipoUsuario.CLIENTE),
]


def connect(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def get_db():
    """Conexão com escopo de requisição (uma por app context, fechada no teardown)."""
    if "db" not in g:
        g.db = connect(current_app.config["DB_PATH"])
    return g.db


def close_db(_exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db(db_path, seed_password=None):
    conn = connect(db_path)
    try:
        with conn:
            for statement in SCHEMA:
                conn.execute(statement)
            _seed(conn, seed_password)
            _hash_senhas_legadas(conn)
    finally:
        conn.close()


def _seed(conn, seed_password):
    if conn.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] > 0:
        return

    conn.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        PRODUTOS_SEED,
    )

    if not seed_password:
        seed_password = secrets.token_urlsafe(12)
        logger.warning("SEED_USER_PASSWORD não definida; senha gerada para usuários de exemplo: %s", seed_password)

    senha_hash = generate_password_hash(seed_password)
    conn.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        [(nome, email, senha_hash, tipo) for nome, email, tipo in USUARIOS_SEED],
    )


def _hash_senhas_legadas(conn):
    """Migra bancos antigos que guardavam senha em texto puro."""
    rows = conn.execute("SELECT id, senha FROM usuarios").fetchall()
    for row in rows:
        senha = row["senha"]
        if senha and not senha.startswith(HASH_PREFIXES):
            conn.execute(
                "UPDATE usuarios SET senha = ? WHERE id = ?",
                (generate_password_hash(senha), row["id"]),
            )
