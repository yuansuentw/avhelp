"""
MediaFile模型和Repository的單元測試
"""

import os
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, Any
import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.exc import IntegrityError

from models.media_file import MediaFile, auto_calculate_file_signature
from database.repositories import MediaFileRepository


class TestMediaFileModel:
    """MediaFile模型測試"""
    
    def setup_method(self):
        """每個測試方法前的設置"""
        # 建立記憶體資料庫
        self.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.engine)
    
    def create_test_file(self, content: bytes, suffix: str = ".txt") -> str:
        """建立測試檔案"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(content)
            return f.name
    
    def test_calculate_file_hashes_small_file(self):
        """測試小檔案（<2MB）的hash計算"""
        # 建立1MB的測試檔案
        content = b"A" * (1024 * 1024)  # 1MB
        test_file = self.create_test_file(content)
        
        try:
            hash_info = MediaFile.calculate_file_hashes(test_file)
            
            # 驗證結果
            assert hash_info['head_hash'] is not None
            assert hash_info['tail_hash'] is None  # 小檔案沒有tail_hash
            assert hash_info['file_signature'] == hash_info['head_hash']  # 小檔案signature等於完整hash
            assert hash_info['hash_chunk_size'] == len(content)
            
            # 驗證hash正確性
            expected_hash = hashlib.sha256(content).hexdigest()
            assert hash_info['head_hash'] == expected_hash
            
        finally:
            os.unlink(test_file)
    
    def test_calculate_file_hashes_large_file(self):
        """測試大檔案（≥2MB）的hash計算"""
        # 建立3MB的測試檔案
        head_content = b"HEAD" * (256 * 1024)  # 1MB頭部
        middle_content = b"MID" * (341 * 1024)  # 1MB中間
        tail_content = b"TAIL" * (256 * 1024)  # 1MB尾部
        full_content = head_content + middle_content + tail_content
        
        test_file = self.create_test_file(full_content)
        
        try:
            hash_info = MediaFile.calculate_file_hashes(test_file)
            
            # 驗證結果
            assert hash_info['head_hash'] is not None
            assert hash_info['tail_hash'] is not None
            assert hash_info['file_signature'] is not None
            assert hash_info['hash_chunk_size'] == 1048576  # 1MB
            
            # 驗證hash正確性
            expected_head_hash = hashlib.sha256(head_content).hexdigest()
            expected_tail_hash = hashlib.sha256(tail_content).hexdigest()
            
            assert hash_info['head_hash'] == expected_head_hash
            assert hash_info['tail_hash'] == expected_tail_hash
            
            # 驗證signature
            signature_data = f"{len(full_content)}:{expected_head_hash}:{expected_tail_hash}"
            expected_signature = hashlib.sha256(signature_data.encode()).hexdigest()
            assert hash_info['file_signature'] == expected_signature
            
        finally:
            os.unlink(test_file)
    
    def test_calculate_file_hashes_file_not_found(self):
        """測試檔案不存在的情況"""
        with pytest.raises(FileNotFoundError):
            MediaFile.calculate_file_hashes("/nonexistent/path/file.txt")
    
    def test_media_file_creation_with_event(self):
        """測試MediaFile建立時的事件觸發"""
        # 建立測試檔案
        content = b"Test content for hash calculation"
        test_file = self.create_test_file(content)
        
        try:
            with Session(self.engine) as session:
                # 建立MediaFile，不設置hash欄位
                media_file = MediaFile(
                    abs_path=test_file,
                    init_filename="test.txt",
                    size=len(content)
                )\n                
                session.add(media_file)
                session.commit()
                
                # 重新讀取以確保資料正確
                session.refresh(media_file)
                
                # 驗證事件是否正確計算了hash
                assert media_file.file_signature is not None
                assert media_file.head_hash is not None
                assert media_file.hash_chunk_size == len(content)  # 小檔案
        
        finally:
            os.unlink(test_file)
    
    def test_media_file_creation_file_not_exists(self):
        """測試檔案不存在時的fallback機制"""
        with Session(self.engine) as session:
            media_file = MediaFile(
                abs_path="/nonexistent/file.txt",
                init_filename="test.txt",
                size=1024
            )
            
            session.add(media_file)
            session.commit()
            session.refresh(media_file)
            
            # 驗證fallback機制生成了signature
            assert media_file.file_signature is not None
            assert len(media_file.file_signature) == 32  # MD5 hash長度


class TestMediaFileRepository:
    """MediaFileRepository測試"""
    
    def setup_method(self):
        """每個測試方法前的設置"""
        self.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.engine)
        self.session = Session(self.engine)
        self.repo = MediaFileRepository(self.session)
    
    def teardown_method(self):
        """每個測試方法後的清理"""
        self.session.close()
    
    def create_test_file(self, content: bytes, suffix: str = ".txt") -> str:
        """建立測試檔案"""
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
            f.write(content)
            return f.name
    
    def test_add_or_get_existing_new_file(self):
        """測試添加新檔案"""
        content = b"Test file content"
        test_file = self.create_test_file(content)
        
        try:
            # 添加新檔案
            media_file = self.repo.add_or_get_existing({
                'abs_path': test_file,
                'init_filename': 'test.txt',
                'size': len(content)
            })
            
            assert media_file.id is not None
            assert media_file.abs_path == test_file
            assert media_file.file_signature is not None
            
        finally:
            os.unlink(test_file)
    
    def test_add_or_get_existing_duplicate_file(self):
        """測試重複檔案的處理"""
        content = b"Duplicate test content"
        test_file1 = self.create_test_file(content, ".txt")
        test_file2 = self.create_test_file(content, ".backup")
        
        try:
            # 添加第一個檔案
            media_file1 = self.repo.add_or_get_existing({
                'abs_path': test_file1,
                'init_filename': 'original.txt',
                'size': len(content)
            })
            original_id = media_file1.id
            
            # 嘗試添加相同內容的檔案
            media_file2 = self.repo.add_or_get_existing({
                'abs_path': test_file2,
                'init_filename': 'duplicate.txt', 
                'size': len(content)
            })
            
            # 應該返回同一個記錄，但路徑被更新
            assert media_file2.id == original_id
            assert media_file2.abs_path == test_file2  # 路徑已更新
            
        finally:
            os.unlink(test_file1)
            os.unlink(test_file2)
    
    def test_find_by_signature(self):
        """測試根據signature查找檔案"""
        content = b"Content for signature test"
        test_file = self.create_test_file(content)
        
        try:
            # 添加檔案
            media_file = self.repo.add_or_get_existing({
                'abs_path': test_file,
                'init_filename': 'signature_test.txt',
                'size': len(content)
            })
            
            # 根據signature查找
            found_file = self.repo.find_by_signature(media_file.file_signature)
            
            assert found_file is not None
            assert found_file.id == media_file.id
            assert found_file.abs_path == test_file
            
        finally:
            os.unlink(test_file)
    
    def test_find_by_path(self):
        """測試根據路徑查找檔案"""
        content = b"Content for path test"
        test_file = self.create_test_file(content)
        
        try:
            # 添加檔案
            media_file = self.repo.add_or_get_existing({
                'abs_path': test_file,
                'init_filename': 'path_test.txt',
                'size': len(content)
            })
            
            # 根據路徑查找
            found_file = self.repo.find_by_path(test_file)
            
            assert found_file is not None
            assert found_file.id == media_file.id
            
        finally:
            os.unlink(test_file)
    
    def test_find_by_partial_hash(self):
        """測試根據partial hash查找檔案"""
        # 建立大檔案以觸發partial hash
        content = b"LARGE" * (500 * 1024)  # 約2.5MB
        test_file = self.create_test_file(content)
        
        try:
            # 添加檔案
            media_file = self.repo.add_or_get_existing({
                'abs_path': test_file,
                'init_filename': 'large_file.bin',
                'size': len(content)
            })
            
            # 根據partial hash查找
            found_files = self.repo.find_by_partial_hash(
                head_hash=media_file.head_hash,
                tail_hash=media_file.tail_hash,
                size=media_file.size
            )
            
            assert len(found_files) == 1
            assert found_files[0].id == media_file.id
            
        finally:
            os.unlink(test_file)
    
    def test_get_files_without_signature(self):
        """測試獲取沒有signature的檔案"""
        # 直接插入沒有signature的記錄（繞過事件）
        media_file = MediaFile(
            abs_path="/test/path/file.txt",
            init_filename="test.txt",
            size=1024,
            file_signature=None  # 明確設置為None
        )
        
        self.session.add(media_file)
        self.session.commit()
        
        # 查找沒有signature的檔案
        files_without_signature = self.repo.get_files_without_signature()
        
        assert len(files_without_signature) == 1
        assert files_without_signature[0].id == media_file.id
    
    def test_update_file_hashes(self):
        """測試更新檔案hash資訊"""
        # 建立檔案但不設置hash
        media_file = MediaFile(
            abs_path="/test/update/file.txt",
            init_filename="update_test.txt",
            size=2048,
            file_signature=None
        )
        
        self.session.add(media_file)
        self.session.commit()
        
        # 更新hash資訊
        hash_info = {
            'head_hash': 'test_head_hash_123',
            'tail_hash': 'test_tail_hash_456',
            'file_signature': 'test_signature_789',
            'hash_chunk_size': 1048576
        }
        
        updated_file = self.repo.update_file_hashes(media_file, hash_info)
        
        assert updated_file.head_hash == 'test_head_hash_123'
        assert updated_file.tail_hash == 'test_tail_hash_456'
        assert updated_file.file_signature == 'test_signature_789'
        assert updated_file.hash_chunk_size == 1048576


# 整合測試
class TestMediaFileIntegration:
    """MediaFile整合測試"""
    
    def setup_method(self):
        self.engine = create_engine("sqlite:///:memory:")
        SQLModel.metadata.create_all(self.engine)
    
    def test_complete_workflow(self):
        """測試完整的工作流程"""
        # 建立兩個內容相同的測試檔案
        content = b"Integration test content" * 1000  # 約24KB
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f1:
            f1.write(content)
            file1_path = f1.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f2:
            f2.write(content)
            file2_path = f2.name
        
        try:
            with Session(self.engine) as session:
                repo = MediaFileRepository(session)
                
                # 1. 添加第一個檔案
                media_file1 = repo.add_or_get_existing({
                    'abs_path': file1_path,
                    'init_filename': 'file1.txt',
                    'size': len(content)
                })
                
                assert media_file1.file_signature is not None
                original_signature = media_file1.file_signature
                
                # 2. 添加相同內容的第二個檔案
                media_file2 = repo.add_or_get_existing({
                    'abs_path': file2_path,
                    'init_filename': 'file2.txt',
                    'size': len(content)
                })
                
                # 3. 驗證返回的是同一個記錄（去重成功）
                assert media_file1.id == media_file2.id
                assert media_file2.abs_path == file2_path  # 路徑已更新
                assert media_file2.file_signature == original_signature
                
                # 4. 驗證資料庫中只有一筆記錄
                all_files = session.exec(select(MediaFile)).all()
                signatures = [f.file_signature for f in all_files if f.file_signature == original_signature]
                assert len(signatures) == 1
                
        finally:
            os.unlink(file1_path)
            os.unlink(file2_path)


if __name__ == '__main__':
    pytest.main([__file__])