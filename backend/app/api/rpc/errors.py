from app.services.exceptions import (
    DomainError,
    InvalidCredentialsError,
    LotNotAvailableError,
    LotNotFoundError,
    LotSetNotFoundError,
)

# JSON-RPC 2.0 резервирует -32000..-32099 под ошибки сервера/приложения.
# Один и тот же DomainError на REST-стороне превращается в HTTP-код
# (app/core/errors.py), здесь — в RPC-код. Ошибка бросается в services/
# один раз, каждый протокол сам решает, во что её завернуть (п.8.1 PLAN.md).
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603

DOMAIN_ERROR_CODE: dict[type[DomainError], int] = {
    LotNotFoundError: -32001,
    LotSetNotFoundError: -32002,
    LotNotAvailableError: -32003,
    InvalidCredentialsError: -32004,
}


class RpcError(Exception):
    def __init__(self, code: int, message: str, data: object = None) -> None:
        self.code = code
        self.message = message
        self.data = data
        super().__init__(message)

    def to_dict(self) -> dict:
        body: dict = {"code": self.code, "message": self.message}
        if self.data is not None:
            body["data"] = self.data
        return body


def code_for_domain_error(error: DomainError) -> int:
    for error_type, code in DOMAIN_ERROR_CODE.items():
        if isinstance(error, error_type):
            return code
    return INTERNAL_ERROR
