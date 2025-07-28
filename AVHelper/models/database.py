"""
Database configuration and utilities for AVHelper
Supports both SQLite and PostgreSQL
"""

from typing import Optional
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3


# Enable JSON1 extension for SQLite
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable SQLite extensions and optimizations"""
    if isinstance(dbapi_connection, sqlite3.Connection):
        # Enable JSON1 extension
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.execute("PRAGMA temp_store=MEMORY")
        cursor.close()


class DatabaseManager:
    """Database manager for AVHelper"""
    
    def __init__(self, database_url: str):
        """
        Initialize database manager
        
        Args:
            database_url: Database connection URL
                SQLite: sqlite:///path/to/database.db
                PostgreSQL: postgresql://user:password@host:port/database
        """
        self.database_url = database_url
        self.engine = create_engine(
            database_url,
            echo=False,  # Set to True for SQL debugging
            connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
        )
    
    def create_tables(self):
        """Create all tables"""
        SQLModel.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        """Get database session"""
        return Session(self.engine)
    
    def close(self):
        """Close database connection"""
        self.engine.dispose()


# Default database path for development
DEFAULT_DB_PATH = "../Shared/DEV_DB/avhelper.sqlite"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DB_PATH}"