from sqlalchemy.orm import Session

from app.models.lot import Lot
from app.repositories import lot_sets as lot_sets_repo
from app.repositories import lots as lots_repo
from app.schemas.lot import LotFilter
from app.services.exceptions import LotNotFoundError


def list_active_lots(db: Session, filters: LotFilter) -> tuple[list[Lot], int]:
    """Витрина показывает лоты только активного набора (см. п.2 ТЗ)."""
    active_set = lot_sets_repo.get_active(db)
    if active_set is None:
        return [], 0
    return lots_repo.list_by_set(db, active_set.id, filters)


def get_lot(db: Session, lot_id: int) -> Lot:
    lot = lots_repo.get_by_id(db, lot_id)
    if lot is None:
        raise LotNotFoundError(lot_id)
    return lot
