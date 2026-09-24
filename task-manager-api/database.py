from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class CRUDMixin:
    """Acesso a dados comum a todos os models (substitui o legado Model.query.get)."""

    @classmethod
    def get(cls, record_id):
        return db.session.get(cls, record_id)

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            db.session.commit()


def commit():
    db.session.commit()
