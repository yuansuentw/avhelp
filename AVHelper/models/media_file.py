"""
MediaFile model for AVHelper database
"""

import hashlib
import os
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import UniqueConstraint, event
from sqlmodel import Column, Field, SQLModel

from ..database import get_json_column

class MediaFile(SQLModel, table=True):
    """媒體檔案資訊模型"""

    __tablename__ = "media_file"
    __table_args__ = (
        UniqueConstraint('file_signature', name='uq_media_file_signature'),
    )

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

    # 檔案識別欄位
    file_signature: Optional[str] = Field(default=None, max_length=64, unique=True, description="檔案唯一識別碼")
    head_hash: Optional[str] = Field(default=None, max_length=64, description="檔案頭部hash(前1MB或完整檔案)")
    tail_hash: Optional[str] = Field(default=None, max_length=64, description="檔案尾部hash(後1MB)")
    hash_algorithm: str = Field(default="sha256", max_length=20, description="Hash演算法")
    hash_chunk_size: Optional[int] = Field(default=None, description="Hash計算chunk大小(bytes)")

    # 時間戳記
    download_dt: Optional[datetime] = Field(default=None, description="下載時間")
    add_dt: datetime = Field(default_factory=datetime.now, description="新增時間")

    class Config:
        """SQLModel configuration"""
        arbitrary_types_allowed = True

    @staticmethod
    def calculate_file_hashes(file_path: str) -> Dict[str, Any]:
        """計算檔案hash資訊
        
        Args:
            file_path: 檔案絕對路徑
            
        Returns:
            包含hash資訊的字典：{
                'head_hash': str,
                'tail_hash': Optional[str], 
                'file_signature': str,
                'hash_chunk_size': int
            }
        """
        CHUNK_SIZE = 1048576  # 1MB
        MIN_SIZE_FOR_PARTIAL = 2097152  # 2MB
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        file_size = os.path.getsize(file_path)
        
        if file_size < MIN_SIZE_FOR_PARTIAL:
            # 小於2MB：完整檔案hash
            with open(file_path, 'rb') as f:
                content = f.read()
                full_hash = hashlib.sha256(content).hexdigest()
            
            return {
                'head_hash': full_hash,
                'tail_hash': None,
                'file_signature': full_hash,
                'hash_chunk_size': file_size
            }
        else:
            # 大於等於2MB：頭尾各1MB hash
            with open(file_path, 'rb') as f:
                # 讀取頭部1MB
                head_data = f.read(CHUNK_SIZE)
                head_hash = hashlib.sha256(head_data).hexdigest()
                
                # 讀取尾部1MB
                f.seek(-CHUNK_SIZE, 2)
                tail_data = f.read(CHUNK_SIZE)
                tail_hash = hashlib.sha256(tail_data).hexdigest()
                
                # 組合signature
                signature_data = f"{file_size}:{head_hash}:{tail_hash}"
                file_signature = hashlib.sha256(signature_data.encode()).hexdigest()
            
            return {
                'head_hash': head_hash,
                'tail_hash': tail_hash,
                'file_signature': file_signature,
                'hash_chunk_size': CHUNK_SIZE
            }

    def __repr__(self) -> str:
        return f"<MediaFile(id={self.id}, filename='{self.init_filename}', signature='{self.file_signature[:8] if self.file_signature else None}...')>"


# SQLAlchemy事件監聽器：自動計算檔案signature
@event.listens_for(MediaFile, 'before_insert')
def auto_calculate_file_signature(mapper, connection, target):
    """插入前自動計算檔案signature"""
    if target.file_signature is None and target.abs_path:
        try:
            hash_info = MediaFile.calculate_file_hashes(target.abs_path)
            target.head_hash = hash_info['head_hash']
            target.tail_hash = hash_info['tail_hash']
            target.file_signature = hash_info['file_signature']
            target.hash_chunk_size = hash_info['hash_chunk_size']
        except (FileNotFoundError, PermissionError, OSError) as e:
            # Fallback: 使用路徑+大小作為識別
            fallback_data = f"{target.abs_path}:{target.size or 0}"
            target.file_signature = hashlib.md5(fallback_data.encode()).hexdigest()
            target.hash_chunk_size = target.size or 0