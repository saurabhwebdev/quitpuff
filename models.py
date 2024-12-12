from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(80), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    cigs_per_day = db.Column(db.Integer, nullable=True)
    cost_per_cig = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(10), nullable=True)
    cigs_per_pack = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    cigarettes = db.relationship('Cigarette', backref='user', lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'created_at' not in kwargs:
            self.created_at = datetime.utcnow()

class Cigarette(db.Model):
    __tablename__ = 'cigarettes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    smoked_at = db.Column(db.DateTime, default=datetime.utcnow)
    cost = db.Column(db.Float, nullable=False) 