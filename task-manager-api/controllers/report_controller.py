from models.errors import NotFoundError
from models.user import User


class ReportController:
    def __init__(self, report_service):
        self.report_service = report_service

    def summary_report(self):
        return self.report_service.summary(), 200

    def user_report(self, user_id):
        user = User.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        return self.report_service.user_report(user), 200
