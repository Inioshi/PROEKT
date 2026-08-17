"""Planting some seeds for the database"""

from .database import SessionLocal
from .models import VideoGame, User, Genre, Tag, Review, Collection, Friendship

def plant_seeds():
    db = SessionLocal()
    return None