# models.py

from flask_login import UserMixin
from . import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(1000), nullable=False)


class Preference(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    rate = db.Column(db.Integer, nullable=False)
