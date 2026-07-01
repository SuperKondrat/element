from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import BookingStatus
from app.schemas.contact import ContactBase


class BookingCreate(ContactBase):
    lot_id: int


class BookingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_id: int
    contact_name: str
    contact_phone: str | None
    contact_email: str | None
    status: BookingStatus
    created_at: datetime
