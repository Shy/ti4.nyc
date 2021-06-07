from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import (
    LoginForm,
    RegistrationForm,
    ProfileForm,
    GameRegistrationForm,
    GameCreationForm,
)
from app.models import User, Game, SignUp
from config import Config
from app.filters import (
    _jinja2_filter_datetime,
    _playerlookup,
    _registeredlookup,
    _waitlistlookup,
    _zodiacstaticimage,
)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="Home")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid Email or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("index")
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if current_user.is_anonymous:
        return redirect(url_for("index"))
    form = ProfileForm()
    if request.method == "GET":
        form.vaccinated.data = current_user.vaccinated
    if request.method == "POST" and form.validate():
        if form.validate_on_submit():
            if current_user.check_password(form.oldpassword.data):
                if form.password.data:
                    current_user.set_password(form.password.data)
                current_user.vaccinated = form.vaccinated.data
                db.session.commit()
            else:
                flash("Invalid password")
    return render_template(
        "profile.html", title="Profile", form=form, user=current_user.username
    )


@app.route("/event/<int:gameID>")
def eventView(gameID):
    if current_user.admin:
        game = Game.query.filter_by(id=gameID).first()
        return render_template("event.html", game=game)
    return redirect(url_for("index"))


@app.route("/gamesCreate", methods=["POST"])
def gamesCreate():
    if current_user.admin:
        form = GameCreationForm()
        game = Game(zodiac_sign=form.name.data, date=form.date.data)
        db.session.add(game)
        db.session.commit()
    return redirect(url_for("games"))


@app.route("/games", methods=["GET", "POST"])
def games():
    if current_user.is_anonymous:
        return redirect(url_for("index"))
    elif current_user.is_authenticated:
        form = GameRegistrationForm()
        if request.method == "POST":
            signup = SignUp.query.filter_by(
                user_id=form.user_id.data, event_id=form.game_id.data
            ).first()
            if signup:
                db.session.delete(signup)
            else:
                user = User.query.filter_by(id=form.user_id.data).first()
                if user.vaccinated:
                    signup = SignUp(
                        user_id=form.user_id.data, event_id=form.game_id.data
                    )
                    db.session.add(signup)
                else:
                    flash(
                        "Only vaccinated users can sign up for games. Head over to your profile to confirm your vaccination status."
                    )
            db.session.commit()
        games = Game.query.order_by(Game.date).all()
        if current_user.admin:
            adminForm = GameCreationForm()
        else:
            adminForm = ""
        return render_template(
            "games.html",
            title="Upcoming Games",
            games=games,
            form=form,
            adminForm=adminForm,
        )
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data.lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)
