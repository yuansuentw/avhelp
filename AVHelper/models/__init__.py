"""
AVHelper Database Models

This module contains SQLModel definitions for the AVHelper database.
Designed for compatibility with both SQLite and PostgreSQL.
"""

from .actress import Actress
from .video import Video
from .posts import Post
from .trends import Trend

__all__ = ["Actress", "Video", "Post", "Trend"]