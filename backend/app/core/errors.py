import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services.exceptions import (
    DomainError,
    InvalidCredentialsError,
    LotNotAvailableError,
    LotNotFoundError,
    LotSetNotFoundError,
)

logger = logging.getLogger(__name__)

# Общая карта: доменная ошибка -> HTTP статус. REST-роутеры полагаются на
# глобальный handler ниже; JSON-RPC dispatcher использует ту же карту,
# только переводит в RPC-коды (см. app/api/rpc/errors.py).
DOMAIN_ERROR_STATUS: dict[type[DomainError], int] = {
    LotNotFoundError: status.HTTP_404_NOT_FOUND,
    LotSetNotFoundError: status.HTTP_404_NOT_FOUND,
    LotNotAvailableError: status.HTTP_409_CONFLICT,
    InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
}


def _status_for(error: DomainError) -> int:
    for error_type, code in DOMAIN_ERROR_STATUS.items():
        if isinstance(error, error_type):
            return code
    return status.HTTP_400_BAD_REQUEST


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        return JSONResponse(status_code=_status_for(exc), content={"detail": str(exc)})

    @app.exception_handler(Exception)
    async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Необработанная ошибка при обработке %s %s", request.method, request.url.path)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Внутренняя ошибка сервера"},
        )
