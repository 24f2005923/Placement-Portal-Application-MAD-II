from models import db
from exceptions import NotFound

class BaseRepository:
    """Reusable base repository for common SQLAlchemy queries."""
    
    @classmethod
    def get_by_id(cls, model, record_id):
        return db.session.query(model).filter(model.id == record_id).first()

    @classmethod
    def get_by_id_or_404(cls, model, record_id, not_found_msg="Record not found"):
        record = cls.get_by_id(model, record_id)
        if not record:
            raise NotFound(not_found_msg)
        return record

    @classmethod
    def first_or_404(cls, query, not_found_msg="Record not found"):
        record = query.first()
        if not record:
            raise NotFound(not_found_msg)
        return record

    @classmethod
    def get_by_field_or_404(cls, model, field_name, value, not_found_msg="Record not found"):
        field = getattr(model, field_name)
        return cls.first_or_404(
            db.session.query(model).filter(field == value),
            not_found_msg,
        )
