"""
Database connection and session management.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import sys

# Add parent directory to path to import models
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.models import Base

# Database file path
DB_PATH = os.path.join(os.path.dirname(__file__), 'server.db')
DATABASE_URL = f'sqlite:///{DB_PATH}'

# Global engine (singleton)
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            echo=False,  # Set to True for SQL query logging during development
            connect_args={"check_same_thread": False}  # Needed for SQLite
        )
    return _engine


def get_session_factory():
    """Get or create the session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


@contextmanager
def get_session():
    """
    Context manager for database sessions.

    Usage:
        with get_session() as session:
            # do database operations
            session.commit()

    Automatically handles session cleanup and rollback on errors.
    """
    SessionLocal = get_session_factory()
    session = SessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def init_db():
    """
    Initialize the database by creating all tables defined in models.
    Safe to call multiple times - only creates tables that don't exist.
    """
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
    print(f"Database initialized at {DB_PATH}")
