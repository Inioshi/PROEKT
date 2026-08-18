from flask import Flask, render_template, request, url_for, redirect
from flask_login import login_required
from .auth import auth, login_manager

app = Flask(__name__)

app.config["SECRET_KEY"] = "passpass"

login_manager.init_app(app)
app.register_blueprint(auth)

@app.route("/")
def index():
    return render_template("index.html")

#@app.route("/search")
#def search():
#    return render_template("")

@app.route("/video_games/<int:game_id>")
def game_page(game_id):
    return render_template("index.html", title="", game=game_id)

@app.route("/profile")
@login_required
def profile():
    return "help"

@app.route("/search")
def search():
    return "help"

if __name__ == "__main__":
    app.run()
