"""CRUD methods for video games"""

from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import select

from proekt.database import SessionLocal
from proekt.models import VideoGame, Genre, Review, UserRoles

games = Blueprint("games", __name__)


def is_admin(user):
    return user.role == UserRoles.ADMIN

def can_manage_game(user, game):
    return is_admin(user) or (user.role == UserRoles.STUDIO and game.studio_id == user.id)


@games.route("/video_games", methods=["POST"])
@login_required
def create_game():
    if current_user.role not in (UserRoles.STUDIO, UserRoles.ADMIN):
        abort(403)

    title = request.form.get("title", "").strip()
    short_description = request.form.get("short_description", "").strip()
    studio_id = request.form.get("studio_id", type=int)

    if not title:
        flash("Title can't be empty.")
        return redirect(url_for("profile", user_id=current_user.id))

    if len(title) > 50:
        flash("Title is too long.")
        return redirect(url_for("profile", user_id=current_user.id))

    if not short_description:
        flash("Description can't be empty.")
        return redirect(url_for("profile", user_id=current_user.id))

    if len(short_description) > 600:
        flash("Description is too long.")
        return redirect(url_for("profile", user_id=current_user.id))

    if current_user.role == UserRoles.STUDIO:
        studio_id = current_user.id
    elif not studio_id:
        flash("Studio is required.")
        return redirect(url_for("profile", user_id=current_user.id))

    with SessionLocal() as session:
        game = VideoGame(title=title, short_description=short_description,
                         studio_id=studio_id)
        session.add(game)
        session.commit()
        game_id = game.id

    return redirect(url_for("game_page", game_id=game_id))


@games.route("/video_games/<int:game_id>/edit", methods=["POST"])
@login_required
def edit_game(game_id):
    title = request.form.get("title", "").strip()
    short_description = request.form.get("short_description", "").strip()

    with SessionLocal() as session:
        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)
        if not can_manage_game(current_user, game):
            abort(403)

        if title:
            if len(title) > 50:
                flash("Title is too long.")
                return redirect(url_for("game_page", game_id=game_id))
            game.title = title

        if short_description:
            if len(short_description) > 600:
                flash("Description is too long.")
                return redirect(url_for("game_page", game_id=game_id))
            game.short_description = short_description

        session.commit()

    return redirect(url_for("game_page", game_id=game_id))


@games.route("/video_games/<int:game_id>/delete", methods=["POST"])
@login_required
def delete_game(game_id):
    with SessionLocal() as session:
        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)
        if not can_manage_game(current_user, game):
            abort(403)

        studio_id = game.studio_id
        session.delete(game)
        session.commit()

    return redirect(url_for("profile", user_id=studio_id))


@games.route("/video_games/<int:game_id>/genres", methods=["POST"])
@login_required
def add_genre(game_id):
    genre_name = request.form.get("genre", "").strip()

    if not genre_name:
        flash("Genre can't be empty.")
        return redirect(url_for("game_page", game_id=game_id))

    if len(genre_name) > 20:
        flash("Genre name is too long.")
        return redirect(url_for("game_page", game_id=game_id))

    with SessionLocal() as session:
        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)
        if not can_manage_game(current_user, game):
            abort(403)

        genre = session.scalar(select(Genre).where(Genre.name == genre_name))
        if genre is None:
            genre = Genre(name=genre_name)
            session.add(genre)

        if genre not in game.genres:
            game.genres.append(genre)

        session.commit()

    return redirect(url_for("game_page", game_id=game_id))


@games.route("/video_games/<int:game_id>/genres/<int:genre_id>/delete", methods=["POST"])
@login_required
def remove_genre(game_id, genre_id):
    if not is_admin(current_user):
        abort(403)

    with SessionLocal() as session:
        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)

        genre = session.get(Genre, genre_id)
        if genre is None:
            abort(404)

        if genre in game.genres:
            game.genres.remove(genre)

        session.commit()

    return redirect(url_for("game_page", game_id=game_id))


@games.route("/video_games/<int:game_id>/cover", methods=["POST"])
@login_required
def set_cover(game_id):
    cover_url = request.form.get("cover_url", "").strip()

    if not cover_url:
        flash("Cover URL can't be empty.")
        return redirect(url_for("game_page", game_id=game_id))

    if len(cover_url) > 200:
        flash("Cover URL is too long.")
        return redirect(url_for("game_page", game_id=game_id))

    with SessionLocal() as session:
        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)
        if not can_manage_game(current_user, game):
            abort(403)

        game.cover_url = cover_url
        session.commit()

    return redirect(url_for("game_page", game_id=game_id))


@games.route("/video_games/<int:game_id>/cover/delete", methods=["POST"])
@login_required
def remove_cover(game_id):
    if not is_admin(current_user):
        abort(403)

    with SessionLocal() as session:
        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)

        game.cover_url = None
        session.commit()

    return redirect(url_for("game_page", game_id=game_id))


@games.route("/video_games/<int:game_id>/reviews/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review_as_manager(game_id, review_id):
    with SessionLocal() as session:
        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)
        if not can_manage_game(current_user, game):
            abort(403)

        review = session.get(Review, review_id)
        if review is None or review.game_id != game_id:
            abort(404)

        session.delete(review)
        session.commit()

    return redirect(url_for("game_page", game_id=game_id))
