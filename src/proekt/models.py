"""Definitions of the database models used to represent the API web app data"""

from enum import Enum
from sqlalchemy import Enum as SQLEnum, ForeignKey, Integer, String, Table, Column
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


#association table for Many-To-Many relationships
assoc_game_genre = Table("game_genre",
                        Base.metadata,
                        Column("video_game_id", ForeignKey("video_game.id"), primary_key=True),
                        Column("genre_id", ForeignKey("genre.id"), primary_key=True))


class VideoGame(Base):
    """Model for video games"""

    __tablename__ = "video_game"

    title: Mapped[str] = mapped_column(String(50), nullable=False)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    short_description: Mapped[str] = mapped_column(String(400), nullable=False)
    studio_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"), nullable=False)
    #rating will be calculated

    genres: Mapped[list["Genre"]] = relationship(secondary=assoc_game_genre, back_populates="games")
    tags: Mapped[list["Tag"]] = relationship()
    studio: Mapped["User"] = relationship()
    reviews: Mapped[list["Review"]] = relationship()

class Tag(Base):
    """Model for user video game tags"""

    __tablename__ = "user_game_tag"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user_account.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("video_game.id"), nullable=False)
    game_tag: Mapped[str] = mapped_column(String(50), nullable=False)

    user: Mapped["User"] = relationship()
    game: Mapped["VideoGame"] = relationship()


class Genre(Base):
    """Model for video game genres"""

    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False)
    games: Mapped[list["VideoGame"]] = relationship(secondary=assoc_game_genre,
                                                    back_populates="genres")


class Review(Base):
    """Model for video game reviews"""

    __tablename__ = "game_review"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"), nullable=False)
    game_id: Mapped[int] = mapped_column(Integer, ForeignKey("video_game.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(400))

    user: Mapped["User"] = relationship()
    game: Mapped["VideoGame"] = relationship()

class Collection(Base):
    """Model for video game collections"""

    __tablename__ = "game_collection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user_account.id"))
    name: Mapped[str] = mapped_column(String(50))
    games: Mapped[list[str] | None] = mapped_column()


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
    password: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[UserRoles] = mapped_column(SQLEnum(UserRoles),
                                            nullable=False,
                                            default=UserRoles.REGISTERED_USER)
    default_collections: Mapped[Collection] = mapped_column()
    collections: Mapped[Collection] = mapped_column()
    tags: Mapped[str] = mapped_column()
    reviews: Mapped[list["Review"]] = mapped_column()
    friends_list: Mapped[list[str] | None] = mapped_column()
    made_games: Mapped[list["VideoGame"]] = relationship() # only if user is a studio/admin
