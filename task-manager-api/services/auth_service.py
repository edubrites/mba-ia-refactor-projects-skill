import hashlib
import hmac

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from models.errors import ForbiddenError, UnauthorizedError
from models.user import User


class AuthService:
    """Emite e valida o token assinado devolvido por POST /login."""

    def __init__(self, secret_key, max_age):
        self.serializer = URLSafeTimedSerializer(secret_key, salt='auth-token')
        self.max_age = max_age

    @staticmethod
    def _password_version(user):
        # Muda sempre que a senha muda: tokens emitidos antes da troca deixam de valer.
        return hashlib.sha256(user.password.encode()).hexdigest()[:16]

    def issue_token(self, user):
        return self.serializer.dumps({'uid': user.id, 'pv': self._password_version(user)})

    def user_from_header(self, auth_header):
        if not auth_header or not auth_header.startswith('Bearer '):
            return None
        try:
            payload = self.serializer.loads(auth_header[len('Bearer '):], max_age=self.max_age)
        except (BadSignature, SignatureExpired):
            return None
        user = User.get(payload.get('uid'))
        if not user or not user.active:
            return None
        if not hmac.compare_digest(str(payload.get('pv', '')), self._password_version(user)):
            return None
        return user

    def require_admin(self, auth_header):
        user = self.user_from_header(auth_header)
        if not user:
            raise UnauthorizedError('Autenticação de administrador necessária')
        if not user.is_admin():
            raise ForbiddenError('Apenas administradores podem alterar role ou status de usuários')
        return user

    def require_self_or_admin(self, auth_header, user_id):
        user = self.user_from_header(auth_header)
        if not user:
            raise UnauthorizedError('Autenticação necessária')
        if user.id != user_id and not user.is_admin():
            raise ForbiddenError('Sem permissão para alterar este usuário')
        return user
