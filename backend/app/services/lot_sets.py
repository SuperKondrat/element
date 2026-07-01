from sqlalchemy.orm import Session

from app.models.lot_set import LotSet
from app.repositories import lot_sets as lot_sets_repo
from app.repositories import lots as lots_repo
from app.services.exceptions import LotSetNotFoundError
from app.services.feed_parser import FeedParseError, parse_feed

__all__ = ["FeedParseError"]


def upload_feed(db: Session, filename: str, content: bytes) -> tuple[LotSet, int]:
    """Парсит фид и создаёт новый набор лотов. Набор не становится активным
    автоматически — активация отдельным действием (см. п.2 ТЗ)."""
    result = parse_feed(content)

    lot_set = lot_sets_repo.create(db, name=filename, lots_count=len(result.lots))
    lots_repo.bulk_create(db, lot_set.id, result.lots)
    db.commit()
    db.refresh(lot_set)
    return lot_set, result.skipped_count


def list_sets(db: Session) -> list[LotSet]:
    return lot_sets_repo.list_all(db)


def activate_set(db: Session, set_id: int) -> LotSet:
    lot_set = lot_sets_repo.get_by_id(db, set_id)
    if lot_set is None:
        raise LotSetNotFoundError(set_id)

    lot_sets_repo.deactivate_all(db)
    lot_set.is_active = True
    db.commit()
    db.refresh(lot_set)
    return lot_set
