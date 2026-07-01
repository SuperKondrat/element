from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import ApplicationStatus


class Application(Base):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    lot_id: Mapped[int | None] = mapped_column(
        ForeignKey("lots.id", ondelete="SET NULL"), nullable=True, index=True
    )

    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    status: Mapped[ApplicationStatus] = mapped_column(
        SqlEnum(ApplicationStatus, name="application_status", native_enum=False, length=20),
        nullable=False,
        default=ApplicationStatus.NEW,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    lot: Mapped["Lot | None"] = relationship()
