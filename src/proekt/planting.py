"""Planting some seeds for the database"""

from sqlalchemy import select
from werkzeug.security import generate_password_hash

from proekt.database import SessionLocal
from proekt.models import (VideoGame, User, UserRoles, Genre, Tag,
                     Review, Collection, Friendship,
                     DefaultCollection, FriendStatus)

def plant_genres(session):
    """Populating the database with genres"""

    genres = ["RPG", "Horror", "Adventure", "Action", "Co-op",
              "FPS", "Sports", "Single-player", "Indie", "Puzzle"]

    for genre in genres:
        exists = session.scalar(select(Genre).where(Genre.name == genre))
        if exists is None:
            session.add(Genre(name=genre))

    session.flush()

def plant_users(session):
    """Populating the database with users"""

    users = [
        {"username": "gamer_bg", "password_hash": "1234", "role": UserRoles.REGISTERED_USER},
        {"username": "RENo1Fan", "password_hash": "1234", "role": UserRoles.REGISTERED_USER},
        {"username": "Capcom", "password_hash": "1234", "role": UserRoles.STUDIO},
        {"username": "KONAMI", "password_hash": "1234", "role": UserRoles.STUDIO},
        {"username": "admin", "password_hash": "1234", "role": UserRoles.ADMIN},
    ]

    for user in users:
        exists = session.scalar(select(User).where(User.username == user["username"]))
        if exists is None:
            session.add(User(username=user["username"],
                              password_hash=generate_password_hash(user["password_hash"]),
                              role=user["role"]))

    session.flush()

def plant_games(session):
    """Populating the database with games"""

    games = [
        {
            "title": "Resident Evil Requiem",
            "studio": "Capcom",
            "cover_url": "https://cdn.mobygames.com/covers/21305841-resident-evil-requiem-windows-front-cover.jpg",
            "genres": ["Action", "Single-player"],
            "short_description": 
                    "A new era of survival horror arrives with Resident Evil Requiem, " \
                    "the latest and most immersive entry yet in the iconic Resident Evil series. " \
                    "Experience terrifying survival horror with FBI analyst Grace Ashcroft, " \
                    "and dive into pulse-pounding action with legendary agent Leon S. Kennedy. " \
                    "Both of their journeys and unique gameplay styles intertwine into a " \
                    "heart-stopping, emotional experience that will chill you to your core."
        },
        {
            "title": "Silent Hill 2",
            "studio": "KONAMI",
            "cover_url": "https://upload.wikimedia.org/wikipedia/ru/c/c1/Silent_Hill_2_remake_cover.jpg?utm_source=ru.wikipedia.org&utm_campaign=index&utm_content=original",
            "genres": ["Horror", "Puzzle", "Single-player"],
            "short_description":
                    "Having received a letter from his deceased wife, "\
                    "James heads to where they shared so many memories, "\
                    "in the hope of seeing her one more time: Silent Hill. "\
                    "There, by the lake, he finds a woman eerily similar to her..."\
                    "\"My name… is Maria,\" the woman smiles. Her face, her voice... "\
                    "She's just like her. Experience a master-class in psychological"\
                    " horror―lauded as the best in the series―on the latest hardware"\
                    " with chilling visuals and visceral sounds."
        }]

    for game in games:
        exists = session.scalar(select(VideoGame).where(VideoGame.title == game["title"]))
        studio = session.scalar(select(User).where(User.username == game["studio"]))
        genre_lst = session.scalars(select(Genre).where(Genre.name.in_(game["genres"]))).all()

        if exists is None:
            session.add(VideoGame(title=game["title"],
                                  cover_url=game["cover_url"],
                                  short_description=game["short_description"],
                                  studio_id=studio.id,
                                  genres=list(genre_lst)))

    session.flush()

