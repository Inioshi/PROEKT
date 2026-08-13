"""Definitions of the database models used to represent the API web app data"""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass

class VideoGame(Base):
    """Model for video games"""

    __tablename__ = "video_game"

    title: Mapped[str] = mapped_column(String(50))
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    genres: Mapped[list["Genre"]] = relationship()
    short_description: Mapped[str] = mapped_column(String(200))
    studio: Mapped[str] = mapped_column(ForeignKey("user_account.id"))
    rating: Mapped[float] = mapped_column(Integer)
    tags: Mapped[str] = mapped_column(ForeignKey("user_account.id"))


class Genre(Base):
    """Model for video game genres"""

    __tablename__ = "genre"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20))
    rating: Mapped[int] = mapped_column(Integer)

class Review(Base):
    """Model for video game reviews"""

    __tablename__ = "game_review"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"))
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("video_game.id"))
    rating: Mapped[int] = mapped_column(Integer)
    comment: Mapped[str | None] = mapped_column(String(400))

class Collection(Base):
    """Model for video game collections"""

    __tablename__ = "game_collection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"))
    name: Mapped[str] = mapped_column(String(50))
    games: Mapped[list[str] | None] = mapped_column()

class User(Base):
    """Model for web app users"""

    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(20))
    password: Mapped[str] = mapped_column(String(20))
    role: Mapped[str]
    default_collections: Mapped[Collection] = mapped_column()
    collections: Mapped[Collection] = mapped_column()
    tags: Mapped[str] = mapped_column()
    reviews: Mapped[list[str]] = mapped_column()
    friends_list: Mapped[list[str] | None] = mapped_column()

