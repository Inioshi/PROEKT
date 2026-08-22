"""Tests for web API"""

# pylint: disable=redefined-outer-name

import os
import tempfile
from collections.abc import Generator
import pytest
from flask import Flask
from sqlalchemy import create_engine, select
from werkzeug.security import generate_password_hash

from proekt import database
from proekt.models import (Base, User, UserRoles, VideoGame, Genre,
                           Collection, DefaultCollection, Tag, Friendship, FriendStatus,
                           Review)
from proekt.main import app as flask_app

PASSWORD = "1234"

@pytest.fixture()
def app() -> Generator[Flask, None, None]:
    """Make an app with a temp database"""
    db_fd, db_path = tempfile.mkstemp(suffix=".sqlite3")
    engine = create_engine(f"sqlite:///{db_path}")

    Base.metadata.create_all(engine)
    database.SessionLocal.configure(bind=engine)

    flask_app.config.update(TESTING=True, SECRET_KEY="test-secret")

    yield flask_app

    engine.dispose()
    os.close(db_fd)
    os.unlink(db_path)


def make_user(username: str, role: UserRoles = UserRoles.REGISTERED_USER) -> int:
    """Make a test user"""
    with database.SessionLocal() as session:
        user = User(
            username=username,
            password_hash=generate_password_hash(PASSWORD),
            role=role)

        session.add(user)
        session.flush()

        session.add_all([
                Collection(user_id=user.id, name="Wishlist", is_default=True,
                           default_type=DefaultCollection.WISHLIST),
                Collection(user_id=user.id, name="Playing", is_default=True,
                           default_type=DefaultCollection.PLAYING),
                Collection(user_id=user.id, name="Completed", is_default=True,
                           default_type=DefaultCollection.COMPLETED)])

        session.commit()
        return user.id


def make_game(studio_id: int, genres: list[str] | None = None) -> int:
    """Make a test game"""
    with database.SessionLocal() as session:
        game = VideoGame(
            title="Test Game",
            short_description="desc",
            studio_id=studio_id,)

        for name in genres or []:
            genre = Genre(name=name)
            session.add(genre)
            game.genres.append(genre)

        session.add(game)
        session.commit()

        return game.id


def make_review(user_id: int, game_id: int, rating: int = 3, comment: str = "") -> int:
    """Make a test review"""
    with database.SessionLocal() as session:
        review = Review(user_id=user_id, game_id=game_id, rating=rating, comment=comment)
        session.add(review)
        session.commit()
        return review.id


def login_as(app: Flask, username: str):
    """Login into test user profile"""
    client = app.test_client()
    client.post("/login", data={"username": username, "password": PASSWORD,},)
    return client


def test_create_delete_tags(app: Flask) -> None:
    """Test making a tag and deleting it"""
    user_id = make_user("ivan")
    game_id = make_game(make_user("studio"))

    client = login_as(app, "ivan")
    client.post(f"/video_games/{game_id}/tags", data={"tag": "cozy"})

    with database.SessionLocal() as session:
        tag = session.scalar(select(Tag).where(Tag.user_id == user_id))
        assert tag is not None
        tag_id = tag.id

    client.post(f"/tags/{tag_id}/delete")

    with database.SessionLocal() as session:
        assert session.get(Tag, tag_id) is None


def test_remove_other_user_tag(app: Flask) -> None:
    """Test user trying to delete somebody else's tags"""
    ivan_id = make_user("ivan")
    make_user("sasho")
    game_id = make_game(make_user("studio"))

    login_as(app, "ivan").post(f"/video_games/{game_id}/tags", data={"tag": "cozy"},)

    with database.SessionLocal() as session:
        tag = session.scalar(select(Tag).where(Tag.user_id == ivan_id))
        assert tag is not None
        tag_id = tag.id

    response = login_as(app, "sasho").post(f"/tags/{tag_id}/delete")

    assert response.status_code == 403


def test_only_own_tags_visible(app: Flask) -> None:
    """Test a user can only see their own tags"""
    make_user("ivan")
    make_user("sasho")
    studio_id = make_user("studio")
    game_a = make_game(studio_id)
    game_b = make_game(studio_id)

    login_as(app, "ivan").post(f"/video_games/{game_a}/tags", data={"tag": "cozy"})
    login_as(app, "sasho").post(f"/video_games/{game_b}/tags", data={"tag": "nice"})

    response = login_as(app, "ivan").get("/tags/nice")

    assert response.status_code == 404


