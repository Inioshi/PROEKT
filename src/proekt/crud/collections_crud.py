"""CRUD methods for video game collections"""

from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import select

from proekt.database import SessionLocal
from proekt.models import Collection, VideoGame

collections = Blueprint("collections", __name__)

@collections.route("/collections", methods=["POST"])
@login_required
def create_collection():
    name = request.form.get("name", "").strip()

    if not name:
        flash("Collection name is required.")
        return redirect(url_for("profile", user_id=current_user.id))

    if len(name) > 50:
        flash("Collection name is too long.")
        return redirect(url_for("profile", user_id=current_user.id))

    with SessionLocal() as session:
        session.add(Collection(user_id=current_user.id, name=name,
                               is_default=False, default_type=None))
        session.commit()

    return redirect(url_for("profile", user_id=current_user.id))

@collections.route("/collections/<int:collection_id>/edit", methods=["POST"])
@login_required
def edit_collection(collection_id):
    name = request.form.get("name", "").strip()

    if not name:
        flash("Collection name is required.")
        return redirect(url_for("profile"))

    if len(name) > 50:
        flash("Collection name is too long.")
        return redirect(url_for("profile", user_id=current_user.id))

    with SessionLocal() as session:
        collection = session.get(Collection, collection_id)
        if collection is None:
            abort(404)
        if collection.user_id != current_user.id:
            abort(403)
        if collection.is_default:
            flash("Default collections can't be renamed.")
            return redirect(url_for("profile", user_id=current_user.id))

        collection.name = name
        session.commit()

    return redirect(url_for("profile", user_id=current_user.id))

@collections.route("/collections/<int:collection_id>/delete", methods=["POST"])
@login_required
def delete_collection(collection_id):
    with SessionLocal() as session:
        collection = session.get(Collection, collection_id)
        if collection is None:
            abort(404)
        if collection.user_id != current_user.id:
            abort(403)
        if collection.is_default:
            flash("Default collections can't be deleted.")
            return redirect(url_for("profile", user_id=current_user.id))

        session.delete(collection)
        session.commit()

    return redirect(url_for("profile", user_id=current_user.id))    

@collections.route("/collections/<int:collection_id>/games", methods=["POST"])
@login_required
def add_game_to_collection(collection_id):
    game_id = request.form.get("game_id", type=int)

    with SessionLocal() as session:
        collection = session.get(Collection, collection_id)
        if collection is None:
            abort(404)
        if collection.user_id != current_user.id:
            abort(403)

        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)

        if collection.is_default:
            other_defaults = session.scalars(
                select(Collection).where(Collection.user_id == current_user.id,
                                        Collection.is_default.is_(True),
                                        Collection.id != collection.id)).all()
            for other in other_defaults:
                if game in other.games:
                    other.games.remove(game)

        if game not in collection.games:
            collection.games.append(game)

        session.commit()

    return redirect(url_for("game_page", game_id=game_id))

@collections.route("/collections/<int:collection_id>/games/<int:game_id>/delete", methods=["POST"])
@login_required
def remove_game_from_collection(collection_id, game_id):
    with SessionLocal() as session:
        collection = session.get(Collection, collection_id)
        if collection is None:
            abort(404)
        if collection.user_id != current_user.id:
            abort(403)

        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)

        if game in collection.games:
            collection.games.remove(game)

        session.commit()

    return redirect(url_for("collection_page", collection_id=collection_id))
