class AppError(Exception):
    """Erro de domínio traduzido para resposta HTTP pelo error handler central."""

    status_code = 400

    def __init__(self, mensagem, status_code=None, **extra):
        super().__init__(mensagem)
        self.mensagem = mensagem
        if status_code is not None:
            self.status_code = status_code
        self.extra = extra

    def to_dict(self):
        return {"erro": self.mensagem, **self.extra}


class ValidationError(AppError):
    status_code = 400


class NotFoundError(AppError):
    status_code = 404


class UnauthorizedError(AppError):
    status_code = 401
