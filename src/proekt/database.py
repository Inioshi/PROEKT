"""Configurates the SQLite database, engine and database session"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .models import Base

DB_URL = "sqlite:///goodgames-database.db"

#remember- turn echo off when final product is done
engine = create_engine(DB_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False)

#this creates all tables in the models file
Base.metadata.create_all(engine)
