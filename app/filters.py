from app import app, db
import datetime
import pendulum
from app.models import User, Game, SignUp
from flask import url_for


@app.template_filter("strftime")
def _jinja2_filter_datetime(date, fmt="dddd MMMM Do"):
    date = pendulum.parse(f"{date.year}-{date.month}-{date.day}", strict=False)
    return date.format(fmt)


@app.template_filter("playerLookup")
def _playerLookup(gameID):
    gameSignUps = SignUp.query.filter_by(event_id=gameID).order_by(SignUp.id).all()
    return gameSignUps


@app.template_filter("registeredLookup")
def _registeredLookup(gameID):
    gameSignUps = _playerLookup(gameID)
    if len(gameSignUps) <= 6:
        return gameSignUps
    return gameSignUps[: -(len(gameSignUps) % 6)]


@app.template_filter("waitlistLookup")
def _waitlistLookup(gameID):
    gameSignUps = _playerLookup(gameID)
    if len(gameSignUps) <= 6:
        return []
    return gameSignUps[-(len(gameSignUps) % 6) :]


@app.template_filter("zodiacStaticImage")
def _zodiacStaticImage(zodiacSign):
    return url_for(
        "static", filename=f"icons/{zodiacSign.lower().replace(' ', '')}.svg"
    )
