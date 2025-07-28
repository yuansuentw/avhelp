"""
Media model for AVHelper database
"""

from typing import Dict, Any, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Column
from ..database import get_json_column


class Media(SQLModel, table=True):
    """媒體檔案資訊模型"""
    
    __tablename__ = "media"
    
    # 主鍵
    id: Optional[int] = Field(default=None, primary_key=True)
    
    # 路徑相關欄位
    media_directory: Optional[int] = Field(default=None, foreign_key="media_directory.id", description="關聯的媒體目錄ID")
    abs_path: str = Field(max_length=1000, description="絕對檔案路徑")
    
    # 關聯欄位
    video_id: Optional[str] = Field(default=None, foreign_key="video.id", max_length=60, description="關聯的影片ID")
    
    # 檔案資訊
    init_filename: str = Field(max_length=300, description="原始檔案名稱")
    normalized_name: Optional[str] = Field(default=None, max_length=300, description="標準化檔案名稱")
    size: Optional[int] = Field(default=None, description="檔案大小(bytes)")
    resolution: Optional[str] = Field(default=None, max_length=20, description="影片解析度(如1920x1080)")
    
    # 狀態欄位
    is_ignore_rename: bool = Field(default=False, description="是否忽略重新命名")
    deleted: bool = Field(default=False, description="是否已刪除")
    delete_meta: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column("delete_meta", get_json_column(), nullable=True),
        description="刪除相關的元數據(JSON)"
    )
    
    # 時間戳記
    download_dt: Optional[datetime] = Field(default=None, description="下載時間")
    add_dt: datetime = Field(default_factory=datetime.now, description="新增時間")

    class Config:
        """SQLModel configuration"""
        arbitrary_types_allowed = True

    def __repr__(self) -> str:
        return f"<Media(id={self.id}, filename='{self.init_filename}', video_id='{self.video_id}')>"