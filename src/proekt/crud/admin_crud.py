"""Methods specifically for admin"""

from flask import Blueprint, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy import select, or_, and_

from proekt.database import SessionLocal
from proekt.models import UserRoles, Friendship, FriendStatus

admin = Blueprint("admin", __name__)


@admin.route("/admin/users/<int:user_id>/friends/<int:friend_id>/remove", methods=["POST"])
@login_required
def remove_user_friend(user_id, friend_id):
    if current_user.role != UserRoles.ADMIN:
        abort(403)

    with SessionLocal() as session:
        friendship = session.scalar(
            select(Friendship).where(
                or_(and_(Friendship.user_id == user_id, Friendship.friend_id == friend_id),
                    and_(Friendship.user_id == friend_id, Friendship.friend_id == user_id)),
                Friendship.status == FriendStatus.ACCEPTED))

        if friendship is None:
            abort(404)

        session.delete(friendship)
        session.commit()

    return redirect(url_for("profile", user_id=user_id))
