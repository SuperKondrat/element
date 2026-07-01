from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy import Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.enums import LotStatus


class Lot(Base):
    __tablename__ = "lots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    set_id: Mapped[int] = mapped_column(
        ForeignKey("lot_sets.id", ondelete="CASCADE"), nullable=False, index=True
    )

    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    rooms: Mapped[int] = mapped_column(Integer, nullable=False)
    area: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    price_base: Mapped[float] = mapped_column(Numeric(14, 2), nullable=False)
    status: Mapped[LotStatus] = mapped_column(
        SqlEnum(LotStatus, name="lot_status", native_enum=False, length=20),
        nullable=False,
        default=LotStatus.FOR_SALE,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    lot_set: Mapped["LotSet"] = relationship(back_populates="lots")

    @property
    def price_per_sqm(self) -> float | None:
        if not self.area:
            return None
        return round(float(self.price) / float(self.area), 2)