def test_delete_default_collection(app: Flask) -> None:
    """Test default collection can't be deleted"""
    user_id = make_user("ivan")

    with database.SessionLocal() as session:
        wishlist = session.scalar(
            select(Collection).where(
                Collection.user_id == user_id,
                Collection.default_type == DefaultCollection.WISHLIST,
            )
        )

        assert wishlist is not None
        wishlist_id = wishlist.id

    login_as(app, "ivan").post(f"/collections/{wishlist_id}/delete")

    with database.SessionLocal() as session:
        assert session.get(Collection, wishlist_id) is not None


def test_default_collection_exclusivity(app: Flask) -> None:
    """Game can only be in one of the default collections at the same time"""

    user_id = make_user("ivan")
    game_id = make_game(make_user("studio"))
    client = login_as(app, "ivan")

    with database.SessionLocal() as session:
        wishlist = session.scalar(
            select(Collection).where(
                Collection.user_id == user_id,
                Collection.default_type == DefaultCollection.WISHLIST,))

        playing = session.scalar(
            select(Collection).where(
                Collection.user_id == user_id,
                Collection.default_type == DefaultCollection.PLAYING,))

        assert wishlist is not None
        assert playing is not None

        wishlist_id = wishlist.id
        playing_id = playing.id

    client.post(f"/collections/{wishlist_id}/games", data={"game_id": game_id},)
    client.post(f"/collections/{playing_id}/games", data={"game_id": game_id},)

    with database.SessionLocal() as session:
        wishlist = session.get(Collection, wishlist_id)
        playing = session.get(Collection, playing_id)

        assert wishlist is not None
        assert playing is not None

        assert game_id not in [game.id for game in wishlist.games]
        assert game_id in [game.id for game in playing.games]


def test_delete_other_users_collection(app: Flask) -> None:
    """Test a user can't delete somebody else's collection"""
    ivan_id = make_user("ivan")
    make_user("sasho")
    login_as(app, "ivan").post("/collections", data={"name": "Roguelikes"})

    with database.SessionLocal() as session:
        collection = session.scalar(
            select(Collection).where(Collection.user_id == ivan_id,
                                     Collection.name == "Roguelikes"))
        assert collection is not None
        collection_id = collection.id

    response = login_as(app, "sasho").post(f"/collections/{collection_id}/delete")

    assert response.status_code == 403

    with database.SessionLocal() as session:
        assert session.get(Collection, collection_id) is not None


def test_friendships(app: Flask) -> None:
    """Test sending, accepting and removing a friend"""

    ivan_id = make_user("ivan")
    sasho_id = make_user("sasho")

    login_as(app, "ivan").post(f"/friends/request/{sasho_id}")

    with database.SessionLocal() as session:
        friendship = session.scalar(
            select(Friendship).where(
                Friendship.user_id == ivan_id,
                Friendship.friend_id == sasho_id,))

        assert friendship is not None
        assert friendship.status == FriendStatus.PENDING

        friendship_id = friendship.id

    login_as(app, "sasho").post(f"/friends/{friendship_id}/accept")

    with database.SessionLocal() as session:
        friendship = session.get(Friendship, friendship_id)

        assert friendship is not None
        assert friendship.status == FriendStatus.ACCEPTED

    login_as(app, "ivan").post(f"/friends/{sasho_id}/remove")

    with database.SessionLocal() as session:
        assert session.get(Friendship, friendship_id) is None


def test_accept_request_forbidden(app: Flask) -> None:
    """Test not being able to accept your own friend request"""

    ivan_id = make_user("ivan")
    sasho_id = make_user("sasho")

    ivan = login_as(app, "ivan")
    ivan.post(f"/friends/request/{sasho_id}")

    with database.SessionLocal() as session:
        friendship = session.scalar(
            select(Friendship).where(
                Friendship.user_id == ivan_id,
                Friendship.friend_id == sasho_id,
            )
        )

        assert friendship is not None
        friendship_id = friendship.id

    response = ivan.post(f"/friends/{friendship_id}/accept")

    assert response.status_code == 403


