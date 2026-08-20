"""CRUD methods for reviews"""

from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import select

from proekt.database import SessionLocal
from proekt.models import VideoGame, Review, UserRoles

reviews = Blueprint("reviews", __name__)

@reviews.route("/video_games/<int:game_id>/reviews", methods=["POST"])
@login_required
def create_review(game_id):
    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip() or None

    if rating is None or not (1 <= rating <= 5):
        flash("Rating must be between 1 and 5.")
        return redirect(url_for("game_page", game_id=game_id))

    with SessionLocal() as session:
        game = session.get(VideoGame, game_id)
        if game is None:
            abort(404)

        existing = session.scalar(
            select(Review).where(Review.user_id == current_user.id,
                                  Review.game_id == game_id))
        if existing is not None:
            flash("You've already reviewed this game. Edit your existing review instead.")
            return redirect(url_for("game_page", game_id=game_id))

        review = Review(user_id=current_user.id, game_id=game_id,
                         rating=rating, comment=comment)
        session.add(review)
        session.commit()

    return redirect(url_for("game_page", game_id=game_id))

@reviews.route("/reviews/<int:review_id>/edit", methods=["POST"])
@login_required
def edit_review(review_id):
    with SessionLocal() as session:
        review = session.get(Review, review_id)
        if review is None:
            abort(404)
        if review.user_id != current_user.id:
            abort(403)

        rating = request.form.get("rating", type=int)
        comment = request.form.get("comment", "").strip()

        if rating is None or not (1 <= rating <= 5):
            flash("Rating must be between 1 and 5.")
            return redirect(url_for("game_page", game_id=review.game_id))
    
        review.rating = rating
        review.comment = comment or None

        session.commit()
    flash("Review updated successfully.")
    return redirect(url_for("profile", user_id=current_user.id))

@reviews.route("/reviews/<int:review_id>/delete", methods=["POST"])
@login_required
def delete_review(review_id):
    with SessionLocal() as session:
        review = session.get(Review, review_id)
        if review is None:
            abort(404)
        if review.user_id != current_user.id and current_user.role != UserRoles.ADMIN:
            abort(403)

        game_id = review.game_id
        session.delete(review)
        session.commit()

    return redirect(url_for("game_page", game_id=game_id))
