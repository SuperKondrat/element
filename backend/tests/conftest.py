import os

from tests.helpers import TEST_ADMIN_PASSWORD, TEST_ADMIN_USERNAME

# POSTGRES_* — значения по умолчанию совпадают с config/app.env + .env.example,
# чтобы `pytest` работал из коробки при поднятой `docker compose up -d db`.
# Переопределяются реальными env-переменными, если они уже заданы (CI и т.п.) —
# тут это осознанно, т.к. пароль обязан совпадать с реально поднятой БД.
os.environ.setdefault("POSTGRES_HOST", "localhost")
os.environ.setdefault("POSTGRES_PORT", "5432")
os.environ.setdefault("POSTGRES_DB", "element")
os.environ.setdefault("POSTGRES_USER", "element")
os.environ.setdefault("POSTGRES_PASSWORD", "devpass")

# ADMIN_*/JWT_SECRET_KEY — наоборот, жёстко перезаписываются (не setdefault):
# это чисто тестовые значения, которым не с чем совпадать вовне. Если их
# переопределять условно, случайно оставшийся в шелле реальный ADMIN_PASSWORD
# из .env тихо подменит собой тестовый — и хардкод пароля в тестах перестанет
# совпадать с тем, что реально проверяет auth.
os.environ["ADMIN_USERNAME"] = TEST_ADMIN_USERNAME
os.environ["ADMIN_PASSWORD"] = TEST_ADMIN_PASSWORD
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.db import Base, get_db
from app.main import app

settings = get_settings()
engine = create_engine(settings.database_url)
TestSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session():
    """Каждый тест — в своей внешней транзакции, которая откатывается по
    завершении. Сервисы вызывают db.commit() сами (см. services/), поэтому
    внутри внешней транзакции держим SAVEPOINT и открываем новый после
    каждого commit — стандартный паттерн SQLAlchemy для тестов с commit()."""
    connection = engine.connect()
    outer_transaction = connection.begin()
    session = TestSessionLocal(bind=connection)
    nested = connection.begin_nested()

    @event.listens_for(session, "after_transaction_end")
    def _restart_savepoint(sess, trans):
        nonlocal nested
        if not nested.is_active:
            nested = connection.begin_nested()

    try:
        yield session
    finally:
        session.close()
        outer_transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
