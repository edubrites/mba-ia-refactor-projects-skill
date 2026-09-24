import hashlib
import hmac
import re

from werkzeug.security import check_password_hash, generate_password_hash

from database import CRUDMixin, db
from models.constants import ROLE_ADMIN, ROLE_USER
from models.task import Task
from utils.helpers import utcnow

# Hash MD5 legado (32 hex) gravado pela versão antiga; aceito só para migrar no próximo login.
_LEGACY_MD5_RE = re.compile(r'^[0-9a-f]{32}$')


class User(CRUDMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=ROLE_USER)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
            'active': self.active,
            'created_at': str(self.created_at),
        }

    def set_password(self, pwd):
        self.password = generate_password_hash(pwd)

    def check_password(self, pwd):
        if _LEGACY_MD5_RE.match(self.password or ''):
            return hmac.compare_digest(self.password, hashlib.md5(pwd.encode()).hexdigest())
        return check_password_hash(self.password, pwd)

    def needs_rehash(self):
        return bool(_LEGACY_MD5_RE.match(self.password or ''))

    def is_admin(self):
        return self.role == ROLE_ADMIN

    def delete_with_tasks(self):
        Task.delete_by_user(self.id)
        self.delete()

    @classmethod
    def list_all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    @classmethod
    def count(cls):
        return cls.query.count()
