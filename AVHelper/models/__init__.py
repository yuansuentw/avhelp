"""
AVHelper Database Models

This module contains SQLModel definitions for the AVHelper database.
Designed for compatibility with both SQLite and PostgreSQL.
"""

from .actress import Actress
from .video import Video
from .post import Post
from .trend import Trend
from .media_directory import MediaDirectory, PathType

__all__ = ["Actress", "Video", "Post", "Trend", "MediaDirectory", "PathType"]