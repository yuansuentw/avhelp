"""Base repository class for AVHelper"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Generic
from datetime import datetime
from sqlmodel import Session, SQLModel, select, func

T = TypeVar('T', bound=SQLModel)


class BaseRepository(Generic[T], ABC):
    """基礎 Repository 類別"""
    
    def __init__(self, session: Session, model_class: Type[T]):
        self.session = session
        self.model_class = model_class
    
    def get_by_id(self, id: Any) -> Optional[T]:
        """根據 ID 獲取單個記錄"""
        statement = select(self.model_class).where(self.model_class.id == id)
        return self.session.exec(statement).first()
    
    def get_all(
        self, 
        page: int = 1, 
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None
    ) -> Tuple[List[T], int]:
        """獲取分頁記錄列表"""
        # 基礎查詢
        statement = select(self.model_class)
        count_statement = select(func.count(self.model_class.id))
        
        # 應用過濾條件
        if filters:
            statement, count_statement = self._apply_filters(statement, count_statement, filters)
        
        # 應用排序
        if order_by:
            statement = self._apply_ordering(statement, order_by)
        
        # 獲取總數
        total_count = self.session.exec(count_statement).one()
        
        # 應用分頁
        offset = (page - 1) * page_size
        statement = statement.offset(offset).limit(page_size)
        
        # 執行查詢
        results = self.session.exec(statement).all()
        
        return results, total_count
    
    def create(self, data: Dict[str, Any]) -> T:
        """創建新記錄"""
        # 添加創建時間
        if hasattr(self.model_class, 'data_date'):
            data['data_date'] = datetime.now()
        if hasattr(self.model_class, 'addDate'):
            data['addDate'] = datetime.now()
        
        instance = self.model_class(**data)
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance
    
    def update(self, id: Any, data: Dict[str, Any]) -> Optional[T]:
        """更新記錄"""
        instance = self.get_by_id(id)
        if not instance:
            return None
        
        # 添加更新時間
        if hasattr(instance, 'update_date'):
            data['update_date'] = datetime.now()
        
        # 更新字段
        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        
        self.session.add(instance)
        self.session.commit()
        self.session.refresh(instance)
        return instance
    
    def delete(self, id: Any, soft_delete: bool = True) -> bool:
        """刪除記錄（支援軟刪除）"""
        instance = self.get_by_id(id)
        if not instance:
            return False
        
        if soft_delete:
            # 軟刪除
            if hasattr(instance, 'is_delete'):
                instance.is_delete = True
            elif hasattr(instance, 'isIgnore'):
                instance.isIgnore = True
            
            if hasattr(instance, 'delete_date'):
                instance.delete_date = datetime.now()
            
            self.session.add(instance)
        else:
            # 硬刪除
            self.session.delete(instance)
        
        self.session.commit()
        return True
    
    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """計算記錄總數"""
        statement = select(func.count(self.model_class.id))
        
        if filters:
            _, statement = self._apply_filters(select(self.model_class), statement, filters)
        
        return self.session.exec(statement).one()
    
    def exists(self, id: Any) -> bool:
        """檢查記錄是否存在"""
        statement = select(func.count(self.model_class.id)).where(self.model_class.id == id)
        count = self.session.exec(statement).one()
        return count > 0
    
    @abstractmethod
    def _apply_filters(self, statement, count_statement, filters: Dict[str, Any]):
        """應用過濾條件（子類別需實作）"""
        pass
    
    def _apply_ordering(self, statement, order_by: str):
        """應用排序（可被子類別覆寫）"""
        if hasattr(self.model_class, order_by):
            column = getattr(self.model_class, order_by)
            statement = statement.order_by(column)
        return statement