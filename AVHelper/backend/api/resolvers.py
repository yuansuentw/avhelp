"""GraphQL resolvers for AVHelper API"""

from typing import List, Optional
import strawberry
from strawberry.types import Info
from sqlmodel import Session

from models.database import DatabaseManager
from .repositories import ActressRepository, VideoRepository
from .schema import (
    ActressType, ActressInput, ActressFilter,
    VideoType, VideoInput, VideoFilter,
    PaginationInfo, PaginatedResult
)


# 創建具體的分頁結果類型
@strawberry.type
class ActressPaginatedResult:
    """分頁的 Actress 結果"""
    items: List[ActressType]
    pagination: PaginationInfo


@strawberry.type
class VideoPaginatedResult:
    """分頁的 Video 結果"""
    items: List[VideoType]
    pagination: PaginationInfo


def get_db_session() -> Session:
    """獲取數據庫會話"""
    # 這裡應該從依賴注入或上下文中獲取
    # 暫時使用默認配置
    from models.database import DEFAULT_DATABASE_URL
    db_manager = DatabaseManager(DEFAULT_DATABASE_URL)
    return db_manager.get_session()


def actress_to_type(actress) -> ActressType:
    """將 Actress 模型轉換為 GraphQL 類型"""
    return ActressType(
        id=actress.id,
        name=actress.name,
        rating=actress.rating,
        face=actress.face,
        style=actress.style,
        breast=actress.breast,
        waist=actress.waist,
        legs=actress.legs,
        body=actress.body,
        hair=actress.hair,
        features=actress.features,
        role_type=actress.role_type,
        common=actress.common,
        is_delete=actress.is_delete,
        data_date=actress.data_date,
        update_date=actress.update_date,
        alias=actress.alias
    )


def video_to_type(video) -> VideoType:
    """將 Video 模型轉換為 GraphQL 類型"""
    return VideoType(
        id=video.id,
        id_series=video.idSeries,
        id_number=video.idNumber,
        dmm_id=video.dmmID,
        javdb_id=video.javdbID,
        pub_date=video.pubDate,
        duration=video.duration,
        title=video.title,
        actress_name=video.actress_name,
        actress_id=video.actressID,
        rating=video.rating,
        is_downloaded=video.isDownloaded,
        is_ignore=video.isIgnore,
        add_date=video.addDate,
        download_date=video.downloadDate,
        delete_date=video.deleteDate,
        delete_reason=video.deleteReason,
        remark=video.remark
    )


@strawberry.type
class Query:
    """GraphQL 查詢"""
    
    @strawberry.field
    def actress(self, id: int) -> Optional[ActressType]:
        """根據 ID 獲取單個 Actress"""
        with get_db_session() as session:
            repo = ActressRepository(session)
            actress = repo.get_by_id(id)
            return actress_to_type(actress) if actress else None
    
    @strawberry.field
    def actresses(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[ActressFilter] = None
    ) -> ActressPaginatedResult:
        """獲取 Actress 列表，支援分頁和過濾"""
        with get_db_session() as session:
            repo = ActressRepository(session)
            actresses, total_count = repo.get_all(page, page_size, filters)
            
            actress_types = [actress_to_type(actress) for actress in actresses]
            pagination = PaginationInfo.create(total_count, page, page_size)
            
            return ActressPaginatedResult(
                items=actress_types,
                pagination=pagination
            )
    
    @strawberry.field
    def video(self, id: str) -> Optional[VideoType]:
        """根據 ID 獲取單個 Video"""
        with get_db_session() as session:
            repo = VideoRepository(session)
            video = repo.get_by_id(id)
            return video_to_type(video) if video else None
    
    @strawberry.field
    def videos(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[VideoFilter] = None
    ) -> VideoPaginatedResult:
        """獲取 Video 列表，支援分頁和過濾"""
        with get_db_session() as session:
            repo = VideoRepository(session)
            videos, total_count = repo.get_all(page, page_size, filters)
            
            video_types = [video_to_type(video) for video in videos]
            pagination = PaginationInfo.create(total_count, page, page_size)
            
            return VideoPaginatedResult(
                items=video_types,
                pagination=pagination
            )


@strawberry.type
class Mutation:
    """GraphQL 變更"""
    
    @strawberry.mutation
    def create_actress(self, input: ActressInput) -> ActressType:
        """創建新的 Actress"""
        with get_db_session() as session:
            repo = ActressRepository(session)
            actress_data = {
                k: v for k, v in input.__dict__.items() 
                if v is not None
            }
            actress = repo.create(actress_data)
            return actress_to_type(actress)
    
    @strawberry.mutation
    def update_actress(self, id: int, input: ActressInput) -> Optional[ActressType]:
        """更新 Actress"""
        with get_db_session() as session:
            repo = ActressRepository(session)
            actress_data = {
                k: v for k, v in input.__dict__.items() 
                if v is not None
            }
            actress = repo.update(id, actress_data)
            return actress_to_type(actress) if actress else None
    
    @strawberry.mutation
    def delete_actress(self, id: int) -> bool:
        """刪除 Actress（軟刪除）"""
        with get_db_session() as session:
            repo = ActressRepository(session)
            return repo.delete(id)
    
    @strawberry.mutation
    def create_video(self, input: VideoInput) -> VideoType:
        """創建新的 Video"""
        with get_db_session() as session:
            repo = VideoRepository(session)
            video_data = {
                # 映射字段名稱
                'id': input.id,
                'idSeries': input.id_series,
                'idNumber': input.id_number,
                'dmmID': input.dmm_id,
                'javdbID': input.javdb_id,
                'pubDate': input.pub_date,
                'duration': input.duration,
                'title': input.title,
                'actress_name': input.actress_name,
                'actressID': input.actress_id,
                'rating': input.rating,
                'isDownloaded': input.is_downloaded,
                'isIgnore': input.is_ignore,
                'deleteReason': input.delete_reason,
                'remark': input.remark
            }
            # 移除 None 值
            video_data = {k: v for k, v in video_data.items() if v is not None}
            video = repo.create(video_data)
            return video_to_type(video)
    
    @strawberry.mutation
    def update_video(self, id: str, input: VideoInput) -> Optional[VideoType]:
        """更新 Video"""
        with get_db_session() as session:
            repo = VideoRepository(session)
            video_data = {
                # 映射字段名稱
                'idSeries': input.id_series,
                'idNumber': input.id_number,
                'dmmID': input.dmm_id,
                'javdbID': input.javdb_id,
                'pubDate': input.pub_date,
                'duration': input.duration,
                'title': input.title,
                'actress_name': input.actress_name,
                'actressID': input.actress_id,
                'rating': input.rating,
                'isDownloaded': input.is_downloaded,
                'isIgnore': input.is_ignore,
                'deleteReason': input.delete_reason,
                'remark': input.remark
            }
            # 移除 None 值
            video_data = {k: v for k, v in video_data.items() if v is not None}
            video = repo.update(id, video_data)
            return video_to_type(video) if video else None
    
    @strawberry.mutation
    def delete_video(self, id: str) -> bool:
        """刪除 Video（軟刪除）"""
        with get_db_session() as session:
            repo = VideoRepository(session)
            return repo.delete(id)