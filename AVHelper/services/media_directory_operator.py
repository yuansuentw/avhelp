"""
Media Directory Operations using fsspec
"""

from typing import List, Optional, Dict, Any
from pathlib import Path
import logging
from urllib.parse import urlparse

import fsspec
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.ftp import FTPFileSystem
from fsspec.implementations.sftp import SFTPFileSystem

from models.media_directory import MediaDirectory, PathType


logger = logging.getLogger(__name__)


class MediaDirectoryOperator:
    """媒體目錄操作類

    使用fsspec提供統一的文件系統操作接口，支援本地和遠程文件系統
    """

    def __init__(self, media_directory: MediaDirectory):
        """初始化媒體目錄操作器

        Args:
            media_directory: MediaDirectory模型實例
        """
        self.media_directory = media_directory
        self._fs: Optional[fsspec.AbstractFileSystem] = None
        self._connection_params: Dict[str, Any] = {}

    def connect(self, **kwargs) -> bool:
        """連接到媒體目錄

        Args:
            **kwargs: 連接參數，根據不同的路徑類型需要不同參數
                     - SMB: host, username, password, port等
                     - FTP: host, username, password, port等
                     - SFTP: host, username, password, port等

        Returns:
            bool: 連接是否成功
        """
        try:
            path_type = self.media_directory.path_type
            path = self.media_directory.path

            if path_type == PathType.LOCAL:
                self._fs = LocalFileSystem()
                logger.info(f"Connected to local directory: {path}")

            elif path_type == PathType.SMB:
                # SMB需要安裝smbprotocol: pip install smbprotocol
                self._fs = fsspec.filesystem('smb', **kwargs)
                logger.info(f"Connected to SMB share: {path}")

            elif path_type == PathType.FTP:
                self._fs = FTPFileSystem(**kwargs)
                logger.info(f"Connected to FTP server: {path}")

            elif path_type == PathType.SFTP:
                self._fs = SFTPFileSystem(**kwargs)
                logger.info(f"Connected to SFTP server: {path}")

            else:
                raise ValueError(f"Unsupported path type: {path_type}")

            self._connection_params = kwargs
            return True

        except Exception as e:
            logger.error(f"Failed to connect to {path_type} directory {path}: {e}")
            return False

    def list_all_files(self, extensions: Optional[List[str]] = None,
                      recursive: bool = True) -> List[str]:
        """列出目錄中的所有文件

        Args:
            extensions: 文件擴展名過濾列表，如 ['.mp4', '.avi', '.mkv']
            recursive: 是否遞歸搜索子目錄

        Returns:
            List[str]: 文件路徑列表
        """
        if not self._fs:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            path = self.media_directory.path

            if recursive:
                # 遞歸列出所有文件
                files = self._fs.find(path, detail=False)
            else:
                # 只列出當前目錄的文件
                all_items = self._fs.ls(path, detail=True)
                files = [item['name'] for item in all_items if item['type'] == 'file']

            # 過濾文件擴展名
            if extensions:
                extensions = [ext.lower() for ext in extensions]
                filtered_files = []
                for file_path in files:
                    file_ext = Path(file_path).suffix.lower()
                    if file_ext in extensions:
                        filtered_files.append(file_path)
                files = filtered_files

            logger.info(f"Found {len(files)} files in {path}")
            return files

        except Exception as e:
            logger.error(f"Failed to list files in {path}: {e}")
            raise

    def delete_file(self, file_path: str) -> bool:
        """刪除指定文件

        Args:
            file_path: 要刪除的文件路徑

        Returns:
            bool: 刪除是否成功
        """
        if not self._fs:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            # 檢查文件是否存在
            if not self._fs.exists(file_path):
                logger.warning(f"File does not exist: {file_path}")
                return False

            # 刪除文件
            self._fs.rm(file_path)
            logger.info(f"Successfully deleted file: {file_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
            return False

    def delete_files(self, file_paths: List[str]) -> Dict[str, bool]:
        """批量刪除文件

        Args:
            file_paths: 要刪除的文件路徑列表

        Returns:
            Dict[str, bool]: 每個文件的刪除結果
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.delete_file(file_path)
        return results

    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """獲取文件資訊

        Args:
            file_path: 文件路徑

        Returns:
            Optional[Dict[str, Any]]: 文件資訊字典，包含大小、修改時間等
        """
        if not self._fs:
            raise RuntimeError("Not connected. Call connect() first.")

        try:
            if not self._fs.exists(file_path):
                return None

            info = self._fs.info(file_path)
            return info

        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return None

    def disconnect(self):
        """斷開連接"""
        if hasattr(self._fs, 'close'):
            self._fs.close()
        self._fs = None
        self._connection_params = {}
        logger.info("Disconnected from media directory")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.disconnect()