from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.enums import BookingStatus
from app.schemas.contact import ContactBase


def create(db: Session, lot_id: int, contact: ContactBase) -> Booking:
    booking = Booking(
        lot_id=lot_id,
        contact_name=contact.contact_name,
        contact_phone=contact.contact_phone,
        contact_email=contact.contact_email,
        status=BookingStatus.ACTIVE,
    )
    db.add(booking)
    db.flush()
    return booking


def list_all(db: Session) -> list[Booking]:
    return list(db.execute(select(Booking).order_by(Booking.created_at.desc())).scalars().all())
