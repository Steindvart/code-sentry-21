import re

from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


class NotFoundHTTPException(HTTPException):
  def __init__(self, id: int, collection_name: str):
    super().__init__(
      status_code=status.HTTP_404_NOT_FOUND,
      detail=f"Item with id {id} in {collection_name} collection not found"
    )


# @app.exception_handler(NotFoundHTTPException)
async def not_found_exception_handler(request: Request, exc: NotFoundHTTPException):
  return JSONResponse(
    status_code=exc.status_code,
    content={"detail": exc.detail},
  )


# @app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
  """
  Обработка SQLAlchemy IntegrityError с форматированным сообщением об ошибке.
  """
  error_message = str(exc.orig)
  details = []

  # Проверка нарушения внешнего ключа
  if "foreign key constraint" in error_message.lower():
    # Пытаемся найти поле, указанное в сообщении ошибки
    match = re.search(r"Key \((\w+)\)=\((.*?)\)", error_message)
    if match:
      field = match.group(1)  # Название поля
      value = match.group(2)  # Значение из ошибки
      details.append({
        "loc": ["body", field],
        "msg": f"A non-existent foreign key is specified: value {value}",
        "type": "foreign_key_violation"
      })
    else:
      # Если поле не найдено, добавляем общее сообщение
      details.append({
        "loc": ["body"],
        "msg": "A non-existent foreign key is specified",
        "type": "foreign_key_violation"
      })
  else:
    # Обработка других IntegrityError
    details.append({
      "loc": ["body"],
      "msg": "Violation of database restrictions",
      "type": "integrity_error"
    })

  return JSONResponse(
    status_code=status.HTTP_400_BAD_REQUEST,
    content={"detail": details}
  )