from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config.settings import settings

# NOTE - development mode - localhost
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.db_user}:{settings.db_pass}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

if not database_exists(engine.url):
  create_database(engine.url)

def get_db():
  db = session_local()
  try:
    yield db
  finally:
    db.close()
