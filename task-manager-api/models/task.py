from sqlalchemy import case, func
from sqlalchemy.orm import joinedload

from database import CRUDMixin, db
from models.constants import DEFAULT_PRIORITY, FINAL_STATUSES, STATUS_DONE, STATUS_PENDING, VALID_STATUSES
from utils.helpers import utcnow


class Task(CRUDMixin, db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=STATUS_PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref='tasks')
    category = db.relationship('Category', backref='tasks')

    def to_dict(self, include_overdue=False):
        data = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'tags': self.tags.split(',') if self.tags else [],
        }
        if include_overdue:
            data['overdue'] = self.is_overdue()
        return data

    def to_summary_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'status': self.status,
            'priority': self.priority,
            'created_at': str(self.created_at),
            'due_date': str(self.due_date) if self.due_date else None,
            'overdue': self.is_overdue(),
        }

    @staticmethod
    def validate_status(new_status):
        return new_status in VALID_STATUSES

    def is_overdue(self, now=None):
        now = now or utcnow()
        return bool(self.due_date and self.due_date < now and self.status not in FINAL_STATUSES)

    @classmethod
    def list_all(cls):
        return cls.query.order_by(cls.id).all()

    @classmethod
    def list_with_relations(cls):
        return (cls.query
                .options(joinedload(cls.user), joinedload(cls.category))
                .order_by(cls.id)
                .all())

    @classmethod
    def list_by_user(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.id).all()

    @classmethod
    def search(cls, text=None, status=None, priority=None, user_id=None):
        query = cls.query
        if text:
            pattern = f'%{text}%'
            query = query.filter(db.or_(cls.title.like(pattern), cls.description.like(pattern)))
        if status:
            query = query.filter(cls.status == status)
        if priority is not None:
            query = query.filter(cls.priority == priority)
        if user_id is not None:
            query = query.filter(cls.user_id == user_id)
        return query.order_by(cls.id).all()

    @classmethod
    def count(cls):
        return cls.query.count()

    @classmethod
    def count_by_status(cls):
        rows = db.session.query(cls.status, func.count(cls.id)).group_by(cls.status).all()
        return dict(rows)

    @classmethod
    def count_by_priority(cls):
        rows = db.session.query(cls.priority, func.count(cls.id)).group_by(cls.priority).all()
        return dict(rows)

    @classmethod
    def _overdue_filter(cls, now):
        return (cls.due_date.isnot(None), cls.due_date < now, cls.status.notin_(FINAL_STATUSES))

    @classmethod
    def count_overdue(cls, now):
        return cls.query.filter(*cls._overdue_filter(now)).count()

    @classmethod
    def list_overdue(cls, now):
        return cls.query.filter(*cls._overdue_filter(now)).order_by(cls.id).all()

    @classmethod
    def count_created_since(cls, since):
        return cls.query.filter(cls.created_at >= since).count()

    @classmethod
    def count_done_since(cls, since):
        return cls.query.filter(cls.status == STATUS_DONE, cls.updated_at >= since).count()

    @classmethod
    def counts_per_user(cls):
        """{user_id: (total, concluídas)} em uma única query agregada."""
        done = func.sum(case((cls.status == STATUS_DONE, 1), else_=0))
        rows = (db.session.query(cls.user_id, func.count(cls.id), done)
                .filter(cls.user_id.isnot(None))
                .group_by(cls.user_id)
                .all())
        return {user_id: (total, int(completed or 0)) for user_id, total, completed in rows}

    @classmethod
    def counts_per_category(cls):
        rows = (db.session.query(cls.category_id, func.count(cls.id))
                .filter(cls.category_id.isnot(None))
                .group_by(cls.category_id)
                .all())
        return dict(rows)

    @classmethod
    def delete_by_user(cls, user_id):
        cls.query.filter_by(user_id=user_id).delete(synchronize_session=False)
