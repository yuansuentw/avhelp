"""
GraphQL schema for Video model using Strawberry
"""

from typing import Optional
from datetime import datetime, time
import strawberry


@strawberry.type
class VideoType:
    """GraphQL type for Video model"""
    
    id: str
    id_series: Optional[str] = None
    id_number: Optional[str] = None
    dmm_id: Optional[str] = None
    javdb_id: Optional[str] = None
    pub_date: Optional[datetime] = None
    duration: Optional[time] = None
    title: Optional[str] = None
    actress_name: Optional[str] = None
    actress_id: Optional[str] = None
    rating: Optional[float] = None
    is_downloaded: Optional[bool] = None
    is_ignore: Optional[bool] = None
    add_date: Optional[datetime] = None
    download_date: Optional[datetime] = None
    delete_date: Optional[datetime] = None
    delete_reason: Optional[str] = None
    remark: Optional[str] = None


@strawberry.input
class VideoInput:
    """GraphQL input type for creating/updating Video"""
    
    id: str
    id_series: Optional[str] = None
    id_number: Optional[str] = None
    dmm_id: Optional[str] = None
    javdb_id: Optional[str] = None
    pub_date: Optional[datetime] = None
    duration: Optional[time] = None
    title: Optional[str] = None
    actress_name: Optional[str] = None
    actress_id: Optional[str] = None
    rating: Optional[float] = None
    is_downloaded: Optional[bool] = None
    is_ignore: Optional[bool] = None
    add_date: Optional[datetime] = None
    download_date: Optional[datetime] = None
    delete_date: Optional[datetime] = None
    delete_reason: Optional[str] = None
    remark: Optional[str] = None


@strawberry.input
class VideoFilter:
    """GraphQL input type for filtering Videos"""
    
    id_series: Optional[str] = None
    id_number: Optional[str] = None
    dmm_id: Optional[str] = None
    javdb_id: Optional[str] = None
    title: Optional[str] = None
    actress_name: Optional[str] = None
    actress_id: Optional[str] = None
    is_downloaded: Optional[bool] = None
    is_ignore: Optional[bool] = None
    rating_min: Optional[float] = None
    rating_max: Optional[float] = None