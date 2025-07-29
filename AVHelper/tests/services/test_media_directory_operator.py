"""
Test cases for MediaDirectoryOperator.scan_and_create_media_objects method
"""

import pytest
from unittest.mock import Mock, patch
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add the AVHelper directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "AVHelper"))

from services.MediaLibrary.media_directory_operator import MediaDirectoryOperator
from models.media_directory import MediaDirectory, PathType
from models.media import Media


class TestMediaDirectoryOperatorScanAndCreateMediaObjects:
    """Test class for scan_and_create_media_objects method"""

    @pytest.fixture
    def local_media_directory(self) -> MediaDirectory:
        """Create a local media directory for testing"""
        return MediaDirectory(
            id=1,
            name="Test Directory",
            path="/test/media",
            path_type=PathType.LOCAL
        )

    @pytest.fixture
    def operator(self, local_media_directory) -> MediaDirectoryOperator:
        """Create MediaDirectoryOperator instance"""
        return MediaDirectoryOperator(local_media_directory)

    @pytest.fixture
    def mock_file_list(self) -> List[str]:
        """Mock file list for testing"""
        return [
            "/test/media/video1.mp4",
            "/test/media/video2.avi",
            "/test/media/subfolder/video3.mkv",
            "/test/media/video4.mov",
            "/test/media/video5.wmv",
            "/test/media/video6.MP4",  # Test case sensitivity
            "/test/media/document.txt"  # Non-video file
        ]

    @pytest.fixture
    def mock_file_info(self) -> Dict[str, Dict[str, Any]]:
        """Mock file info dictionary"""
        return {
            "/test/media/video1.mp4": {
                "name": "/test/media/video1.mp4",
                "size": 1024000,
                "type": "file",
                "mtime": 1640995200.0  # 2022-01-01 timestamp
            },
            "/test/media/video2.avi": {
                "name": "/test/media/video2.avi", 
                "size": 2048000,
                "type": "file",
                "mtime": 1641081600.0  # 2022-01-02 timestamp
            },
            "/test/media/subfolder/video3.mkv": {
                "name": "/test/media/subfolder/video3.mkv",
                "size": 3072000,
                "type": "file", 
                "mtime": 1641168000.0  # 2022-01-03 timestamp
            },
            "/test/media/video4.mov": {
                "name": "/test/media/video4.mov",
                "size": 4096000,
                "type": "file",
                "mtime": 1641340800.0  # 2022-01-05 timestamp
            },
            "/test/media/video5.wmv": {
                "name": "/test/media/video5.wmv",
                "size": 5120000,
                "type": "file",
                "mtime": 1641427200.0  # 2022-01-06 timestamp
            },
            "/test/media/video6.MP4": {
                "name": "/test/media/video6.MP4",
                "size": 6144000,
                "type": "file",
                "mtime": 1641513600.0  # 2022-01-07 timestamp
            },
            "/test/media/document.txt": {
                "name": "/test/media/document.txt",
                "size": 1024,
                "type": "file",
                "mtime": 1641254400.0  # 2022-01-04 timestamp
            }
        }

    def test_scan_and_create_media_objects_not_connected(self, operator):
        """Test scan_and_create_media_objects when not connected should raise RuntimeError"""
        with pytest.raises(RuntimeError, match="Not connected. Call connect\\(\\) first."):
            operator.scan_and_create_media_objects()

    @patch.object(MediaDirectoryOperator, 'list_all_files')
    @patch.object(MediaDirectoryOperator, 'get_file_info')
    def test_scan_and_create_media_objects_basic(
        self,
        mock_get_file_info,
        mock_list_all_files,
        operator,
        mock_file_list,
        mock_file_info
    ):
        """Test basic functionality of scan_and_create_media_objects"""
        # Setup
        operator._fs = Mock()  # Mock connection
        mock_list_all_files.return_value = mock_file_list
        mock_get_file_info.side_effect = lambda path: mock_file_info.get(path)

        # Execute
        result = operator.scan_and_create_media_objects()

        # Verify
        assert isinstance(result, list)
        assert len(result) == 7  # All files should be processed
        
        # Check that all results are Media objects
        for media in result:
            assert isinstance(media, Media)
            assert media.media_directory == operator.media_directory.id
            assert media.abs_path in mock_file_list
            assert media.init_filename is not None
            assert media.size is not None

    @patch.object(MediaDirectoryOperator, 'list_all_files')
    @patch.object(MediaDirectoryOperator, 'get_file_info')
    def test_scan_and_create_media_objects_with_extensions_filter(
        self,
        mock_get_file_info,
        mock_list_all_files,
        operator,
        mock_file_list,
        mock_file_info
    ):
        """Test scan_and_create_media_objects with extension filtering"""
        # Setup
        operator._fs = Mock()
        video_extensions = ['.mp4', '.avi', '.mkv']
        expected_video_files = [f for f in mock_file_list if Path(f).suffix in video_extensions]
        
        mock_list_all_files.return_value = expected_video_files
        mock_get_file_info.side_effect = lambda path: mock_file_info.get(path)

        # Execute
        result = operator.scan_and_create_media_objects(extensions=video_extensions)

        # Verify
        assert len(result) == 3  # Only video files (.mp4, .avi, .mkv)
        mock_list_all_files.assert_called_once_with(extensions=video_extensions, recursive=True)
        
        for media in result:
            assert Path(media.abs_path).suffix in video_extensions

    @patch.object(MediaDirectoryOperator, 'list_all_files')
    @patch.object(MediaDirectoryOperator, 'get_file_info')
    def test_scan_and_create_media_objects_non_recursive(
        self,
        mock_get_file_info,
        mock_list_all_files,
        operator,
        mock_file_list,
        mock_file_info
    ):
        """Test scan_and_create_media_objects with non-recursive scanning"""
        # Setup
        operator._fs = Mock()
        mock_list_all_files.return_value = mock_file_list
        mock_get_file_info.side_effect = lambda path: mock_file_info.get(path)

        # Execute
        result = operator.scan_and_create_media_objects(recursive=False)

        # Verify
        mock_list_all_files.assert_called_once_with(extensions=None, recursive=False)

    @patch.object(MediaDirectoryOperator, 'list_all_files')
    @patch.object(MediaDirectoryOperator, 'get_file_info')
    def test_scan_and_create_media_objects_file_info_none(
        self,
        mock_get_file_info,
        mock_list_all_files,
        operator,
        mock_file_list
    ):
        """Test scan_and_create_media_objects when get_file_info returns None"""
        # Setup
        operator._fs = Mock()
        mock_list_all_files.return_value = mock_file_list
        mock_get_file_info.return_value = None  # Simulate file not found

        # Execute
        result = operator.scan_and_create_media_objects()

        # Verify - should skip files with no info but not crash
        assert isinstance(result, list)
        # All files should be skipped since get_file_info returns None
        assert len(result) == 0

    @patch.object(MediaDirectoryOperator, 'list_all_files')
    def test_scan_and_create_media_objects_empty_file_list(
        self,
        mock_list_all_files,
        operator
    ):
        """Test scan_and_create_media_objects with empty file list"""
        # Setup
        operator._fs = Mock()
        mock_list_all_files.return_value = []

        # Execute
        result = operator.scan_and_create_media_objects()

        # Verify
        assert result == []

    def test_default_media_extensions_constant(self, operator):
        """Test that DEFAULT_MEDIA_EXTENSIONS constant is properly defined"""
        expected_extensions = [
            '.mp4', '.avi', '.mkv', '.mov', '.wmv', '.flv', 
            '.webm', '.m4v', '.ts', '.rmvb'
        ]
        assert operator.DEFAULT_MEDIA_EXTENSIONS == expected_extensions
        assert MediaDirectoryOperator.DEFAULT_MEDIA_EXTENSIONS == expected_extensions

    @patch.object(MediaDirectoryOperator, 'list_all_files')
    @patch.object(MediaDirectoryOperator, 'get_file_info')
    def test_scan_and_create_media_objects_uses_default_extensions(
        self,
        mock_get_file_info,
        mock_list_all_files,
        operator,
        mock_file_info
    ):
        """Test that scan_and_create_media_objects uses default extensions when none provided"""
        # Setup - only include default video format files
        default_format_files = [
            "/test/media/video1.mp4",
            "/test/media/video2.avi", 
            "/test/media/subfolder/video3.mkv",
            "/test/media/video4.mov",
            "/test/media/video5.wmv"
        ]
        
        operator._fs = Mock()
        mock_list_all_files.return_value = default_format_files
        mock_get_file_info.side_effect = lambda path: mock_file_info.get(path)

        # Execute - call without specifying extensions
        result = operator.scan_and_create_media_objects()

        # Verify that list_all_files was called with default extensions
        mock_list_all_files.assert_called_once_with(
            extensions=operator.DEFAULT_MEDIA_EXTENSIONS, 
            recursive=True
        )
        
        # Verify all default format files are processed
        assert len(result) == 5
        for media in result:
            assert isinstance(media, Media)
            assert media.abs_path in default_format_files

    @patch.object(MediaDirectoryOperator, 'list_all_files')
    @patch.object(MediaDirectoryOperator, 'get_file_info')
    def test_scan_and_create_media_objects_custom_extensions_override_default(
        self,
        mock_get_file_info,
        mock_list_all_files,
        operator,
        mock_file_info
    ):
        """Test that custom extensions override default extensions"""
        # Setup - only include mp4 files
        custom_extensions = ['.mp4']
        mp4_files = ["/test/media/video1.mp4"]
        
        operator._fs = Mock()
        mock_list_all_files.return_value = mp4_files
        mock_get_file_info.side_effect = lambda path: mock_file_info.get(path)

        # Execute - call with custom extensions
        result = operator.scan_and_create_media_objects(extensions=custom_extensions)

        # Verify that list_all_files was called with custom extensions, not default
        mock_list_all_files.assert_called_once_with(
            extensions=custom_extensions, 
            recursive=True
        )
        
        # Verify only mp4 files are processed
        assert len(result) == 1
        assert result[0].abs_path == "/test/media/video1.mp4"