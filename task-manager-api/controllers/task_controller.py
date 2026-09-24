import logging

from models.category import Category
from models.errors import NotFoundError
from models.task import Task
from models.user import User
from models.validators import parse_int_param, validate_task
from utils.helpers import utcnow

logger = logging.getLogger(__name__)


class TaskController:
    def __init__(self, notification_service, report_service):
        self.notification_service = notification_service
        self.report_service = report_service

    def list_tasks(self):
        result = []
        for task in Task.list_with_relations():
            data = task.to_dict(include_overdue=True)
            data['user_name'] = task.user.name if task.user else None
            data['category_name'] = task.category.name if task.category else None
            result.append(data)
        return result, 200

    def get_task(self, task_id):
        return self._get_or_404(task_id).to_dict(include_overdue=True), 200

    def create_task(self, data):
        fields = validate_task(data)
        user = self._check_references(fields)

        task = Task(**fields)
        task.save()
        logger.info("Task criada: %s - %s", task.id, task.title)
        if user:
            self.notification_service.notify_task_assigned(user, task)
        return task.to_dict(), 201

    def update_task(self, task_id, data):
        task = self._get_or_404(task_id)
        fields = validate_task(data, partial=True)
        user = self._check_references(fields)
        reassigned = user is not None and fields['user_id'] != task.user_id

        for name, value in fields.items():
            setattr(task, name, value)
        task.updated_at = utcnow()
        task.save()
        logger.info("Task atualizada: %s", task.id)
        if reassigned:
            self.notification_service.notify_task_assigned(user, task)
        return task.to_dict(), 200

    def delete_task(self, task_id):
        self._get_or_404(task_id).delete()
        logger.info("Task deletada: %s", task_id)
        return {'message': 'Task deletada com sucesso'}, 200

    def search_tasks(self, args):
        tasks = Task.search(
            text=args.get('q', ''),
            status=args.get('status', ''),
            priority=parse_int_param(args.get('priority'), 'priority'),
            user_id=parse_int_param(args.get('user_id'), 'user_id'),
        )
        return [task.to_dict() for task in tasks], 200

    def task_stats(self):
        return self.report_service.task_stats(), 200

    @staticmethod
    def _get_or_404(task_id):
        task = Task.get(task_id)
        if not task:
            raise NotFoundError('Task não encontrada')
        return task

    @staticmethod
    def _check_references(fields):
        """Garante que user_id/category_id informados existem; devolve o usuário atribuído (se houver)."""
        user = None
        if fields.get('user_id'):
            user = User.get(fields['user_id'])
            if not user:
                raise NotFoundError('Usuário não encontrado')
        if fields.get('category_id') and not Category.get(fields['category_id']):
            raise NotFoundError('Categoria não encontrada')
        return user
