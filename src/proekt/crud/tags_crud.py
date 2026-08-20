"""CRUD methods for game tags"""

from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import select

from proekt.database import SessionLocal
from proekt.models import Tag, VideoGame

tags = Blueprint("tags", __name__)

@tags.route("/video_games/<int:game_id>/tags", methods=["POST"])
@login_required
def add_tag(game_id):
    tag_text = request.form.get("tag", "").strip()

    if not tag_text:
        flash("Tag can't be empty.")
        return redirect(url_for("game_page", game_id=game_id))

    if len(tag_text) > 50:
        flash("Tag is too long.")
        return redirect(url_for("game_page", game_id=game_id))

    with SessionLocal() as session:
        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)

        tag = session.scalar(
            select(Tag).where(Tag.user_id == current_user.id,
                              Tag.game_id == game_id,
                              Tag.tag == tag_text))
        if tag is None:
            session.add(Tag(user_id=current_user.id, game_id=game_id, tag=tag_text))
            session.commit()

    return redirect(url_for("game_page", game_id=game_id))


@tags.route("/tags/<int:tag_id>/delete", methods=["POST"])
@login_required
def remove_tag(tag_id):
    """Remove tag from game page"""
    with SessionLocal() as session:
        tag = session.get(Tag, tag_id)
        if tag is None:
            abort(404)
        if tag.user_id != current_user.id:
            abort(403)

        game_id = tag.game_id
        session.delete(tag)
        session.commit()

    return redirect(url_for("game_page", game_id=game_id))

@tags.route("/profile/tags/<int:tag_id>/edit", methods=["POST"])
@login_required
def edit_tag(tag_id):
    tag_text = request.form.get("tag", "").strip()
 
    with SessionLocal() as session:
        tag = session.get(Tag, tag_id)
        if tag is None:
            abort(404)
        if tag.user_id != current_user.id:
            abort(403)
 
        if not tag_text:
            flash("Tag can't be empty.")
            return redirect(url_for("profile", user_id=tag.user_id))

        if len(tag_text) > 50:
            flash("Tag is too long.")
            return redirect(url_for("profile", user_id=tag.user_id))
 
        duplicate = session.scalar(
            select(Tag).where(Tag.user_id == current_user.id,
                              Tag.game_id == tag.game_id,
                              Tag.tag == tag_text,
                              Tag.id != tag.id))
        if duplicate is not None:
            flash("You already have that tag on this game.")
            return redirect(url_for("profile", user_id=tag.user_id))
 
        tag.tag = tag_text
        user_id = tag.user_id
        session.commit()
 
    return redirect(url_for("profile", user_id=user_id))

@tags.route("/profile/tags/<int:tag_id>/delete", methods=["POST"])
@login_required
def delete_tag(tag_id):
    with SessionLocal() as session:
        tag = session.get(Tag, tag_id)
        if tag is None:
            abort(404)
        if tag.user_id != current_user.id:
            abort(403)
 
        user_id = tag.user_id
        session.delete(tag)
        session.commit()
 
    return redirect(url_for("profile", user_id=user_id))