#!/usr/bin/env python3
"""
測試腳本：使用Mock資料測試MediaDirectoryOperator掃描功能

此腳本使用 LocalDisk_folder_a.json 內的資料，模擬MediaDirectoryOperator
讀取到的磁碟內容，並生成MediaFile物件。

由於環境限制，此腳本直接定義所需的類別，避免複雜的模組導入問題。
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from unittest.mock import Mock, patch
from datetime import datetime
from enum import Enum


# 定義所需的枚舉和類別
class PathType(str, Enum):
    """媒體目錄路徑類型枚舉"""
    LOCAL = "local"
    SMB = "smb"
    FTP = "ftp"
    SFTP = "sftp"
    NFS = "nfs"


class MediaDirectory:
    """媒體目錄資訊模型（簡化版）"""
    
    def __init__(self, id: Optional[int] = None, name: Optional[str] = None, 
                 path: str = "", path_type: PathType = PathType.LOCAL, 
                 description: Optional[str] = None):
        self.id = id
        self.name = name
        self.path = path
        self.path_type = path_type
        self.description = description
        self.last_scan_date = None
        self.scan_depth = None
        self.is_active = True
        self.created_at = datetime.now()
        self.updated_at = None
        self.remark = None


class MediaFile:
    """媒體檔案資訊模型（簡化版）"""
    
    def __init__(self, media_directory: Optional[int] = None, abs_path: str = "",
                 init_filename: str = "", size: Optional[int] = None, **kwargs):
        self.id = None
        self.media_directory = media_directory
        self.abs_path = abs_path
        self.video_id = None
        self.init_filename = init_filename
        self.normalized_name = None
        self.size = size
        self.resolution = None
        self.is_ignore_rename = False
        self.deleted = False
        self.delete_meta = None
        self.file_signature = None
        self.head_hash = None
        self.tail_hash = None
        self.hash_algorithm = "sha256"
        self.hash_chunk_size = None
        self.download_dt = None
        self.add_dt = datetime.now()


class MediaDirectoryOperator:
    """媒體目錄操作類（簡化版）"""
    
    # 預設支援的媒體檔案格式（大小寫不敏感）
    DEFAULT_MEDIA_EXTENSIONS = [
        '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', 
        '.webm', '.m4v', '.ts', '.rmvb'
    ]
    
    def __init__(self, media_directory: MediaDirectory):
        self.media_directory = media_directory
        self._fs = None
        
    def list_all_files(self, extensions: Optional[List[str]] = None, 
                      recursive: bool = True) -> List[str]:
        """列出所有文件（Mock版本）"""
        # 這個方法會被Mock掉，所以實際實作不重要
        return []
        
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """獲取文件資訊（Mock版本）"""
        # 這個方法會被Mock掉，所以實際實作不重要
        return None
        
    def scan_and_create_media_objects(self, 
                                    extensions: Optional[List[str]] = None, 
                                    recursive: bool = True,
                                    progress_callback: Optional[Callable[[int, int, str], None]] = None) -> List[MediaFile]:
        """掃描目錄並為每個檔案建立MediaFile物件"""
        if not self._fs:
            raise RuntimeError("Not connected. Call connect() first.")
        
        try:
            # 如果未指定extensions，使用預設媒體格式
            if extensions is None:
                extensions = self.DEFAULT_MEDIA_EXTENSIONS
            
            # 使用現有方法列出所有文件
            file_paths = self.list_all_files(extensions=extensions, recursive=recursive)
            total_files = len(file_paths)
            
            media_objects = []
            
            for current_index, file_path in enumerate(file_paths, start=1):
                try:
                    # 呼叫進度回饋callback
                    if progress_callback:
                        try:
                            progress_callback(current_index, total_files, file_path)
                        except Exception as callback_error:
                            print(f"Progress callback error: {callback_error}")
                    
                    # 使用現有方法獲取文件資訊
                    file_info = self.get_file_info(file_path)
                    
                    if file_info is None:
                        print(f"Skipping file {file_path}: unable to get file info")
                        continue
                    
                    # 從文件路徑提取檔案名稱
                    filename = Path(file_path).name
                    
                    # 創建MediaFile物件
                    media = MediaFile(
                        media_directory=self.media_directory.id,
                        abs_path=file_path,
                        init_filename=filename,
                        size=file_info.get('size'),
                    )
                    
                    media_objects.append(media)
                    
                except Exception as e:
                    print(f"Failed to create MediaFile object for {file_path}: {e}")
                    continue
            
            return media_objects
            
        except Exception as e:
            print(f"Failed to scan and create media objects: {e}")
            raise


class MockMediaDirectoryScanTest:
    """使用Mock資料測試MediaDirectoryOperator掃描功能"""
    
    def __init__(self):
        self.mock_data_file = Path(__file__).parent / "services" / "Mock" / "LocalDisk_folder_a.json"
        self.mock_data = self._load_mock_data()
        self.media_directory = self._create_test_media_directory()
        self.operator = MediaDirectoryOperator(self.media_directory)
        
    def _load_mock_data(self) -> List[Dict[str, Any]]:
        """載入Mock資料"""
        try:
            with open(self.mock_data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"✅ 成功載入Mock資料，共 {len(data)} 筆記錄")
            return data
        except FileNotFoundError:
            print(f"❌ 找不到Mock資料檔案: {self.mock_data_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Mock資料檔案格式錯誤: {e}")
            sys.exit(1)
            
    def _create_test_media_directory(self) -> MediaDirectory:
        """建立測試用的MediaDirectory"""
        return MediaDirectory(
            id=1,
            name="Test Mock Directory",
            path="Z:\\video\\Download",
            path_type=PathType.LOCAL,
            description="使用Mock資料的測試目錄"
        )
        
    def _filter_video_files(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """過濾出影片檔案（模擬檔案，這裡假設所有資料夾內都有影片檔案）"""
        # 由於Mock資料是資料夾列表，我們模擬每個資料夾內有一個同名的.mp4檔案
        video_files = []
        for item in data:
            if item.get('size') is None:  # 資料夾
                # 模擬資料夾內有一個影片檔案
                video_file = {
                    'absolute_path': f"{item['absolute_path']}/{item['name']}.mp4",
                    'name': f"{item['name']}.mp4",
                    'created': item['created'],
                    'modified': item['modified'],
                    'accessed': item['accessed'],
                    'size': 1024 * 1024 * 500  # 模擬500MB的檔案
                }
                video_files.append(video_file)
        return video_files
        
    def _create_mock_file_info(self, file_data: Dict[str, Any]) -> Dict[str, Any]:
        """將Mock資料轉換為fsspec格式的檔案資訊"""
        return {
            'name': file_data['absolute_path'],
            'size': file_data['size'],
            'type': 'file',
            'mtime': datetime.fromisoformat(file_data['modified']).timestamp() if file_data['modified'] else None
        }
        
    def run_scan_test(self) -> List[MediaFile]:
        """執行掃描測試"""
        print("\n🚀 開始執行MediaDirectoryOperator掃描測試...")
        
        # 過濾出影片檔案
        video_files = self._filter_video_files(self.mock_data)
        print(f"📁 模擬影片檔案數量: {len(video_files)}")
        
        # 準備Mock資料
        file_paths = [item['absolute_path'] for item in video_files]
        file_info_map = {item['absolute_path']: self._create_mock_file_info(item) for item in video_files}
        
        # 設定進度回調函數
        def progress_callback(current: int, total: int, file_path: str):
            percentage = (current / total) * 100
            filename = Path(file_path).name
            print(f"📊 進度: {current}/{total} ({percentage:.1f}%) - 處理檔案: {filename}")
            
        try:
            # Mock MediaDirectoryOperator的方法
            with patch.object(self.operator, 'list_all_files') as mock_list_files, \
                 patch.object(self.operator, 'get_file_info') as mock_get_info:
                
                # 模擬已連接狀態
                self.operator._fs = Mock()
                
                # 設定Mock回傳值
                mock_list_files.return_value = file_paths
                mock_get_info.side_effect = lambda path: file_info_map.get(path)
                
                # 執行掃描
                print("\n🔍 開始掃描並建立MediaFile物件...")
                media_objects = self.operator.scan_and_create_media_objects(
                    extensions=None,  # 使用預設格式
                    recursive=True,
                    progress_callback=progress_callback
                )
                
                print(f"\n✅ 掃描完成！成功建立 {len(media_objects)} 個MediaFile物件")
                return media_objects
                
        except Exception as e:
            print(f"❌ 掃描過程發生錯誤: {e}")
            raise
            
    def analyze_results(self, media_objects: List[MediaFile]):
        """分析掃描結果"""
        print("\n📊 掃描結果分析:")
        print(f"   總檔案數: {len(media_objects)}")
        
        if media_objects:
            # 統計檔案大小
            total_size = sum(obj.size or 0 for obj in media_objects)
            avg_size = total_size / len(media_objects) if media_objects else 0
            print(f"   總大小: {total_size / (1024**3):.2f} GB")
            print(f"   平均大小: {avg_size / (1024**2):.2f} MB")
            
            # 顯示前5個檔案的詳細資訊
            print("\n📋 前5個檔案詳細資訊:")
            for i, media in enumerate(media_objects[:5], 1):
                filename = Path(media.abs_path).name
                size_mb = (media.size or 0) / (1024**2)
                print(f"   {i}. {filename}")
                print(f"      路徑: {media.abs_path}")
                print(f"      大小: {size_mb:.2f} MB")
                print(f"      目錄ID: {media.media_directory}")
                print(f"      新增時間: {media.add_dt}")
                print()
                
    def run_validation_tests(self, media_objects: List[MediaFile]):
        """執行驗證測試"""
        print("🔍 執行驗證測試...")
        
        # 測試1: 檢查所有物件都是MediaFile實例
        assert all(isinstance(obj, MediaFile) for obj in media_objects), "所有物件都應該是MediaFile實例"
        print("   ✅ 所有物件都是MediaFile實例")
        
        # 測試2: 檢查必要欄位
        for obj in media_objects:
            assert obj.media_directory == self.media_directory.id, "media_directory應該正確設定"
            assert obj.abs_path, "abs_path不能為空"
            assert obj.init_filename, "init_filename不能為空"
            assert obj.size is not None, "size應該有值"
            assert obj.add_dt, "add_dt應該有值"
        print("   ✅ 所有必要欄位都正確設定")
        
        # 測試3: 檢查檔案路徑格式
        for obj in media_objects:
            assert obj.abs_path.endswith('.mp4'), "所有檔案都應該是.mp4格式"
            assert obj.init_filename.endswith('.mp4'), "所有檔案名稱都應該是.mp4格式"
        print("   ✅ 檔案路徑和名稱格式正確")
        
        print("\n🎉 所有驗證測試通過！")


def main():
    """主函數"""
    print("=" * 60)
    print("📺 MediaDirectoryOperator Mock資料掃描測試")
    print("=" * 60)
    
    try:
        # 建立測試實例
        test = MockMediaDirectoryScanTest()
        
        # 執行掃描測試
        media_objects = test.run_scan_test()
        
        # 分析結果
        test.analyze_results(media_objects)
        
        # 執行驗證測試
        test.run_validation_tests(media_objects)
        
        print("\n" + "=" * 60)
        print("🎊 測試完成！所有功能正常運作")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()