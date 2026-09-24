import logging

from models.constants import PRIVILEGED_ROLES
from models.errors import ConflictError, ForbiddenError, NotFoundError, UnauthorizedError, ValidationError
from models.task import Task
from models.user import User
from models.validators import require_body, validate_user

logger = logging.getLogger(__name__)


class UserController:
    def __init__(self, auth_service):
        self.auth_service = auth_service

    def list_users(self):
        task_counts = Task.counts_per_user()
        result = []
        for user in User.list_all():
            data = user.to_dict()
            data['task_count'] = task_counts.get(user.id, (0, 0))[0]
            result.append(data)
        return result, 200

    def get_user(self, user_id):
        user = self._get_or_404(user_id)
        data = user.to_dict()
        data['tasks'] = [task.to_dict() for task in Task.list_by_user(user_id)]
        return data, 200

    def create_user(self, data, auth_header=None):
        fields = validate_user(data)
        if User.find_by_email(fields['email']):
            raise ConflictError('Email já cadastrado')
        # Cadastro é público: role privilegiado só pode ser atribuído por um admin autenticado.
        if fields['role'] in PRIVILEGED_ROLES:
            self.auth_service.require_admin(auth_header)

        password = fields.pop('password')
        user = User(**fields)
        user.set_password(password)
        user.save()
        logger.info("Usuário criado: %s - %s", user.id, user.name)
        return user.to_dict(), 201

    def update_user(self, user_id, data, auth_header=None):
        user = self._get_or_404(user_id)
        data = require_body(data)
        # Autorização antes de validar, para não revelar dados (ex.: email já cadastrado) a quem não pode editar.
        if 'role' in data or 'active' in data:
            self.auth_service.require_admin(auth_header)
        else:
            self.auth_service.require_self_or_admin(auth_header, user_id)
        fields = validate_user(data, partial=True)
        if 'email' in fields:
            existing = User.find_by_email(fields['email'])
            if existing and existing.id != user_id:
                raise ConflictError('Email já cadastrado')

        password = fields.pop('password', None)
        for name, value in fields.items():
            setattr(user, name, value)
        if password:
            user.set_password(password)
        user.save()
        return user.to_dict(), 200

    def delete_user(self, user_id, auth_header=None):
        user = self._get_or_404(user_id)
        self.auth_service.require_self_or_admin(auth_header, user_id)
        user.delete_with_tasks()
        logger.info("Usuário deletado: %s", user_id)
        return {'message': 'Usuário deletado com sucesso'}, 200

    def get_user_tasks(self, user_id):
        self._get_or_404(user_id)
        return [task.to_summary_dict() for task in Task.list_by_user(user_id)], 200

    def login(self, data):
        data = require_body(data)
        email, password = data.get('email'), data.get('password')
        if not email or not password:
            raise ValidationError('Email e senha são obrigatórios')
        if not isinstance(email, str) or not isinstance(password, str):
            raise ValidationError('Email e senha devem ser texto')

        user = User.find_by_email(email)
        if not user or not user.check_password(password):
            raise UnauthorizedError('Credenciais inválidas')
        if not user.active:
            raise ForbiddenError('Usuário inativo')
        if user.needs_rehash():
            user.set_password(password)
            user.save()

        return {
            'message': 'Login realizado com sucesso',
            'user': user.to_dict(),
            'token': self.auth_service.issue_token(user),
        }, 200

    @staticmethod
    def _get_or_404(user_id):
        user = User.get(user_id)
        if not user:
            raise NotFoundError('Usuário não encontrado')
        return user
