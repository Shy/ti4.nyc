from flask_wtf import FlaskForm
from datetime import date
from wtforms import (
    StringField,
    PasswordField,
    SelectField,
    BooleanField,
    SubmitField,
    HiddenField,
    DateField,
)
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    email = StringField(
        "Email",
        render_kw={"placeholder": "info@ti4.nyc"},
        validators=[DataRequired(), Email()],
    )

    password = PasswordField(
        "Password",
        render_kw={"placeholder": "**************************"},
        validators=[DataRequired()],
    )
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class GameCreationForm(FlaskForm):
    name = SelectField(
        "Event Name",
        choices=[
            "Aries",
            "Taurus",
            "Gemini",
            "Cancer",
            "Leo",
            "Virgo",
            "Libra",
            "Scorpio",
            "Sagittarius",
            "Capricorn",
            "Aquarius",
            "Pisces",
            "Eight Player Special",
            "14 Point Special",
        ],
        validators=[DataRequired()],
    )
    date = DateField("Event Date", validators=[DataRequired()], default=date.today)
    submit = SubmitField("Create Event")


class GameRegistrationForm(FlaskForm):
    game_id = HiddenField("game_id", validators=[DataRequired()])
    user_id = HiddenField("user_id", validators=[DataRequired()])
    submit = SubmitField("Sign In/Out")


class RegistrationForm(FlaskForm):
    username = StringField(
        "First Name, and Last initial",
        validators=[DataRequired()],
        render_kw={"placeholder": "Shy R."},
    )
    email = StringField(
        "Email",
        validators=[DataRequired(), Email()],
        render_kw={"placeholder": "info@ti4.nyc"},
    )
    password = PasswordField(
        "Password",
        validators=[DataRequired()],
        render_kw={"placeholder": "**************************"},
    )
    password2 = PasswordField(
        "Repeat Password",
        validators=[DataRequired(), EqualTo("password")],
        render_kw={"placeholder": "**************************"},
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
    oldpassword = PasswordField(
        "Current Password",
        render_kw={"placeholder": "**************************"},
    )
    vaccinated = BooleanField(
        "Are you fully Vaccinated?",
        validators=[
            DataRequired(),
        ],
    )
    coc = BooleanField(
        "Do you agree to abide by our Code of Conduct & League Rules?",
        validators=[
            DataRequired(),
        ],
    )
    host = BooleanField("Can you host games?")
    ownGame = BooleanField(
        "Do you on the game, expansion and are willing to bring them?"
    )
    address = StringField(
        "What's your address? We'll use this if you decide to host, or if we need to mail you a prize. (Optional)",
        render_kw={"placeholder": "1644 Sol System, Brooklyn 21351"},
    )
    password = PasswordField(
        "New Password",
        render_kw={"placeholder": "**************************"},
    )
    password2 = PasswordField(
        "Repeat New Password",
        validators=[EqualTo("password")],
        render_kw={"placeholder": "**************************"},
    )
    submit = SubmitField("Update")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.lower()).first()
        if user is not None:
            raise ValidationError("Please use a different username.")

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data.lower()).first()
        if user is not None:
            raise ValidationError("Please use a different email address.")
