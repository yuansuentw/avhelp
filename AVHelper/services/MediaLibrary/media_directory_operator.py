"""
Media Directory Operations using fsspec
"""

from typing import List, Optional, Dict, Any, Callable
from pathlib import Path
import logging
import time
from urllib.parse import urlparse

import fsspec
from fsspec.implementations.local import LocalFileSystem
from fsspec.implementations.ftp import FTPFileSystem
from fsspec.implementations.sftp import SFTPFileSystem

from ...models.media_directory import MediaDirectory, PathType
from ...models.media import Media


logger = logging.getLogger(__name__)


class MediaDirectoryOperator:
    """媒體目錄操作類

    使用fsspec提供統一的文件系統操作接口，支援本地和遠程文件系統
    """
    
    # 預設支援的媒體檔案格式（大小寫不敏感）
    DEFAULT_MEDIA_EXTENSIONS = [
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', 
        '.webm', '.m4v', '.ts', '.rmvb'
    ]
    
    # 遠程連接配置
    DEFAULT_TIMEOUT = 30  # 默認連接逾時（秒）
    DEFAULT_RETRY_COUNT = 3  # 默認重試次數
    RETRY_DELAY = 2  # 重試間隔（秒）

    def __init__(self, media_directory: MediaDirectory, 
                 connection_timeout: int = DEFAULT_TIMEOUT,
                 retry_count: int = DEFAULT_RETRY_COUNT):
        """初始化媒體目錄操作器

        Args:
            media_directory: MediaDirectory模型實例
            connection_timeout: 連接逾時時間（秒）
            retry_count: 連接失敗重試次數
        """
        self.media_directory = media_directory
        self.connection_timeout = connection_timeout
        self.retry_count = retry_count
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
        path_type = self.media_directory.path_type
        path = self.media_directory.path
        
        # 本地目錄不需要重試機制
        if path_type == PathType.LOCAL:
            try:
                self._fs = LocalFileSystem()
                logger.info(f"Connected to local directory: {path}")
                self._connection_params = kwargs
                return True
            except Exception as e:
                logger.error(f"Failed to connect to local directory {path}: {e}")
                return False
        
        # 遠程連接使用重試機制
        last_exception = None
        for attempt in range(1, self.retry_count + 1):
            try:
                logger.info(f"Attempting to connect to {path_type} directory {path} (attempt {attempt}/{self.retry_count})")
                
                # 為不同類型的遠程連接設置逾時參數
                connection_kwargs = kwargs.copy()
                if path_type in [PathType.FTP, PathType.SFTP]:
                    connection_kwargs.setdefault('timeout', self.connection_timeout)
                
                if path_type == PathType.SMB:
                    # SMB需要安裝smbprotocol: pip install smbprotocol
                    self._fs = fsspec.filesystem('smb', **connection_kwargs)
                elif path_type == PathType.FTP:
                    self._fs = FTPFileSystem(**connection_kwargs)
                elif path_type == PathType.SFTP:
                    self._fs = SFTPFileSystem(**connection_kwargs)
                else:
                    raise ValueError(f"Unsupported path type: {path_type}")
                
                # 測試連接是否真正有效
                self._test_connection()
                
                logger.info(f"Successfully connected to {path_type} directory: {path}")
                self._connection_params = kwargs
                return True
                
            except Exception as e:
                last_exception = e
                logger.warning(f"Connection attempt {attempt} failed: {e}")
                
                if attempt < self.retry_count:
                    logger.info(f"Retrying in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"All {self.retry_count} connection attempts failed for {path_type} directory {path}")
        
        if last_exception:
            logger.error(f"Final connection error: {last_exception}")
        
        return False
    
    def _test_connection(self):
        """測試連接有效性
        
        Raises:
            Exception: 當連接無效時拋出異常
        """
        if not self._fs:
            raise RuntimeError("File system not initialized")
        
        path = self.media_directory.path
        
        try:
            # 嘗試列出目錄內容來測試連接
            self._fs.ls(path, detail=False)
            logger.debug(f"Connection test successful for path: {path}")
        except Exception as e:
            logger.error(f"Connection test failed for path {path}: {e}")
            raise

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

        return self._retry_operation(self._list_files_internal, extensions, recursive)
    
    def _list_files_internal(self, extensions: Optional[List[str]], recursive: bool) -> List[str]:
        """內部文件列表方法，供重試機制使用"""
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
    
    def _retry_operation(self, operation, *args, **kwargs):
        """為遠程操作提供重試機制
        
        Args:
            operation: 要執行的操作函數
            *args: 操作函數的位置參數
            **kwargs: 操作函數的關鍵字參數
            
        Returns:
            操作函數的回傳值
            
        Raises:
            最後一次操作的異常
        """
        # 本地文件系統不需要重試
        if self.media_directory.path_type == PathType.LOCAL:
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                logger.error(f"Local operation failed: {e}")
                raise
        
        # 遠程文件系統使用重試機制
        last_exception = None
        for attempt in range(1, self.retry_count + 1):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Remote operation attempt {attempt} failed: {e}")
                
                if attempt < self.retry_count:
                    logger.info(f"Retrying remote operation in {self.RETRY_DELAY} seconds...")
                    time.sleep(self.RETRY_DELAY)
                else:
                    logger.error(f"All {self.retry_count} remote operation attempts failed")
        
        if last_exception:
            raise last_exception

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
            return self._retry_operation(self._get_file_info_internal, file_path)
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            return None
    
    def _get_file_info_internal(self, file_path: str) -> Optional[Dict[str, Any]]:
        """內部文件資訊獲取方法，供重試機制使用"""
        if not self._fs.exists(file_path):
            return None

        info = self._fs.info(file_path)
        return info

    def scan_and_create_media_objects(self, 
                                    extensions: Optional[List[str]] = None, 
                                    recursive: bool = True,
                                    progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[Media]:
        """掃描目錄並為每個檔案建立Media物件
        
        重用現有的list_all_files和get_file_info方法來掃描檔案，
        並為每個檔案建立Media物件實例（不包含資料庫操作）
        
        Args:
            extensions: 文件擴展名過濾列表，如 ['.mp4', '.avi', '.mkv']
                       如果為None，則使用DEFAULT_MEDIA_EXTENSIONS中定義的預設格式
            recursive: 是否遞歸搜索子目錄
            progress_callback: 進度回饋callback函數，接收參數：(current_index, total_files, current_file_path)
            
        Returns:
            List[Media]: Media物件列表
            
        Raises:
            RuntimeError: 當未連接到文件系統時
        """
        if not self._fs:
            raise RuntimeError("Not connected. Call connect() first.")
        
        try:
            # 如果未指定extensions，使用預設媒體格式
            if extensions is None:
                extensions = self.DEFAULT_MEDIA_EXTENSIONS
                logger.debug(f"Using default media extensions: {extensions}")
            
            # 使用現有方法列出所有文件
            file_paths = self.list_all_files(extensions=extensions, recursive=recursive)
            total_files = len(file_paths)
            logger.info(f"Found {total_files} files to process")
            
            media_objects = []
            
            for current_index, file_path in enumerate(file_paths, start=1):
                try:
                    # 呼叫進度回饋callback
                    if progress_callback:
                        try:
                            progress_callback(current_index, total_files, file_path)
                        except Exception as callback_error:
                            logger.warning(f"Progress callback error: {callback_error}")
                            # 回調錯誤不應中斷主處理流程
                    
                    # 使用現有方法獲取文件資訊
                    file_info = self.get_file_info(file_path)
                    
                    if file_info is None:
                        logger.warning(f"Skipping file {file_path}: unable to get file info")
                        continue
                    
                    # 從文件路徑提取檔案名稱
                    filename = Path(file_path).name
                    
                    # 創建Media物件
                    media = Media(
                        media_directory=self.media_directory.id,
                        abs_path=file_path,
                        init_filename=filename,
                        size=file_info.get('size'),
                        # 設置添加時間為當前時間
                        # add_dt 會使用 default_factory=datetime.now 自動設置
                    )
                    
                    media_objects.append(media)
                    logger.debug(f"Created Media object for {filename} ({current_index}/{total_files})")
                    
                except Exception as e:
                    logger.error(f"Failed to create Media object for {file_path}: {e}")
                    # 繼續處理其他文件，不中斷整個掃描過程
                    continue
            
            logger.info(f"Successfully created {len(media_objects)} Media objects out of {total_files} files")
            return media_objects
            
        except Exception as e:
            logger.error(f"Failed to scan and create media objects: {e}")
            raise

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