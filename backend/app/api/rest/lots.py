from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas.lot import LotFilter, LotListResponse, LotRead
from app.services import lots as lots_service

router = APIRouter(prefix="/lots", tags=["lots"])


@router.get("", response_model=LotListResponse)
def list_lots(
    filters: Annotated[LotFilter, Query()],
    db: Session = Depends(get_db),
) -> LotListResponse:
    """LotFilter как Query-зависимость — FastAPI сам валидирует поля
    (в т.ч. page_size<=100) и возвращает 422, а не падает в необработанный
    ValidationError при ручной пересборке модели."""
    items, total = lots_service.list_active_lots(db, filters)
    return LotListResponse(
        items=[LotRead.model_validate(item) for item in items],
        total=total,
        page=filters.page,
        page_size=filters.page_size,
    )


@router.get("/{lot_id}", response_model=LotRead)
def get_lot(lot_id: int, db: Session = Depends(get_db)) -> LotRead:
    lot = lots_service.get_lot(db, lot_id)
    return LotRead.model_validate(lot)
