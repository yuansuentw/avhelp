"""
Posts model for AVHelper database (formerly nyaa_post)
Flexible JSON-based structure for multi-source compatibility
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import JSONB
import os


def get_json_column():
    """Get appropriate JSON column type based on database URL"""
    db_url = os.getenv("DATABASE_URL", "sqlite://")
    if "postgresql" in db_url:
        return JSONB
    return JSON


class Post(SQLModel, table=True):
    """Posts from various sources (Nyaa, etc.) with flexible JSON data structure"""

    __tablename__ = "posts"

    id: int = Field(primary_key=True, description="Auto-increment primary key")
    post_id: str = Field(max_length=64, description="Unique post identifier (char 64)", unique=True)
    source: str = Field(max_length=20, description="Source identifier (nyaa, other_tracker)")
    videoid: Optional[str] = Field(default=None, max_length=100, description="Video identifier extracted from data")
    data: Dict[str, Any] = Field(
        sa_column=Column(
            "data",
            get_json_column(),
            nullable=False
        ),
        description="Flexible JSON data containing all source-specific fields"
    )
    data_time: datetime = Field(default_factory=datetime.utcnow, description="Data creation timestamp")
    last_update: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        """SQLModel configuration"""
        arbitrary_types_allowed = True


# Legacy field mapping for migration reference
LEGACY_NYAA_FIELDS = {
    "category": "str",
    "title": "str", 
    "torrent_url": "str",
    "magnet": "str",
    "size": "str",
    "pub_time": "datetime",
    "hash": "str",
    "URL": "str", 
    "submitter": "str",
    "grab_time": "datetime",
    "video_quality": "int",
    "info": "str"
    # Note: videoid moved to fixed column
}