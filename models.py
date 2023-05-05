from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin


db=SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    password = db.Column(db.String(100))


class UserMessage(db.Model):
    __tablename__ = 'usermessages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user_name = db.Column(db.String(100))
    message = db.Column(db.String(250), nullable=False)
    time = db.Column(db.String(20))
    status = db.Column(db.String(20))