def test_crud_for_games_as_studio(app: Flask) -> None:
    """Test editing studio's own games, cannot edit somebody else's"""

    studio_a = make_user("studio_a", role=UserRoles.STUDIO)
    make_user("studio_b", role=UserRoles.STUDIO)
    game_id = make_game(studio_a)

    login_as(app, "studio_a").post(f"/video_games/{game_id}/edit", data={"title": "Renamed"},)

    forbidden_response = login_as(app, "studio_b").post(
        f"/video_games/{game_id}/edit", data={"title": "Hijacked"},)

    with database.SessionLocal() as session:
        game = session.get(VideoGame, game_id)

        assert game is not None
        assert game.title == "Renamed"

    assert forbidden_response.status_code == 403


def test_user_game_create(app: Flask) -> None:
    """Test a plain registered user cannot create a game"""
    make_user("ivan")
    client = login_as(app, "ivan")

    response = client.post("/video_games", data={"title": "New Game",
                                                 "short_description": "desc"})

    assert response.status_code == 403


def test_genre_crud_studio_admin(app: Flask) -> None:
    """Test only admin can remove genres"""

    studio_id = make_user("studio", role=UserRoles.STUDIO)
    make_user("root_admin", role=UserRoles.ADMIN)

    game_id = make_game(studio_id, genres=["Roguelike"],)

    with database.SessionLocal() as session:
        genre = session.scalar(
            select(Genre).where(Genre.name == "Roguelike"))

        assert genre is not None
        genre_id = genre.id

    studio_response = login_as(app, "studio").post(
        f"/video_games/{game_id}/genres/{genre_id}/delete")

    login_as(app, "root_admin").post(
        f"/video_games/{game_id}/genres/{genre_id}/delete")

    assert studio_response.status_code == 403

    with database.SessionLocal() as session:
        game = session.get(VideoGame, game_id)

        assert game is not None
        assert genre_id not in [genre.id for genre in game.genres]


def test_delete_other_review_studio(app: Flask) -> None:
    """Test a studio can't delete a review on a game it doesn't own"""
    studio_a = make_user("studio_a", role=UserRoles.STUDIO)
    make_user("studio_b", role=UserRoles.STUDIO)
    reviewer_id = make_user("ivan")
    game_id = make_game(studio_a)
    review_id = make_review(reviewer_id, game_id, rating=1, comment="mean review")

    response = login_as(app, "studio_b").post(
        f"/video_games/{game_id}/reviews/{review_id}/delete")

    assert response.status_code == 403

    with database.SessionLocal() as session:
        assert session.get(Review, review_id) is not None


def test_crud_friendships_as_admin(app: Flask) -> None:
    """Test admin removing friendships"""

    ivan_id = make_user("ivan")
    sasho_id = make_user("sasho")
    make_user("root_admin", role=UserRoles.ADMIN)

    login_as(app, "ivan").post(f"/friends/request/{sasho_id}")

    with database.SessionLocal() as session:
        friendship = session.scalar(
            select(Friendship).where(
                Friendship.user_id == ivan_id,
                Friendship.friend_id == sasho_id,))

        assert friendship is not None
        friendship_id = friendship.id

    login_as(app, "sasho").post(
        f"/friends/{friendship_id}/accept")

    login_as(app, "root_admin").post(
        f"/admin/users/{ivan_id}/friends/{sasho_id}/remove"
    )

    with database.SessionLocal() as session:
        assert session.get(Friendship, friendship_id) is None


def test_remove_friendship_not_admin(app: Flask) -> None:
    """Test a regular user can't remove somebody else's friend"""
    ivan_id = make_user("ivan")
    sasho_id = make_user("sasho")
    make_user("mallory")

    login_as(app, "ivan").post(f"/friends/request/{sasho_id}")

    with database.SessionLocal() as session:
        friendship = session.scalar(
            select(Friendship).where(
                Friendship.user_id == ivan_id,
                Friendship.friend_id == sasho_id,))
        assert friendship is not None
        friendship_id = friendship.id

    login_as(app, "sasho").post(f"/friends/{friendship_id}/accept")

    response = login_as(app, "mallory").post(
        f"/admin/users/{ivan_id}/friends/{sasho_id}/remove")

    assert response.status_code == 403

    with database.SessionLocal() as session:
        assert session.get(Friendship, friendship_id) is not None
