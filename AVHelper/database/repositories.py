"""Repository implementations for AVHelper models"""

from typing import Dict, Any, Tuple, List, Optional
from sqlmodel import Session, select, func, or_, and_
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from ..models.actress import Actress
from ..models.video import Video
from ..models.media_file import MediaFile
from .base import BaseRepository


class ActressRepository(BaseRepository[Actress]):
    """Actress 資料存取層"""
    
    def __init__(self, session: Session):
        super().__init__(session, Actress)
    
    def _apply_filters(self, statement, count_statement, filters: Dict[str, Any]):
        """應用 Actress 特定的過濾條件"""
        conditions = []
        
        # 基本過濾條件
        if filters.get('name'):
            conditions.append(Actress.name.contains(filters['name']))
        
        if filters.get('rating_min') is not None:
            conditions.append(Actress.rating >= filters['rating_min'])
        
        if filters.get('rating_max') is not None:
            conditions.append(Actress.rating <= filters['rating_max'])
        
        if filters.get('role_type'):
            conditions.append(Actress.role_type == filters['role_type'])
        
        if filters.get('face'):
            conditions.append(Actress.face == filters['face'])
        
        if filters.get('style'):
            conditions.append(Actress.style == filters['style'])
        
        if filters.get('breast'):
            conditions.append(Actress.breast == filters['breast'])
        
        # 排除已刪除的記錄
        if not filters.get('include_deleted', False):
            conditions.append(or_(Actress.is_delete.is_(None), Actress.is_delete == False))
        
        # 應用條件
        if conditions:
            combined_condition = and_(*conditions)
            statement = statement.where(combined_condition)
            count_statement = count_statement.where(combined_condition)
        
        return statement, count_statement
    
    def search_by_name(self, name: str, limit: int = 10) -> List[Actress]:
        """根據姓名搜尋 Actress"""
        statement = (
            select(Actress)
            .where(
                and_(
                    Actress.name.contains(name),
                    or_(Actress.is_delete.is_(None), Actress.is_delete == False)
                )
            )
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_by_rating_range(self, min_rating: float, max_rating: float) -> List[Actress]:
        """根據評分範圍獲取 Actress"""
        statement = (
            select(Actress)
            .where(
                and_(
                    Actress.rating >= min_rating,
                    Actress.rating <= max_rating,
                    or_(Actress.is_delete.is_(None), Actress.is_delete == False)
                )
            )
        )
        return self.session.exec(statement).all()
    
    def get_top_rated(self, limit: int = 10) -> List[Actress]:
        """獲取評分最高的 Actress"""
        statement = (
            select(Actress)
            .where(or_(Actress.is_delete.is_(None), Actress.is_delete == False))
            .order_by(Actress.rating.desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()


class VideoRepository(BaseRepository[Video]):
    """Video 資料存取層"""
    
    def __init__(self, session: Session):
        super().__init__(session, Video)
    
    def _apply_filters(self, statement, count_statement, filters: Dict[str, Any]):
        """應用 Video 特定的過濾條件"""
        conditions = []
        
        # 基本過濾條件
        if filters.get('id_series'):
            conditions.append(Video.idSeries.contains(filters['id_series']))
        
        if filters.get('title'):
            conditions.append(Video.title.contains(filters['title']))
        
        if filters.get('actress_name'):
            conditions.append(Video.actress_name.contains(filters['actress_name']))
        
        if filters.get('actress_id'):
            conditions.append(Video.actressID == filters['actress_id'])
        
        if filters.get('rating_min') is not None:
            conditions.append(Video.rating >= filters['rating_min'])
        
        if filters.get('rating_max') is not None:
            conditions.append(Video.rating <= filters['rating_max'])
        
        if filters.get('is_downloaded') is not None:
            conditions.append(Video.isDownloaded == filters['is_downloaded'])
        
        if filters.get('pub_date_from'):
            conditions.append(Video.pubDate >= filters['pub_date_from'])
        
        if filters.get('pub_date_to'):
            conditions.append(Video.pubDate <= filters['pub_date_to'])
        
        if filters.get('duration_min'):
            conditions.append(Video.duration >= filters['duration_min'])
        
        if filters.get('duration_max'):
            conditions.append(Video.duration <= filters['duration_max'])
        
        # 排除已忽略的記錄
        if not filters.get('include_ignored', False):
            conditions.append(or_(Video.isIgnore.is_(None), Video.isIgnore == False))
        
        # 應用條件
        if conditions:
            combined_condition = and_(*conditions)
            statement = statement.where(combined_condition)
            count_statement = count_statement.where(combined_condition)
        
        return statement, count_statement
    
    def search_by_title(self, title: str, limit: int = 10) -> List[Video]:
        """根據標題搜尋 Video"""
        statement = (
            select(Video)
            .where(
                and_(
                    Video.title.contains(title),
                    or_(Video.isIgnore.is_(None), Video.isIgnore == False)
                )
            )
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_by_actress(self, actress_id: int, limit: int = 20) -> List[Video]:
        """根據女優 ID 獲取 Video"""
        statement = (
            select(Video)
            .where(
                and_(
                    Video.actressID == actress_id,
                    or_(Video.isIgnore.is_(None), Video.isIgnore == False)
                )
            )
            .order_by(Video.pubDate.desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_by_series(self, series_id: str, limit: int = 20) -> List[Video]:
        """根據系列 ID 獲取 Video"""
        statement = (
            select(Video)
            .where(
                and_(
                    Video.idSeries == series_id,
                    or_(Video.isIgnore.is_(None), Video.isIgnore == False)
                )
            )
            .order_by(Video.pubDate.desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_downloaded(self, limit: int = 50) -> List[Video]:
        """獲取已下載的 Video"""
        statement = (
            select(Video)
            .where(
                and_(
                    Video.isDownloaded == True,
                    or_(Video.isIgnore.is_(None), Video.isIgnore == False)
                )
            )
            .order_by(Video.downloadDate.desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_recent_added(self, limit: int = 20) -> List[Video]:
        """獲取最近添加的 Video"""
        statement = (
            select(Video)
            .where(or_(Video.isIgnore.is_(None), Video.isIgnore == False))
            .order_by(Video.addDate.desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_top_rated(self, limit: int = 10) -> List[Video]:
        """獲取評分最高的 Video"""
        statement = (
            select(Video)
            .where(
                and_(
                    Video.rating.is_not(None),
                    or_(Video.isIgnore.is_(None), Video.isIgnore == False)
                )
            )
            .order_by(Video.rating.desc())
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def get_statistics(self) -> Dict[str, Any]:
        """獲取 Video 統計資訊"""
        # 總數
        total_count = self.session.exec(
            select(func.count(Video.id))
            .where(or_(Video.isIgnore.is_(None), Video.isIgnore == False))
        ).one()
        
        # 已下載數量
        downloaded_count = self.session.exec(
            select(func.count(Video.id))
            .where(
                and_(
                    Video.isDownloaded == True,
                    or_(Video.isIgnore.is_(None), Video.isIgnore == False)
                )
            )
        ).one()
        
        # 平均評分
        avg_rating = self.session.exec(
            select(func.avg(Video.rating))
            .where(
                and_(
                    Video.rating.is_not(None),
                    or_(Video.isIgnore.is_(None), Video.isIgnore == False)
                )
            )
        ).one()
        
        return {
            'total_count': total_count,
            'downloaded_count': downloaded_count,
            'download_percentage': (downloaded_count / total_count * 100) if total_count > 0 else 0,
            'average_rating': float(avg_rating) if avg_rating else 0.0
        }


class MediaFileRepository(BaseRepository[MediaFile]):
    """MediaFile 資料存取層"""
    
    def __init__(self, session: Session):
        super().__init__(session, MediaFile)
    
    def _apply_filters(self, statement, count_statement, filters: Dict[str, Any]):
        """應用 MediaFile 特定的過濾條件"""
        conditions = []
        
        # 基本過濾條件
        if filters.get('media_directory'):
            conditions.append(MediaFile.media_directory == filters['media_directory'])
        
        if filters.get('video_id'):
            conditions.append(MediaFile.video_id == filters['video_id'])
        
        if filters.get('init_filename'):
            conditions.append(MediaFile.init_filename.contains(filters['init_filename']))
        
        if filters.get('normalized_name'):
            conditions.append(MediaFile.normalized_name.contains(filters['normalized_name']))
        
        if filters.get('resolution'):
            conditions.append(MediaFile.resolution == filters['resolution'])
        
        if filters.get('size_min') is not None:
            conditions.append(MediaFile.size >= filters['size_min'])
        
        if filters.get('size_max') is not None:
            conditions.append(MediaFile.size <= filters['size_max'])
        
        # 排除已刪除的記錄
        if not filters.get('include_deleted', False):
            conditions.append(MediaFile.deleted == False)
        
        # 應用條件
        if conditions:
            combined_condition = and_(*conditions)
            statement = statement.where(combined_condition)
            count_statement = count_statement.where(combined_condition)
        
        return statement, count_statement
    
    def add_or_get_existing(self, file_data: Dict[str, Any]) -> MediaFile:
        """添加媒體檔案，自動處理重複檔案情況
        
        Args:
            file_data: 檔案資料字典
            
        Returns:
            MediaFile: 新建立或現有的MediaFile記錄
        """
        try:
            media_file = MediaFile(**file_data)
            self.session.add(media_file)
            self.session.flush()  # 觸發before_insert事件計算signature
            return media_file
        except IntegrityError:
            self.session.rollback()
            # 查找現有記錄
            if 'abs_path' in file_data:
                try:
                    hash_info = MediaFile.calculate_file_hashes(file_data['abs_path'])
                    existing = self.session.exec(
                        select(MediaFile).where(
                            MediaFile.file_signature == hash_info['file_signature']
                        )
                    ).first()
                    if existing:
                        # 更新檔案路徑（處理檔案移動情況）
                        existing.abs_path = file_data['abs_path']
                        return existing
                except (FileNotFoundError, PermissionError, OSError):
                    pass
            raise  # 重新拋出其他類型的IntegrityError
    
    def find_by_signature(self, file_signature: str) -> Optional[MediaFile]:
        """根據檔案signature查找記錄"""
        statement = select(MediaFile).where(
            and_(
                MediaFile.file_signature == file_signature,
                MediaFile.deleted == False
            )
        )
        return self.session.exec(statement).first()
    
    def find_by_partial_hash(self, head_hash: str, tail_hash: Optional[str], size: int) -> List[MediaFile]:
        """根據partial hash和檔案大小查找可能重複的檔案"""
        conditions = [
            MediaFile.head_hash == head_hash,
            MediaFile.size == size,
            MediaFile.deleted == False
        ]
        
        if tail_hash:
            conditions.append(MediaFile.tail_hash == tail_hash)
        else:
            conditions.append(MediaFile.tail_hash.is_(None))
        
        statement = select(MediaFile).where(and_(*conditions))
        return self.session.exec(statement).all()
    
    def find_by_path(self, abs_path: str) -> Optional[MediaFile]:
        """根據絕對路徑查找記錄"""
        statement = select(MediaFile).where(
            and_(
                MediaFile.abs_path == abs_path,
                MediaFile.deleted == False
            )
        )
        return self.session.exec(statement).first()
    
    def get_files_without_signature(self, limit: int = 100) -> List[MediaFile]:
        """獲取尚未計算signature的檔案記錄"""
        statement = (
            select(MediaFile)
            .where(
                and_(
                    MediaFile.file_signature.is_(None),
                    MediaFile.deleted == False
                )
            )
            .limit(limit)
        )
        return self.session.exec(statement).all()
    
    def update_file_hashes(self, media_file: MediaFile, hash_info: Dict[str, Any]) -> MediaFile:
        """更新檔案的hash資訊"""
        media_file.head_hash = hash_info['head_hash']
        media_file.tail_hash = hash_info['tail_hash']
        media_file.file_signature = hash_info['file_signature']
        media_file.hash_chunk_size = hash_info['hash_chunk_size']
        
        self.session.add(media_file)
        self.session.commit()
        self.session.refresh(media_file)
        return media_file