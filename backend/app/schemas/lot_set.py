from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LotSetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    uploaded_at: datetime
    lots_count: int
    is_active: bool


class LotSetUploadResponse(LotSetRead):
    skipped_count: int
