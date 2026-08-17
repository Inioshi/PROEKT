from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

#@app.route("/search")
#def search():
#    return render_template("")


@app.route("/video_games/<int:game_id>") #dynamic address
def game_page(game_id):
    return render_template("index.html", title="", game=game_id)


@app.route("/login")
def login():
    return "help"

@app.route("/register")
def register():
    return "help"

@app.route("/search")
def search():
    return "help"

if __name__ == "__main__":
    app.run()