from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.enums import LotStatus
from app.repositories import bookings as bookings_repo
from app.repositories import lots as lots_repo
from app.schemas.booking import BookingCreate
from app.services.exceptions import LotNotAvailableError, LotNotFoundError


def create_booking(db: Session, data: BookingCreate) -> Booking:
    """Забронировать лот. Правило (п.3.5 ТЗ): бронировать можно только лот
    в статусе «в продаже»; после брони лот переходит в «забронирован»;
    повторно забронировать нельзя.

    Лот блокируется SELECT ... FOR UPDATE, чтобы две параллельные брони
    одного лота не проскочили обе мимо проверки статуса.
    """
    lot = lots_repo.get_for_update(db, data.lot_id)
    if lot is None:
        raise LotNotFoundError(data.lot_id)
    if lot.status != LotStatus.FOR_SALE:
        raise LotNotAvailableError(data.lot_id)

    booking = bookings_repo.create(db, lot_id=data.lot_id, contact=data)
    lot.status = LotStatus.RESERVED
    db.commit()
    db.refresh(booking)
    return booking


def list_bookings(db: Session) -> list[Booking]:
    return bookings_repo.list_all(db)
