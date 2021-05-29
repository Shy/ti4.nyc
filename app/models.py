from datetime import datetime
from app import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    vaccinated = db.Column(db.Boolean())
    admin = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Game(db.Model):
    __tablename__ = "game"
    id = db.Column(db.Integer, primary_key=True)
    zodiac_sign = db.Column(db.String(140))
    date = db.Column(db.DateTime)

    def __repr__(self):
        return "<Game {}>".format(self.zodiac_sign)


class SignUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey(Game.id), nullable=False)
    user = db.relationship("User", backref=db.backref("user"))
    game = db.relationship("Game", backref=db.backref("game"))

    def __repr__(self):
        return "<Signup {}>".format(self.id)
