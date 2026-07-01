from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.enums import LotStatus
from app.schemas.lot import LotFilter, LotListResponse, LotRead, SortDirection, SortField
from app.services import lots as lots_service

router = APIRouter(prefix="/lots", tags=["lots"])


@router.get("", response_model=LotListResponse)
def list_lots(
    project_name: str | None = None,
    rooms: int | None = None,
    status: LotStatus | None = None,
    price_per_sqm_min: float | None = None,
    price_per_sqm_max: float | None = None,
    sort_by: SortField = SortField.CREATED_AT,
    sort_dir: SortDirection = SortDirection.DESC,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
) -> LotListResponse:
    filters = LotFilter(
        project_name=project_name,
        rooms=rooms,
        status=status,
        price_per_sqm_min=price_per_sqm_min,
        price_per_sqm_max=price_per_sqm_max,
        sort_by=sort_by,
        sort_dir=sort_dir,
        page=page,
        page_size=page_size,
    )
    items, total = lots_service.list_active_lots(db, filters)
    return LotListResponse(
        items=[LotRead.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{lot_id}", response_model=LotRead)
def get_lot(lot_id: int, db: Session = Depends(get_db)) -> LotRead:
    lot = lots_service.get_lot(db, lot_id)
    return LotRead.model_validate(lot)
