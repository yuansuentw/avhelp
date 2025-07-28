"""Pagination schema for GraphQL"""

from typing import List, TypeVar, Generic
import strawberry
from math import ceil


@strawberry.type
class PaginationInfo:
    """分頁資訊"""
    total_count: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_previous: bool
    
    @classmethod
    def create(cls, total_count: int, page: int, page_size: int) -> "PaginationInfo":
        """創建分頁資訊"""
        total_pages = ceil(total_count / page_size) if page_size > 0 else 0
        has_next = page < total_pages
        has_previous = page > 1
        
        return cls(
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            has_next=has_next,
            has_previous=has_previous
        )


T = TypeVar('T')


@strawberry.type
class PaginatedResult(Generic[T]):
    """通用分頁結果"""
    items: List[T]
    pagination: PaginationInfo
    
    @classmethod
    def create(cls, items: List[T], total_count: int, page: int, page_size: int) -> "PaginatedResult[T]":
        """創建分頁結果"""
        pagination = PaginationInfo.create(total_count, page, page_size)
        return cls(items=items, pagination=pagination)