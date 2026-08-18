"""Planting some seeds for the database"""

from sqlalchemy import select
from .database import SessionLocal
from .models import VideoGame, User, UserRoles, Genre, Tag, Review, Collection, Friendship

def plant_genres(session):
    genres = ["RPG", "Horror", "Adventure", "Action", "Co-op",
              "FPS", "Sports", "Single-player", "Indie", "Strategy"]

    for genre in genres:
        exists = session.scalar(select(Genre).where(Genre.name == genre))

        if exists is None:
            session.add(Genre(name=genre))

    session.flush()

def plant_users(session):
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
            session.add(User(**user))

    session.flush()

def plant_games(session):
    games = [
        {
            "title": "Resident Evil Requiem",
            "studio": "Capcom",
            "cover_url": "https://cdn.mobygames.com/covers/21305841-resident-evil-requiem-windows-front-cover.jpg",
            "short_description": 
                    "A new era of survival horror arrives with Resident Evil Requiem," \
                    "the latest and most immersive entry yet in the iconic Resident Evil series." \
                    "Experience terrifying survival horror with FBI analyst Grace Ashcroft," \
                    "and dive into pulse-pounding action with legendary agent Leon S. Kennedy." \
                    "Both of their journeys and unique gameplay styles intertwine into a" \
                    "heart-stopping, emotional experience that will chill you to your core."
        },
        {
            "title": "Silent Hill 2",
            "studio": "KONAMI",
            "cover_url": "https://upload.wikimedia.org/wikipedia/ru/c/c1/Silent_Hill_2_remake_cover.jpg?utm_source=ru.wikipedia.org&utm_campaign=index&utm_content=original",
            "short_description":
                    "Having received a letter from his deceased wife,"\
                    "James heads to where they shared so many memories,"\
                    "in the hope of seeing her one more time: Silent Hill."\
                    "There, by the lake, he finds a woman eerily similar to her..."\
                    "\"My name… is Maria,\" the woman smiles. Her face, her voice... She's just like her."\
                    "Experience a master-class in psychological horror―lauded as the best in "\
                    "the series―on the latest hardware with chilling visuals and visceral sounds."
        }]

    for game in games:
        exist = session.scalar(select(VideoGame).where(VideoGame.title == game["title"]))

        studio = session.scalar(select(User).where(User.username == game["studio"]))

        if exist is None:
            session.add(VideoGame(title=game["title"],
                                  cover_url=game["cover_url"],
                                  short_description=game["short_description"],
                                  studio_id=studio.id))

    session.flush()

def plant_reviews(session):
    pass

def plant_collections(session):
    pass

def plant_tags(session):
    pass

def plant_friendship(session):
    pass

def plant_in_database():
    with SessionLocal() as session:
        with session.begin():
            plant_genres(session)
            plant_users(session)
            plant_collections(session)
            plant_games(session)
            plant_tags(session)
            plant_reviews(session)
            plant_friendship(session)

if __name__ == "__main__":
    plant_in_database()