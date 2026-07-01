from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import LotStatus


class SortField(str, Enum):
    PRICE = "price"
    PRICE_PER_SQM = "price_per_sqm"
    AREA = "area"
    FLOOR = "floor"
    CREATED_AT = "created_at"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


class LotFilter(BaseModel):
    project_name: str | None = None
    rooms: int | None = None
    status: LotStatus | None = None
    price_per_sqm_min: float | None = None
    price_per_sqm_max: float | None = None

    sort_by: SortField = SortField.CREATED_AT
    sort_dir: SortDirection = SortDirection.DESC

    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class LotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    external_id: str
    set_id: int
    project_name: str
    address: str
    rooms: int
    area: float
    floor: int
    price: float
    price_base: float
    price_per_sqm: float | None
    status: LotStatus
    created_at: datetime
    updated_at: datetime


class LotListResponse(BaseModel):
    items: list[LotRead]
    total: int
    page: int
    page_size: int
