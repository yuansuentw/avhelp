"""
MediaDirectory model for AVHelper database
"""

from typing import Optional
from datetime import datetime
from enum import Enum
from sqlmodel import SQLModel, Field, Column, Text


class PathType(str, Enum):
    """媒體目錄路徑類型枚舉"""
    LOCAL = "local"
    SMB = "smb"
    FTP = "ftp"
    SFTP = "sftp"
    NFS = "nfs"


class MediaDirectory(SQLModel, table=True):
    """媒體目錄資訊模型

    用於追蹤和管理媒體庫目錄，支援本地和遠程文件系統
    """

    __tablename__ = "media_directory"

    id: Optional[int] = Field(default=None, primary_key=True)
    path: str = Field(max_length=500, description="目錄路徑")
    path_type: PathType = Field(description="路徑類型")
    name: Optional[str] = Field(default=None, max_length=100, description="目錄名稱")
    description: Optional[str] = Field(default=None, sa_column=Column(Text), description="目錄描述")

    # 掃描相關欄位
    last_scan_date: Optional[datetime] = Field(default=None, description="最後掃描時間")
    scan_depth: Optional[int] = Field(default=None, description="掃描深度")

    # 狀態欄位
    is_active: bool = Field(default=True, description="是否啟用")

    # 時間戳記
    created_at: datetime = Field(default_factory=datetime.now, description="創建時間")
    updated_at: Optional[datetime] = Field(default=None, description="更新時間")

    # 備註
    remark: Optional[str] = Field(default=None, sa_column=Column(Text), description="備註")

    class Config:
        """SQLModel 設定"""
        use_enum_values = True

    def __repr__(self) -> str:
        return f"<MediaDirectory(id={self.id}, path='{self.path}', type='{self.path_type}')>"