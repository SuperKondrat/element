import secrets

from app.config import Settings
from app.services.exceptions import InvalidCredentialsError


def authenticate(settings: Settings, username: str, password: str) -> str:
    """Superuser задаётся конфигом, регистрации нет (п.2 ТЗ) — сравниваем
    с ADMIN_USERNAME/ADMIN_PASSWORD напрямую, constant-time."""
    username_ok = secrets.compare_digest(username, settings.admin_username)
    password_ok = secrets.compare_digest(password, settings.admin_password)
    if not (username_ok and password_ok):
        raise InvalidCredentialsError()
    return settings.admin_username
