from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import BookingStatus


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lot_id: Mapped[int] = mapped_column(
        ForeignKey("lots.id", ondelete="CASCADE"), nullable=False, index=True
    )

    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    status: Mapped[BookingStatus] = mapped_column(
        SqlEnum(BookingStatus, name="booking_status", native_enum=False, length=20),
        nullable=False,
        default=BookingStatus.ACTIVE,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lot: Mapped["Lot"] = relationship()
