from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ApplicationStatus
from app.schemas.contact import ContactBase


class ApplicationCreate(ContactBase):
    lot_id: int | None = None
    comment: str | None = Field(default=None, max_length=4000)


class ApplicationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lot_id: int | None
    contact_name: str
    contact_phone: str | None
    contact_email: str | None
    comment: str | None
    status: ApplicationStatus
    created_at: datetime
