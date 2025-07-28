"""
GraphQL schema for Actress model using Strawberry
"""

from typing import Optional
from datetime import datetime
import strawberry


@strawberry.type
class ActressType:
    """GraphQL type for Actress model"""
    
    id: int
    name: Optional[str] = None
    rating: Optional[str] = None
    face: Optional[str] = None
    style: Optional[str] = None
    breast: Optional[str] = None
    waist: Optional[str] = None
    legs: Optional[str] = None
    body: Optional[str] = None
    hair: Optional[str] = None
    features: Optional[str] = None
    role_type: Optional[str] = None
    common: Optional[str] = None
    is_delete: Optional[bool] = None
    data_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    alias: Optional[str] = None


@strawberry.input
class ActressInput:
    """GraphQL input type for creating/updating Actress"""
    
    name: Optional[str] = None
    rating: Optional[str] = None
    face: Optional[str] = None
    style: Optional[str] = None
    breast: Optional[str] = None
    waist: Optional[str] = None
    legs: Optional[str] = None
    body: Optional[str] = None
    hair: Optional[str] = None
    features: Optional[str] = None
    role_type: Optional[str] = None
    common: Optional[str] = None
    is_delete: Optional[bool] = None
    data_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    alias: Optional[str] = None


@strawberry.input
class ActressFilter:
    """GraphQL input type for filtering Actresses"""
    
    name: Optional[str] = None
    rating: Optional[str] = None
    role_type: Optional[str] = None
    is_delete: Optional[bool] = None