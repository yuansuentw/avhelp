"""Database session management for AVHelper"""

from contextlib import contextmanager
from typing import Generator, Optional
from sqlmodel import SQLModel, Session, create_engine
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


class DatabaseSession:
    """資料庫會話管理器"""
    
    def __init__(self, database_url: str = DEFAULT_DATABASE_URL):
        self.db_manager = DatabaseManager(database_url)
        # 確保資料表已建立
        self.db_manager.create_tables()
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """獲取資料庫會話的上下文管理器"""
        session = self.db_manager.get_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def get_raw_session(self) -> Session:
        """獲取原始資料庫會話（需要手動管理）"""
        return self.db_manager.get_session()


# 全域資料庫會話實例
_db_session = None


def get_database_session() -> DatabaseSession:
    """獲取全域資料庫會話實例"""
    global _db_session
    if _db_session is None:
        _db_session = DatabaseSession()
    return _db_session


def set_database_url(database_url: str) -> None:
    """設定資料庫 URL（重新初始化會話）"""
    global _db_session
    _db_session = DatabaseSession(database_url)