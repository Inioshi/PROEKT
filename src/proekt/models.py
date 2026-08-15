"""Definitions of the database models used to represent the API web app data"""

from enum import Enum
from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, String, Table, Column, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


#association table between games and genres
assoc_game_genre = Table("game_genre",
                        Base.metadata,
                        Column("video_game_id", ForeignKey("video_game.id"), primary_key=True),
                        Column("genre_id", ForeignKey("genre.id"), primary_key=True))


#association table between games and collections
assoc_game_collection = Table("game_collection",
                        Base.metadata,
                        Column("video_game_id", ForeignKey("video_game.id"), primary_key=True),
                        Column("game_collection_id", ForeignKey("game_collection.id"), primary_key=True))


class VideoGame(Base):
    """Model for video games"""

    __tablename__ = "video_game"

    title: Mapped[str] = mapped_column(String(50), nullable=False)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_description: Mapped[str] = mapped_column(String(400), nullable=False)

    cover_url: Mapped[str | None] = mapped_column(String(500)) #?
    #rating will be calculated

    studio_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=False)
    studio: Mapped["User"] = relationship(back_populates="made_games")

    genres: Mapped[list["Genre"]] = relationship(secondary=assoc_game_genre, back_populates="games")
    tags: Mapped[list["Tag"]] = relationship(back_populates="game", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="game", cascade="all, delete-orphan") #every written review for the game

    collections: Mapped[list["Collection"]] = relationship(secondary=assoc_game_collection, back_populates="games")

class Tag(Base):
    """Model for user video game tags"""

    __tablename__ = "user_game_tag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("video_game.id"), nullable=False)

    game_tag: Mapped[str] = mapped_column(String(50), nullable=False)

    user: Mapped["User"] = relationship(back_populates="tags")
    game: Mapped["VideoGame"] = relationship(back_populates="tags")


class Genre(Base):
    """Model for video game genres"""

    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    games: Mapped[list["VideoGame"]] = relationship(secondary=assoc_game_genre,
                                                    back_populates="genres")


class Review(Base):
    """Model for video game reviews"""

    __tablename__ = "game_review"

    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_game_review"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("video_game.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(400))

    user: Mapped["User"] = relationship(back_populates="reviews", cascade="all, delete-orphan" )
    game: Mapped["VideoGame"] = relationship(back_populates="reviews", cascade="all, delete-orphan")


class Collection(Base):
    """Model for video game collections"""

    __tablename__ = "game_collection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)

    user: Mapped["User"] = relationship(back_populates="collections")
    games: Mapped[list["VideoGame"] | None] = relationship(secondary=assoc_game_collection, back_populates="collections")


class UserRoles(Enum):
    """User roles"""

    REGISTERED_USER = "registered_user"
    STUDIO = "studio"
    ADMIN = "admin"

class User(Base):
    """Model for web app users"""

    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[UserRoles] = mapped_column(SQLEnum(UserRoles),
                                            nullable=False,
                                            default=UserRoles.REGISTERED_USER)

    tags: Mapped[list["Tag"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    collections: Mapped[list["Collection"] | None] = relationship(back_populates="user", cascade="all, delete-orphan")
    reviews: Mapped[list["Review"] | None] = relationship(back_populates="user", cascade="all, delete-orphan")
    friends_list: Mapped[list["User"] | None] = relationship()
    made_games: Mapped[list["VideoGame"]] = relationship() # only if user is a studio/admin

class Friendship(Base):
    pass