def plant_reviews(session):
    """Populating the database with reviews"""

    reviews = [
        {"user": "gamer_bg", "game": "Silent Hill 2", "rating": 5,
         "comment": "I'm so fucking scared rn."},
        {"user": "RENo1Fan", "game": "Resident Evil Requiem", "rating": 5,
         "comment": "I liek game. :)"},
        {"user": "RENo1Fan", "game": "Silent Hill 2", "rating": 3,
         "comment": "I don't liek game. :("},]

    for review in reviews:
        user = session.scalar(select(User).where(User.username == review["user"]))
        game = session.scalar(select(VideoGame).where(VideoGame.title == review["game"]))

        if user is None or game is None:
            continue

        exists = session.scalar(
            select(Review).where(Review.user_id == user.id, Review.game_id == game.id))
        if exists is None:
            session.add(Review(user_id=user.id, game_id=game.id,
                               rating=review["rating"], comment=review["comment"]))

    session.flush()

def plant_collections(session):
    """Populating the database with user collections"""

    default_names = {
        DefaultCollection.WISHLIST: "Wishlist",
        DefaultCollection.PLAYING: "Playing",
        DefaultCollection.COMPLETED: "Completed",
    }
    users = session.scalars(select(User)).all()

    for user in users:
        for default_type, name in default_names.items():
            exists = session.scalar(
                select(Collection).where(Collection.user_id == user.id,
                                          Collection.default_type == default_type))
            if exists is None:
                session.add(Collection(user_id=user.id, name=name,
                                       is_default=True, default_type=default_type))

        if user.username == "RENo1Fan":
            exists = session.scalar(select(Collection).where(Collection.user_id == user.id,
                                                             Collection.name == "Resi Games"))
            if exists is None:
                session.add(Collection(user_id=user.id, name="Resi Games",
                                       is_default=False, default_type=None))

    session.flush()

def plant_collection_games(session):
    """Add games to user collections."""

    user = session.scalar(select(User).where(User.username == "RENo1Fan"))
    collection = session.scalar(select(Collection).where(Collection.user_id == user.id,
                                                         Collection.name == "Resi Games"))
    game = session.scalar(select(VideoGame).where(VideoGame.title == "Resident Evil Requiem"))
    if game not in collection.games:
        collection.games.append(game)

    session.flush()

def plant_tags(session):
    """Populating the database with user tags"""

    tags = [
        {"user": "gamer_bg", "game": "Silent Hill 2", "tag": "love it!"},
        {"user": "RENo1Fan", "game": "Resident Evil Requiem", "tag": "tuff"}]

    for tag in tags:
        user = session.scalar(select(User).where(User.username == tag["user"]))
        game = session.scalar(select(VideoGame).where(VideoGame.title == tag["game"]))

        if user is None or game is None:
            continue

        exists = session.scalar(
            select(Tag).where(Tag.user_id == user.id,
                              Tag.game_id == game.id,
                              Tag.tag == tag["tag"]))
        if exists is None:
            session.add(Tag(user_id=user.id, game_id=game.id, tag=tag["tag"]))

    session.flush()

def plant_friendship(session):
    """Populating the database with friendships"""

    friendships = [{"user": "gamer_bg", "friend": "RENo1Fan", "status": FriendStatus.ACCEPTED}]

    for friendship in friendships:
        user = session.scalar(select(User).where(User.username == friendship["user"]))
        friend = session.scalar(select(User).where(User.username == friendship["friend"]))

        if user is None or friend is None:
            continue

        exists = session.scalar(select(Friendship).where(Friendship.user_id == user.id,
                                                         Friendship.friend_id == friend.id))
        if exists is None:
            session.add(Friendship(user_id=user.id, friend_id=friend.id,
                                   status=friendship["status"]))

    session.flush()

def plant_in_database():
    """Populating the database"""

    with SessionLocal() as session:
        with session.begin():
            plant_genres(session)
            plant_users(session)
            plant_collections(session)
            plant_collection_games(session)
            plant_games(session)
            plant_tags(session)
            plant_reviews(session)
            plant_friendship(session)

if __name__ == "__main__":
    plant_in_database()
