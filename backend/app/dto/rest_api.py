from datetime import datetime, timezone
from typing import Generic, TypeVar

from pydantic import BaseModel, Field
from fastapi import status, Request
from functools import wraps


class MetaData(BaseModel):
  timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
  status: int = status.HTTP_200_OK
  message: str = "Success"


T = TypeVar("T")

class APIResponse(BaseModel, Generic[T]):
  data: T
  meta: MetaData
  links: dict[str, str] = {
    'self': 'path/to/self',
    'additionalRelation': 'path/to/additional'
  }


def make_link(base_url, route_path: str, target: str = '') -> str:
  return f'{str(base_url).rstrip('/')}{route_path.rstrip('/')}{target.rstrip('/')}'