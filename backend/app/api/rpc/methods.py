import base64
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel, ValidationError
from sqlalchemy.orm import Session

from app.api.rpc.errors import INVALID_PARAMS, RpcError
from app.auth.jwt import create_access_token
from app.config import Settings
from app.schemas.application import ApplicationCreate, ApplicationRead
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.booking import BookingCreate, BookingRead
from app.schemas.lot import LotFilter, LotListResponse, LotRead
from app.schemas.lot_set import LotSetRead, LotSetUploadResponse
from app.services import applications as applications_service
from app.services import auth as auth_service
from app.services import bookings as bookings_service
from app.services import lot_sets as lot_sets_service
from app.services import lots as lots_service


def _parse_params(model: type[BaseModel], params: dict[str, Any]) -> BaseModel:
    try:
        return model.model_validate(params)
    except ValidationError as exc:
        raise RpcError(INVALID_PARAMS, "Некорректные параметры", data=exc.errors()) from exc


@dataclass(frozen=True)
class MethodSpec:
    handler: Callable[[Session, Settings, dict[str, Any]], BaseModel | list[BaseModel]]
    requires_auth: bool


def _lots_list(db: Session, settings: Settings, params: dict[str, Any]) -> LotListResponse:
    filters = _parse_params(LotFilter, params)
    items, total = lots_service.list_active_lots(db, filters)
    return LotListResponse(
        items=[LotRead.model_validate(item) for item in items],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )


def _lots_get(db: Session, settings: Settings, params: dict[str, Any]) -> LotRead:
    lot_id = params.get("lot_id")
    if not isinstance(lot_id, int):
        raise RpcError(INVALID_PARAMS, "Требуется целочисленный lot_id")
    return LotRead.model_validate(lots_service.get_lot(db, lot_id))


def _bookings_create(db: Session, settings: Settings, params: dict[str, Any]) -> BookingRead:
    data = _parse_params(BookingCreate, params)
    return BookingRead.model_validate(bookings_service.create_booking(db, data))


def _bookings_admin_list(db: Session, settings: Settings, params: dict[str, Any]) -> list[BookingRead]:
    return [BookingRead.model_validate(b) for b in bookings_service.list_bookings(db)]


def _applications_create(db: Session, settings: Settings, params: dict[str, Any]) -> ApplicationRead:
    data = _parse_params(ApplicationCreate, params)
    return ApplicationRead.model_validate(applications_service.create_application(db, data))


def _applications_admin_list(db: Session, settings: Settings, params: dict[str, Any]) -> list[ApplicationRead]:
    return [ApplicationRead.model_validate(a) for a in applications_service.list_applications(db)]


def _auth_login(db: Session, settings: Settings, params: dict[str, Any]) -> TokenResponse:
    data = _parse_params(LoginRequest, params)
    subject = auth_service.authenticate(settings, data.username, data.password)
    return TokenResponse(access_token=create_access_token(settings, subject))


def _lot_sets_admin_list(db: Session, settings: Settings, params: dict[str, Any]) -> list[LotSetRead]:
    return [LotSetRead.model_validate(s) for s in lot_sets_service.list_sets(db)]


def _lot_sets_admin_activate(db: Session, settings: Settings, params: dict[str, Any]) -> LotSetRead:
    set_id = params.get("set_id")
    if not isinstance(set_id, int):
        raise RpcError(INVALID_PARAMS, "Требуется целочисленный set_id")
    return LotSetRead.model_validate(lot_sets_service.activate_set(db, set_id))


def _lot_sets_admin_upload(db: Session, settings: Settings, params: dict[str, Any]) -> LotSetUploadResponse:
    """JSON-RPC не умеет multipart — фид передаётся как base64 в JSON.
    REST для этой же операции принимает multipart напрямую: разница
    в форме передачи бинарных данных — одна из точек сравнения
    протоколов в отчёте."""
    filename = params.get("filename")
    content_base64 = params.get("content_base64")
    if not isinstance(filename, str) or not isinstance(content_base64, str):
        raise RpcError(INVALID_PARAMS, "Требуются filename и content_base64")

    try:
        content = base64.b64decode(content_base64, validate=True)
    except Exception as exc:
        raise RpcError(INVALID_PARAMS, "content_base64 не является валидным base64") from exc

    max_bytes = settings.max_feed_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise RpcError(INVALID_PARAMS, f"Файл превышает лимит {settings.max_feed_size_mb} МБ")

    try:
        lot_set, skipped_count = lot_sets_service.upload_feed(db, filename, content)
    except lot_sets_service.FeedParseError as exc:
        raise RpcError(INVALID_PARAMS, str(exc)) from exc

    return LotSetUploadResponse(
        id=lot_set.id,
        name=lot_set.name,
        uploaded_at=lot_set.uploaded_at,
        lots_count=lot_set.lots_count,
        is_active=lot_set.is_active,
        skipped_count=skipped_count,
    )


METHOD_REGISTRY: dict[str, MethodSpec] = {
    "auth.login": MethodSpec(_auth_login, requires_auth=False),
    "lots.list": MethodSpec(_lots_list, requires_auth=False),
    "lots.get": MethodSpec(_lots_get, requires_auth=False),
    "bookings.create": MethodSpec(_bookings_create, requires_auth=False),
    "applications.create": MethodSpec(_applications_create, requires_auth=False),
    "admin.bookings.list": MethodSpec(_bookings_admin_list, requires_auth=True),
    "admin.applications.list": MethodSpec(_applications_admin_list, requires_auth=True),
    "admin.lot_sets.list": MethodSpec(_lot_sets_admin_list, requires_auth=True),
    "admin.lot_sets.activate": MethodSpec(_lot_sets_admin_activate, requires_auth=True),
    "admin.lot_sets.upload": MethodSpec(_lot_sets_admin_upload, requires_auth=True),
}
