from app import db, login, app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    __tablename__ = "user"
    username = db.Column(db.String(64), index=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    vaccinated = db.Column(db.Boolean, default=False, nullable=False)
    ownGame = db.Column(db.Boolean, default=False, nullable=False)
    host = db.Column(db.Boolean, default=False, nullable=False)
    coc = db.Column(db.Boolean, default=False, nullable=False)
    address = db.Column(db.String(256))
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    admin = db.Column(db.Boolean(), default=False, nullable=False)

    def __repr__(self):
        return "<User {}>".format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time() + expires_in},
            app.config["SECRET_KEY"],
            algorithm="HS256",
        )

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, app.config["SECRET_KEY"], algorithms=["HS256"])[
                "reset_password"
            ]
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Game(db.Model):
    __tablename__ = "game"
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, server_default=db.func.now())
    updated = db.Column(
        db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now()
    )
    zodiac_sign = db.Column(db.String(140))
    date = db.Column(db.DateTime)

    def __repr__(self):
        return "<Game {}>".format(self.zodiac_sign)


class SignUp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, server_default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable=False)
    event_id = db.Column(db.Integer, db.ForeignKey(Game.id), nullable=False)
    user = db.relationship("User", backref=db.backref("user"))
    game = db.relationship("Game", backref=db.backref("game"))

    def __repr__(self):
        return "<Signup {}>".format(self.id)
