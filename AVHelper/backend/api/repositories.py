"""Repository layer for database operations"""

from typing import List, Optional, Tuple
from sqlmodel import Session, select, func
from datetime import datetime

from models.actress import Actress
from models.video import Video
from .schema.actress import ActressFilter
from .schema.video import VideoFilter


class ActressRepository:
    """Repository for Actress model operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, actress_id: int) -> Optional[Actress]:
        """根據 ID 獲取 Actress"""
        return self.session.get(Actress, actress_id)
    
    def get_all(
        self, 
        page: int = 1, 
        page_size: int = 20, 
        filters: Optional[ActressFilter] = None
    ) -> Tuple[List[Actress], int]:
        """獲取所有 Actress，支援分頁和過濾"""
        query = select(Actress)
        
        # 應用過濾條件
        if filters:
            if filters.name:
                query = query.where(Actress.name.contains(filters.name))
            if filters.rating:
                query = query.where(Actress.rating == filters.rating)
            if filters.role_type:
                query = query.where(Actress.role_type == filters.role_type)
            if filters.is_delete is not None:
                query = query.where(Actress.is_delete == filters.is_delete)
        
        # 計算總數
        total_count = self.session.exec(select(func.count()).select_from(query.subquery())).one()
        
        # 應用分頁
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        actresses = self.session.exec(query).all()
        return list(actresses), total_count
    
    def create(self, actress_data: dict) -> Actress:
        """創建新的 Actress"""
        actress_data['data_date'] = datetime.now()
        actress_data['update_date'] = datetime.now()
        actress = Actress(**actress_data)
        self.session.add(actress)
        self.session.commit()
        self.session.refresh(actress)
        return actress
    
    def update(self, actress_id: int, actress_data: dict) -> Optional[Actress]:
        """更新 Actress"""
        actress = self.get_by_id(actress_id)
        if not actress:
            return None
        
        actress_data['update_date'] = datetime.now()
        for key, value in actress_data.items():
            if hasattr(actress, key) and value is not None:
                setattr(actress, key, value)
        
        self.session.add(actress)
        self.session.commit()
        self.session.refresh(actress)
        return actress
    
    def delete(self, actress_id: int) -> bool:
        """軟刪除 Actress"""
        actress = self.get_by_id(actress_id)
        if not actress:
            return False
        
        actress.is_delete = True
        actress.update_date = datetime.now()
        self.session.add(actress)
        self.session.commit()
        return True


class VideoRepository:
    """Repository for Video model operations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, video_id: str) -> Optional[Video]:
        """根據 ID 獲取 Video"""
        return self.session.get(Video, video_id)
    
    def get_all(
        self, 
        page: int = 1, 
        page_size: int = 20, 
        filters: Optional[VideoFilter] = None
    ) -> Tuple[List[Video], int]:
        """獲取所有 Video，支援分頁和過濾"""
        query = select(Video)
        
        # 應用過濾條件
        if filters:
            if filters.id_series:
                query = query.where(Video.idSeries.contains(filters.id_series))
            if filters.id_number:
                query = query.where(Video.idNumber.contains(filters.id_number))
            if filters.dmm_id:
                query = query.where(Video.dmmID == filters.dmm_id)
            if filters.javdb_id:
                query = query.where(Video.javdbID == filters.javdb_id)
            if filters.title:
                query = query.where(Video.title.contains(filters.title))
            if filters.actress_name:
                query = query.where(Video.actress_name.contains(filters.actress_name))
            if filters.actress_id:
                query = query.where(Video.actressID == filters.actress_id)
            if filters.is_downloaded is not None:
                query = query.where(Video.isDownloaded == filters.is_downloaded)
            if filters.is_ignore is not None:
                query = query.where(Video.isIgnore == filters.is_ignore)
            if filters.rating_min is not None:
                query = query.where(Video.rating >= filters.rating_min)
            if filters.rating_max is not None:
                query = query.where(Video.rating <= filters.rating_max)
        
        # 計算總數
        total_count = self.session.exec(select(func.count()).select_from(query.subquery())).one()
        
        # 應用分頁
        offset = (page - 1) * page_size
        query = query.offset(offset).limit(page_size)
        
        videos = self.session.exec(query).all()
        return list(videos), total_count
    
    def create(self, video_data: dict) -> Video:
        """創建新的 Video"""
        video_data['addDate'] = datetime.now()
        video = Video(**video_data)
        self.session.add(video)
        self.session.commit()
        self.session.refresh(video)
        return video
    
    def update(self, video_id: str, video_data: dict) -> Optional[Video]:
        """更新 Video"""
        video = self.get_by_id(video_id)
        if not video:
            return None
        
        for key, value in video_data.items():
            if hasattr(video, key) and value is not None:
                setattr(video, key, value)
        
        self.session.add(video)
        self.session.commit()
        self.session.refresh(video)
        return video
    
    def delete(self, video_id: str) -> bool:
        """軟刪除 Video"""
        video = self.get_by_id(video_id)
        if not video:
            return False
        
        video.isIgnore = True
        video.deleteDate = datetime.now()
        self.session.add(video)
        self.session.commit()
        return True