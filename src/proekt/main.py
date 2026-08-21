from sqlalchemy import select, or_
from flask import Flask, render_template, request, abort
from flask_login import login_required, current_user
from proekt.auth import auth, login_manager
from proekt.database import SessionLocal
from proekt.models import VideoGame, User, UserRoles, Genre, Collection
from proekt.recommendations import compute_recommendations

from proekt.crud import reviews, tags, collections

app = Flask(__name__)

app.config["SECRET_KEY"] = "passpass"

login_manager.init_app(app)
app.register_blueprint(auth)
#app.register_blueprint(games)
#app.register_blueprint(friends_bp)
app.register_blueprint(reviews)
app.register_blueprint(tags)
app.register_blueprint(collections)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/video_games/<int:game_id>")
def game_page(game_id):
    with SessionLocal() as session:
        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)

        average_rating = (
            sum(review.rating for review in game.reviews) / len(game.reviews)
            if game.reviews
            else None)

        user_collections = []
        if current_user.is_authenticated:
            user_collections = session.scalars(
                select(Collection).where(Collection.user_id == current_user.id)).all()

        return render_template("video_game.html", game=game,
                               average_rating=average_rating,
                               user_collections=user_collections)

@app.route("/profile/<int:user_id>")
def profile(user_id):
    with SessionLocal() as session:
        user = session.get(User, user_id)

        if user is None:
            abort(404)
        if not current_user.is_authenticated and user.role != UserRoles.STUDIO:
            abort(403)

        group_tags = []
        if current_user.is_authenticated and current_user.id == user.id:
            grouped = {}
            for t in user.tags:
                grouped.setdefault(t.tag, []).append(t)
            group_tags = list(grouped.items())

        return render_template("user_profile.html", user=user,
                               UserRoles=UserRoles, group_tags=group_tags)

@app.route("/search")
def search():
    query_text = request.args.get("q", "").strip()
    search_type = request.args.get("type", "")

    if not query_text:
        return render_template("search.html", query_text=query_text,
                               search_type=search_type, games=[], studios=[], users=[])

    with SessionLocal() as session:
        game_results = []
        studio_results = []
        users_results = []
        if search_type == "name":
            game_results = session.scalars(
                select(VideoGame).where(VideoGame.title.ilike(f"%{query_text}%"))).all()
        elif search_type == "genre":
            game_results = session.scalars(
                select(VideoGame).join(VideoGame.genres)
                                  .where(Genre.name.ilike(f"%{query_text}%"))).all()
        elif search_type == "studio":
            studio_results = session.scalars(
                select(User).where(User.role == UserRoles.STUDIO,
                                   User.username.ilike(f"%{query_text}%"))).all()
        elif search_type == "user":
            if current_user.is_authenticated:
                users_results = session.scalars(
                    select(User).where(User.role == UserRoles.REGISTERED_USER,
                                       User.username.ilike(f"%{query_text}%"))).all()
        else:
            game_results = session.scalars(
                select(VideoGame).outerjoin(VideoGame.genres)
                                  .outerjoin(User, VideoGame.studio_id == User.id)
                                  .where(or_(
                                      VideoGame.title.ilike(f"%{query_text}%"),
                                      Genre.name.ilike(f"%{query_text}%"),
                                      User.username.ilike(f"%{query_text}%"))).distinct()).all()
            studio_results = session.scalars(
                select(User).where(
                    User.role == UserRoles.STUDIO,
                    User.username.ilike(f"%{query_text}%"))).all()

            if current_user.is_authenticated:
                users_results = session.scalars(
                    select(User).where(User.username.ilike(f"%{query_text}%"))).all()
        return render_template("search.html", query_text=query_text,
                                              search_type=search_type,
                                              games=game_results,
                                              studios=studio_results,
                                              users=users_results,
                                              UserRoles=UserRoles)

@app.route("/collections/<int:collection_id>")
@login_required
def collection_page(collection_id):
    with SessionLocal() as session:
        collection = session.get(Collection, collection_id)
        if collection is None:
            abort(404)

        return render_template("collection.html", collection=collection)

@app.route("/recommendations")
@login_required
def recommendations():
    with SessionLocal() as session:
        games_rec = compute_recommendations(session, current_user.id)
        return render_template("recommendations.html", games=games_rec)

@app.errorhandler(404)
def not_found(_error):
    return render_template("error.html", code=404, message="Page not found."), 404

@app.errorhandler(403)
def forbidden(_error):
    return render_template("error.html", code=403, message="No permission to view page"), 403

if __name__ == "__main__":
    app.run()
