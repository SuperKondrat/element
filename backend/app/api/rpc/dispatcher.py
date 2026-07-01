import json
import logging
from typing import Any

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.api.rpc.errors import (
    INTERNAL_ERROR,
    INVALID_PARAMS,
    INVALID_REQUEST,
    METHOD_NOT_FOUND,
    PARSE_ERROR,
    RpcError,
    code_for_domain_error,
)
from app.api.rpc.methods import METHOD_REGISTRY
from app.auth.dependencies import resolve_admin_subject
from app.auth.jwt import TokenError
from app.config import Settings, get_settings
from app.db import get_db
from app.services.exceptions import DomainError, InvalidCredentialsError

logger = logging.getLogger(__name__)

router = APIRouter()


def _error(call_id: Any, code: int, message: str, data: Any = None) -> dict:
    error: dict = {"code": code, "message": message}
    if data is not None:
        error["data"] = data
    return {"jsonrpc": "2.0", "error": error, "id": call_id}


def _success(call_id: Any, result: Any) -> dict:
    return {"jsonrpc": "2.0", "result": result, "id": call_id}


def _serialize(result: BaseModel | list[BaseModel]) -> Any:
    if isinstance(result, list):
        return [item.model_dump(mode="json") for item in result]
    return result.model_dump(mode="json")


def _handle_call(db: Session, settings: Settings, token: str | None, call: Any) -> dict | None:
    is_notification = isinstance(call, dict) and "id" not in call
    call_id = call.get("id") if isinstance(call, dict) else None

    if not isinstance(call, dict) or call.get("jsonrpc") != "2.0" or not isinstance(call.get("method"), str):
        return None if is_notification else _error(call_id, INVALID_REQUEST, "Некорректный запрос")

    method_name = call["method"]
    params = call.get("params", {})
    if not isinstance(params, dict):
        return None if is_notification else _error(call_id, INVALID_PARAMS, "params должен быть объектом")

    spec = METHOD_REGISTRY.get(method_name)
    if spec is None:
        return None if is_notification else _error(call_id, METHOD_NOT_FOUND, f"Метод {method_name} не найден")

    if spec.requires_auth:
        try:
            resolve_admin_subject(settings, token)
        except TokenError as exc:
            code = code_for_domain_error(InvalidCredentialsError())
            return None if is_notification else _error(call_id, code, "Недействительный токен", data=str(exc))

    try:
        result = spec.handler(db, settings, params)
    except RpcError as exc:
        return None if is_notification else _error(call_id, exc.code, exc.message, exc.data)
    except DomainError as exc:
        return None if is_notification else _error(call_id, code_for_domain_error(exc), str(exc))
    except Exception:
        logger.exception("rpc: необработанная ошибка метода %s", method_name)
        return None if is_notification else _error(call_id, INTERNAL_ERROR, "Внутренняя ошибка сервера")

    return None if is_notification else _success(call_id, _serialize(result))


@router.post("/rpc")
async def rpc_endpoint(
    request: Request,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> Response:
    try:
        body = await request.json()
    except Exception:
        return _json_response(_error(None, PARSE_ERROR, "Некорректный JSON"))

    is_batch = isinstance(body, list)
    calls = body if is_batch else [body]
    if is_batch and not calls:
        return _json_response(_error(None, INVALID_REQUEST, "Пустой batch-запрос"))

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.removeprefix("Bearer ").strip() if auth_header.startswith("Bearer ") else None

    responses = [r for call in calls if (r := _handle_call(db, settings, token, call)) is not None]

    if not responses:
        return Response(status_code=204)

    return _json_response(responses if is_batch else responses[0])


def _json_response(payload: Any) -> Response:
    return Response(content=json.dumps(payload, ensure_ascii=False), media_type="application/json")
