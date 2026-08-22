"""Configurates the SQLite database, engine and database session"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

DB_URL = "sqlite:///goodgames-database.db"

engine = create_engine(DB_URL, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base.metadata.create_all(engine)
