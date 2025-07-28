"""
Series model for AVHelper database
"""

from typing import Dict, Any, Optional
from sqlmodel import SQLModel, Field, Column
from ..database import get_json_column


class Series(SQLModel, table=True):
    """系列資訊模型"""
    
    __tablename__ = "series"
    
    # 主鍵
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 系列識別碼 (關聯到Video.idSeries)
    series_id: str = Field(max_length=30, unique=True, description="系列唯一識別碼")
    
    # 影片ID模式匹配
    video_id_pattern: Optional[str] = Field(default=None, max_length=100, description="影片ID匹配模式(regex)")
    
    # 來源資訊
    vendor: Optional[str] = Field(default=None, max_length=50, description="廠商/製作商")
    websource_order: Optional[int] = Field(default=None, description="網路來源優先順序")
    
    # 元數據
    meta: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column("meta", get_json_column(), nullable=True),
        description="系列相關元數據(JSON)"
    )

    class Config:
        """SQLModel configuration"""
        arbitrary_types_allowed = True

    def __repr__(self) -> str:
        return f"<Series(id={self.id}, series_id='{self.series_id}', vendor='{self.vendor}')>"