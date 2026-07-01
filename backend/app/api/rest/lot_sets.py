from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_admin
from app.config import Settings, get_settings
from app.db import get_db
from app.schemas.lot_set import LotSetRead, LotSetUploadResponse
from app.services import lot_sets as lot_sets_service

router = APIRouter(prefix="/admin/lot-sets", tags=["lot-sets"])


@router.post("/upload", response_model=LotSetUploadResponse, status_code=201)
async def upload_lot_set(
    file: UploadFile,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
    admin: str = Depends(get_current_admin),
) -> LotSetUploadResponse:
    content = await file.read()
    max_bytes = settings.max_feed_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail=f"Файл превышает лимит {settings.max_feed_size_mb} МБ",
        )

    try:
        lot_set, skipped_count = lot_sets_service.upload_feed(db, file.filename or "feed.xml", content)
    except lot_sets_service.FeedParseError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return LotSetUploadResponse(
        id=lot_set.id,
        name=lot_set.name,
        uploaded_at=lot_set.uploaded_at,
        lots_count=lot_set.lots_count,
        is_active=lot_set.is_active,
        skipped_count=skipped_count,
    )


@router.get("", response_model=list[LotSetRead])
def list_lot_sets(db: Session = Depends(get_db), admin: str = Depends(get_current_admin)) -> list[LotSetRead]:
    return [LotSetRead.model_validate(s) for s in lot_sets_service.list_sets(db)]


@router.post("/{set_id}/activate", response_model=LotSetRead)
def activate_lot_set(
    set_id: int, db: Session = Depends(get_db), admin: str = Depends(get_current_admin)
) -> LotSetRead:
    lot_set = lot_sets_service.activate_set(db, set_id)
    return LotSetRead.model_validate(lot_set)
