from application import db, login_manager
from datetime import datetime, timedelta
from flask_login import UserMixin


class User(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    creation_time = db.Column(
        db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8)
    )

    def get_id(self):
        return str(self.user_id)


class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)


class History(db.Model):
    entry_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    worker_id = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    creation_time = db.Column(
        db.DateTime, default=lambda: datetime.utcnow() + timedelta(hours=8)
    )
    image = db.Column(db.LargeBinary)
