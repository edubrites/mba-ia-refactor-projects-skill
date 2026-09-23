from services import relatorio_service


class RelatorioController:
    def __init__(self, get_db):
        self.get_db = get_db

    def vendas(self):
        return {"dados": relatorio_service.relatorio_vendas(self.get_db()), "sucesso": True}, 200
