from app import app, db
from app.models import User, Game


@app.shell_context_processor
def make_shell_context():
    return {"db": db, "User": User, "Game": Game}


if __name__ == "__main__":
    # Setting debug to True enables debug output. This line should be
    # removed before deploying a production app.
    app.debug = True
    app.run()
