"""
Trends model for AVHelper database (formerly nyaa_post_trends)
Flexible JSON-based structure for tracking statistics over time
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from ..database import get_json_column


class Trend(SQLModel, table=True):
    """Trend statistics for posts with flexible JSON data structure"""

    __tablename__ = "trends"

    id: int = Field(primary_key=True)
    post_id: str = Field(foreign_key="posts.post_id", max_length=64, description="Reference to posts table (char 64)")
    trend_data: Dict[str, Any] = Field(
        sa_column=Column(
            "trend_data", 
            get_json_column(),
            nullable=False
        ),
        description="Flexible JSON data containing trend statistics"
    )
    data_time: datetime = Field(default_factory=datetime.utcnow, description="Data timestamp")

    class Config:
        """SQLModel configuration"""
        arbitrary_types_allowed = True


# Legacy field mapping for migration reference
LEGACY_TRENDS_FIELDS = {
    "seeder": "int",
    "leecher": "int", 
    "complete": "int",
    "data_time": "datetime"
}