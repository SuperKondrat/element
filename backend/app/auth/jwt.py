from datetime import datetime, timedelta, timezone

import jwt

from app.config import Settings


class TokenError(Exception):
    pass


def create_access_token(settings: Settings, subject: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_access_token(settings: Settings, token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise TokenError(str(exc)) from exc
    subject = payload.get("sub")
    if not subject:
        raise TokenError("Токен не содержит subject")
    return subject
