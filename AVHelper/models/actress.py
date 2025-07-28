"""
Actress model for AVHelper database
"""

from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Actress(SQLModel, table=True):
    """Actress/performer information"""

    __tablename__ = "actress"

    id: int = Field(primary_key=True)
    name: Optional[str] = Field(default=None, max_length=30)
    rating: Optional[str] = Field(default=None, max_length=3)
    face: Optional[str] = Field(default=None, max_length=30)
    style: Optional[str] = Field(default=None, max_length=30)
    breast: Optional[str] = Field(default=None, max_length=30)
    waist: Optional[str] = Field(default=None, max_length=30)
    legs: Optional[str] = Field(default=None, max_length=30)
    body: Optional[str] = Field(default=None, max_length=30)
    hair: Optional[str] = Field(default=None, max_length=30)
    features: Optional[str] = Field(default=None, max_length=100)
    role_type: Optional[str] = Field(default=None, max_length=30)
    common: Optional[str] = Field(default=None, max_length=200)
    is_delete: Optional[bool] = Field(default=False)
    data_date: Optional[datetime] = Field(default=None)
    update_date: Optional[datetime] = Field(default=None)
    alias: Optional[str] = Field(default=None, max_length=100)