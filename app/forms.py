from flask_wtf import FlaskForm
from datetime import date
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    HiddenField,
    DateField,
)
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class GameCreationForm(FlaskForm):
    name = StringField("Event Name", validators=[DataRequired()])
    date = DateField("Event Date", validators=[DataRequired()], default=date.today)
    submit = SubmitField("Create Event")


class GameRegistrationForm(FlaskForm):
    game_id = HiddenField("game_id", validators=[DataRequired()])
    user_id = HiddenField("user_id", validators=[DataRequired()])
    submit = SubmitField("Sign In/Out")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError("That username is already taken.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError("That email is already taken.")


class ProfileForm(FlaskForm):
    oldpassword = PasswordField("Current Password", validators=[DataRequired()])
    vaccinated = BooleanField("Are you fully Vaccinated?")
    password = PasswordField(
        "New Password",
    )
    password2 = PasswordField("Repeat New Password", validators=[EqualTo("password")])
    submit = SubmitField("Update")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")
