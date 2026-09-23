TABELAS_RESET = ["itens_pedido", "pedidos", "produtos", "usuarios"]


def limpar_tabelas(db):
    with db:
        for tabela in TABELAS_RESET:
            db.execute(f"DELETE FROM {tabela}")  # nomes vêm da allowlist acima, nunca do request
