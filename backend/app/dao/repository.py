from typing import List, Optional, Type, TypeVar, Generic

from sqlalchemy.orm import Session

from app.models import *


T = TypeVar("T")

class BaseRepository(Generic[T]):
  def __init__(self, db: Session, model: Type[T]):
    self.db = db
    self.model = model

  def is_exists(self, id: int) -> bool:
    return self.get_by_id(id) is not None

  def get_by_id(self, id: int) -> Optional[T]:
    return self.db.query(self.model).filter(self.model.id == id).first()

  def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[T]:
    query = self.db.query(self.model)
    if limit is not None:
      query = query.limit(limit)
    if offset is not None:
      query = query.offset(offset)
    return query.all()

  def create(self, entity: T) -> T:
    self.db.add(entity)
    self.db.commit()
    self.db.refresh(entity)
    return entity

  def update(self, entity: T, update_data: dict) -> T:
    for key, value in update_data.items():
      if hasattr(entity, key) and value is not None:
        setattr(entity, key, value)

    self.db.commit()
    self.db.refresh(entity)
    return entity

  def delete(self, entity: T) -> None:
    self.db.delete(entity)
    self.db.commit()
