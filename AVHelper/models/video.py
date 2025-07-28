"""
Video model for AVHelper database
"""

from typing import Optional
from datetime import datetime, time
from sqlmodel import SQLModel, Field, Column, Text


class Video(SQLModel, table=True):
    """Video/movie information"""

    __tablename__ = "video"

    id: str = Field(primary_key=True, max_length=60)
    idSeries: Optional[str] = Field(default=None, max_length=30)
    idNumber: Optional[str] = Field(default=None, max_length=30)
    dmmID: Optional[str] = Field(default=None, max_length=15)
    javdbID: Optional[str] = Field(default=None, max_length=20)
    pubDate: Optional[datetime] = Field(default=None)
    duration: Optional[time] = Field(default=None)
    title: Optional[str] = Field(default=None, max_length=300)
    actress_name: Optional[str] = Field(default=None, sa_column=Column(Text))
    actressID: Optional[str] = Field(default=None, max_length=20)
    rating: Optional[float] = Field(default=None)
    isDownloaded: Optional[bool] = Field(default=False)
    isIgnore: Optional[bool] = Field(default=False)
    addDate: Optional[datetime] = Field(default=None)
    downloadDate: Optional[datetime] = Field(default=None)
    deleteDate: Optional[datetime] = Field(default=None)
    deleteReason: Optional[str] = Field(default=None, sa_column=Column(Text))
    remark: Optional[str] = Field(default=None, sa_column=Column(Text))