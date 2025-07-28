"""Database factory for creating repository instances"""

from typing import Optional
from sqlmodel import Session

from .session import DatabaseSession, get_database_session
from .repositories import ActressRepository, VideoRepository


class DatabaseFactory:
    """資料庫工廠類別，用於創建 Repository 實例"""
    
    def __init__(self, db_session: Optional[DatabaseSession] = None):
        self.db_session = db_session or get_database_session()
    
    def create_actress_repository(self, session: Optional[Session] = None) -> ActressRepository:
        """創建 ActressRepository 實例"""
        if session:
            return ActressRepository(session)
        return ActressRepository(self.db_session.get_raw_session())
    
    def create_video_repository(self, session: Optional[Session] = None) -> VideoRepository:
        """創建 VideoRepository 實例"""
        if session:
            return VideoRepository(session)
        return VideoRepository(self.db_session.get_raw_session())
    
    def with_session(self, session: Session) -> 'SessionBoundFactory':
        """創建綁定特定會話的工廠"""
        return SessionBoundFactory(session)


class SessionBoundFactory:
    """綁定特定會話的工廠"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create_actress_repository(self) -> ActressRepository:
        """創建 ActressRepository 實例"""
        return ActressRepository(self.session)
    
    def create_video_repository(self) -> VideoRepository:
        """創建 VideoRepository 實例"""
        return VideoRepository(self.session)


# 全域工廠實例
_factory = None


def get_database_factory() -> DatabaseFactory:
    """獲取全域資料庫工廠實例"""
    global _factory
    if _factory is None:
        _factory = DatabaseFactory()
    return _factory


def create_repositories_with_session(session: Session) -> SessionBoundFactory:
    """使用指定會話創建 Repository 工廠"""
    return SessionBoundFactory(session)