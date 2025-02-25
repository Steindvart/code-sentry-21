import pytest
import os
import subprocess

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import database_exists, create_database
from fastapi.testclient import TestClient

# @todo - подумать как более оптимально и гибко сделать включение "тестового режима"
os.environ["TESTING"] = "true"

from app.db.database import get_db
from app.config.settings import settings
from app.config.app import app

from tests.dataset import NormalModels

# @todo - обернуть интеграционное тестирование в Docker-контейнер
#      Преимущества: изоляция, гибкость, безопасность
#      Недостатки: необходимость каждый раз устанавливать зависимости, более длительно по времени


# Путь к корневой директории, где находится alembic.ini
ALEMBIC_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
SQLALCHEMY_DATABASE_URL = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URL)
testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

if not database_exists(engine.url):
  create_database(engine.url)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
  """Настраивает тестовую базу данных перед запуском тестов"""

  try:
    engine.connect()
    print("✅ Тестовая БД доступна!")
  except Exception:
    raise RuntimeError("❌ Не удалось подключиться к тестовой БД")

  print(f"🔄 Запуск Alembic из {ALEMBIC_PATH}...")
  subprocess.run(
    ["alembic", "-c", "alembic.ini", "upgrade", "head"],
    cwd=ALEMBIC_PATH, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
  )

  print("🧹 Очистка тестовой БД...")
  with engine.begin() as conn:
    # @todo - сделать через ORM и чтобы автоматически подхватывались имеющиеся таблицы
    conn.execute(text('TRUNCATE TABLE ... RESTART IDENTITY CASCADE;'))

  print("📌 Заполняем тестовую БД данными...")
  seed_test_database()

  yield


@pytest.fixture(scope="function")
def test_app():
    """Фикстура для тестового клиента API с общей транзакцией на весь тест."""

    connection = engine.connect()
    transaction = connection.begin()  # 🔥 Открываем транзакцию на весь тест
    session = testing_session_local(bind=connection)  # ✅ Используем одну сессию

    def override_get_db():
      """Всегда возвращает одну и ту же сессию в рамках теста"""
      yield session

    # Подменяем зависимость FastAPI
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
      yield test_client  # ✅ Тест использует одну сессию

    # 🔥 Откатываем все изменения после завершения теста!
    session.close()
    transaction.rollback()
    connection.close()



def seed_test_database():
  """Заполняет тестовую базу данных начальными данными"""
  db = testing_session_local()

  try:
    db.add_all(...)
    db.flush()  # Получаем ID после вставки

    db.commit()
    print("✅ База данных успешно заполнена тестовыми данными!")

  except Exception as e:
    db.rollback()
    print(f"❌ Ошибка при заполнении тестовой БД: {e}")
  finally:
    db.close()