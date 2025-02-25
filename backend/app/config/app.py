from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routers import router as api_v1_router
from app.exceptions.handlers import (
    NotFoundHTTPException, not_found_exception_handler,
    IntegrityError, integrity_error_handler
)

import logging as log
from app.config.settings import settings


# @warning: configure immediately after logging and settings import is IMPORTANT!
log.basicConfig(
  filename=settings.log_file,
  level=log._nameToLevel[settings.log_level],
  format='[{asctime}] {levelname:8} {filename}: {lineno} - {name} - {message}',
  style='{',
  encoding='utf-8'
)

app = FastAPI()

# app = FastAPI(
#   title=settings.app_title,
#   description=settings.app_description,
#   docs_url=settings.docs_url
# )

# Настройка CORS
app.add_middleware(
  CORSMiddleware,
  allow_origins=settings.cors_allow_origins,
  allow_credentials=settings.cors_allow_credentials,
  allow_methods=settings.cors_allow_methods,
  allow_headers=settings.cors_allow_headers,
)

app.include_router(api_v1_router)

app.add_exception_handler(NotFoundHTTPException, not_found_exception_handler)
app.add_exception_handler(IntegrityError, integrity_error_handler)
