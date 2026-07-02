"""Дропает таблицы приложения — то же самое, что and так делает teardown
сессии pytest (см. tests/conftest.py::_create_schema) в конце каждого
прогона. Нужен, чтобы backend-тесты стартовали с гарантированно пустой
схемой, даже если до них в БД остались данные от e2e/ручного запуска сервера.
Не трогает ничего, кроме таблиц из app.models (lot_sets, lots, bookings,
applications) — alembic_version и другие БД не затрагиваются.
"""

from app import models  # noqa: F401 (регистрирует модели в Base.metadata)
from app.db import Base, engine

if __name__ == "__main__":
    Base.metadata.drop_all(engine)
    print("Таблицы приложения очищены (drop_all).")
