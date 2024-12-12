from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))  # Indian Standard Time offset

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
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(IST), nullable=False)
    cigarettes = db.relationship('Cigarette', backref='user', lazy=True)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if 'created_at' not in kwargs:
            self.created_at = datetime.utcnow()

class Cigarette(db.Model):
    __tablename__ = 'cigarettes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    smoked_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(IST))
    cost = db.Column(db.Float, nullable=False)
    
    def __init__(self, **kwargs):
        super(Cigarette, self).__init__(**kwargs)
        if 'smoked_at' not in kwargs:
            self.smoked_at = datetime.now(IST)
    
    @property
    def formatted_time(self):
        """Return the smoked_at time in IST format"""
        if self.smoked_at.tzinfo is None:
            return self.smoked_at.replace(tzinfo=IST)
        return self.smoked_at.astimezone(IST) 