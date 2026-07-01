import pytest
from sqlalchemy.orm import Session

from app.models.enums import LotStatus
from app.models.lot import Lot
from app.models.lot_set import LotSet
from app.schemas.booking import BookingCreate
from app.services import bookings as bookings_service
from app.services.exceptions import LotNotAvailableError, LotNotFoundError


def _make_lot(db: Session, status: LotStatus = LotStatus.FOR_SALE) -> Lot:
    lot_set = LotSet(name="test-set", lots_count=1, is_active=True)
    db.add(lot_set)
    db.flush()

    lot = Lot(
        external_id="ext-1",
        set_id=lot_set.id,
        project_name="ЖК Тест",
        address="г. Тест, ул. Тестовая, 1",
        rooms=2,
        area=45.5,
        floor=3,
        price=10_000_000,
        price_base=11_000_000,
        status=status,
    )
    db.add(lot)
    db.flush()
    return lot


def test_booking_moves_lot_to_reserved(db_session: Session):
    lot = _make_lot(db_session)

    booking = bookings_service.create_booking(
        db_session,
        BookingCreate(lot_id=lot.id, contact_name="Иван", contact_phone="+7 (999) 000-00-00"),
    )

    assert booking.lot_id == lot.id
    assert lot.status == LotStatus.RESERVED


def test_cannot_book_already_reserved_lot(db_session: Session):
    lot = _make_lot(db_session, status=LotStatus.RESERVED)

    with pytest.raises(LotNotAvailableError):
        bookings_service.create_booking(
            db_session,
            BookingCreate(lot_id=lot.id, contact_name="Иван", contact_phone="+7 (999) 000-00-00"),
        )


def test_cannot_book_sold_lot(db_session: Session):
    lot = _make_lot(db_session, status=LotStatus.SOLD)

    with pytest.raises(LotNotAvailableError):
        bookings_service.create_booking(
            db_session,
            BookingCreate(lot_id=lot.id, contact_name="Иван", contact_phone="+7 (999) 000-00-00"),
        )


def test_booking_unknown_lot_raises_not_found(db_session: Session):
    with pytest.raises(LotNotFoundError):
        bookings_service.create_booking(
            db_session,
            BookingCreate(lot_id=999_999, contact_name="Иван", contact_phone="+7 (999) 000-00-00"),
        )


def test_second_booking_attempt_after_first_fails(db_session: Session):
    lot = _make_lot(db_session)

    bookings_service.create_booking(
        db_session,
        BookingCreate(lot_id=lot.id, contact_name="Иван", contact_phone="+7 (999) 000-00-00"),
    )

    with pytest.raises(LotNotAvailableError):
        bookings_service.create_booking(
            db_session,
            BookingCreate(lot_id=lot.id, contact_name="Пётр", contact_email="petr@example.com"),
        )
