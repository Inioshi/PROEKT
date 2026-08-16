from flask import Flask, render_template, request, url_for, redirect

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run()

#@app.route("/video_games/<game_id>") #dynamic address
#def game_page(game_id):
#    return render_template("index.html", title="", game=game_id)

