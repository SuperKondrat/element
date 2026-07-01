from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.lot_set import LotSet


def create(db: Session, name: str, lots_count: int) -> LotSet:
    lot_set = LotSet(name=name, lots_count=lots_count, is_active=False)
    db.add(lot_set)
    db.flush()
    return lot_set


def get_by_id(db: Session, set_id: int) -> LotSet | None:
    return db.get(LotSet, set_id)


def get_active(db: Session) -> LotSet | None:
    return db.execute(select(LotSet).where(LotSet.is_active.is_(True))).scalar_one_or_none()


def list_all(db: Session) -> list[LotSet]:
    return list(db.execute(select(LotSet).order_by(LotSet.uploaded_at.desc())).scalars().all())


def deactivate_all(db: Session) -> None:
    db.execute(update(LotSet).where(LotSet.is_active.is_(True)).values(is_active=False))
