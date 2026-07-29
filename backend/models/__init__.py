from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class TimestampMixin:
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class DictMixin:
    def as_dict(self, fields):
        return {f: getattr(self, f, None) for f in fields}

