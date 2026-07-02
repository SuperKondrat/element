"""Идемпотентно создаёт отсутствующие таблицы. Ничего не удаляет и не
трогает существующие данные — безопасно запускать многократно.
Используется локальным раннером тестов (scripts/test-all.mjs) перед e2e,
т.к. реальный uvicorn (в отличие от pytest-фикстур) схему сам не создаёт.
"""

from app import models  # noqa: F401 (регистрирует модели в Base.metadata)
from app.db import Base, engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Схема БД в порядке (create_all выполнен).")
