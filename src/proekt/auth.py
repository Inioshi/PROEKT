"""Login and register logic for the web app"""

from functools import wraps
from sqlalchemy import select
from flask import render_template, request, url_for, redirect, Blueprint, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from .database import SessionLocal
from .models import User, UserRoles, Collection, DefaultCollection

auth = Blueprint("auth", __name__)

login_manager = LoginManager()
login_manager.login_view = "auth.login" # type: ignore[assignment]

@login_manager.user_loader
def load_user(user_id: str):
    with SessionLocal() as session:
        return session.get(User, int(user_id))

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        with SessionLocal() as session:
            statement = select(User).where(User.username == username)

            user = session.scalar(statement)

            if user is None or not check_password_hash(user.password_hash, password):
                flash("Invalid username or password. Please try again")
                return redirect(url_for("auth.login"))

            login_user(user)

        return redirect(url_for("profile", user_id=user.id))
    return render_template("login.html")

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"]

        if not username or not password:
            flash("Username and password are required.")
            return redirect(url_for("auth.register"))

        with SessionLocal() as session:
            statement = select(User).where(User.username == username)

            existing_user = session.scalar(statement)

            if existing_user is not None:
                flash("Username is already taken.")
                return redirect(url_for("auth.register"))

            is_studio = request.form.get("is_studio") == "on"

            role = UserRoles.STUDIO if is_studio else UserRoles.REGISTERED_USER

            user = User(username=username,password_hash=generate_password_hash(password),
                        role=role)
            session.add(user)
            session.flush()

            default_collections = [
                Collection(user_id=user.id, name="Wishlist", is_default=True,
                           default_type=DefaultCollection.WISHLIST),
                Collection(user_id=user.id, name="Playing", is_default=True,
                           default_type=DefaultCollection.PLAYING),
                Collection(user_id=user.id, name="Completed", is_default=True,
                           default_type=DefaultCollection.COMPLETED)]

            session.add_all(default_collections)
            session.commit()

        flash("Account created successfully.")
        return redirect(url_for("auth.login"))

    return render_template("register.html")

def roles_required(*roles):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.role not in roles:
                abort(403)
            return f(*args, **kwargs)
        return wrapped
    return decorator

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
