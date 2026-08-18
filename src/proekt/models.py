"""Definitions of the database models used to represent the API web app data"""

from enum import Enum
from datetime import datetime, timezone
from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, String, Boolean
from sqlalchemy import DateTime, Table, Column, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from flask_login import UserMixin


class Base(DeclarativeBase):
    pass

#association table between games and genres
game_genre = Table(
        "game_genre",
        Base.metadata,
        Column("video_game_id", ForeignKey("video_game.id"), primary_key=True),
        Column("genre_id", ForeignKey("genre.id"), primary_key=True))

#association table between games and collections
collection_game = Table(
        "collection_game",
        Base.metadata,
        Column("video_game_id", ForeignKey("video_game.id"), primary_key=True),
        Column("game_collection_id", ForeignKey("game_collection.id"), primary_key=True))

class VideoGame(Base):
    """Contents of a video game"""

    __tablename__ = "video_game"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    cover_url: Mapped[str | None] = mapped_column(String(200))
    short_description: Mapped[str] = mapped_column(String(600), nullable=False)
    studio_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=False)
    genres: Mapped[list["Genre"]] = relationship(secondary=game_genre,
                                                 back_populates="games")
    collections: Mapped[list["Collection"]] = relationship(secondary=collection_game,
                                                           back_populates="games")
    tags: Mapped[list["Tag"]] = relationship(back_populates="game",
                                             cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="game",
                                                   cascade="all, delete-orphan")
    studio: Mapped["User"] = relationship(foreign_keys=[studio_id],
                                          back_populates="made_games")

class Tag(Base):
    """Contents of a game tag"""

    __tablename__ = "user_game_tag"

    __table_args__ = (UniqueConstraint("user_id", "game_id", "tag", name="uq_user_game_tag"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("video_game.id"), nullable=False)
    tag: Mapped[str] = mapped_column(String(50), nullable=False)
    user: Mapped["User"] = relationship(back_populates="tags")
    game: Mapped["VideoGame"] = relationship(back_populates="tags")

class Genre(Base):
    """Contents of a game genre"""

    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, unique=True)
    games: Mapped[list["VideoGame"]] = relationship(secondary=game_genre, back_populates="genres")

class Review(Base):
    """Contents of a game review"""

    __tablename__ = "game_review"

    __table_args__ = (UniqueConstraint("user_id", "game_id", name="uq_user_game_review"),
                      CheckConstraint("rating >= 1 AND rating <= 5", name="check_rating"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("video_game.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(400))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),
                                                 default=lambda: datetime.now(timezone.utc))
    user: Mapped["User"] = relationship(back_populates="reviews")
    game: Mapped["VideoGame"] = relationship(back_populates="reviews")


class DefaultCollection(Enum):
    """Default collections that every registered user should have,
        these collections cannot be deleted"""

    WISHLIST = "wishlist"
    PLAYING = "playing"
    COMPLETED = "completed"

class Collection(Base):
    """Contents of a game collection"""

    __tablename__ = "game_collection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_type: Mapped[DefaultCollection | None] = mapped_column(SQLEnum(DefaultCollection),
                                                                   nullable=True)
    user: Mapped["User"] = relationship(back_populates="collections")
    games: Mapped[list["VideoGame"]] = relationship(secondary=collection_game,
                                                    back_populates="collections")

class UserRoles(Enum):
    """User roles for the web application,
       a user can be either registered or a studio,
       the role admin is reserved for only one person"""

    REGISTERED_USER = "registered_user"
    STUDIO = "studio"
    ADMIN = "admin"

class User(Base, UserMixin):
    """Contents that web app users have"""

    __tablename__ = "user_account"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped["UserRoles"] = mapped_column(SQLEnum(UserRoles),
                                            nullable=False,
                                            default=UserRoles.REGISTERED_USER)
    tags: Mapped[list["Tag"]] = relationship(back_populates="user",
                                             cascade="all, delete-orphan")
    collections: Mapped[list["Collection"]] = relationship(back_populates="user",
                                                           cascade="all, delete-orphan")
    reviews: Mapped[list["Review"]] = relationship(back_populates="user",
                                                   cascade="all, delete-orphan")
    made_games: Mapped[list["VideoGame"]] = relationship(foreign_keys=[VideoGame.studio_id],
                                                         back_populates="studio")
    friendreq_sent: Mapped[list["Friendship"]] = relationship(
            foreign_keys="Friendship.user_id",
            back_populates="user")
    friendreq_accepted: Mapped[list["Friendship"]] = relationship(
            foreign_keys="Friendship.friend_id",
            back_populates="friend")

class FriendStatus(Enum):
    """Friendship status between users"""

    PENDING = "pending"
    ACCEPTED = "accepted"
    DECLINED = "declined"

class Friendship(Base):
    """Friendships between users"""

    __tablename__ = "friends"
    __table_args__ = (UniqueConstraint("user_id", "friend_id", name="uq_friendship"),
                      CheckConstraint("user_id != friend_id", name="check_not_self"))

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"), nullable=False)
    friend_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"), nullable=False)
    status: Mapped["FriendStatus"] = mapped_column(SQLEnum(FriendStatus), nullable=False)
    user: Mapped["User"] = relationship(foreign_keys=[user_id],
                                        back_populates="friendreq_sent")
    friend: Mapped["User"] = relationship(foreign_keys=[friend_id],
                                          back_populates="friendreq_accepted")
