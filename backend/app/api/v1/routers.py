from fastapi import APIRouter

from .paths import base_api


router = APIRouter(prefix=base_api)
