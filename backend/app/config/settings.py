import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):

  # Настройка CORS - разрешаем всё, чтобы не было проблем
  cors_allow_origins: list[str] = ["*"]  # Разрешить все источники. Можно указать конкретные домены, например: ["http://localhost:3000"]
  cors_allow_credentials: bool = True
  cors_allow_methods: list[str] = ["*"]  # Разрешить все HTTP методы: GET, POST, PUT, DELETE и т.д.
  cors_allow_headers: list[str] = ["*"]  # Разрешить все заголовки

  db_host: str = "localhost"
  db_port: int = 5432
  db_name: str
  db_user: str
  db_pass: str

  testing: bool = os.getenv("TESTING") == "true"
  test_db_name: str = 'code-sentry-21-db-test'

  @property
  def database_url(self):
    if self.testing:
      return f"postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.test_db_name}"
    return f"postgresql://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

  model_config = SettingsConfigDict(
    env_file=".env",
    env_file_encoding="utf-8",
    extra="allow"  # Дополнительные переменные допускаются
  )

# Загрузка настроек
settings = AppSettings()
