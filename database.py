"""
database.py - Database configuration and session management.

Uses SQLite with SQLAlchemy ORM.
The database file (bookings.db) is created automatically in the project root.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite database URL — file-based, no server needed
DATABASE_URL = "sqlite:///./bookings.db"

# Create the SQLAlchemy engine
# check_same_thread=False is required for SQLite with FastAPI (multi-threaded)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Each instance of SessionLocal will be a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()
