from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
from app import app, db
from app.forms import (
    LoginForm,
    RegistrationForm,
    ProfileForm,
    GameRegistrationForm,
    GameCreationForm,
    EmailForm,
    ResetPasswordForm,
    ResetPasswordRequestForm,
)
from app.models import User, Game, SignUp
from app.sendgrid import sendEmail, sendPasswordResetEmail
from app.filters import (
    _jinja2_filter_datetime,
    _playerLookup,
    _registeredLookup,
    _waitlistLookup,
    _zodiacStaticImage,
    _chunker,
)


@app.route("/")
@app.route("/index")
def index():
    return render_template("index.html", title="TI4.NYC")


# @app.route("/password")
# def passwordreset():
#     reset = User.query.filter_by(email="").first()
#     reset.set_password("")
#     db.session.commit()
#     return "Done"


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid Email or password", "error ")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for("profile"))
    return render_template("login.html", form=form, title="Login")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),
            coc=False,
            ownGame=False,
            host=False,
            vaccinated=False,
            admin=False,
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congratulations, you are now a registered user!", "success ")
        return redirect(url_for("login"))
    return render_template("register.html", form=form, title="Register")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if current_user.is_anonymous:
        return redirect(url_for("index"))
    form = ProfileForm()
    if request.method == "GET":
        form.username.data = current_user.username
        form.vaccinated.data = current_user.vaccinated
        form.coc.data = current_user.coc
        form.host.data = current_user.host
        form.ownGame.data = current_user.ownGame
        form.address.data = current_user.address
    if form.validate_on_submit():
        if form.password.data:
            if current_user.check_password(form.oldpassword.data):
                current_user.set_password(form.password.data)
            else:
                flash(
                    "Please provide current password to update your password.",
                    "warning",
                )
        current_user.username = form.username.data
        current_user.vaccinated = form.vaccinated.data
        current_user.coc = form.coc.data
        current_user.host = form.host.data
        current_user.address = form.address.data
        current_user.ownGame = form.ownGame.data
        db.session.commit()

    return render_template(
        "profile.html", title="Profile", form=form, user=current_user.username
    )


@app.route("/game/<int:gameID>", methods=["GET", "POST"])
def gameView(gameID):
    if current_user.admin:
        emailForm = EmailForm()
        if request.method == "POST":
            if emailForm.validate_on_submit():
                playerLookup = _playerLookup(gameID)
                toEmails = []
                for player in playerLookup:
                    toEmails.append([player.user.email, player.user.username])
                if (
                    sendEmail(
                        from_email=emailForm.fromEmail.data,
                        reply_to=current_user.email,
                        to_emails=toEmails,
                        subject=emailForm.subject.data,
                        content=emailForm.content.data,
                    )
                    in [200, 202]
                ):
                    flash("Emails Sent!", "success")
                else:
                    flash(
                        "Emails Failed to send. Try again or let Shy know something went wrong.",
                        "error",
                    )
        emailForm.fromEmail.data = (
            current_user.id - 1
        )  # Sean and I are the first 2 users in the DB. If someone else becomes and Admin you'll need to rewrite this.
        game = Game.query.filter_by(id=gameID).first()
        return render_template(
            "game.html", game=game, title=game.zodiac_sign, emailForm=emailForm
        )
    return redirect(url_for("index"))


@app.route("/gamesCreate", methods=["POST"])
def gamesCreate():
    if current_user.admin:
        form = GameCreationForm()
        game = Game(zodiac_sign=form.name.data, date=form.date.data)
        db.session.add(game)
        db.session.commit()
    return redirect(url_for("games"))


@app.route("/emailAll", methods=["POST"])
def emailAll():
    if current_user.admin:
        emailForm = EmailForm()
        if emailForm.validate_on_submit():
            players = User.query.all()

            to_email = []
            for player in players:
                to_email.append([player.email, player.username])
            if (
                sendEmail(
                    from_email=emailForm.fromEmail.data,
                    reply_to=current_user.email,
                    to_emails=to_email,
                    subject=emailForm.subject.data,
                    content=emailForm.content.data,
                )
                in [200, 202]
            ):
                flash("Emails Sent!", "success")
            else:
                flash(
                    "Emails Failed to send. Try again or let Shy know something went wrong.",
                    "error",
                )
        emailForm.fromEmail.data = (
            current_user.id - 1
        )  # Sean and I are the first 2 users in the DB. If someone else becomes and Admin you'll need to rewrite this.
    return redirect(url_for("games"))


@app.route("/games", methods=["GET", "POST"])
def games():
    if current_user.is_anonymous:
        return redirect(url_for("index"))
    elif not (current_user.coc & current_user.vaccinated):
        flash(
            "Only players who have agreed to our rules, COC and are fully vaccinated can sign up for games.",
            "warning",
        )
        return redirect(url_for("profile"))
    else:
        form = GameRegistrationForm()
        if request.method == "POST":
            signup = SignUp.query.filter_by(
                user_id=form.user_id.data, event_id=form.game_id.data
            ).first()
            if signup:
                db.session.delete(signup)
            else:
                user = User.query.filter_by(id=form.user_id.data).first()
                if user.vaccinated == True & user.coc == True:
                    signup = SignUp(
                        user_id=form.user_id.data, event_id=form.game_id.data
                    )
                    db.session.add(signup)
                else:
                    flash(
                        "Only players who have agreed to our rules, COC and are fully vaccinated can sign up for games. Head over to your profile to indicate your vaccination status and agreement to the rules.",
                        "warning",
                    )
                    return redirect(url_for("profile"))
            db.session.commit()
        games = Game.query.order_by(Game.date).all()
        if current_user.admin:
            adminForm = GameCreationForm()
            emailForm = EmailForm()
            emailForm.fromEmail.data = current_user.id - 1
        else:
            adminForm = ""
            emailForm = ""
        return render_template(
            "games.html",
            title="Upcoming Games",
            games=games,
            form=form,
            adminForm=adminForm,
            emailForm=emailForm,
        )
    return redirect(url_for("login"))


@app.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            sendPasswordResetEmail(user)
        flash(
            "Check your email (and Spam) for the instructions to reset your password",
            "info",
        )
        return redirect(url_for("login"))
    return render_template(
        "reset_password_request.html", title="Reset Password", form=form
    )


@app.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.", "success")
        return redirect(url_for("login"))
    return render_template("reset_password.html", form=form)
