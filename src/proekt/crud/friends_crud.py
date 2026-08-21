"""CRUD endpoints for friend requests and friendships"""

from flask import Blueprint, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import select, or_, and_

from proekt.database import SessionLocal
from proekt.models import Friendship, FriendStatus, User

friends = Blueprint("friends", __name__)


@friends.route("/friends/request/<int:friend_id>", methods=["POST"])
@login_required
def send_request(friend_id):

    if friend_id == current_user.id:
        flash("You can't friend yourself.")
        return redirect(url_for("profile", user_id=friend_id))

    with SessionLocal() as session:
        friend = session.get(User, friend_id)
        if friend is None:
            abort(404)

        existing = session.scalar(
            select(Friendship).where(
                or_(and_(Friendship.user_id == current_user.id, Friendship.friend_id == friend_id),
                    and_(Friendship.user_id == friend_id, Friendship.friend_id == current_user.id))))

        if existing is not None:
            if existing.status == FriendStatus.ACCEPTED:
                flash("You're already friends.")
            elif existing.status == FriendStatus.PENDING:
                flash("A friend request is already pending.")
            else:
                existing.user_id = current_user.id
                existing.friend_id = friend_id
                existing.status = FriendStatus.PENDING
                session.commit()
                flash("Friend request sent.")
        else:
            session.add(Friendship(user_id=current_user.id, friend_id=friend_id,
                                   status=FriendStatus.PENDING))
            session.commit()
            flash("Friend request sent.")

    return redirect(url_for("profile", user_id=friend_id))


@friends.route("/friends/<int:friendship_id>/accept", methods=["POST"])
@login_required
def accept_request(friendship_id):
    with SessionLocal() as session:
        friendship = session.get(Friendship, friendship_id)
        if friendship is None:
            abort(404)
        if friendship.friend_id != current_user.id:
            abort(403)
        if friendship.status != FriendStatus.PENDING:
            flash("This request is no longer pending.")
            return redirect(url_for("profile", user_id=current_user.id))

        friendship.status = FriendStatus.ACCEPTED
        session.commit()

    return redirect(url_for("profile", user_id=current_user.id))


@friends.route("/friends/<int:friendship_id>/decline", methods=["POST"])
@login_required
def decline_request(friendship_id):
    with SessionLocal() as session:
        friendship = session.get(Friendship, friendship_id)
        if friendship is None:
            abort(404)
        if friendship.friend_id != current_user.id:
            abort(403)
        if friendship.status != FriendStatus.PENDING:
            flash("This request is no longer pending.")
            return redirect(url_for("profile", user_id=current_user.id))

        friendship.status = FriendStatus.DECLINED
        session.commit()

    return redirect(url_for("profile", user_id=current_user.id))


@friends.route("/friends/<int:friend_id>/remove", methods=["POST"])
@login_required
def remove_friend(friend_id):
    with SessionLocal() as session:
        friendship = session.scalar(
            select(Friendship).where(
                or_(and_(Friendship.user_id == current_user.id, Friendship.friend_id == friend_id),
                    and_(Friendship.user_id == friend_id, Friendship.friend_id == current_user.id)),
                Friendship.status == FriendStatus.ACCEPTED))

        if friendship is None:
            abort(404)

        session.delete(friendship)
        session.commit()

    return redirect(url_for("profile", user_id=current_user.id))
