from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.auth.jwt import TokenError, decode_access_token
from app.config import Settings, get_settings

_bearer_scheme = HTTPBearer(auto_error=False)


def resolve_admin_subject(settings: Settings, token: str | None) -> str:
    """Протокол-независимая проверка Bearer-токена — переиспользуется
    REST-зависимостью и JSON-RPC dispatcher'ом, каждый сам решает,
    как завернуть ошибку (HTTPException vs RPC-код), см. п.8.4 PLAN.md."""
    if not token:
        raise TokenError("Токен не передан")
    return decode_access_token(settings, token)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    settings: Settings = Depends(get_settings),
) -> str:
    token = credentials.credentials if credentials else None
    try:
        return resolve_admin_subject(settings, token)
    except TokenError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Недействительный токен") from exc
