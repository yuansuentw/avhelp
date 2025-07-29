"""Tests for video ID extraction system."""

import pytest
from result import Ok, Err
from Core.video_id_extractor import VideoIDExtractor
from Core.config_loader import load_series_config
from Core.result import VideoIDData


class TestVideoIDExtractor:
    """Test cases for VideoIDExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create extractor instance for testing."""
        return VideoIDExtractor(load_series_config)
    
    def test_extractor_initialization(self, extractor):
        """Test that extractor initializes properly."""
        assert extractor.get_resolver_count() > 0
        assert len(extractor.get_resolver_names()) > 0
    
    def test_normal_format_extraction(self, extractor):
        """Test extraction of normal AV format."""
        result = extractor.extract("SSIS-123")
        assert isinstance(result, Ok)
        data = result.ok_value
        assert isinstance(data, VideoIDData)
        assert data.series == "SSIS"
        assert data.number == "123"
    
    def test_fc2_format_extraction(self, extractor):
        """Test extraction of FC2 format."""
        result = extractor.extract("FC2-PPV-1234567")
        assert isinstance(result, Ok)
        data = result.ok_value
        assert data.series == "FC2"
        assert data.number == "1234567"
    
    def test_heyzo_format_extraction(self, extractor):
        """Test extraction of HEYZO format."""
        result = extractor.extract("HEYZO-1234")
        assert isinstance(result, Ok)
        data = result.ok_value
        assert data.series == "HEYZO"
        assert data.number == "1234"
    
    def test_invalid_input(self, extractor):
        """Test handling of invalid input."""
        result = extractor.extract("invalid-text-123abc")
        assert isinstance(result, Err)
    
    def test_empty_input(self, extractor):
        """Test handling of empty input."""
        result = extractor.extract("")
        assert isinstance(result, Err)
        
        result = extractor.extract("   ")
        assert isinstance(result, Err)
    
    def test_config_reload(self, extractor):
        """Test configuration reload functionality."""
        initial_count = extractor.get_resolver_count()
        extractor.reload_config()
        assert extractor.get_resolver_count() == initial_count