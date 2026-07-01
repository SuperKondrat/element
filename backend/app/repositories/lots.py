from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.lot import Lot
from app.schemas.lot import LotFilter, SortDirection, SortField
from app.services.feed_parser import ParsedLot

_SORT_COLUMNS = {
    SortField.PRICE: Lot.price,
    SortField.PRICE_PER_SQM: Lot.price / func.nullif(Lot.area, 0),
    SortField.AREA: Lot.area,
    SortField.FLOOR: Lot.floor,
    SortField.CREATED_AT: Lot.created_at,
}


def get_by_id(db: Session, lot_id: int) -> Lot | None:
    return db.get(Lot, lot_id)


def get_for_update(db: Session, lot_id: int) -> Lot | None:
    return db.execute(select(Lot).where(Lot.id == lot_id).with_for_update()).scalar_one_or_none()


def list_by_set(db: Session, set_id: int, filters: LotFilter) -> tuple[list[Lot], int]:
    query = select(Lot).where(Lot.set_id == set_id)

    if filters.project_name:
        query = query.where(Lot.project_name.ilike(f"%{filters.project_name}%"))
    if filters.rooms is not None:
        query = query.where(Lot.rooms == filters.rooms)
    if filters.status is not None:
        query = query.where(Lot.status == filters.status)
    if filters.price_per_sqm_min is not None:
        query = query.where(Lot.price / func.nullif(Lot.area, 0) >= filters.price_per_sqm_min)
    if filters.price_per_sqm_max is not None:
        query = query.where(Lot.price / func.nullif(Lot.area, 0) <= filters.price_per_sqm_max)

    total = db.execute(select(func.count()).select_from(query.subquery())).scalar_one()

    sort_column = _SORT_COLUMNS[filters.sort_by]
    sort_column = sort_column.desc() if filters.sort_dir == SortDirection.DESC else sort_column.asc()
    query = query.order_by(sort_column).offset((filters.page - 1) * filters.page_size).limit(filters.page_size)

    items = list(db.execute(query).scalars().all())
    return items, total


def bulk_create(db: Session, set_id: int, parsed_lots: list[ParsedLot]) -> None:
    db.bulk_insert_mappings(
        Lot,
        [
            {
                "external_id": lot.external_id,
                "set_id": set_id,
                "project_name": lot.project_name,
                "address": lot.address,
                "rooms": lot.rooms,
                "area": lot.area,
                "floor": lot.floor,
                "price": lot.price,
                "price_base": lot.price_base,
                "status": lot.status,
            }
            for lot in parsed_lots
        ],
    )
